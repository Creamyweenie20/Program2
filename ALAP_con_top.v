// Auto-generated top module. Do not edit by hand.
// sw[15] = 0  ->  variables (sw[12:8] = index):
//    0 = B   (input, loadable)
//    1 = C   (input, loadable)
//    2 = E   (input, loadable)
//    3 = G   (input, loadable)
//    4 = I   (input, loadable)
//    5 = K   (input, loadable)
//    6 = L   (input, loadable)
//    7 = J   (result)
//    8 = H   (result)
// sw[15] = 1  ->  functional units (value the unit is computing in the CURRENT cycle):
//    0 = add0   (A in cycle 1, D in cycle 2, F in cycle 3, H in cycle 4)
//    1 = add1   (J in cycle 4)
module ALAP_con_top(
    input         clk,
    input  [15:0] sw,
    input         btnC,   // STEP
    input         btnL,   // LOAD
    input         btnU,   // RESET
    output [6:0]  seg,
    output [7:0]  an,     // Nexys A7 has 8 digits; 0 = digit on
    output        dp,     // decimal point; 1 = off
    output [15:0] led
);
    localparam WIDTH = 8;

    // Buttons -> one-clock-tick pulses
    wire ui_step, ui_load, ui_rst;
    button_step bs_step (.clk(clk), .btn(btnC), .pulse(ui_step));
    button_step bs_load (.clk(clk), .btn(btnL), .pulse(ui_load));
    button_step bs_rst  (.clk(clk), .btn(btnU), .pulse(ui_rst));

    // Switch decoding
    wire [4:0] ui_idx = sw[12:8];
    wire [7:0] ui_val = sw[7:0];
    wire       ui_unit_mode = sw[15];

    // One stored register per input. LOAD writes the number on sw[7:0] into the chosen one.
    reg [WIDTH-1:0] B = 0;
    reg [WIDTH-1:0] C = 0;
    reg [WIDTH-1:0] E = 0;
    reg [WIDTH-1:0] G = 0;
    reg [WIDTH-1:0] I = 0;
    reg [WIDTH-1:0] K = 0;
    reg [WIDTH-1:0] L = 0;
    always @(posedge clk) begin
        if (ui_load && !ui_unit_mode) begin
            case (ui_idx)
                5'd0: B <= ui_val;
                5'd1: C <= ui_val;
                5'd2: E <= ui_val;
                5'd3: G <= ui_val;
                5'd4: I <= ui_val;
                5'd5: K <= ui_val;
                5'd6: L <= ui_val;
                default: ;
            endcase
        end
    end

    // The synthesized core
    wire [2:0] state;
    wire [WIDTH-1:0] J, H;
    wire [WIDTH-1:0] ui_obs_out;
    ALAP_con #(.WIDTH(WIDTH)) core (
        .clk(clk),
        .rst(ui_rst),
        .stp(ui_step),
        .B(B),
        .C(C),
        .E(E),
        .G(G),
        .I(I),
        .K(K),
        .L(L),
        .J(J),
        .H(H),
        .obs_sel(ui_idx),
        .obs_out(ui_obs_out),
        .state(state)
    );

    // Display mux
    reg [WIDTH-1:0] ui_var;
    always @(*) begin
        case (ui_idx)
            5'd0: ui_var = B;
            5'd1: ui_var = C;
            5'd2: ui_var = E;
            5'd3: ui_var = G;
            5'd4: ui_var = I;
            5'd5: ui_var = K;
            5'd6: ui_var = L;
            5'd7: ui_var = J;
            5'd8: ui_var = H;
            default: ui_var = 0;
        endcase
    end
    wire [WIDTH-1:0] ui_unit = ({1'b0, ui_idx} < 6'd2) ? ui_obs_out : {WIDTH{1'b0}};
    wire [WIDTH-1:0] ui_shown = ui_unit_mode ? ui_unit : ui_var;

    wire [7:0]  ui_lo   = ui_shown;
    wire [15:0] ui_full = ui_shown;
    wire [15:0] ui_disp = (WIDTH <= 8) ? {ui_unit_mode, 2'b00, ui_idx, ui_lo} : ui_full;
    // seg_driver.v drives 4 digits. They go on the right; the 4 left digits and the dot stay off.
    wire [3:0] ui_an;
    seg_driver disp (.clk(clk), .value(ui_disp), .seg(seg), .an(ui_an));
    assign an = {4'b1111, ui_an};
    assign dp = 1'b1;

    // LEDs show the current schedule step
    assign led = 16'd0 | state;
endmodule