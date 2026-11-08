from collections import defaultdict

def write_generator(dag, sched, module_name = "generator"): 
    lines = [f"module {module_name} #(parameter WIDTH = 8)("]
    lines.append("input     clk,")
    lines.append("input     rst,")
    lines.append("input     stp,")

    op_nodes = [n for n in dag.nodes if n.op in ["+", "-", "*"]]
    base = min(sched[n.id] for n in op_nodes)
    level = {n.id: sched[n.id] - base + 1 for n in dag.nodes}

    num_states = max(level[n.id] for n in op_nodes)
    state_w = max(1, num_states.bit_length())

    for n in dag.topo_order(): 
        if n.op in ['input']:
            lines.append(f'input [WIDTH - 1 : 0]    {n.result},')
        elif not n.child: 
            lines.append(f"output reg [WIDTH - 1 : 0]   {n.result},")

    lines.append("input [4:0]    obs_sel,")
    lines.append("output reg [WIDTH - 1 : 0]   obs_out,")
    lines.append(f"output reg [{state_w - 1}:0]    state);")
    inner = [n.result for n in dag.nodes if n.op in ["+", "-", "*"] and n.child]
    if inner:
        lines.append("    reg [WIDTH - 1 : 0] " + ", ".join(inner) + ";")
    
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
        in_add += 1

    in_sub = 0
    for i in range(maxes['-']):
        regiters += f" sub_in{i}_a, sub_in{i}_b,"
        in_sub += 1

    in_mult = 0 
    for i in range(maxes['*']):
        regiters += f" mult_in{i}_a, mult_in{i}_b,"
        in_mult += 1 

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

    for i in range(maxes["+"]):
        lines.append(f"    n_bit_adder #(WIDTH) add{i} (.a(add_in{i}_a), .b(add_in{i}_b), .cin(1'b0), .cout(), .sum_out(add_out{i}));")
    for i in range(maxes['-']):
        lines.append(f"    n_bit_subtractor #(WIDTH) sub{i} (.a(sub_in{i}_a), .b(sub_in{i}_b), .sub_out(sub_out{i}));")
    for i in range(maxes['*']):
        lines.append(f"    wire [2*WIDTH - 1 : 0] mult_full{i};")
        lines.append(f"    n_bit_multiplier #(WIDTH) mult{i} (.a(mult_in{i}_a), .b(mult_in{i}_b), .product(mult_full{i}));")
        lines.append(f"    assign mult_out{i} = mult_full{i}[WIDTH - 1 : 0];")

    lines.append("    always @(*) begin")
    lines.append("        case (obs_sel)")
    k = 0
    for op, prefix in (("+", "add"), ("-", "sub"), ("*", "mult")):
        for i in range(maxes[op]):
            lines.append(f"            {k}: obs_out = {prefix}_out{i};")
            k += 1
    lines.append("            default: obs_out = 0;")
    lines.append("        endcase")
    lines.append("    end")

    lines.append("    always @(*) begin")

    setting = '        '
    for i in range(in_add):
        setting += f"add_in{i}_a = 0; add_in{i}_b = 0; "
    for i in range(in_sub): 
        setting += f"sub_in{i}_a = 0; sub_in{i}_b = 0; "
    for i in range(in_mult): 
        setting += f'mult_in{i}_a = 0; mult_in{i}_b = 0; '

    lines.append(setting)

    lines.append("        case (state)")

    names = {"+": "add", "-": "sub", "*": "mult"}
    ops = [n for n in dag.nodes if n.op in names]
    num_states = max(level[n.id] for n in ops)   

    unit = {}
    for s in range(num_states):
        lines.append(f"            {s}: begin")
        idx = defaultdict(int)
        for n in ops:
            if level[n.id] != s + 1:
                continue
            i = idx[n.op]
            idx[n.op] += 1
            unit[n.id] = i
            p = names[n.op]
            lines.append(f"                {p}_in{i}_a = {n.parent[0].result}; {p}_in{i}_b = {n.parent[1].result};")
        lines.append("            end")
    lines.append("        endcase")
    lines.append("    end")

    lines.append("    always @(posedge clk) begin")
    lines.append("        if (rst) begin")
    lines.append("            state <= 0; " + " ".join(f"{n.result} <= 0;" for n in ops))
    lines.append("        end else if (stp) begin")
    lines.append("            case (state)")
    for s in range(num_states):
        lines.append(f"                {s}: begin")
        for n in ops:
            if level[n.id] == s + 1:
                lines.append(f"                    {n.result} <= {names[n.op]}_out{unit[n.id]};")
        lines.append("                end")
    lines.append("            endcase")
    lines.append(f"            if (state != {num_states}) state <= state + 1;")
    lines.append("        end")
    lines.append("    end")
    lines.append("endmodule")

    return "\n".join(lines)
