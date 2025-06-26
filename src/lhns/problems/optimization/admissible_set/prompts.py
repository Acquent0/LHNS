class GetPrompts():
    def __init__(self):
        self.prompt_task = "I need help developing a novel scoring function to evaluate vectors for potential inclusion in a set. This involves iteratively scoring the priority of adding a vector 'el' to the set based on analysis (like bitwise), with the objective of maximizing the set's size."
        self.prompt_func_name = "priority"
        self.prompt_func_inputs = ["el", "n", "w"]
        self.prompt_func_outputs = ["score"]
        self.prompt_inout_inf = "`el` is the candidate vectors for the admissible set. `n` is the number of dimensions and the length of a vector. `w` is the weight of each vector. 'score' is the priority of `el`."
        self.prompt_other_inf = "'el' is a int tuple, 'n' is int, 'w' is int, 'score' is a float."

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
