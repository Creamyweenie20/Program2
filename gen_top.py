"""Generates the top-level Verilog module (buttons, switches, 7-segment display)
around the core produced by the ORIGINAL Generator.write_generator().
This file does not import Generator.py.

Board: Digilent Nexys A7 (100 MHz clock, 16 switches, 5 buttons, 8-digit display).
Only the four right-most digits are used; the other four are switched off.

Controls
    sw[7:0]    number to load
    sw[12:8]   index: which input to load / which variable or unit to display
    sw[15]     display mode: 0 = variables (inputs and final results)
                             1 = functional units (add0, add1, sub0, mult0, ...)
    btnC       STEP   (one press = one schedule cycle)
    btnL       LOAD   (stores sw[7:0] into the input chosen by sw[12:8]; only works when sw[15] = 0)
    btnU       RESET  (restarts the schedule; loaded inputs are kept)

Display (4 hex digits): left two = mode and index (00-1F variables, 80-9F units),
                        right two = the value shown.

Unit view shows what each unit is computing in the CURRENT cycle, i.e. the result that
the next STEP press will store. This is how the in-between values (which are not outputs
of the core) can be inspected.

unit_view=True needs the core to have the obs_sel / obs_out ports (see the generator patch).
Use unit_view=False with a core that does not have them.

Pass the same name you gave write_generator(..., module_name=...) as core_name.
"""
from collections import defaultdict

NAMES = {"+": "add", "-": "sub", "*": "mult"}


def write_top(dag, sched, core_name="generator", top_name="top", width=8, verbose=True, unit_view=True):
    order = list(dag.topo_order())
    inputs = [n for n in order if n.op == "input"]
    # Same rule Generator.py uses to decide which nodes become output ports
    outputs = [n for n in order if n.op != "input" and not n.child]
    variables = inputs + outputs

    ops = [n for n in dag.nodes if n.op in NAMES]
    if not ops:
        raise ValueError("The DAG has no arithmetic operations.")

    # Same formulas Generator.py uses for the state counter
    base = min(sched[n.id] for n in ops)
    level = {n.id: sched[n.id] - base + 1 for n in ops}
    num_states = max(level.values())
    state_w = max(1, num_states.bit_length())

    # Which unit instance runs each operation, and how many units of each type exist.
    # Same rule as Generator.py: within a cycle, operations take units 0, 1, ... in dag.nodes order.
    unit = {}
    maxes = {"+": 0, "-": 0, "*": 0}
    for s in range(1, num_states + 1):
        used = defaultdict(int)
        for n in ops:
            if level[n.id] == s:
                unit[n.id] = used[n.op]
                used[n.op] += 1
        for op, c in used.items():
            maxes[op] = max(maxes[op], c)
    # Unit numbering used by obs_sel: all adders, then all subtractors, then all multipliers
    units = [(op, i) for op in ("+", "-", "*") for i in range(maxes[op])]

    if len(variables) > 32:
        raise ValueError(f"{len(variables)} variables, but the 5 index switches can only address 32.")
    if unit_view and len(units) > 32:
        raise ValueError(f"{len(units)} functional units, but the 5 index switches can only address 32.")

    work = defaultdict(list)
    for n in ops:
        work[(n.op, unit[n.id])].append((level[n.id], n.result))

    map_lines = ["sw[15] = 0  ->  variables (sw[12:8] = index):"]
    for i, n in enumerate(variables):
        kind = "input, loadable" if n.op == "input" else "result"
        map_lines.append(f"  {i:2d} = {n.result}   ({kind})")
    if unit_view:
        map_lines.append("sw[15] = 1  ->  functional units (value the unit is computing in the CURRENT cycle):")
        for k, (op, i) in enumerate(units):
            jobs = ", ".join(f"{r} in cycle {c}" for c, r in sorted(work[(op, i)]))
            map_lines.append(f"  {k:2d} = {NAMES[op]}{i}   ({jobs})")
    if verbose:
        print("\n".join(map_lines))

    L = []
    a = L.append

    a("// Auto-generated top module. Do not edit by hand.")
    for m in map_lines:
        a("// " + m)
    a(f"module {top_name}(")
    a("    input         clk,")
    a("    input  [15:0] sw,")
    a("    input         btnC,   // STEP")
    a("    input         btnL,   // LOAD")
    a("    input         btnU,   // RESET")
    a("    output [6:0]  seg,")
    a("    output [7:0]  an,     // Nexys A7 has 8 digits; 0 = digit on")
    a("    output        dp,     // decimal point; 1 = off")
    a("    output [15:0] led")
    a(");")
    a(f"    localparam WIDTH = {width};")
    a("")

    a("    // Buttons -> one-clock-tick pulses")
    a("    wire ui_step, ui_load, ui_rst;")
    a("    button_step bs_step (.clk(clk), .btn(btnC), .pulse(ui_step));")
    a("    button_step bs_load (.clk(clk), .btn(btnL), .pulse(ui_load));")
    a("    button_step bs_rst  (.clk(clk), .btn(btnU), .pulse(ui_rst));")
    a("")

    a("    // Switch decoding")
    a("    wire [4:0] ui_idx = sw[12:8];")
    a("    wire [7:0] ui_val = sw[7:0];")
    if unit_view:
        a("    wire       ui_unit_mode = sw[15];")
    a("")

    load_cond = "ui_load && !ui_unit_mode" if unit_view else "ui_load"
    a("    // One stored register per input. LOAD writes the number on sw[7:0] into the chosen one.")
    for n in inputs:
        a(f"    reg [WIDTH-1:0] {n.result} = 0;")
    if inputs:
        a("    always @(posedge clk) begin")
        a(f"        if ({load_cond}) begin")
        a("            case (ui_idx)")
        for i, n in enumerate(inputs):
            a(f"                5'd{i}: {n.result} <= ui_val;")
        a("                default: ;")
        a("            endcase")
        a("        end")
        a("    end")
    a("")

    a("    // The synthesized core")
    a(f"    wire [{state_w - 1}:0] state;")
    if outputs:
        a("    wire [WIDTH-1:0] " + ", ".join(n.result for n in outputs) + ";")
    conns = [".clk(clk)", ".rst(ui_rst)", ".stp(ui_step)"]
    conns += [f".{n.result}({n.result})" for n in variables]
    if unit_view:
        a("    wire [WIDTH-1:0] ui_obs_out;")
        conns += [".obs_sel(ui_idx)", ".obs_out(ui_obs_out)"]
    conns += [".state(state)"]
    a(f"    {core_name} #(.WIDTH(WIDTH)) core (")
    a("        " + ",\n        ".join(conns))
    a("    );")
    a("")

    a("    // Display mux")
    a("    reg [WIDTH-1:0] ui_var;")
    a("    always @(*) begin")
    a("        case (ui_idx)")
    for i, n in enumerate(variables):
        a(f"            5'd{i}: ui_var = {n.result};")
    a("            default: ui_var = 0;")
    a("        endcase")
    a("    end")
    if unit_view:
        a("    wire [WIDTH-1:0] ui_unit = ({1'b0, ui_idx} < 6'd" + str(len(units)) + ") ? ui_obs_out : {WIDTH{1'b0}};")
        a("    wire [WIDTH-1:0] ui_shown = ui_unit_mode ? ui_unit : ui_var;")
        mode_bit = "ui_unit_mode"
    else:
        a("    wire [WIDTH-1:0] ui_shown = ui_var;")
        mode_bit = "1'b0"
    a("")
    a("    wire [7:0]  ui_lo   = ui_shown;")
    a("    wire [15:0] ui_full = ui_shown;")
    a("    wire [15:0] ui_disp = (WIDTH <= 8) ? {" + mode_bit + ", 2'b00, ui_idx, ui_lo} : ui_full;")
    a("    // seg_driver.v drives 4 digits. They go on the right; the 4 left digits and the dot stay off.")
    a("    wire [3:0] ui_an;")
    a("    seg_driver disp (.clk(clk), .value(ui_disp), .seg(seg), .an(ui_an));")
    a("    assign an = {4'b1111, ui_an};")
    a("    assign dp = 1'b1;")
    a("")
    a("    // LEDs show the current schedule step")
    a("    assign led = 16'd0 | state;")
    a("endmodule")

    return "\n".join(L)
