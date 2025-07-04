import numpy as np
import importlib
import pickle
from .get_instance import GetData
from .prompts import GetPrompts
from .prompts_black import GetPromptsBlack
import types
import warnings
import sys
from func_timeout import func_set_timeout, FunctionTimedOut

class BPONLINE():
    def __init__(self, problem_type='white-box'):
        getdate = GetData()
        self.problem_type = problem_type
        self.instances = {}
        for i in [5]:  # [1, 5]:
            data_file = 'problems/optimization/bp_online/test_dataset_{}k.pkl'.format(i)
            k_100 = getdate.read_dataset_from_file(data_file, 100)
            # k_500 = getdate.read_dataset_from_file(data_file, 500)

            self.instances.update(k_100)
            # self.instances.update(k_500)

        # self.instances = getdate.read_dataset_from_file('problems/optimization/bp_online/instances.pkl', 100)  # 5k_100
        getdate.datasets = self.instances
        self.instances, self.lb = getdate.get_instances()

        if self.problem_type == 'white-box':
            self.prompts = GetPrompts()
        else:
            self.prompts = GetPromptsBlack()

    def get_valid_bin_indices(self,item: float, bins: np.ndarray) -> np.ndarray:
        """Returns indices of bins in which item can fit."""
        return np.nonzero((bins - item) >= 0)[0]


    def online_binpack(self,items: tuple, bins: np.ndarray, alg):
        """Performs online binpacking of `items` into `bins`."""
        # Track which items are added to each bin.
        packing = [[] for _ in bins]
        # Add items to bins.
        n = 1
        for item in items:
            # Extract bins that have sufficient space to fit item.
            valid_bin_indices = self.get_valid_bin_indices(item, bins)
            # Score each bin based on heuristic.
            if self.problem_type == 'white-box':
                priorities = alg.score(item, bins[valid_bin_indices])
            else:
                priorities = alg.heuristics(item, bins[valid_bin_indices])
            # Add item to bin with highest priority.
            best_bin = valid_bin_indices[np.argmax(priorities)]
            bins[best_bin] -= item
            packing[best_bin].append(item)
            n=n+1
            
        # Remove unused bins from packing.
        packing = [bin_items for bin_items in packing if bin_items]
        return packing, bins


    # @funsearch.run
    @func_set_timeout(60)
    def evaluateGreedy(self,alg) -> float:
        # algorithm_module = importlib.import_module("ael_alg")
        # alg = importlib.reload(algorithm_module)  
        """Evaluate heuristic function on a set of online binpacking instances."""
        # List storing number of bins used for each instance.
        #num_bins = []
        # Perform online binpacking for each instance.
        # for name in instances:
        #     #print(name)

        instances_fiteness = []
        for name, dataset in self.instances.items():
            num_bins_list = []
            for _, instance in dataset.items():

                capacity = instance['capacity']
                items = np.array(instance['items'])

                # items = items/capacity
                # capacity = 1.0

                # Create num_items bins so there will always be space for all items,
                # regardless of packing order. Array has shape (num_items,).
                bins = np.array([capacity for _ in range(instance['num_items'])])
                # Pack items into bins and return remaining capacity in bins_packed, which
                # has shape (num_items,).
                _, bins_packed = self.online_binpack(items, bins, alg)
                # If remaining capacity in a bin is equal to initial capacity, then it is
                # unused. Count number of used bins.
                num_bins = (bins_packed != capacity).sum()

                num_bins_list.append(-num_bins)

            # avg_num_bins = -self.evaluateGreedy(dataset, algorithm)
            avg_num_bins = -np.mean(np.array(num_bins_list))
            fitness = (avg_num_bins - self.lb[name]) / self.lb[name]
            instances_fiteness.append(fitness)

        fitness = np.mean(instances_fiteness)


        # Score of heuristic function is negative of average number of bins used
        # across instances (as we want to minimize number of bins).

        return fitness



    # def evaluate(self):
    #     try:

    #         for name, dataset in self.instances.items():
    #             # Parallelize the loop
    #             num_bins = Parallel(n_jobs=4,timeout=30)(delayed(self.evaluateGreedy)(instance) for _, instance in dataset.items())
    #             # avg_num_bins = -self.evaluateGreedy(dataset, algorithm)
    #             avg_num_bins = -np.mean(num_bins)
    #             excess = (avg_num_bins - self.lb[name]) / self.lb[name]
    #             #print(name)
    #             #print(f'\t Average number of bins: {avg_num_bins}')
    #             #print(f'\t Lower bound on optimum: {self.lb[name]}')
    #             #print(f'\t Excess: {100 * excess:.2f}%')        
    #         return excess
    #     except Exception as e:
    #         #print("Error:", str(e))  # Print the error message
    #         return None
        
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

                fitness = self.evaluateGreedy(heuristic_module)

                return fitness
        except FunctionTimedOut or Exception as e:
            #print("Error:", str(e))
            return None




