module ALAP #(parameter WIDTH = 8)(
input     clk,
input     rst,
input     stp,
input [WIDTH - 1 : 0]    B,
input [WIDTH - 1 : 0]    C,
input [WIDTH - 1 : 0]    E,
input [WIDTH - 1 : 0]    G,
input [WIDTH - 1 : 0]    I,
input [WIDTH - 1 : 0]    K,
input [WIDTH - 1 : 0]    L,
output reg [WIDTH - 1 : 0]   J,
output reg [WIDTH - 1 : 0]   H,
input [4:0]    obs_sel,
output reg [WIDTH - 1 : 0]   obs_out,
output reg [2:0]    state);
    reg [WIDTH - 1 : 0] A, D, F;
    reg [WIDTH - 1 : 0] add_in0_a, add_in0_b, add_in1_a, add_in1_b;
    wire [WIDTH - 1 : 0] add_out0, add_out1;
    n_bit_adder #(WIDTH) add0 (.a(add_in0_a), .b(add_in0_b), .cin(1'b0), .cout(), .sum_out(add_out0));
    n_bit_adder #(WIDTH) add1 (.a(add_in1_a), .b(add_in1_b), .cin(1'b0), .cout(), .sum_out(add_out1));
    always @(*) begin
        case (obs_sel)
            0: obs_out = add_out0;
            1: obs_out = add_out1;
            default: obs_out = 0;
        endcase
    end
    always @(*) begin
        add_in0_a = 0; add_in0_b = 0; add_in1_a = 0; add_in1_b = 0; 
        case (state)
            0: begin
                add_in0_a = B; add_in0_b = C;
            end
            1: begin
                add_in0_a = A; add_in0_b = E;
            end
            2: begin
                add_in0_a = D; add_in0_b = G;
            end
            3: begin
                add_in0_a = F; add_in0_b = I;
                add_in1_a = K; add_in1_b = L;
            end
        endcase
    end
    always @(posedge clk) begin
        if (rst) begin
            state <= 0; A <= 0; D <= 0; F <= 0; H <= 0; J <= 0;
        end else if (stp) begin
            case (state)
                0: begin
                    A <= add_out0;
                end
                1: begin
                    D <= add_out0;
                end
                2: begin
                    F <= add_out0;
                end
                3: begin
                    H <= add_out0;
                    J <= add_out1;
                end
            endcase
            if (state != 4) state <= state + 1;
        end
    end
endmodule