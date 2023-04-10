# This is a sample Python script.

# Importing docplex package
from docplex.mp.model import Model

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Create an optimization model
    milp_model = Model(name="MILP")

    # Add decision variables
    x = milp_model.binary_var(name= 'x')
    y = milp_model.continuous_var(name='y', lb=0)
    z = milp_model.integer_var(name='z', lb=0)

    # Add the constraints
    c1 = milp_model.add_constraint(x + 2*y + z <= 4, ctname="constraint1")
    c2 = milp_model.add_constraint(y + 2 * z <= 5, ctname="constraint2")
    c3 = milp_model.add_constraint(x + y >= 1, ctname="constraint3")

    # Define objective function
    obj_fn = z*x + y + 3*z
    milp_model.set_objective('max', obj_fn)

    # Solve the model
    milp_model.solve()

    # Output the result
    milp_model.print_solution()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
