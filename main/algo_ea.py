import numpy as np
import random

from .initialization import generate_initial_population_with_clustering_sa
from .manufacturing import calculate_cost
from .cycle_crossover_support import cycle_crossover_optimal


def order_crossover(p1, p2):
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child = [-1] * n
    child[a:b] = p1[a:b]
    p2_remaining = [gene for gene in p2 if gene not in child]
    idx = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = p2_remaining[idx]
            idx += 1
    return child


def mutate_swap(individual, rate):
    if random.random() < rate:
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
    return individual


def local_search_2opt(individual, flow, dist, max_iter=100):
    n = len(individual)
    improved = True
    best_cost = calculate_cost(individual, flow, dist)
    best_perm = individual[:]
    iter_count = 0
    while improved and iter_count < max_iter:
        improved = False
        for i in range(n - 1):
            for j in range(i + 1, n):
                new_perm = best_perm[:]
                new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
                new_cost = calculate_cost(new_perm, flow, dist)
                if new_cost < best_cost:
                    best_cost = new_cost
                    best_perm = new_perm
                    improved = True
        iter_count += 1
    return best_perm, best_cost

def start_position(init_method, n, pop_size, flow, dist):
    if init_method == "random":
        return [list(np.random.permutation(n)) for _ in range(pop_size)]
    elif init_method == "clustering_sa":
        return generate_initial_population_with_clustering_sa(flow, dist, pop_size, max_clusters=min(10, n), sa_iter=1000)
    else:
        raise ValueError(f"Unknown init_method: {init_method}")


def select_new_generation(population, costs, flow, dist,
                          pop_size, elitism, cross_rate, mut_rate,
                          tourn_size, strategy,
                          offspring_mult = 2):
    """
    Формирует новое поколение согласно выбранной стратегии.
    population: список особей (перестановок)
    costs: список стоимостей особей
    flow, dist: матрицы задачи QAP
    остальные параметры – настройки эволюции
    """
    n = len(population)
    if strategy == 'generational':
        # Элитизм + потомки
        sorted_idx = np.argsort(costs)
        new_pop = [population[sorted_idx[i]][:] for i in range(elitism)]

        while len(new_pop) < pop_size:
            contenders = random.sample(range(n), tourn_size)
            p1_idx = min(contenders, key=lambda i: costs[i])
            contenders = random.sample(range(n), tourn_size)
            p2_idx = min(contenders, key=lambda i: costs[i])
            parent1 = population[p1_idx]
            parent2 = population[p2_idx]

            if random.random() < cross_rate:
                child = cycle_crossover_optimal(parent1, parent2, flow, dist)
            else:
                child = parent1[:]
            child = mutate_swap(child, mut_rate)
            new_pop.append(child)
        return new_pop

    elif strategy == 'plus':
        # (μ + λ): создаём λ=pop_size потомков, объединяем, выбираем лучших
        sorted_idx = np.argsort(costs)
        offspring = [population[sorted_idx[i]][:] for i in range(elitism)]

        while len(offspring) < pop_size:
            contenders = random.sample(range(n), tourn_size)
            p1_idx = min(contenders, key=lambda i: costs[i])
            contenders = random.sample(range(n), tourn_size)
            p2_idx = min(contenders, key=lambda i: costs[i])
            parent1 = population[p1_idx]
            parent2 = population[p2_idx]

            if random.random() < cross_rate:
                child = cycle_crossover_optimal(parent1, parent2, flow, dist)
            else:
                child = parent1[:]
            child = mutate_swap(child, mut_rate)
            offspring.append(child)

        combined = population + offspring
        combined_costs = [calculate_cost(ind, flow, dist) for ind in combined]
        sorted_combined = sorted(zip(combined, combined_costs), key=lambda x: x[1])
        return [ind for ind, _ in sorted_combined[:pop_size]]

    elif strategy == 'comma':
        # (μ, λ): генерируем λ = offspring_mult*pop_size потомков, отбираем лучших из них
        offspring_size = offspring_mult * pop_size
        sorted_idx = np.argsort(costs)
        offspring = [population[sorted_idx[i]][:] for i in range(elitism)]

        while len(offspring) < offspring_size:
            contenders = random.sample(range(n), tourn_size)
            p1_idx = min(contenders, key=lambda i: costs[i])
            contenders = random.sample(range(n), tourn_size)
            p2_idx = min(contenders, key=lambda i: costs[i])
            parent1 = population[p1_idx]
            parent2 = population[p2_idx]

            if random.random() < cross_rate:
                child = cycle_crossover_optimal(parent1, parent2, flow, dist)
            else:
                child = parent1[:]
            child = mutate_swap(child, mut_rate)
            offspring.append(child)

        offspring_costs = [calculate_cost(ind, flow, dist) for ind in offspring]
        sorted_offspring = sorted(zip(offspring, offspring_costs), key=lambda x: x[1])
        return [ind for ind, _ in sorted_offspring[:pop_size]]

    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def evolutionary_algorithm(flow, dist, pop_size, gens,
                           cross_rate, mut_rate, tourn_size,
                           elitism, use_local_search, ls_freq,
                           strategy, init_method):
    n = flow.shape[0]
    population = start_position(init_method, n, pop_size, flow, dist)

    best_cost_history = []

    for gen in range(gens):
        costs = [calculate_cost(ind, flow, dist) for ind in population]
        best_idx = np.argmin(costs)
        best_cost = costs[best_idx]
        best_sol = population[best_idx][:]

        best_cost_history.append(best_cost)

        # Локальный поиск для лучшей особи (опционально)
        if use_local_search and gen % ls_freq == 0 and gen > 0:
            improved_sol, improved_cost = local_search_2opt(best_sol, flow, dist)
            if improved_cost < best_cost:
                population[best_idx] = improved_sol
                costs[best_idx] = improved_cost

        # Формирование нового поколения
        population = select_new_generation(
            population, costs, flow, dist,
            pop_size, elitism, cross_rate, mut_rate,
            tourn_size, strategy=strategy,
        )

    # Финальный отбор лучшего решения
    final_costs = [calculate_cost(ind, flow, dist) for ind in population]
    best_idx = np.argmin(final_costs)
    best_sol = population[best_idx]
    best_cost = final_costs[best_idx]

    if use_local_search:
        best_sol, best_cost = local_search_2opt(best_sol, flow, dist, max_iter=200)

    return best_sol, best_cost, best_cost_history