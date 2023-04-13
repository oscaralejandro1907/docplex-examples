# This is a sample Python script.

import numpy as np
from docplex.mp.model import Model

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Create input data (cost matrix)
    n = 4
    cost_matrix = np.random.randint(1, 10, (n, n))  # generate pseudo random integer number within a range

    # Creating the model
    assignment_model = Model('Linear Assignment')

    # Creating decision variables
    # x_ij if worker i performs task j
    x = assignment_model.binary_var_matrix(cost_matrix.shape[0],cost_matrix.shape[1], name='x')

    # Defining objective function
    obj_fn = sum(cost_matrix[i, j]*x[i, j] for i in range(cost_matrix.shape[0]) for j in range(cost_matrix.shape[1]))
    assignment_model.set_objective('min', obj_fn)

    # Adding the Constraints
    # For each worker, only one task j must be assigned
    for i in range(cost_matrix.shape[0]):
        assignment_model.add_constraint(sum(x[i, j] for j in range(cost_matrix.shape[1])) == 1,
                                        ctname=f"workload_worker_{i}")

    # For each task j, it must be done by one worker
    for j in range(cost_matrix.shape[1]):
        assignment_model.add_constraint(sum(x[i, j] for i in range(cost_matrix.shape[0])) == 1,
                                        ctname=f"task_execution_{j}")

    # Inspect Model by printing lp model
    print("Cost Matrix:\n", cost_matrix)
    print(assignment_model.export_as_lp_string())

    # Solve Model and output the solution
    assignment_model.solve()

    # Get Values
    assignment_model.print_solution()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
