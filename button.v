module button_step #(parameter LIMIT = 1_000_000)(   // 1,000,000 ticks = 10 ms at 100 MHz
    input      clk,
    input      btn,       
    output reg pulse = 0  
);
    
    reg sync0 = 0, sync1 = 0;
    always @(posedge clk) begin
        sync0 <= btn;
        sync1 <= sync0;
    end

    
    reg [19:0] count  = 0;
    reg        stable = 0;
    always @(posedge clk) begin
        if (sync1 == stable)
            count <= 0;                      
        else begin
            count <= count + 1;              
            if (count == LIMIT - 1) begin    
                stable <= sync1;             
                count  <= 0;
            end
        end
    end

    
    reg stable_prev = 0;
    always @(posedge clk) begin
        stable_prev <= stable;
        pulse       <= stable & ~stable_prev;   
    end
endmodule