
# from .selection import prob_rank,equal,roulette_wheel,tournament
# from .management import pop_greedy,ls_greedy,ls_sa

class Methods():
    def __init__(self,paras,problem) -> None:
        self.paras = paras      
        self.problem = problem

        
    def get_method(self):

        if self.paras.method == "lhns":
            from .lhns.lhns import LHNS
            return LHNS(self.paras, self.problem)
        else:
            print("method "+self.paras.method+" has not been implemented!")
            exit()