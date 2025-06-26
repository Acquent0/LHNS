import types
import warnings
import sys

import numpy as np
from .get_instance import GetData
from .prompts import GetPrompts
from .prompts_black import GetPromptsBlack
import itertools
from typing import List, Tuple
from typing import Any, Callable
from func_timeout import func_set_timeout, FunctionTimedOut

TRIPLES = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 2), (0, 2, 1), (1, 1, 1), (2, 2, 2)]
INT_TO_WEIGHT = [0, 1, 1, 2, 2, 3, 3]

class ADMISSIBLESET():
    def __init__(self, problem_type='white-box'):
        getdate = GetData()
        self.problem_type = problem_type
        self.n, self.w = getdate.get_instances()
        self.prompts = GetPrompts()

        if self.problem_type == 'white-box':
            self.prompts = GetPrompts()
        else:
            self.prompts = GetPromptsBlack()



    def expand_admissible_set(self, pre_admissible_set: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
        """Expands a pre-admissible set into an admissible set."""
        num_groups = len(pre_admissible_set[0])
        admissible_set_15_10 = []
        for row in pre_admissible_set:
            rotations = [[] for _ in range(num_groups)]
            for i in range(num_groups):
                x, y, z = TRIPLES[row[i]]
                rotations[i].append((x, y, z))
                if not x == y == z:
                    rotations[i].append((z, x, y))
                    rotations[i].append((y, z, x))
            product = list(itertools.product(*rotations))
            concatenated = [sum(xs, ()) for xs in product]
            admissible_set_15_10.extend(concatenated)
        return admissible_set_15_10

    def get_surviving_children(self, extant_elements, new_element, valid_children):
        """Returns the indices of `valid_children` that remain valid after adding `new_element` to `extant_elements`."""
        bad_triples = {(0, 0, 0), (0, 1, 1), (0, 2, 2), (0, 3, 3), (0, 4, 4), (0, 5, 5), (0, 6, 6), (1, 1, 1),
                       (1, 1, 2),
                       (1, 2, 2), (1, 2, 3), (1, 2, 4), (1, 3, 3), (1, 4, 4), (1, 5, 5), (1, 6, 6), (2, 2, 2),
                       (2, 3, 3),
                       (2, 4, 4), (2, 5, 5), (2, 6, 6), (3, 3, 3), (3, 3, 4), (3, 4, 4), (3, 4, 5), (3, 4, 6),
                       (3, 5, 5),
                       (3, 6, 6), (4, 4, 4), (4, 5, 5), (4, 6, 6), (5, 5, 5), (5, 5, 6), (5, 6, 6), (6, 6, 6)}

        # Compute.
        valid_indices = []
        for index, child in enumerate(valid_children):
            # Invalidate based on 2 elements from `new_element` and 1 element from a
            # potential child.
            if all(INT_TO_WEIGHT[x] <= INT_TO_WEIGHT[y]
                   for x, y in zip(new_element, child)):
                continue
            # Invalidate based on 1 element from `new_element` and 2 elements from a
            # potential child.
            if all(INT_TO_WEIGHT[x] >= INT_TO_WEIGHT[y]
                   for x, y in zip(new_element, child)):
                continue
            # Invalidate based on 1 element from `extant_elements`, 1 element from
            # `new_element`, and 1 element from a potential child.
            is_invalid = False
            for extant_element in extant_elements:
                if all(tuple(sorted((x, y, z))) in bad_triples
                       for x, y, z in zip(extant_element, new_element, child)):
                    is_invalid = True
                    break
            if is_invalid:
                continue

            valid_indices.append(index)
        return valid_indices

    def solve(self, n: int, w: int, priority) -> Tuple[np.ndarray, np.ndarray]:
        """Generates a symmetric constant-weight admissible set I(n, w)."""
        num_groups = n // 3
        assert 3 * num_groups == n

        # Compute the scores of all valid (weight w) children.
        valid_children = []
        for child in itertools.product(range(7), repeat=num_groups):
            weight = sum(INT_TO_WEIGHT[x] for x in child)
            if weight == w:
                valid_children.append(np.array(child, dtype=np.int32))

        if self.problem_type == 'white-box':
            valid_scores = np.array([
                priority.priority(sum([TRIPLES[x] for x in xs], ()), n, w)
                for xs in valid_children])
        else:
            valid_scores = np.array([
                priority.heuristics(sum([TRIPLES[x] for x in xs], ()), n, w)
                for xs in valid_children])

        # Greedy search guided by the scores.
        pre_admissible_set = np.empty((0, num_groups), dtype=np.int32)
        while valid_children:
            max_index = np.argmax(valid_scores)
            max_child = valid_children[max_index]
            surviving_indices = self.get_surviving_children(pre_admissible_set, max_child, valid_children)
            valid_children = [valid_children[i] for i in surviving_indices]
            valid_scores = valid_scores[surviving_indices]

            pre_admissible_set = np.concatenate([pre_admissible_set, max_child[None]], axis=0)

        return pre_admissible_set, np.array(self.expand_admissible_set(pre_admissible_set))

    # @func_set_timeout(100)
    def evaluateGreedy(self, n: int, w: int, priority) -> int:
        """Returns the size of the expanded admissible set."""
        _, admissible_set_15_10 = self.solve(n, w, priority)
        return -(len(admissible_set_15_10) - 3003)

    def evaluate(self, code_string):
        try:
            # Suppress warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # Create a new module object
                heuristic_module = types.ModuleType("heuristic_module")

                # Execute the code string in the new module's namespace
                exec(code_string, heuristic_module.__dict__)

                # Add the module to sys.modules so it can be imported
                sys.modules[heuristic_module.__name__] = heuristic_module

                fitness = self.evaluateGreedy(self.n, self.w, heuristic_module)

                return fitness
        except FunctionTimedOut or Exception as e:
            return None
