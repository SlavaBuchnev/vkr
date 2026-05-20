import random

import numpy as np

from main.manufacturing import calculate_cost


def agglomerative_clustering_by_flow(flow, k):
    """
    Агломеративная кластеризация по сумме потоков между кластерами.
    Возвращает список кластеров (каждый – список индексов).
    """
    n = flow.shape[0]
    clusters = [[i] for i in range(n)]
    # Матрица потоков между кластерами (список списков)
    while len(clusters) > k:
        best_pair = None
        best_flow = -1
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                total = 0
                for a in clusters[i]:
                    for b in clusters[j]:
                        total += flow[a, b] + flow[b, a]  # симметричная сумма
                if total > best_flow:
                    best_flow = total
                    best_pair = (i, j)
        if best_pair is None:
            break
        i, j = best_pair
        clusters[i].extend(clusters[j])
        del clusters[j]
    return clusters

def build_permutation_from_clusters(clusters, flow, random_order=False):
    """
    Строит перестановку из кластеров.
    Если random_order=False, внутри кластера элементы сортируются по убыванию
    суммы потоков внутри кластера (симметричных). Требуется матрица flow.
    """
    perm = []
    for cluster in clusters:
        if random_order:
            order = list(cluster)
            random.shuffle(order)
        else:
            strengths = {}
            for i in cluster:
                s = 0
                for j in cluster:
                    s += flow[i, j] + flow[j, i]
                strengths[i] = s
            order = sorted(cluster, key=lambda x: strengths[x], reverse=True)
        perm.extend(order)
    return perm

def simulated_annealing(init_perm, flow, dist, max_iter=2000, temp0=1000, alpha=0.995):
    """
    Имитация отжига с операцией swap.
    Возвращает лучшую найденную перестановку и её стоимость.
    """
    n = len(init_perm)
    current = init_perm[:]
    best = current[:]
    current_cost = calculate_cost(current, flow, dist)
    best_cost = current_cost
    temp = temp0

    for _ in range(max_iter):
        # Генерация соседа – swap двух случайных позиций
        i, j = random.sample(range(n), 2)
        neighbor = current[:]
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        neighbor_cost = calculate_cost(neighbor, flow, dist)
        delta = neighbor_cost - current_cost

        if delta < 0 or random.random() < np.exp(-delta / temp):
            current, current_cost = neighbor, neighbor_cost
            if current_cost < best_cost:
                best, best_cost = current[:], current_cost

        temp *= alpha
        if temp < 1e-6:
            break
    return best, best_cost

def generate_initial_population_with_clustering_sa(flow, dist, pop_size, max_clusters=None, sa_iter=1000):
    """
    Генерирует начальную популяцию с помощью кластеризации + имитации отжига.
    Для каждого k от 2 до max_clusters (но не больше n) создаётся одно решение,
    остальные места заполняются случайными перестановками.
    """
    n = flow.shape[0]
    if max_clusters is None:
        max_clusters = min(10, n)  # иначе слишком много
    solutions = []

    for k in range(2, max_clusters + 1):
        clusters = agglomerative_clustering_by_flow(flow, k)
        # Два варианта порядка внутри кластера: детерминированный и случайный
        for random_order in [False, True]:
            init_perm = build_permutation_from_clusters(clusters, flow, random_order)
            best_perm, _ = simulated_annealing(init_perm, flow, dist, max_iter=sa_iter)
            solutions.append(best_perm)
            if len(solutions) >= pop_size:
                break
        if len(solutions) >= pop_size:
            break

    # Добавить случайные, если не хватает
    while len(solutions) < pop_size:
        solutions.append(list(np.random.permutation(n)))

    return solutions[:pop_size]