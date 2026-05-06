import numpy as np
import random

from .manufacturing import calculate_cost
from .cycle_crossover_support import *

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
        for i in range(n-1):
            for j in range(i+1, n):
                new_perm = best_perm[:]
                new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
                new_cost = calculate_cost(new_perm, flow, dist)
                if new_cost < best_cost:
                    best_cost = new_cost
                    best_perm = new_perm
                    improved = True
        iter_count += 1
    return best_perm, best_cost



def evolutionary_algorithm(flow, dist, pop_size=100, gens=200,
                           cross_rate=0.9, mut_rate=0.2, tourn_size=5,
                           elitism=2, use_local_search=False, ls_freq=10,
                           verbose=False):
    n = flow.shape[0]
    population = [list(np.random.permutation(n)) for _ in range(pop_size)]
    costs = [calculate_cost(ind, flow, dist) for ind in population]

    best_cost_history = []

    for gen in range(gens):
        costs = [calculate_cost(ind, flow, dist) for ind in population]
        best_idx = np.argmin(costs)
        best_cost = costs[best_idx]
        best_sol = population[best_idx][:]

        best_cost_history.append(best_cost)

        # Элитизм
        sorted_idx = np.argsort(costs)
        new_pop = [population[sorted_idx[i]][:] for i in range(elitism)]

        # Локальный поиск для лучшей особи
        if use_local_search and gen % ls_freq == 0 and gen > 0:
            improved_sol, improved_cost = local_search_2opt(best_sol, flow, dist)
            if improved_cost < best_cost:
                population[best_idx] = improved_sol
                costs[best_idx] = improved_cost

        # Формирование нового поколения
        while len(new_pop) < pop_size:
            contenders = random.sample(range(pop_size), tourn_size)
            p1_idx = min(contenders, key=lambda i: costs[i])
            contenders = random.sample(range(pop_size), tourn_size)
            p2_idx = min(contenders, key=lambda i: costs[i])
            parent1 = population[p1_idx]
            parent2 = population[p2_idx]

            if random.random() < cross_rate:
                # child = order_crossover(parent1, parent2)
                child = cycle_crossover_optimal(parent1, parent2)
            else:
                child = parent1[:]

            child = mutate_swap(child, mut_rate)
            new_pop.append(child)

        population = new_pop

    final_costs = [calculate_cost(ind, flow, dist) for ind in population]
    best_idx = np.argmin(final_costs)
    best_sol = population[best_idx]
    best_cost = final_costs[best_idx]

    if use_local_search:
        best_sol, best_cost = local_search_2opt(best_sol, flow, dist, max_iter=200)

    return best_sol, best_cost, best_cost_history