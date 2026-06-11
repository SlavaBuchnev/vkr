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
    """Создаёт полную матрицу include (для всех pop_size)."""
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
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Подкоманда: single – для одного pop_size
    single_parser = subparsers.add_parser("single", help="Generate chunks for a single pop_size")
    single_parser.add_argument("--pop_size", type=int, required=True)
    single_parser.add_argument("--output", required=True, help="Output JSON file for chunks")
    single_parser.add_argument("--max_jobs", type=int, default=256)

    # Подкоманда: full – для всех pop_size сразу (как раньше)
    full_parser = subparsers.add_parser("full", help="Generate full matrix for all pop_size")
    full_parser.add_argument("--chunks-file", default="all_chunks.json")
    full_parser.add_argument("--matrix-file", default="matrix.json")
    full_parser.add_argument("--max-jobs", type=int, default=256, dest="max_jobs")

    args = parser.parse_args()

    if args.command == "single":
        pop_size = args.pop_size
        max_jobs = args.max_jobs
        chunks_list = generate_chunks_for_pop(pop_size, max_jobs)
        if not chunks_list:
            print(f"No combinations for pop_size={pop_size}", file=sys.stderr)
            sys.exit(1)
        with open(args.output, "w") as f:
            json.dump(chunks_list, f, indent=2)
        print(f"Chunks for pop_size={pop_size} saved to {args.output}", file=sys.stderr)
        # Для GitHub Actions: выводим batch_indices в stdout как JSON
        batch_indices = list(range(len(chunks_list)))
        print(json.dumps(batch_indices))  # stdout пойдёт в ${{ steps.gen.outputs.batch_indices }}
        # Дополнительно в GITHUB_OUTPUT
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"batch_indices={json.dumps(batch_indices)}\n")

    elif args.command == "full":
        pop_sizes = PARAM_GRID["pop_size"]
        all_chunks, matrix_include = build_matrix(pop_sizes, args.max_jobs)
        with open(args.chunks_file, "w") as f:
            json.dump(all_chunks, f, indent=2)
        with open(args.matrix_file, "w") as f:
            json.dump(matrix_include, f, indent=2)
        print(f"Full matrix saved: {args.chunks_file}, {args.matrix_file}", file=sys.stderr)
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"matrix_json={json.dumps(matrix_include)}\n")
