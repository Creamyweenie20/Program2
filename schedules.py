from Dag import DAG

def d(n): 
    return 0 if n.op in ['input', 'const'] else 1 

def ASAP(dag): 
    t = {}
    for n in dag.topo_order(): 
        t[n.id] = max((t[p.id] + d(p) for p in n.parent), default = 0)

    return t

def ASAP_con(dag, limits):
    alap = ALAP(dag)
    t = {}
    remaining = set()
    for n in dag.nodes:
        if n.op in ['input', 'const']:
            t[n.id] = 0
        else: 
            remaining.add(n.id)

    cycle = 0

    while remaining: 
        ready = [n for n in dag.nodes if n.id in remaining and all(p.id in t and t[p.id] + d(p) <= cycle for p in n.parent)]
        ready.sort(key = lambda n: alap[n.id])

        used = {}

        for n in ready:
            if used.get(n.op, 0) < limits.get(n.op, float('inf')):
                t[n.id] = cycle
                used[n.op] = used.get(n.op, 0) + 1
                remaining.remove(n.id)
        cycle += 1 

    return t


def ALAP(dag, L = None):
    if L == None: 
        L = max(dag.levels().values())

    t = {}

    for n in reversed(dag.topo_order()): 
        t[n.id] = min((t[c.id] for c in n.child), default = L) - d(n)

    return t 


def ALAP_con(dag, limits, L = None): 
    if L is None: 
        L = max(dag.levels().values()) + 1

    asap = ASAP(dag) 
    t = {}
    remaining = {n.id for n in dag.nodes if d(n) > 0}

    for cycle in range(L - 1, -1, -1): 
        ready = [n for n in dag.nodes if n.id in remaining and all(c.id in t and t[c.id] >= cycle + d(n) for c in n.child)]

        ready.sort(key = lambda n: -asap[n.id]) 

        used = {}
        for n in ready:
            if used.get(n.op, 0) < limits.get(n.op, float('inf')):
                t[n.id] = cycle
                used[n.op] = used.get(n.op, 0) + 1
                remaining.remove(n.id)

    for n in reversed(dag.topo_order()): 
        if d(n) == 0: 
            t[n.id] = min((t[c.id] for c in n.child), default = L)

    return t 