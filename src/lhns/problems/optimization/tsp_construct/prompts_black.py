
class GetPromptsBlack():
    def __init__(self):
        self.prompt_task = "Solving a black-box graph combinatorial optimization problem via " + "'heuristics'."
        self.prompt_func_name = "heuristics"
        self.prompt_func_inputs = ["node1","node2","nodes","edge_attrs"]
        self.prompt_func_outputs = ["node"]
        self.prompt_inout_inf = "'node1', 'node2', 'node', and 'nodes' are node IDs. 'edge_attrs' is the edge attributes. All are Numpy arrays."
        self.prompt_other_inf = "Please analyze the given code and function description to identify the specific problem it addresses. Based on your analysis to design improved heuristics."

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

if __name__ == "__main__":
    getprompts = GetPrompts()
    print(getprompts.get_task())
