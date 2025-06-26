import itertools
import json
import multiprocessing
import os
import sys
from typing import Any, Callable

import numpy as np

sys.path.append('../')
# from my_task import _evaluator_accelerate

TRIPLES = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 2), (0, 2, 1), (1, 1, 1), (2, 2, 2)]
INT_TO_WEIGHT = [0, 1, 1, 2, 2, 3, 3]


def expand_admissible_set(
        pre_admissible_set: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
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


def get_surviving_children(extant_elements, new_element, valid_children):
    """Returns the indices of `valid_children` that remain valid after adding `new_element` to `extant_elements`."""
    bad_triples = {(0, 0, 0), (0, 1, 1), (0, 2, 2), (0, 3, 3), (0, 4, 4), (0, 5, 5), (0, 6, 6), (1, 1, 1), (1, 1, 2),
                   (1, 2, 2), (1, 2, 3), (1, 2, 4), (1, 3, 3), (1, 4, 4), (1, 5, 5), (1, 6, 6), (2, 2, 2), (2, 3, 3),
                   (2, 4, 4), (2, 5, 5), (2, 6, 6), (3, 3, 3), (3, 3, 4), (3, 4, 4), (3, 4, 5), (3, 4, 6), (3, 5, 5),
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


def solve(n: int, w: int, priority: Callable) -> tuple[np.ndarray, np.ndarray]:
    """Generates a symmetric constant-weight admissible set I(n, w)."""
    num_groups = n // 3
    assert 3 * num_groups == n

    # Compute the scores of all valid (weight w) children.
    valid_children = []
    for child in itertools.product(range(7), repeat=num_groups):
        weight = sum(INT_TO_WEIGHT[x] for x in child)
        if weight == w:
            valid_children.append(np.array(child, dtype=np.int32))
    valid_scores = np.array([
        priority(sum([TRIPLES[x] for x in xs], ()), n, w)
        for xs in valid_children])

    # Greedy search guided by the scores.
    pre_admissible_set = np.empty((0, num_groups), dtype=np.int32)
    while valid_children:
        max_index = np.argmax(valid_scores)
        max_child = valid_children[max_index]
        surviving_indices = get_surviving_children(pre_admissible_set, max_child,
                                                   valid_children)
        valid_children = [valid_children[i] for i in surviving_indices]
        valid_scores = valid_scores[surviving_indices]

        pre_admissible_set = np.concatenate([pre_admissible_set, max_child[None]],
                                            axis=0)

    return pre_admissible_set, np.array(expand_admissible_set(pre_admissible_set))


def evaluate(n: int, w: int, priority) -> int:
    """Returns the size of the expanded admissible set."""
    _, admissible_set_15_10 = solve(n, w, priority)
    return -(len(admissible_set_15_10) - 3003)


test = '''
def pri_or_ity(el: tuple[int, ...], n: int, w: int) -> float:
    """Returns the priority with which we want to add `el` to the set."""
    return 0.0
'''


class Evaluation:
    _total = 0

    def __init__(self, verbose=False, numba_accelerate=False, timeout=10):
        self._verbose = verbose
        self._numba_accelerate = numba_accelerate
        self._timeout = timeout
        self._dirpath = path = os.path.dirname(__file__)
        os.makedirs(os.path.join(path, 'samples'), exist_ok=True)

    def evaluate(self, function):
        if Evaluation._total >= 10_000:
            sys.exit(0)
        result = self._evaluate(function)
        Evaluation._total += 1

        with open(os.path.join(self._dirpath, 'samples', f'samples_{Evaluation._total}.json'), 'w') as f:
            content = {
                'function': function,
                'score': result
            }
            json.dump(content, f)
            f.close()

        return result

    def _evaluate(self, function) -> Any:
        try:
            function = _evaluator_accelerate.add_import_package_statement(function, 'numpy', 'np')
            function_name = _evaluator_accelerate._extract_function_name(function)
            if self._numba_accelerate:
                function = _evaluator_accelerate._add_numba_decorator(function, function_name)
            # compile the program, and maps the global func/var/class name to its address
            all_globals_namespace = {}
            # execute the program, map func/var/class to global namespace
            exec(function, all_globals_namespace)
            # get the pointer of 'function_to_run'
            func_pointer = all_globals_namespace[function_name]

            result_queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=self._compile_and_run_function,
                args=(func_pointer, result_queue)
            )

            process.start()
            process.join(timeout=self._timeout)
            if process.is_alive():
                # if the process is not finished in time, we consider the program illegal
                process.terminate()
                process.join()
                results = None
            else:
                if not result_queue.empty():
                    results = result_queue.get_nowait()
                else:
                    results = None
            return float(results)
        except Exception as e:
            # print(e)
            return None

    def _compile_and_run_function(self, function: Callable, result_queue):
        try:
            results = evaluate(15, 10, function)
            # the results must be int or float
            if not isinstance(results, (int, float)):
                result_queue.put(None)
                return
            result_queue.put(results)
        except Exception as e:
            # if raise any exception, we assume the execution failed
            result_queue.put(None)
