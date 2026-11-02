`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/02/2026 12:19:22 AM
// Design Name: 
// Module Name: functions
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module n_bit_adder#(parameter WIDTH = 16)(
    input [WIDTH - 1 : 0] a, 
    input [WIDTH - 1 : 0] b,
    input                 cin, 
    output                cout,  
    output [WIDTH - 1 : 0]     sum_out
    );
    
    assign {cout, sum_out} = a + b + cin;
    
endmodule

module n_bit_subtractor #(parameter WIDTH = 16) (
    input [WIDTH - 1 : 0] a, 
    input [WIDTH - 1 : 0] b, 
    output [WIDTH - 1 : 0]               sub_out
); 
    assign sub_out = a + ~b + 1;
endmodule 

module n_bit_multiplier #(parameter WIDTH = 16)(
    input  [WIDTH-1:0] a,
    input  [WIDTH-1:0] b,
    output reg [2*WIDTH-1:0] product
);
    integer i;
    reg [2*WIDTH-1:0] acc;

    always @(*) begin
        acc = {2*WIDTH{1'b0}};
        for (i = 0; i < WIDTH; i = i + 1) begin
            acc = acc + ((a & {WIDTH{b[i]}}) << i);
        end
        product = acc;
    end
endmodule
