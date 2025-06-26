
import random

from .utils import createFolders
from .methods import methods
from .problems import problems

# main class for AEL
class EVOL:

    # initilization
    def __init__(self, paras, prob=None, **kwargs):

        print("----------------------------------------- ")
        print("---              Start LHNS            ---")
        print("-----------------------------------------")
        # Create folder #
        createFolders.create_folders(paras.exp_output_path)
        print("- output folder created -")

        self.paras = paras

        print("-  parameters loaded -")

        self.prob = prob

        
    # run methods
    def run(self, num_turns, filepath):

        problemGenerator = problems.Probs(self.paras)

        problem = problemGenerator.get_problem()

        methodGenerator = methods.Methods(self.paras, problem)

        method = methodGenerator.get_method()

        m, b, test_results, times = method.run(num_turns=num_turns, filepath=filepath)

        print("> End of Evolution! ")
        print("----------------------------------------- ")
        print("---     LHNS successfully finished !   ---")
        print("-----------------------------------------")

        return m, b, test_results, times
