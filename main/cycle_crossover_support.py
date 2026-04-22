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


def solve(p, k):
  n = len(p)
  ind = set()
  ans = list(range(n))
  for i in range(n):
    if len(ind)>=k:
      break
    if i not in ind:
      c_ind = i
      # Заносим в множество индексы из цикла
      while c_ind not in ind and len(ind)<k:
        ans[c_ind] = p[c_ind]
        ind.add(c_ind)
        c_ind = p[c_ind]
      if c_ind not in ind:
        ans[c_ind]=i
  return ans

def decompose_cycles(p):
    """Разложение перестановки на циклы. Возвращает список циклов (каждый цикл – список индексов)."""
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
    Поиск подмножества циклов, сумма длин которых равна target.
    Возвращает список индексов выбранных циклов или None, если невозможно.
    Используется динамическое программирование (рюкзак) с восстановлением ответа.
    """
    # Длины циклов
    lengths = [len(c) for c in cycles]
    m = len(cycles)
    # DP: dp[s] = можно ли набрать сумму s, и какой последний использованный цикл
    dp = [None] * (target + 1)
    dp[0] = []  # пустое подмножество
    for idx, length in enumerate(lengths):
        if length > target:
            continue
        for s in range(target, length - 1, -1):
            if dp[s - length] is not None and dp[s] is None:
                dp[s] = dp[s - length] + [idx]
    if dp[target] is None:
        return None
    return dp[target]

def build_ans_from_cycles(p, cycles, selected_indices):
    """
    Строит перестановку ans, где для всех позиций в выбранных циклах ans[i] = p[i],
    а для остальных ans[i] = i.
    """
    n = len(p)
    ans = list(range(n))
    selected_set = set()
    for idx in selected_indices:
        for node in cycles[idx]:
            selected_set.add(node)
    for i in range(n):
        if i in selected_set:
            ans[i] = p[i]
    return ans

def cycle_crossover_optimal(a, b):
    """
    Возвращает перестановку c, максимизирующую min(r(a,c), r(b,c)).
    Если n чётное и существует подмножество циклов p с суммой n/2, то достигается
    r(a,c)=r(b,c)=n/2. Иначе используется эвристика solve(p, n//2).
    """
    n = len(a)
    # Вычисляем p = b ∘ a^{-1}
    a_inv = reverse(a)
    p = mul(b, a_inv)

    # Разбиваем p на циклы
    cycles = decompose_cycles(p)

    # Пытаемся найти идеальное решение для чётных n
    if n % 2 == 0:
        target = n // 2
        selected = find_subset_sum(cycles, target)
        if selected is not None:
            ans = build_ans_from_cycles(p, cycles, selected)
            # c = ans ∘ a
            c = mul(ans, a)
            return c

    k = n // 2
    ans = solve(p, k)
    c = mul(ans, a)
    return c
