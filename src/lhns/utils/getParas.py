
class Paras():
    def __init__(self):
        #####################
        ### General settings  ###
        #####################
        self.method = 'lhns'
        self.problem = 'tsp_construct'

        #####################
        ### LLM settings  ###
        #####################
        self.llm_api_endpoint = "XXX"
        self.llm_api_key = "XXX"  # use your key
        self.llm_model = "gpt-3.5-turbo-1106"

        #####################
        ###  Exp settings  ###
        #####################
        self.exp_debug_mode = False  # if debug
        self.exp_output_path = "./"  # default folder for ael outputs
        self.exp_use_seed = True
        self.exp_seed_path = "./seeds/seeds.json"
        self.exp_use_continue = False
        self.exp_continue_id = 0
        self.exp_continue_path = "./results/pops/population_generation_0.json"
        self.exp_n_proc = 1
        
        #####################
        ###  Evaluation settings  ###
        #####################
        self.eva_timeout = 30
        self.eva_numba_decorator = False

        #####################
        ###  Heuristic settings  ###
        #####################
        self.ini_ratio = "0.1"  # [0, 1]
        self.heuristic_type = "vns"  # ['vns', 'ils', 'ts']
        self.problem_type = "white-box"  # ['black-box','white-box']
        self.iterations = 1000
        self.rounds = 3


    def set_parallel(self):
        import multiprocessing
        num_processes = multiprocessing.cpu_count()
        if self.exp_n_proc == -1 or self.exp_n_proc > num_processes:
            self.exp_n_proc = num_processes
            print(f"Set the number of proc to {num_processes} .")
            
    def set_evaluation(self):
        # Initialize evaluation settings
        if self.problem == 'admissible_set':
            self.eva_timeout = 30
            # self.eva_numba_decorator = True
        elif self.problem == 'bp_online':
            self.eva_timeout = 20
            # self.eva_numba_decorator = True
        elif self.problem == 'tsp_construct':
            self.eva_timeout = 20
        elif self.problem == 'tsp_gls':
            self.eva_timeout = 120
                
    def set_paras(self, *args, **kwargs):
        
        # Map paras
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
              
        # Identify and set parallel 
        self.set_parallel()
        
        # Initialize evaluation settings
        self.set_evaluation()




if __name__ == "__main__":

    # Create an instance of the Paras class
    paras_instance = Paras()

    # Setting parameters using the set_paras method
    paras_instance.set_paras(llm_use_local=True, llm_local_url='http://example.com', ec_pop_size=8)

    # Accessing the updated parameters
    print(paras_instance.llm_use_local)  # Output: True
    print(paras_instance.llm_local_url)  # Output: http://example.com
    print(paras_instance.ec_pop_size)    # Output: 8
            
            
            
