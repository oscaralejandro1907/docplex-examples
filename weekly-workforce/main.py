# This is a sample Python script.

from docplex.mp.model import Model  # Importing docplex package
import json

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


class Instance:
    def __init__(self):
        # Define days (1 week)
        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Enter shifts of each day
        self.shifts = ['morning', 'evening', 'night']  # 3 shifts of 8 hours
        # dict with day as key and list of its shifts as value
        self.days_shifts = {day: self.shifts for day in self.days}

        # Enter workers ids (name, number, ...)
        self.workers = ['Worker' + str(i) for i in range(1, 11)]  # 10 workers available, more than needed


class Solution:
    def __init__(self, instance):
        self.instance = instance

        self.workers_needed = []    # list with the required workers
        self.week_table = dict()    # dict with the optimal timetable
        self.workers_no_pref = []   # list with the non-satisfied workers (work on Sat but not on Sun)


class Solver:
    def __init__(self, instance):
        self.instance = instance

        # Create optimization model
        self.model = Model('weekly-workforce')

        # Add decision variables
        # binary variables representing if a worker is scheduled somewhere
        self.w = {(i, j, k): self.model.binary_var(name=f'w_{i}_{j}_{k}') for i in self.instance.workers
                  for j in self.instance.days
                  for k in self.instance.days_shifts[j]}

        # binary variables representing if a worker is necessary
        self.n = {i: self.model.binary_var(name=f'n_{i}') for i in self.instance.workers}

        # binary variables representing if a worker worked on sunday but not on saturday (avoid if possible)
        self.a = {i: self.model.binary_var(name=f'a_{i}') for i in self.instance.workers}

        # Define objective function
        c = len(self.instance.workers)
        obj_fn = sum(self.a[i] for i in self.instance.workers) + sum(c * self.n[i] for i in self.instance.workers)
        # we multiply the second term by a constant to make sure that it is the primary objective
        # since sum(a) is at most len(workers), len(workers) + 1 is a valid constant.
        self.model.set_objective('min', obj_fn)

        # Adding the Constraints
        # All shifts are assigned
        for day in self.instance.days:
            for shift in self.instance.days_shifts[day]:
                if day in self.instance.days[:-1] and shift in ['morning', 'evening']:
                    # weekdays' and Saturdays' day shifts have exactly two workers
                    self.model.add_constraint(sum(self.w[i, day, shift] for i in self.instance.workers) == 2,
                                              ctname=f"workforce_in_{day}_shift_{shift}")
                else:
                    # Sundays' and nights' shifts have exactly one worker
                    self.model.add_constraint(sum(self.w[i, day, shift] for i in self.instance.workers) == 1,
                                              ctname=f"workforce_in_{day}_shift_{shift}")

        # No more than 40 hours worked
        for worker in self.instance.workers:
            self.model.add_constraint(sum(8 * self.w[worker, day, shift] for day in self.instance.days
                                          for shift in self.instance.days_shifts[day]) <= 40,
                                      ctname=f"working_time_{worker}")

        # Rest between two shifts is of 12 hours (i.e., at least two shifts)
        for worker in self.instance.workers:
            for day in range(len(self.instance.days)):
                # if working in morning, cannot work again that day
                self.model.add_constraint(sum(self.w[worker, self.instance.days[day], shift]
                                              for shift in self.instance.days_shifts[self.instance.days[day]]) <= 1,
                                          ctname=f'Rest_for_{worker}_if_work_in_day_{day}_in_morning')

                # if working in evening, until next evening (note that after sunday comes next monday)
                self.model.add_constraint(sum(self.w[worker, self.instance.days[day], shift]
                                              for shift in ['evening', 'night']) +
                                          self.w[worker, self.instance.days[(day + 1) % 7], 'morning'] <= 1,
                                          ctname=f'Rest_for_{worker}_if_work_in_day_{day}_in_evening')

                # if working at night, until next night (note that after sunday comes next monday)
                self.model.add_constraint(self.w[worker, self.instance.days[day], 'night'] +
                                          sum(self.w[worker, self.instance.days[(day + 1) % 7], shift]
                                              for shift in ['morning', 'evening']) <= 1,
                                          ctname=f'Rest_for_{worker}_if_work_in_day_{day}_at_night')

        # Weekend working preference
        # if not working on sunday but working saturday 'a' must be 1; else will be zero
        # to reduce the obj function
        for worker in self.instance.workers:
            self.model.add_constraint(sum(self.w[worker, 'Sat', shift] for shift in self.instance.days_shifts['Sat']) -
                                      sum(self.w[worker, 'Sun', shift] for shift in self.instance.days_shifts['Sun']) <=
                                      self.a[worker], ctname=f'Weekend_preference_for_{worker}')

        # Preference to reduce workers
        # if any w[worker, ·, ·] is non-zero, n[worker] must be one; else is zero to reduce the obj function;
        # 10000 is to remark, but 5 was enough since max of 40 hours yields max of 5 shifts, the maximum possible sum.
        for worker in self.instance.workers:
            self.model.add_constraint(sum(self.w[worker, day, shift] for day in self.instance.days
                                          for shift in self.instance.days_shifts[day]) <= 10000 * self.n[worker],
                                      ctname=f'Reduce_assistance_of_{worker}_in_the_week')

        # Inspect Model by printing lp model
        print(self.model.export_as_lp_string())

    def solve(self):
        # Solve Model and output the solution
        sol = Solution(self.instance)
        self.model.solve()

        # Get Values in console
        self.model.print_solution()

        sol.workers_needed = self.get_workers_needed(self.n)
        sol.week_table = self.get_work_table(self.w)
        sol.workers_no_pref = self.get_no_preference(self.a)

        # Print solution
        print('Workers needed:')
        [print('  ' + worker) for worker in sol.workers_needed]

        print('Workers not satisfied by weekend condition:')
        [print('  ' + worker) for worker in sol.workers_no_pref]

        print('Work schedule:')
        print(json.dumps(sol.week_table, indent=2))

    def get_workers_needed(self, n):
        # Extract to a list the needed workers for the optimal solution
        workers_needed = []
        for worker in self.instance.workers:
            if n[worker].solution_value == 1:
                workers_needed.append(worker)
        return workers_needed

    def get_work_table(self, w):
        # Build a timetable of the week as a dictionary from the model's optimal solution
        week_table = {day: {shift: [] for shift in self.instance.days_shifts[day]} for day in self.instance.days}
        for worker in self.instance.workers:
            for day in self.instance.days:
                for shift in self.instance.days_shifts[day]:
                    if w[worker, day, shift].solution_value == 1:
                        week_table[day][shift].append(worker)
        return week_table

    def get_no_preference(self, a):
        # Extract to a list the workers not satisfied with their weekend preference
        return [worker for worker in self.instance.workers if a[worker].solution_value == 1]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = Instance()
    solver = Solver(data)
    solver.solve()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
