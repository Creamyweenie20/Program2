from Dag import DAG

def d(n): 
    return 0 if n.op in ['input', 'const'] else 1 

def ASAP(dag): 
    t = {}
    for n in dag.topo_order(): 
        t[n.id] = max((t[p.id] + d(p) for p in n.parent), default = 0)

    return t

def ALAP(dag, L = None):
    if L == None: 
        L = max(dag.levels().values())

    t = {}

    for n in reversed(dag.topo_order()): 
        t[n.id] = min((t[c.id] for c in n.child), default = L) - d(n)

    return t 
