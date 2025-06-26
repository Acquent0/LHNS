class GetPromptsBlack():
    def __init__(self):
        self.prompt_task = "Solving a black-box combinatorial optimization problem via " + "'heuristics'."
        self.prompt_func_name = "heuristics"
        self.prompt_func_inputs = ['node', 'nodes']
        self.prompt_func_outputs = ['node_attrs']
        self.prompt_inout_inf = "Note that 'node' is of type int, while 'nodes' and 'node_attrs' are both Numpy arrays."
        self.prompt_other_inf = "Please analyze the given code and function description to identify the specific problem it addresses. Based on your analysis to design improved heuristics."
#Include the following imports at the beginning of the code: 'import numpy as np', and 'from numba import jit'. Place '@jit(nopython=True)' just above the 'priority' function definition."

    def get_task(self):
        return self.prompt_task
    
    def get_func_name(self):
        return self.prompt_func_name
    
    def get_func_inputs(self):
        return self.prompt_func_inputs
    
    def get_func_outputs(self):
        return self.prompt_func_outputs
    
    def get_inout_inf(self):
        return self.prompt_inout_inf

    def get_other_inf(self):
        return self.prompt_other_inf

