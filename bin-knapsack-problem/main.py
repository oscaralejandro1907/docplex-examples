# This is a sample Python script.

import itertools
from docplex.mp.model import Model  # Importing docplex package


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

class Object():
    id = itertools.count()

    def __init__(self, w, p):
        self.id = next(Object.id)
        self.weight = w  # weight of the object
        self.profit = p  # profit for taking the object


class Instance():
    def __init__(self):
        self.capacity = 15  # capacity of the knapsack
        self.objects = set()  # set of objects

        # Define objects
        obj0 = Object(4, 10)
        obj1 = Object(2, 5)
        obj2 = Object(5, 18)
        obj3 = Object(4, 12)
        obj4 = Object(5, 15)
        obj5 = Object(1, 1)
        obj6 = Object(3, 2)
        obj7 = Object(5, 8)

        # Add objects to the set
        self.objects.add(obj0)
        self.objects.add(obj1)
        self.objects.add(obj2)
        self.objects.add(obj3)
        self.objects.add(obj4)
        self.objects.add(obj5)
        self.objects.add(obj6)
        self.objects.add(obj7)


class Solver():
    def __init__(self, instance):
        self.instance = instance  # Get instance data
        self.n = len(self.instance.objects)  # total elements

        # Convert set to list (ordered by id) since set objects are unordered and not subscriptable
        # (non-iterable to use in a 'for' loop for example)
        self.listObjects = sorted(self.instance.objects, key=lambda x: x.id)

        # Create optimization model
        knapsack_model = Model('knapsack')

        # Add binary decision variables
        x = knapsack_model.binary_var_list(self.n, name='x')

        # Define the objective function
        obj_fn = sum(self.listObjects[i].profit * x[i] for i in range(self.n))
        knapsack_model.set_objective('max', obj_fn)

        # Add the constraints
        knapsack_model.add_constraint(sum(self.listObjects[i].weight * x[i] for i in range(self.n)) <=
                                      self.instance.capacity)

        # Solve the model and output the solution
        knapsack_model.solve()
        knapsack_model.print_solution()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = Instance()
    solver = Solver(data)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
