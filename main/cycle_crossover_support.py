import random
from .manufacturing import calculate_cost

def mul(a, b):
    """Композиция перестановок: c[i] = b[a[i]] (сначала a, затем b)."""
    n = len(a)
    return [b[a[i]] for i in range(n)]

def reverse(p):
    """Обратная перестановка: rev[p[i]] = i."""
    n = len(p)
    rev = [0] * n
    for i, pi in enumerate(p):
        rev[pi] = i
    return rev

def decompose_cycles(p):
    """Разложение перестановки на циклы. Возвращает список циклов (каждый цикл – список индексов в порядке обхода)."""
    n = len(p)
    visited = [False] * n
    cycles = []
    for i in range(n):
        if not visited[i]:
            cycle = []
            cur = i
            while not visited[cur]:
                visited[cur] = True
                cycle.append(cur)
                cur = p[cur]
            cycles.append(cycle)
    return cycles

def find_subset_sum(cycles, target):
    """
    Ищет подмножество циклов (целиком) с максимальной суммой длин, не превышающей target.
    Возвращает (selected_indices, total_length).
    Используется DP (рюкзак) с восстановлением ответа.
    """
    lengths = [len(c) for c in cycles]
    m = len(cycles)
    dp = [None] * (target + 1)
    dp[0] = []  # пустое подмножество
    for idx, length in enumerate(lengths):
        if length > target:
            continue
        for s in range(target, length - 1, -1):
            if dp[s - length] is not None and dp[s] is None:
                dp[s] = dp[s - length] + [idx]
    # Находим максимальную достижимую сумму
    best_sum = 0
    best_selected = []
    for s in range(target, -1, -1):
        if dp[s] is not None:
            best_sum = s
            best_selected = dp[s]
            break
    return best_selected, best_sum

def break_cycle(cycle, need):
    """
    Разрывает цикл, беря из него первые 'need' элементов.
    Возвращает словарь {index: new_value} для этих элементов.
    Правило:
      - Для первых need-1 элементов: ans[cycle[k]] = cycle[k+1] (т.е. p[cycle[k]]).
      - Для последнего взятого (cycle[need-1]): ans[cycle[need-1]] = cycle[0] (замыкание).
    Остальные элементы цикла (с индекса need) остаются на месте (ans[i] = i).
    """
    mapping = {}
    if need == 0:
        return mapping
    # Первые need-1 элементов: идём по порядку цикла
    for k in range(need - 1):
        mapping[cycle[k]] = cycle[k + 1]
    # Замыкание последнего взятого на первый взятый
    mapping[cycle[need - 1]] = cycle[0]
    return mapping

def build_ans(p, cycles, selected_cycles_indices, broken_cycle_idx, broken_need):
    """
    Строит перестановку ans на основе выбранных целых циклов и (возможно) разорванного цикла.
    - selected_cycles_indices: индексы циклов, взятых целиком.
    - broken_cycle_idx: индекс цикла, который разрывается, или -1, если разрыва нет.
    - broken_need: количество элементов, взятых из разорванного цикла (если broken_cycle_idx != -1).
    """
    n = len(p)
    ans = list(range(n))
    # Обрабатываем целые циклы
    for idx in selected_cycles_indices:
        cycle = cycles[idx]
        for i in range(len(cycle)):
            # для целого цикла: ans[cycle[i]] = p[cycle[i]] = cycle[(i+1) % len(cycle)]
            ans[cycle[i]] = p[cycle[i]]
    # Обрабатываем разорванный цикл
    if broken_cycle_idx != -1 and broken_need > 0:
        cycle = cycles[broken_cycle_idx]
        mapping = break_cycle(cycle, broken_need)
        for i, val in mapping.items():
            ans[i] = val
    return ans

def cycle_crossover_optimal(a, b, flow=None, dist=None):
    """
    Возвращает перестановку c, максимизирующую min(r(a,c), r(b,c)).
    Для чётного n достигает ровно n/2 расстояния до каждого родителя.
    Для нечётного n, если переданы flow и dist, пробует два варианта (floor и ceil) и выбирает потомка с лучшей стоимостью.
    """
    n = len(a)
    a_inv = reverse(a)
    p = mul(b, a_inv)
    cycles = decompose_cycles(p)

    # Сортируем циклы по убыванию длины (для адаптивности при выборе разрываемого цикла)
    # Но индексы после сортировки нужно помнить, чтобы потом сопоставить с исходными
    indexed_cycles = list(enumerate(cycles))
    indexed_cycles.sort(key=lambda x: len(x[1]), reverse=True)
    # оставим cycles как есть, а для выбора разрываемого будем искать среди невыбранных самый длинный.
    # Для удобства сделаем копию списка циклов с индексами.
    cycles_with_idx = list(enumerate(cycles))
    cycles_with_idx.sort(key=lambda x: len(x[1]), reverse=True)  # сортируем по длине

    def build_for_target(target):
        # 1. Выбираем подмножество целых циклов (максимальная сумма <= target)
        selected_indices, sum_selected = find_subset_sum(cycles, target)
        remaining = target - sum_selected
        broken_cycle_idx = -1
        broken_need = 0
        if remaining > 0:
            # Нужно разорвать один цикл, чтобы добрать remaining элементов.
            # Выбираем самый длинный цикл, который ещё не выбран целиком.
            selected_set = set(selected_indices)
            # Идём по отсортированным циклам (по убыванию длины)
            for orig_idx, cycle in cycles_with_idx:
                if orig_idx not in selected_set:
                    if len(cycle) >= remaining:
                        broken_cycle_idx = orig_idx
                        broken_need = remaining
                        break
            # Если по какой-то причине не нашли (например, все циклы короче remaining – не бывает, т.к. sum_selected + max_len >= n)
            # На всякий случай: возьмём самый длинный из всех невыбранных
            if broken_cycle_idx == -1:
                # Выбираем самый длинный из оставшихся (первый в отсортированном списке, не в selected_set)
                for orig_idx, cycle in cycles_with_idx:
                    if orig_idx not in selected_set:
                        broken_cycle_idx = orig_idx
                        broken_need = min(len(cycle), remaining)
                        break
        # Строим ans
        ans = build_ans(p, cycles, selected_indices, broken_cycle_idx, broken_need)
        c = mul(ans, a)
        return c

    if n % 2 == 0:
        target = n // 2
        c = build_for_target(target)
        return c
    else:
        target_floor = n // 2
        target_ceil = n // 2 + 1
        c_floor = build_for_target(target_floor)
        c_ceil = build_for_target(target_ceil)
        cost_floor = calculate_cost(c_floor, flow, dist)
        cost_ceil = calculate_cost(c_ceil, flow, dist)
        return c_floor if cost_floor < cost_ceil else c_ceil