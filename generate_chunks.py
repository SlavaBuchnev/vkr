import argparse
import itertools
import json
import math
import os
import sys

PARAM_GRID = {
    "pop_size": [250, 500, 1000],
    "gens": [50, 100, 300],
    "cross_rate": [0.5, 0.75, 1],
    "mut_rate": [0.1, 0.3, 0.5],
    "tourn_size": [1, 5, 20],
    "elitism": [0, 25, 50],
    "use_local_search": [True, False],
    "ls_freq": [1, 5, 10],
    "strategy": ["generational", "plus", "comma"],
    "init_method": ["random", "clustering_sa"],
}

def generate_all_combinations(pop_size_filter=None):
    keys = list(PARAM_GRID.keys())
    values = list(PARAM_GRID.values())
    for combo in itertools.product(*values):
        d = dict(zip(keys, combo))
        if pop_size_filter is not None and d["pop_size"] != pop_size_filter:
            continue
        yield d

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def generate_chunks_for_pop(pop_size, max_jobs=256):
    combos = list(generate_all_combinations(pop_size))
    total = len(combos)
    if total == 0:
        return []
    chunk_size = math.ceil(total / max_jobs)
    return list(chunks(combos, chunk_size))

def build_matrix(pop_sizes, max_jobs=256):
    """Создаёт список заданий для матрицы include и сохраняет чанки в JSON."""
    all_chunks = {}
    matrix_include = []

    for pop in pop_sizes:
        ch_list = generate_chunks_for_pop(pop, max_jobs)
        all_chunks[str(pop)] = ch_list
        for batch_idx in range(len(ch_list)):
            matrix_include.append({
                "pop_size": pop,
                "batch": batch_idx
            })

    return all_chunks, matrix_include

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks-file", default="all_chunks.json", help="File with all chunks per pop_size")
    parser.add_argument("--matrix-file", default="matrix.json", help="Matrix include JSON for GitHub Actions")
    parser.add_argument("--max-jobs", type=int, default=256, help="Max jobs per pop_size group")
    args = parser.parse_args()

    pop_sizes = PARAM_GRID["pop_size"]
    all_chunks, matrix_include = build_matrix(pop_sizes, args.max_jobs)

    # Сохраняем чанки
    with open(args.chunks_file, "w") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"Chunks saved to {args.chunks_file}", file=sys.stderr)

    # Сохраняем матрицу
    with open(args.matrix_file, "w") as f:
        json.dump(matrix_include, f, indent=2)
    print(f"Matrix include ({len(matrix_include)} jobs) saved to {args.matrix_file}", file=sys.stderr)

    # Для GitHub Actions – выводим матрицу в GITHUB_OUTPUT
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"matrix_json={json.dumps(matrix_include)}\n")
