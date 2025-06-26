import json
from argparse import ArgumentParser
import sys
import os

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(ABS_PATH, "..")
sys.path.append(ROOT_PATH)  # This is for finding all the modules
from aell.src.ael import ael
from aell.src.ael.utils import createFolders

# =======================================================
api_endpoint = ""
api_key = ""
llm_model = ""
# =======================================================


# output path
output_path = "./"  # default folder for ael outputs
createFolders.create_folders(output_path)

seed = '''
import numpy as np

def priority(el: tuple[int, ...], n: int, w: int) -> float:
    """Returns the priority with which we want to add `el` to the set."""
    return 0.0
'''

seeds = [seed, seed]

load_data = {
    "use_seed": True,
    "seeds": seeds,
    "use_pop": False,
    "pop_path": output_path + "/ael_results/pops/population_generation_0.json",
    "n_pop_initial": 0
}

# Experimental settings
pop_size = 100  # number of algorithms in each population, default = 10
n_pop = 100  # number of populations, default = 10

# evolution operators: ['e1','e2','m1','m2'], default = ['e1','m1']
operators = ['e1', 'e2', 'm1', 'm2']

m = 2  # number of parents for 'e1' and 'e2' operators, default = 2

# weights for operators,
# the probability of use the operator in each iteration , default = [1,1,1,1]
operator_weights = [1, 1, 1, 1]

### Debug model ###
debug_mode = False  # if debug

# AEL
print(">>> Start AEL ")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--run', type=int)
    # parser.add_argument('--port', type=int, default=11045)
    parser.add_argument('--config', type=str, default='runtime_config.json')
    parser.add_argument('--i', type=str)

    args = parser.parse_args()

    cur_path = os.path.dirname(__file__)
    config_path = os.path.join(cur_path, args.config)
    algorithmEvolution = ael.AEL(api_endpoint, api_key, llm_model, pop_size, n_pop, operators, m, operator_weights,
                                 load_data, output_path, debug_mode, use_local_llm=False,
                                 config_path=config_path)

    # run AEL
    algorithmEvolution.run()

    print("AEL successfully finished !")
