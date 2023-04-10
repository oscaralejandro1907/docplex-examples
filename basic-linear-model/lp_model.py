# This is a sample Python script.

# Importing docplex package
from docplex.mp.model import Model

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Create an optimization model
    opt_mod = Model(name="Linear Program")

    # Add continuous decision variables to a model
    x = opt_mod.continuous_var(name='x', lb=0)
    y = opt_mod.continuous_var(name='y', lb=0)

    # Define the objective function
    obj_fn = 5*x + 4*y
    opt_mod.set_objective('min', obj_fn)

    # Add the constraints
    c1 = opt_mod.add_constraint(x + y >= 8, ctname='constraint1')
    c2 = opt_mod.add_constraint(2*x + y >= 10, ctname='constraint2')
    c3 = opt_mod.add_constraint(x + 4*y >= 11, ctname='constraint3')

    # Solve the model
    opt_mod.solve()

    # Output the result
    opt_mod.print_solution()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
