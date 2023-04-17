import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from docplex.mp.model import Model


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

class Instance:
    def __init__(self, file):
        # Reading data (point 1 is the depot)
        self.df_dem = pd.read_excel(file, sheet_name='demands', header=1, index_col=0)
        self.df_coord = pd.read_excel(file, sheet_name='coordinates', header=1, index_col=0)

        assert len(self.df_dem) == len(self.df_coord)

        self.Q = 90  # capacity of a truck  10nodes->Q=15 ; 30nodes -> Q=90
        self.clients = self.df_dem.index[1:]  # all nodes except the depot (N)
        self.vertices = self.df_dem.index  # all nodes of the graph (V)
        self.arcs = [(i, j) for i in self.df_dem.index for j in self.df_dem.index if i != j]

    def distance(self, origin, destination):  # (int, int) pass the indexes
        return np.hypot(self.df_coord.loc[origin, 'X'] - self.df_coord.loc[destination, 'X'],
                        self.df_coord.loc[origin, 'Y'] - self.df_coord.loc[destination, 'Y'])


class Solution:
    def __init__(self, instance):
        self.instance = instance

        self.active_arcs = list()
        self.routes = dict()


class Solver:
    def __init__(self, instance):
        self.instance = instance

        # Create optimization model
        self.model = Model('cvrp')

        # Add decision variables
        # binary variables representing a travel from point i to j
        self.x = self.model.binary_var_dict(self.instance.arcs, name='x')

        # continuous variables representing the cumulative demand up to a point
        self.u = self.model.continuous_var_dict(self.instance.clients, ub=self.instance.Q, name='u')

        # Define objective function
        obj_fn = sum(self.instance.distance(i, j) * self.x[i, j] for i, j in self.instance.arcs)
        self.model.set_objective('min', obj_fn)

        # Add the constraints
        # At node i, go to one node exactly once
        for i in self.instance.clients:
            self.model.add_constraint(sum(self.x[i, j] for j in self.instance.vertices if j != i) == 1,
                                      ctname=f"Outflow_from_node_{i}")

        # To reach node j, come from one node
        for j in self.instance.clients:
            self.model.add_constraint(sum(self.x[i, j] for i in self.instance.vertices if i != j) == 1,
                                      ctname=f"Inflow_to_node_{j}")

        # Sub-tour elimination
        for i, j in self.instance.arcs:
            if i != 1 and j != 1:  # not the depot
                self.model.add_indicator(self.x[i, j], self.u[i] + self.instance.df_dem.loc[j, 'demand'] == self.u[j],
                                         name=f"Sub_tour_elimination_arc_{i}_{j}")

        # Lower bound of u variables
        for i in self.instance.clients:
            self.model.add_constraint(self.u[i] >= self.instance.df_dem.loc[i, 'demand'],
                                      ctname=f"Lower_bound_u_{i}")

        print(self.model.export_as_lp_string())
        print(self.model.print_information())

    def solve(self):
        self.model.parameters.timelimit = 60  # seconds

        # Solve Model and output the solution
        model_solution = self.model.solve(log_output=True)

        print(model_solution.solve_status)
        print(self.model.print_solution())
        print(self.model.solve_details)

    def get_solution(self):
        solution = Solution(self.instance)  # init solution object
        solution.active_arcs = [a for a in self.instance.arcs if self.x[a].solution_value > 0.9]

        remaining_arcs = solution.active_arcs.copy()
        current_route = 1

        while len(remaining_arcs) != 0:

            x, y = remaining_arcs[0]
            if x == 1:
                solution.routes[current_route] = [(x, y)]
                current_route += 1
                remaining_arcs.remove(remaining_arcs[0])
            else:
                for route in solution.routes:
                    last_y = solution.routes[route][-1][1]
                    if last_y == x:
                        solution.routes[route].append((x, y))
                        remaining_arcs.remove(remaining_arcs[0])
                        break  # break the for
                    elif route == len(solution.routes):
                        remaining_arcs += [remaining_arcs.pop(0)]  # move the arc to the end of the remaining list

        return solution


class Graph:
    def __init__(self, instance):
        self.instance = instance
        self.G = nx.Graph()
        self.active_arcs = list()

        for i, row in instance.df_coord.iterrows():
            self.G.add_node(i, pos=(row['X'], row['Y']))

        self.pos = nx.get_node_attributes(self.G, 'pos')
        # nx.draw(self.G, self.pos, with_labels=True)

    def draw_solution(self, active_arcs):
        color_map = []
        for node in self.G:
            if node == 1:
                color_map.append('red')
            else:
                color_map.append('skyblue')

        self.G.add_edges_from(active_arcs)

        nx.draw(self.G, self.pos, node_color=color_map, with_labels=True)
        plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = Instance('vrp_data_30.xlsx')
    slv = Solver(data)
    slv.solve()
    sol = slv.get_solution()
    graph = Graph(data).draw_solution(sol.active_arcs)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Data from https://www.youtube.com/watch?v=-DjyO0DK9Ys&t=623s
# Model from https://www.youtube.com/watch?v=-hGL39jdtQE&t=1256s
