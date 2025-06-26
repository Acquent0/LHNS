import numpy as np
import pickle
class GetData():
    def __init__(self) -> None:
        self.demensions = 15
        self.weight = 10

    def get_instances(self):
        return self.demensions, self.weight


