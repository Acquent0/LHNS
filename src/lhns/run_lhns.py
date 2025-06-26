import os, sys
import logging
from logging import getLogger

import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "..")  # for problem_def
sys.path.insert(0, "../..")  # for utils

from src.lhns import lhns
from src.lhns.utils.getParas import Paras
from log_utils import create_logger, copy_all_src, set_result_folder_ini, get_result_folder

# Parameter initilization #
paras = Paras()

# Set parameters #
paras.set_paras(method = "lhns",    # method
                ini_ratio = 0.1,  # ruin ratio
                heuristic_type = "vns",  # ['vns', 'ils', 'ts']
                problem = "bp_online",  # ['tsp_construct','bp_online', 'admissible_set', 'tsp_gls']
                problem_type = "white-box",  # ['black-box','white-box']
                llm_api_endpoint = "api.bltcy.ai",
                llm_api_key = "your api key",
                llm_model = "gpt-4o-mini", #  [gpt-3.5-turbo-0125, gemini-pro, claude-3-5-sonnet-20240620]
                iterations = 1000,
                rounds = 1,
                exp_debug_mode = False)

def _print_config(logger):
    logger.info("problem: {}".format(paras.problem))
    logger.info("problem_type: {}".format(paras.problem_type))
    logger.info("heuristic_type: {}".format(paras.heuristic_type))
    logger.info("ini_ratio: {}".format(paras.ini_ratio))
    [logger.info(g_key + "{}".format(globals()[g_key])) for g_key in globals().keys() if g_key.endswith('params')]

logger_params = {
    'log_file': {
        'desc': '',
        'filename': 'run_log'
    }
}

# initilization
logger = getLogger('root')
logger_params['log_file']['desc'] = paras.problem + "_" + paras.problem_type + "_" + paras.heuristic_type
create_logger(**logger_params)
_print_config(logger)
copy_all_src(get_result_folder())
set_result_folder_ini()

history_mean = []
history_best = []
test_results_list = []
test_averages = []
test_times = []

for i in range(paras.rounds):  # index for runs
    if paras.problem_type == 'white-box':
        paras.exp_seed_path = "problems/optimization/" + paras.problem + "/ini_state.json"
    else:
        paras.exp_seed_path = "problems/optimization/" + paras.problem + "/ini_state_black.json"
    evolution = lhns.EVOL(paras)

    # run
    m, b, test_results, times = evolution.run(i, logger_params['log_file']['filepath'])
    history_mean.append(m)
    history_best.append(b)
    test_results_list.append(test_results)
    test_times.append(times)

logger.info('=================================================================')
logger.info('Test Done !')
logger.info('Average Obj: {}'.format(np.mean(history_mean)))
logger.info('Best Obj List: {}'.format([e for e in history_best]))
logger.info('Average Best Obj: {}'.format(np.mean(history_best)))
logger.info('Test Best Obj List: {}'.format(test_results_list))
# logger.info('Test times: {}'.format(test_times))
# logger.info('Average Test Best Obj: {}'.format(np.mean(test_averages)))

