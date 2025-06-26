class GetPromptsBlack():
    def __init__(self):
        self.prompt_task = "Solving a black-box combinatorial optimization problem via " + "'heuristics'."
        self.prompt_func_name = "heuristics"  # "priority"
        self.prompt_func_inputs = ["vector", "number1", "number2"]  # ["el", "n", "w"]
        self.prompt_func_outputs = ["vector_attr"]
        self.prompt_inout_inf = "'vector' is a int tuple, 'number1' is int, 'number2' is int, 'vector_attr' is a float"
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
