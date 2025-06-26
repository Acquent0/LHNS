# LHNS: LLM-Driven Neighborhood Search for Efficient Heuristic Design
CEC 2025 Oral

### Quick Start:

> [!Note]
> Configure your LLM api before running the script. For example:
>
> 1) Set `host`: 'api.deepseek.com' or 'api.metaihub.cn' or ...
> 2) Set `key`: 'your api key'
> 3) Set `model`: 'deepseek-v3' or 'gpt-4o-mini' or ...

In run_lhns.py:
```python
# Set parameters #
from src.lhns.utils.getParas import Paras

paras = Paras()
paras.set_paras(method = "lhns",    # method
                ini_ratio = 0.5,  # ruin ratio
                heuristic_type = "vns",  # ['vns', 'ils', 'ts']
                problem = "bp_online",  # ['tsp_construct','bp_online', 'admissible_set', 'tsp_gls']
                problem_type = "white-box",  # ['black-box','white-box']
                llm_api_endpoint = "api.deepseek.com",
                llm_api_key = "your api key",
                llm_model = "deepseek-v3", #  [gpt-3.5-turbo-0125, gemini-pro, claude-3-5-sonnet-20240620]
                iterations = 1000,
                rounds = 3,  # repeated experiments
                exp_debug_mode = False)
```

## Abstract

Handcrafting heuristics often demands extensive domain knowledge and significant development effort. Recently, heuristic search powered by large language models (LLMs) has emerged as a new approach, offering enhanced automation and promising performance. Existing methods rely on an evolutionary computation (EC) framework with carefully designed prompt strategies. However, the large heuristic search space poses significant challenges for these EC-based methods. This paper proposes a simple yet effective LLM-driven Heuristic Neighborhood Search (LHNS) paradigm to iteratively search in the heuristic neighborhood in a principled way for efficient heuristic design. Three distinct methods are designed under this neighborhood search paradigm and demonstrated on three widely studied problems. Results indicate that LHNS exhibits very competitive performance and surpasses existing EC-based methods in efficiency. It also demonstrates sufficient robustness in the absence of problem-specific knowledge regarding the target problem. The efficiency and robust adaptability make it a practical new solution for efficient heuristic design.

## Cite Our Paper

[1] Z. Xie, F. Liu, Z. Wang and Q. Zhang, 
"LLM-Driven Neighborhood Search for Efficient Heuristic Design," 
2025 IEEE Congress on Evolutionary Computation (CEC), Hangzhou, China, 2025, pp. 1-8, doi: 10.1109/CEC65147.2025.11043025.

[2] Liu F, Zhang R, Xie Z, et al. Llm4ad: A platform for algorithm design with large language model[J]. arXiv preprint arXiv:2412.17287, 2024.
