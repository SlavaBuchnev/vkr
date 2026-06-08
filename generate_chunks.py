import itertools
import json
import sys
import os

# Параметры и их значения (полный перебор)
PARAM_GRID = {
    "pop_size": [250],
    "gens": [50],
    "cross_rate": [0.5],
    "mut_rate": [0.1],
    "tourn_size": [2],
    "elitism": [0],
    "use_local_search": [True, False],
    "ls_freq": [1],
    "strategy": ["generational"],
    "init_method": ["clustering_sa"],
}

# Размер чанка (не более 256, но лучше 200, чтобы оставить запас)
CHUNK_SIZE = 200

def generate_all_combinations():
    keys = list(PARAM_GRID.keys())
    values = list(PARAM_GRID.values())
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))

def chunks(lst, n):
    """Разбивает список на куски по n элементов."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def generate_chunks(chunk_size=CHUNK_SIZE):
    all_combos = list(generate_all_combinations())
    print(f"Total combinations: {len(all_combos)}", file=sys.stderr)
    chunks_list = list(chunks(all_combos, chunk_size))
    print(f"Total chunks: {len(chunks_list)}", file=sys.stderr)
    return chunks_list

if __name__ == "__main__":
    chunks_data = generate_chunks()
    # Если запущено в CI, выводим JSON в $GITHUB_OUTPUT
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"chunks={json.dumps(chunks_data)}\n")
    else:
        # Локальный запуск: просто сохраняем в файл
        with open("chunks.json", "w") as f:
            json.dump(chunks_data, f, indent=2)
        print("chunks.json saved")