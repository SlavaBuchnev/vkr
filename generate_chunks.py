import argparse
import itertools
import json
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

CHUNK_SIZE = 103

def generate_all_combinations():
    keys = list(PARAM_GRID.keys())
    values = list(PARAM_GRID.values())
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def generate_chunks(chunk_size=CHUNK_SIZE):
    all_combos = list(generate_all_combinations())
    print(f"Total combinations: {len(all_combos)}", file=sys.stderr)
    chunks_list = list(chunks(all_combos, chunk_size))
    print(f"Total chunks: {len(chunks_list)}", file=sys.stderr)
    return chunks_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="chunks.json", help="Output JSON file")
    args = parser.parse_args()

    chunks_data = generate_chunks()

    # Проверка, что чанки не пустые
    if len(chunks_data) == 0:
        print("Error: No chunks generated! Check parameter grid.", file=sys.stderr)
        sys.exit(1)

    # Всегда сохраняем JSON в файл
    with open(args.output, "w") as f:
        json.dump(chunks_data, f, indent=2)
    print(f"Chunks saved to {args.output}", file=sys.stderr)

    # Дополнительно пишем в GITHUB_OUTPUT для GitHub Actions
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"chunks={json.dumps(chunks_data)}\n")
