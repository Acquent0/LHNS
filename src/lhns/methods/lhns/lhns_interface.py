import os.path

import numpy as np
from .lhns_prompt import Evolution
import warnings
from .evaluator_accelerate import add_numba_decorator
import re

class Interface():
    def __init__(self, paras, api_endpoint, api_key, llm_model, debug_mode, interface_prob, timeout,use_numba,**kwargs):
        # -----------------------------------------------------------

        # LLM settings
        self.paras = paras
        self.interface_eval = interface_prob
        prompts = interface_prob.prompts
        self.evol = Evolution(api_endpoint, api_key, llm_model, debug_mode,prompts, **kwargs)
        self.debug = debug_mode

        if not self.debug:
            warnings.filterwarnings("ignore")
        
        self.timeout = timeout
        self.use_numba = use_numba
        
    def code2file(self,code):
        with open("./ael_alg.py", "w") as file:
        # Write the code to the file
            file.write(code)
        return
    
    def check_duplicate(self, curr_ind, new_ind):
        if new_ind['code'] == curr_ind['code'] or new_ind['objective'] == curr_ind['objective']:
            return True
        return False
    
    def initial_generation_seed(self, seed):

        fitness = self.interface_eval.evaluate(seed['code'])

        try:
            seed_alg = {
                'algorithm': seed['algorithm'],
                'code': seed['code'],
                'objective': None,
                'other_inf': None
            }

            obj = np.array(fitness)
            seed_alg['objective'] = np.round(obj, 5)
            seed_alg['objective'] = float(seed_alg['objective'])

        except Exception as e:
            print("Error in seed algorithm")
            exit()

        print("Initiliazation finished! Get seed algorithm with objective {}".format(seed_alg['objective']))

        return seed_alg
    

    def _get_alg(self, curr_ind, operator, ratio, ts_ele):
        new_ind = {
            'algorithm': None,
            'code': None,
            'objective': None,
            'other_inf': None
        }
        if operator == "i1":
            parent = None
            [new_ind['code'], new_ind['algorithm']] = self.evol.i1()
        elif operator == "rr":
            parent = curr_ind
            [new_ind['code'], new_ind['algorithm'], new_ind['other_inf']] = self.evol.rr(parent, ratio)
        elif operator == "p1":
            parent = curr_ind
            [new_ind['code'], new_ind['algorithm'], new_ind['other_inf']] = self.evol.p1(parent)
        elif operator == "p2":
            parent = curr_ind
            [new_ind['code'], new_ind['algorithm'], new_ind['other_inf']] = self.evol.p2(parent, ts_ele)
        else:
            print(f"Evolution operator [{operator}] has not been implemented ! \n") 

        return parent, new_ind

    def get_new_ind(self, curr_ind, operator, ratio, ts_ele):

        try:
            parent, next_ind = self._get_alg(curr_ind, operator, ratio, ts_ele)

            if self.use_numba:

                # Regular expression pattern to match function definitions
                pattern = r"def\s+(\w+)\s*\(.*\):"

                # Search for function definitions in the code
                match = re.search(pattern, next_ind['code'])

                function_name = match.group(1)

                code = add_numba_decorator(program=next_ind['code'], function_name=function_name)
            else:
                code = next_ind['code']
                if "import numpy as np" not in code and code is not None:
                    code = "import numpy as np\n" + code

            n_retry = 1
            while self.check_duplicate(curr_ind, next_ind):

                n_retry += 1
                if self.debug:
                    print("duplicated code, wait 1 second and retrying ... ")

                parent, next_ind = self._get_alg(curr_ind, operator, ratio, ts_ele)

                if self.use_numba:
                    # Regular expression pattern to match function definitions
                    pattern = r"def\s+(\w+)\s*\(.*\):"

                    # Search for function definitions in the code
                    match = re.search(pattern, next_ind['code'])

                    function_name = match.group(1)

                    code = add_numba_decorator(program=next_ind['code'], function_name=function_name)
                else:
                    code = next_ind['code']
                    if "import numpy as np" not in code and code is not None:
                        code = "import numpy as np\n" + code
                if n_retry > 1:
                    break

            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     future = executor.submit(self.interface_eval.evaluate, code)
            #     fitness = future.result(timeout=self.timeout)
            #     next_ind['objective'] = np.round(fitness, 5)
            #     future.cancel()
                # fitness = self.interface_eval.evaluate(code)

            next_ind['objective'] = self.interface_eval.evaluate(code)
            next_ind['objective'] = np.round(next_ind['objective'], 5)
            next_ind['objective'] = float(next_ind['objective'])

            # if self.paras.problem_type == 'white-box':
            #     if next_ind['objective'] == curr_ind['objective']:
            #         raise Exception


        except Exception as e:
            print(e)

            next_ind = {
                'algorithm': None,
                'code': None,
                'objective': None,
                'other_inf': None
            }
            parent = None

        # Round the objective values
        return parent, next_ind

    def get_next_heuristic(self, curr_ind, operator, ratio=0.5, ts_ele=None):

        new_ind = {
                'algorithm': None,
                'code': None,
                'objective': 1E10,
                'other_inf': None
            }
        parent = None
        while parent == None:  #  or new_ind['objective'] > 1e6:
            try:
                parent, new_ind = self.get_new_ind(curr_ind, operator, ratio, ts_ele)
                # parent, new_ind = Parallel(n_jobs=self.n_p,timeout=self.timeout+15)(delayed(self.get_new_ind)(curr_ind, operator, ratio, ts_ele))
                if parent == None:
                    print("Error: parent is None")
                    break
            except Exception as e:
                if self.debug:
                    print(f"Error: {e}")
                print(e)
                # break
                # print("Parallel time out .")

        return parent, new_ind