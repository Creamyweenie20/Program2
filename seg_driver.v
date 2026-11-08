module seg_driver(
    input             clk,
    input      [15:0] value,    
    output reg [6:0]  seg,      
    output reg [3:0]  an        
);
    
    reg [17:0] refresh = 0;
    always @(posedge clk) refresh <= refresh + 1;

    reg [3:0] nibble;   
    
    always @(*) begin
        case (refresh[17:16])
            2'd0:    begin an = 4'b1110; nibble = value[3:0];   end  
            2'd1:    begin an = 4'b1101; nibble = value[7:4];   end
            2'd2:    begin an = 4'b1011; nibble = value[11:8];  end
            default: begin an = 4'b0111; nibble = value[15:12]; end  
        endcase
    end

    
    always @(*) begin
        case (nibble)
            4'h0: seg = 7'h40;   4'h1: seg = 7'h79;
            4'h2: seg = 7'h24;   4'h3: seg = 7'h30;
            4'h4: seg = 7'h19;   4'h5: seg = 7'h12;
            4'h6: seg = 7'h02;   4'h7: seg = 7'h78;
            4'h8: seg = 7'h00;   4'h9: seg = 7'h10;
            4'hA: seg = 7'h08;   4'hB: seg = 7'h03;
            4'hC: seg = 7'h46;   4'hD: seg = 7'h21;
            4'hE: seg = 7'h06;   default: seg = 7'h0E;  
        endcase
    end
endmodule