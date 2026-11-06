from collections import defaultdict

def write_generator(dag, module_name = "generator"): 
    lines = [f"module {module_name} #(parameter WIDTH = 8)("]
    lines.append("input     clk,")
    lines.append("input     rst,")
    lines.append("input     stp,")
    for n in dag.topo_order(): 
        if n.op in ['input']:
            lines.append(f'input [WIDTH - 1 : 0]    {n.result},')
        elif not n.child: 
            lines.append(f"output reg [WIDTH - 1 : 0]   {n.result},")
    lines.append("output reg [1:0]    state);")

    level = dag.levels()
    counts = defaultdict(int)
    for n in dag.nodes: 
        if n.op in ['input', 'const']:
            continue 
        counts[(level[n.id], n.op)] += 1

    maxes = {"+": 0, "-": 0, "*": 0}

    for (_, op), count in counts.items(): 
        if op not in maxes: 
            maxes[op] = count
        elif maxes[op] < count: 
            maxes[op] = count

    regiters = "    reg [WIDTH - 1 : 0]"

    in_add = 0 
    for i in range(maxes["+"]):
        regiters += f" add_in{i}_a, add_in{i}_b,"
        in_add += 2 

    in_sub = 0
    for i in range(maxes['-']):
        regiters += f" sub_in{i}_a, sub_in{i}_b,"
        in_sub += 2 

    in_mult = 0 
    for i in range(maxes['*']):
        regiters += f" mult_in{i}_a, mult_in{i}_b,"
        in_mult += 2 

    regiters = regiters[:-1] + ";"

    lines.append(regiters)

    wires = "    wire [WIDTH - 1 : 0]"

    for i in range(maxes["+"]):
        wires += f" add_out{i},"
    for i in range(maxes['-']):
        wires += f" sub_out{i},"
    for i in range(maxes['*']):
        wires += f" mult_out{i},"

    wires = wires[:-1] + ";"

    lines.append(wires)