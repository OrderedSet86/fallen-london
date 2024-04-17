import itertools
import math
from collections import Counter, deque
from copy import deepcopy
from dataclasses import dataclass

from tabulate import tabulate
from termcolor import colored

from game import Activity, GameTree, LIST_OF_ACTIVITIES


INTENT = {
    # "favour in high places": 2.5,
    # "personal recommendation": 1,
    # "comprehensive bribe": 1,
    # "book of hidden bodies": 2,

    # "whispered hint": 80000,

    # "drop of prisoner's honey": 40000,

    # "brilliant soul": 1250,
    # "bazaar permit": 1,
    "legal document": 1,
    # "making waves": 1,

    # "strong-backed labour": 1,
    # "whirring contraption": 1,
}
TOLERANCE = 0.001
TRY_TO_SELL_OUTPUTS = True
SOLUTION_BORDER = '-' * 50
MERGE_SOLUTION_SEQUENCES = True
SOLUTIONS_TO_KEEP = 3

# TODO: Unimplemented
HAVE = {
    "echoes": 34.84,
}
COST = {
    "action": 1,
}
MAX_UNSOLVED_INPUTS = 3


@dataclass
class ActivityQuant:
    activity: Activity
    quantity: float

    def __hash__(self):
        return hash(self.activity)

    # Python does equality checks for hashes in dictionaries too (to mitigate collisions)
    # So if I want to hash by activity AND str, this is needed
    def __eq__(self, other):
        if isinstance(other, str):
            return self.activity.description == other
        else:
            return super().__eq__(other)


def toClosestInt(x):
    if math.isclose(x, int(x), abs_tol=TOLERANCE):
        return int(x)
    else:
        return x


def bold(s):
    return colored(s, attrs=['bold'])


class Solution:
    # An ordered ActivityGroup (stack order)
    def __init__(self, activity_sequence: list[ActivityQuant] = None):
        if activity_sequence is None:
            activity_sequence = []
        self.activity_sequence = activity_sequence
        self.total_actions = 0
        self.total_inputs = Counter()
        self.total_outputs = Counter()
        self._populateTotals()
    
    def __repr__(self):
        return f'Solution({self.activity_sequence=})'

    def _populateTotals(self):
        self.total_actions = 0
        self.total_inputs = Counter()
        self.total_outputs = Counter()

        for aq in self.activity_sequence:
            self.total_actions += aq.activity.actions * aq.quantity
            for inp, inp_quantity in aq.activity.inputs.items():
                self.total_inputs[inp] = self.total_inputs[inp] + inp_quantity * aq.quantity
            for out, out_quantity in aq.activity.outputs.items():
                self.total_outputs[out] = self.total_outputs[out] + out_quantity * aq.quantity
        
        # Merge inputs and outputs
        # TODO: Optimize away this merge
        input_deletion_keys = []
        for k in self.total_inputs:
            if k in self.total_outputs:
                output_quant = self.total_outputs[k]
                if self.total_inputs[k] > output_quant:
                    self.total_inputs[k] = self.total_inputs[k] - output_quant
                    del self.total_outputs[k]
                else:
                    input_deletion_keys.append(k)
                    self.total_outputs[k] = self.total_outputs[k] - self.total_inputs[k]
        for dk in input_deletion_keys:
            del self.total_inputs[dk]

    def addActivity(self, aq: ActivityQuant):
        self.activity_sequence.append(aq)
        self._populateTotals() # TODO: Optimization
    
    def pprint(self, sells=None):
        # Combine inputs and outputs into single dict
        inverted_inputs = {k:-v for k,v in self.total_inputs.items()}
        combined = deepcopy(self.total_outputs)
        combined.update(inverted_inputs)
        # Remove elements near zero and make elements near int into int
        deletion_keys = []
        for item, quantity in combined.items():
            combined[item] = toClosestInt(quantity)
            if quantity == 0:
                deletion_keys.append(item)
        for dk in deletion_keys:
            del combined[dk]

        print(f'{bold("Actions:")} {round(toClosestInt(self.total_actions), 2)}')
        print(bold('Sequence:'))
        for aq in self.activity_sequence[::-1]:
            print(f'   {round(toClosestInt(aq.quantity), 2)}x {aq.activity.description}')
        print(tabulate(
            [
                (
                    k,
                    colored(v, 'green') if v > 0 else colored(v, 'red')
                )
                for k,v
                in sorted(combined.items(), key=lambda x: x[1])
            ],
            headers=[bold('Item'), bold('Quantity')],
            tablefmt='fancy_grid'
        ))

        if sells is not None and sells != []:
            print(bold('Sold:'))
            for iquant, item, echo_value in sells:
                print(f'   {round(toClosestInt(iquant), 2)}x {item} for {round(toClosestInt(echo_value), 2)} echoes')


def solve(have, intent, cost):
    tree = GameTree()

    # Always use cartesian product merges instead of BFS
    # This way it is picking an entire set of actions instead of just one
    # As long as there are no cycles, this should work
    curr_solutions = deque([(Solution(), 1)])
    curr_solutions[0][0].total_inputs.update(INTENT)
    finished_solutions = []
    while len(curr_solutions) > 0:
        soln, _ = curr_solutions.popleft()

        # Find all possible producers for each input
        base_activity_groups = {}
        for want_ingredient, want_quantity in soln.total_inputs.items():
            if want_ingredient == 'echoes':
                continue
            base_activity_groups[want_ingredient] = []

            for activity in tree._output_index[want_ingredient]:
                aq = ActivityQuant(activity, want_quantity / activity.outputs[want_ingredient])
                base_activity_groups[want_ingredient].append(aq)

        all_action_sets = list(itertools.product(*[
            base_activity_groups[want_ingredient] for want_ingredient in base_activity_groups
            if base_activity_groups[want_ingredient] != []
        ]))

        if all_action_sets == [()]:
            # No possible producers left
            finished_solutions.append(soln)
        else:
            for action_set in all_action_sets:
                new_soln = deepcopy(soln)
                for aq in action_set:
                    new_soln.addActivity(aq)
                curr_solutions.append((new_soln, 1))

    if TRY_TO_SELL_OUTPUTS:
        # Figure out activities that are item -> echoes only
        bazaar_sells: dict[str, Activity] = {}
        for activity in LIST_OF_ACTIVITIES:
            if len(activity.outputs) == 1 and 'echoes' in activity.outputs:
                bazaar_sells[list(activity.inputs)[0]] = activity

        sell_solutions = []
        for soln in finished_solutions:
            sold_items = []
            for out, out_quantity in soln.total_outputs.items():
                if out in bazaar_sells:
                    bazaar_activity = bazaar_sells[out]
                    echo_value = out_quantity * (bazaar_activity.outputs['echoes'] / bazaar_activity.inputs[out])
                    sold_items.append((out_quantity, out, echo_value))
        
            total_sell_value = 0
            for iquant, item, echo_value in sold_items:
                total_sell_value += echo_value
                del soln.total_outputs[item]
            soln.total_outputs['echoes'] += total_sell_value
            sell_solutions.append(sold_items)

    if MERGE_SOLUTION_SEQUENCES:
        # Prefer "first" activities in solution
        for solution in finished_solutions:
            locations = {}
            repeats = 0
            for idx, activity_quant in enumerate(solution.activity_sequence):
                activity = activity_quant.activity
                if activity.description in locations:
                    repeats += 1
                    # Merge the two
                    solution.activity_sequence[locations[activity.description]].quantity += activity_quant.quantity
                    solution.activity_sequence[idx] = None
                else:
                    locations[activity.description] = idx
            solution.activity_sequence = [x for x in solution.activity_sequence if x is not None]

    finished_solutions.sort(key=lambda x: x.total_actions)
    finished_solutions = finished_solutions[:SOLUTIONS_TO_KEEP]

    print(SOLUTION_BORDER)
    for idx, solution in enumerate(finished_solutions):
        solution.pprint(sells=sell_solutions[idx] if TRY_TO_SELL_OUTPUTS else None)
        print(SOLUTION_BORDER)


if __name__ == '__main__':
    solve(HAVE, INTENT, COST)