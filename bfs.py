import threading
from collections import deque

_tables = {}
_locks = {}
_master_lock = threading.Lock()

def _build_distance_table(n):
    start = tuple(range(1, n + 1))
    dist = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        next_depth = dist[state] + 1
        for k in range(2, n + 1):
            neighbour = state[:k][::-1] + state[k:]
            if neighbour not in dist:
                dist[neighbour] = next_depth
                queue.append(neighbour)
    return dist

def get_distance_table(n):
    with _master_lock:
        lock = _locks.setdefault(n, threading.Lock())
    with lock:
        if n not in _tables:
            _tables[n] = _build_distance_table(n)
    return _tables[n]

def optimal_flips(stack):
    return get_distance_table(len(stack))[tuple(stack)]

def warm_up(max_n, min_n=3):
    for n in range(min_n, max_n + 1):
        get_distance_table(n)
