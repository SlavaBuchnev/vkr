import numpy as np
import json
from typing import Dict, Any

def load_qap_instance(filepath):
    """Загружает экземпляр КЗН из локального файла формата QAPLIB."""
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    data_lines = []
    for line in lines:
        if line and not line.startswith('#'):
            data_lines.append(line)

    n = int(data_lines[0].split()[0])

    # Извлечение матриц
    matrices = []
    current_matrix = []
    for line in data_lines[1:]:
        numbers = list(map(int, line.split()))
        current_matrix.extend(numbers)
        if len(current_matrix) == n * n:
            matrices.append(np.array(current_matrix).reshape(n, n))
            current_matrix = []

    flow = matrices[0]
    dist = matrices[1]
    return n, flow, dist

def calculate_cost(perm, flow, dist):
    n = len(perm)
    cost = 0
    for i in range(n):
        for j in range(n):
            cost += flow[i, j] * dist[perm[i], perm[j]]
    return cost

def _common_load_json(filepath: str) -> Dict[Any, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_opt_values() -> Dict[str, int]:
    return _common_load_json("configs/opt_values.json")

def load_ea_params() -> Dict[str, Any]:
    params = _common_load_json("configs/ea_params.json")
    pop_size = params['pop_size']
    params['tourn_size'] = max(2, int(params.get('tourn_size', 2) * pop_size / 100))
    params['elitism'] = max(0, int(params.get('elitism', 0) * pop_size / 100))
    params['ls_freq'] = max(1, int(params.get('ls_freq', 1) * pop_size / 100))
    return params

def rewrite_ea_params(params:Dict[str, Any]) -> Dict[str, Any]:
    pop_size = params['pop_size']
    params['tourn_size'] = round(params['tourn_size'] / pop_size * 100, 2)
    params['elitism'] = round(params['elitism'] / pop_size * 100, 2)
    params['ls_freq'] = round(params['ls_freq'] / pop_size * 100, 2)
    return params
