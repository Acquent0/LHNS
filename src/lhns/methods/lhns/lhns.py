import os

import numpy as np
import json
import random
import time
from logging import getLogger

from .lhns_interface import Interface

class LHNS:

    # initilization
    def __init__(self, paras, problem, **kwargs):

        self.paras = paras
        self.prob = problem
        self.logger = getLogger()
        
        # LLM settings
        self.api_endpoint = paras.llm_api_endpoint  # currently only API2D + GPT
        self.api_key = paras.llm_api_key
        self.llm_model = paras.llm_model

        # -------------------------------------------------------

        # Experimental settings
        self.debug_mode = paras.exp_debug_mode  # if debug
        self.ndelay = 1  # default

        self.use_seed = paras.exp_use_seed
        self.seed_path = paras.exp_seed_path
        self.load_pop = paras.exp_use_continue
        self.load_pop_path = paras.exp_continue_path
        self.load_pop_id = paras.exp_continue_id

        self.output_path = paras.exp_output_path

        self.exp_n_proc = paras.exp_n_proc
        
        self.timeout = paras.eva_timeout

        self.use_numba = paras.eva_numba_decorator

        print("- EoH parameters loaded -")

        # Set a random seed
        random.seed(2024)

    def simulated_annealing(self, next_ind, curr_ind, rounds, cooling_rate, ils_count):

        new_obj = next_ind['objective']
        temperature = cooling_rate * (1 - (rounds - 1) / self.paras.iterations)

        if new_obj is None:
            ils_count += 1
            return False, ils_count

        # for minimization
        if new_obj >= curr_ind['objective']:
            temp_value = ((curr_ind['objective'] - new_obj) / (curr_ind['objective'] + 1E-10)) / temperature

            if np.random.rand() < np.exp(temp_value):
                accept = True
            else:
                accept = False
            ils_count += 1
        else:
            accept = True
            ils_count = 0

        return accept, ils_count

    def update_ts_table(self, ts_table, ts_size, next_ind):

        if next_ind['objective'] in [e['objective'] for e in ts_table] or next_ind['objective'] is None:
            return

        table_element = {
            'algorithm': None,
            'code': None,
            'objective': None,
            'code_feature': []
        }

        if len(ts_table) < ts_size:
            table_element['algorithm'] = next_ind['algorithm']
            table_element['code'] = next_ind['code']
            table_element['objective'] = next_ind['objective']
            table_element['code_feature'] = next_ind['other_inf']
            ts_table.append(table_element)
        else:
            obj_list = [e['objective'] for e in ts_table]
            max_index = np.argmax(obj_list)
            if next_ind['objective'] < obj_list[max_index]:
                table_element['algorithm'] = next_ind['algorithm']
                table_element['code'] = next_ind['code']
                table_element['objective'] = next_ind['objective']
                table_element['code_feature'] = next_ind['other_inf']
                ts_table[max_index] = table_element

    def judge_ts(self, ts_table, next_ind):
        if next_ind['objective'] in [e['objective'] for e in ts_table]:
            return False
        return True

    # run eoh 
    def run(self, num_turns, filepath):

        print("- LHNS Start -")

        time_start = time.time()

        # interface for evaluation
        interface_prob = self.prob

        # interface for ec operators
        interface = Interface(self.paras, self.api_endpoint, self.api_key, self.llm_model,
                                 self.debug_mode, interface_prob, n_p=self.exp_n_proc,
                                 timeout = self.timeout, use_numba=self.use_numba
                                 )

        # initialization
        # a = interface.get_next_heuristic(1, 'i1', 1, 1)
        ini_ind = None
        history = []
        history_descend = []
        cooling_rate = 0.1
        ils_count = 0
        history_best = None
        ils_flag = False

        if self.use_seed:
            with open(self.seed_path) as file:
                data = json.load(file)
            ini_ind = interface.initial_generation_seed(data)

            history_best = ini_ind
            n_start = 0
        else:
            assert print("self.use_seed is False!")

        # main loop
        if self.paras.heuristic_type == 'vns':
            curr_ind = ini_ind
            initial_ratio = self.paras.ini_ratio
            ratio = initial_ratio
            round_count = 0
            ratio_list = []

            for i in range(self.paras.iterations):
                round_count += 1
                ratio_list.append(ratio)

                # generate new individual
                # print(f"step: {round_count} ")
                _, new_ind = interface.get_next_heuristic(curr_ind, 'rr', ratio=ratio)
                history.append([curr_ind, new_ind])

                # SA
                accept, ils_count = self.simulated_annealing(new_ind, curr_ind, round_count, cooling_rate, ils_count)

                if accept:
                    curr_ind = new_ind
                    ratio = initial_ratio
                    if curr_ind['objective'] < history_best['objective']:
                        history_best = curr_ind
                else:
                    if ratio < 1.0:
                        ratio += 0.1
                        ratio = round(ratio, 1)
                    else:
                        ratio = initial_ratio
                history_descend.append(curr_ind)

                # write history to file
                filename = self.output_path + f"{filepath}/history/" + self.paras.problem + "_" + self.paras.problem_type + "_" + self.paras.heuristic_type + "_" + str(
                    num_turns + 1) + ".json"
                with open(filename, 'w') as f:
                    json.dump(history, f, indent=5)

                # print
                print("================Evaluated Function=================")
                print(f"{new_ind['algorithm']}")
                print("---------------------------------------------------")
                print(f"{new_ind['code']}")
                print("---------------------------------------------------")
                print(f"Score: {new_ind['objective']}")
                print(f"Sample orders: {round_count}")
                print(f"Ratio: {ratio}")
                print(f"Type: Perturb")
                print(f"Current best score: {curr_ind['objective']}")
                print("===================================================")

        elif self.paras.heuristic_type == 'ils':
            curr_ind = ini_ind
            initial_ratio = self.paras.ini_ratio
            ratio = initial_ratio
            round_count = 0

            for i in range(self.paras.iterations):
                round_count += 1

                # generate new individual
                # print(f"step: {round_count} ")
                if ils_count >= 10:
                    parent = history_best
                    _, new_ind = interface.get_next_heuristic(parent, 'p1')
                    ils_count = 0
                    ils_flag = True
                else:
                    parent = curr_ind
                    _, new_ind = interface.get_next_heuristic(parent, 'rr', ratio=ratio)
                    ils_flag = False
                history.append([parent, new_ind])

                # SA
                accept, ils_count = self.simulated_annealing(new_ind, curr_ind, round_count, cooling_rate, ils_count)

                if accept:
                    curr_ind = new_ind
                    if curr_ind['objective'] < history_best['objective']:
                        history_best = curr_ind
                history_descend.append(curr_ind)

                # write history to file
                filename = self.output_path + f"{filepath}/history/" + self.paras.problem + "_" + self.paras.problem_type + "_" + self.paras.heuristic_type + "_" + str(
                    num_turns + 1) + ".json"
                with open(filename, 'w') as f:
                    json.dump(history, f, indent=5)

                # print
                if ils_flag:
                    print("================Evaluated Function=================")
                    print(f"{new_ind['algorithm']}")
                    print("---------------------------------------------------")
                    print(f"{new_ind['code']}")
                    print("---------------------------------------------------")
                    print(f"Score: {new_ind['objective']}")
                    print(f"Sample orders: {round_count}")
                    print(f"Ratio: {ratio}")
                    print(f"Type: Perturb")
                    print(f"Current best score: {curr_ind['objective']}")
                    print("===================================================")
                else:
                    print("================Evaluated Function=================")
                    print(f"{new_ind['algorithm']}")
                    print("---------------------------------------------------")
                    print(f"{new_ind['code']}")
                    print("---------------------------------------------------")
                    print(f"Score: {new_ind['objective']}")
                    print(f"Sample orders: {round_count}")
                    print(f"Ratio: {ratio}")
                    print(f"Type: Normal")
                    print(f"Current best score: {curr_ind['objective']}")
                    print("===================================================")

        elif self.paras.heuristic_type == 'ts':
            curr_ind = ini_ind
            initial_ratio = self.paras.ini_ratio
            ratio = initial_ratio
            round_count = 0
            ts_table = []
            ts_size = 5

            for i in range(self.paras.iterations):
                round_count += 1

                # generate new individual
                # print(f"step: {round_count} ")
                if ils_count >= 10:
                    while True:
                        ts_ele = np.random.choice(ts_table)
                        if ts_ele['code'] != curr_ind['code'] or len(ts_table) == 1:
                            break
                    _, new_ind = interface.get_next_heuristic(curr_ind, 'p2', ts_ele=ts_ele)
                    ils_count = 0
                    ils_flag = True
                    history.append([curr_ind, ts_ele, new_ind])
                else:
                    _, new_ind = interface.get_next_heuristic(curr_ind, 'rr', ratio=ratio)
                    ils_flag = False
                    history.append([curr_ind, new_ind])

                self.update_ts_table(ts_table, ts_size, new_ind)

                # SA
                accept, ils_count = self.simulated_annealing(new_ind, curr_ind, round_count, cooling_rate, ils_count)

                if accept:
                    curr_ind = new_ind
                    if curr_ind['objective'] < history_best['objective']:
                        history_best = curr_ind
                history_descend.append(curr_ind)

                # write history to file
                filename = self.output_path + f"{filepath}/history/" + self.paras.problem + "_" + self.paras.problem_type + "_" + self.paras.heuristic_type + "_" + str(
                    num_turns + 1) + ".json"
                with open(filename, 'w') as f:
                    json.dump(history, f, indent=5)

                # print
                if ils_flag:
                    print("================Evaluated Function=================")
                    print(f"{new_ind['algorithm']}")
                    print("---------------------------------------------------")
                    print(f"{new_ind['code']}")
                    print("---------------------------------------------------")
                    print(f"Score: {new_ind['objective']}")
                    print(f"Sample orders: {round_count}")
                    print(f"Ratio: {ratio}")
                    print(f"Type: Perturb")
                    print(f"Current best score: {curr_ind['objective']}")
                    print("===================================================")
                else:
                    print("================Evaluated Function=================")
                    print(f"{new_ind['algorithm']}")
                    print("---------------------------------------------------")
                    print(f"{new_ind['code']}")
                    print("---------------------------------------------------")
                    print(f"Score: {new_ind['objective']}")
                    print(f"Sample orders: {round_count}")
                    print(f"Ratio: {ratio}")
                    print(f"Type: Normal")
                    print(f"Current best score: {curr_ind['objective']}")
                    print("===================================================")

        else:
            assert print("Wrong heuristic type!")
        print()
        self.logger.info('=================================================================')
        self.logger.info("Objective list: {}".format([e[-1]['objective'] for e in history]))
        self.logger.info("Objective descend list: {}".format([e['objective'] for e in history_descend]))
        self.logger.info("Objective mean: {}".format(np.mean([e[-1]['objective'] for e in history if e[-1]['objective'] is not None])))
         # Save history to a file
        filename = self.output_path + f"{filepath}/history/" + self.paras.problem + "_" + self.paras.problem_type + "_" + self.paras.heuristic_type + "_" + str(
            num_turns + 1) + ".json"
        with open(filename, 'w') as f:
            json.dump(history, f, indent=5)

        # Save the best one to a file
        filename = self.output_path + f"{filepath}/history_best/" + self.paras.problem + "_" + self.paras.problem_type + "_" + self.paras.heuristic_type + "_" + str(
            num_turns + 1) + ".json"
        with open(filename, 'w') as f:
            json.dump(history_best, f, indent=5)

        self.logger.info(f"--- {num_turns + 1} of {3} finished. Time Cost:  {((time.time() - time_start) / 60):.1f} m")
        self.logger.info("Best Objs: ")
        self.logger.info(str(history_best['objective']) + " ")

        # fitness, times = self.evaluate_best(history_best)
        fitness = None
        times = None

        print(f"test: {fitness}")
        print(f"test time: {times}")

        return np.mean([e[-1]['objective'] for e in history if e[-1]['objective'] is not None]), history_best['objective'], fitness, times
