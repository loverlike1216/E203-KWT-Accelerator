// Original v1 implementation. Signed16 products, signed48 exact accumulation.
module linear_engine #(
    parameter integer LANES = 4
)(
    input wire clk, input wire rst_n, input wire clear, input wire start,
    output reg busy, output reg done, output reg error,
    output reg [31:0] cycles, output reg [31:0] mac_count,
    output wire rd_valid, input wire rd_ready,
    output wire [12:0] x_addr, output wire [11:0] w_addr,
    output wire [5:0] b_addr,
    input wire rsp_valid, output wire rsp_ready, input wire rsp_error,
    input wire signed [15:0] x_data,
    input wire [LANES*16-1:0] w_data,
    input wire [LANES*48-1:0] b_data,
    output wire out_valid, input wire out_ready,
    output wire [14:0] out_index,
    output wire [LANES*48-1:0] out_data
);
    localparam [1:0] IDLE=0, REQUEST=1, RESPONSE=2, WRITEBACK=3;
    reg [1:0] state;
    reg [6:0] row;
    reg [5:0] group_index;
    reg [5:0] k;
    reg signed [47:0] accumulator [0:LANES-1];
    wire [LANES-1:0] overflow;
    wire signed [48:0] sum [0:LANES-1];
    assign rd_valid = busy && state == REQUEST;
    assign rsp_ready = busy && state == RESPONSE;
    assign x_addr = {row,6'b0} + {7'b0,k};
    assign w_addr = {k,6'b0} + {6'b0,group_index};
    assign b_addr = group_index;
    assign out_valid = busy && state == WRITEBACK;
    assign out_index = {row,8'b0} + {7'b0,group_index,2'b0};
    genvar lane;
    generate for (lane=0;lane<LANES;lane=lane+1) begin: lanes
        wire signed [15:0] weight = w_data[lane*16 +: 16];
        wire signed [31:0] product = x_data * weight;
        wire signed [47:0] bias = b_data[lane*48 +: 48];
        wire signed [47:0] base = k == 0 ? bias : accumulator[lane];
        assign sum[lane] = $signed({base[47],base}) + $signed({{17{product[31]}},product});
        assign overflow[lane] = sum[lane][48] != sum[lane][47];
        assign out_data[lane*48 +: 48] = accumulator[lane];
    end endgenerate
    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state<=IDLE; busy<=0; done<=0; error<=0; cycles<=0; mac_count<=0;
            row<=0; group_index<=0; k<=0;
            for(i=0;i<LANES;i=i+1) accumulator[i]<=0;
        end else if (clear) begin
            state<=IDLE; busy<=0; done<=0; error<=0; cycles<=0; mac_count<=0;
            row<=0; group_index<=0; k<=0;
            for(i=0;i<LANES;i=i+1) accumulator[i]<=0;
        end else begin
            if (busy) cycles<=cycles+1'b1;
            if (start && !busy) begin
                state<=REQUEST; busy<=1; done<=0; error<=0; cycles<=0; mac_count<=0;
                row<=0; group_index<=0; k<=0;
            end else case(state)
                REQUEST: if(rd_valid && rd_ready) state<=RESPONSE;
                RESPONSE: if(rsp_valid && rsp_ready) begin
                    if (rsp_error || (|overflow)) begin
                        error<=1; busy<=0; done<=0; state<=IDLE;
                    end else begin
                        for(i=0;i<LANES;i=i+1) accumulator[i]<=sum[i][47:0];
                        mac_count<=mac_count+LANES;
                        if(k==63) state<=WRITEBACK;
                        else begin k<=k+1'b1; state<=REQUEST; end
                    end
                end
                WRITEBACK: if(out_valid && out_ready) begin
                    k<=0;
                    if(group_index==63) begin
                        group_index<=0;
                        if(row==98) begin busy<=0; done<=1; state<=IDLE; end
                        else begin row<=row+1'b1; state<=REQUEST; end
                    end else begin group_index<=group_index+1'b1; state<=REQUEST; end
                end
                default: state<=IDLE;
            endcase
        end
    end
endmodule
