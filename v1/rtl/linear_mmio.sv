// Reference ICB slave adapter. Official address map must be rebound after audit.
// Windows: 0x00000 control, 0x10000 X, 0x20000 W, 0x30000 bias.
module linear_mmio(
    input wire clk, input wire rst_n,
    input wire cmd_valid, output wire cmd_ready,
    input wire [19:0] cmd_addr, input wire cmd_read,
    input wire [31:0] cmd_wdata, input wire [3:0] cmd_wmask,
    output reg rsp_valid, input wire rsp_ready,
    output reg rsp_err, output reg [31:0] rsp_rdata,
    output wire out_valid, input wire out_ready,
    output wire [14:0] out_index, output wire [191:0] out_data,
    output wire done_irq,
    output wire [31:0] compute_cycles, output wire [31:0] mac_count
);
    reg start_pulse, clear_pulse, protocol_error;
    reg clearing;
    reg [11:0] clear_addr;
    reg [11:0] x_words;
    reg [13:0] w_words;
    reg [9:0] b_words;
    reg must_clear;
    wire busy, done, compute_error;
    wire rd_valid, rd_ready, mem_rsp_ready;
    reg mem_rsp_valid;
    wire [12:0] x_addr;
    wire [11:0] w_addr;
    wire [5:0] b_addr;
    wire [15:0] x_out[0:1];
    wire [15:0] w_out[0:3];
    wire [15:0] b_out[0:11];
    reg x_parity;
    assign cmd_ready = !rsp_valid || rsp_ready;
    wire accept = cmd_valid && cmd_ready;
    wire valid_write = accept && !cmd_read && cmd_wmask==4'hf && cmd_addr[1:0]==0 && !busy && !start_pulse && !clearing && !must_clear;
    wire x_write = valid_write && cmd_addr[19:16]==1 && cmd_addr[15:2]=={2'b0,x_words} && x_words<3168;
    wire w_write = valid_write && cmd_addr[19:16]==2 && cmd_addr[15:2]==w_words && w_words<8192;
    wire b_write = valid_write && cmd_addr[19:16]==3 && cmd_addr[15:2]=={4'b0,b_words} && b_words<512;
    assign rd_ready = !clearing && (!mem_rsp_valid || mem_rsp_ready);
    wire read_enable = rd_valid && rd_ready;
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin mem_rsp_valid<=0; x_parity<=0; end
        else begin
            if(mem_rsp_valid && mem_rsp_ready) mem_rsp_valid<=0;
            if(read_enable) begin mem_rsp_valid<=1; x_parity<=x_addr[0]; end
            if(clear_pulse) mem_rsp_valid<=0;
        end
    end
    genvar lane, chunk;
    generate for(lane=0;lane<2;lane=lane+1) begin: input_banks
        sram16_reference #(.AW(12)) ram(.clk(clk), .en(clearing||x_write||read_enable),
            .we(clearing||x_write), .addr(clearing ? clear_addr : x_write ? x_words : x_addr[12:1]),
            .wdata(clearing ? 16'b0 : cmd_wdata[lane*16+:16]), .rdata(x_out[lane]));
    end
    for(lane=0;lane<4;lane=lane+1) begin: weight_banks
        wire host_write = w_write && w_words[0]==(lane/2);
        sram16_reference #(.AW(12)) ram(.clk(clk), .en(clearing||host_write||read_enable),
            .we(clearing||host_write), .addr(clearing ? clear_addr : host_write ? w_words[12:1] : w_addr),
            .wdata(clearing ? 16'b0 : cmd_wdata[(lane%2)*16+:16]), .rdata(w_out[lane]));
        for(chunk=0;chunk<3;chunk=chunk+1) begin: bias_chunks
            wire host_write = b_write && b_words[2:1]==lane && (chunk<2 ? !b_words[0] : b_words[0]);
            wire do_clear = clearing && clear_addr<128;
            sram16_reference #(.AW(7)) ram(.clk(clk), .en(do_clear||host_write||read_enable),
                .we(do_clear||host_write), .addr(do_clear ? clear_addr[6:0] : host_write ? {1'b0,b_words[8:3]} : {1'b0,b_addr}),
                .wdata(do_clear ? 16'b0 : cmd_wdata[(chunk%2)*16+:16]), .rdata(b_out[lane*3+chunk]));
        end
    end endgenerate
    wire [63:0] weights = {w_out[3],w_out[2],w_out[1],w_out[0]};
    wire [191:0] biases;
    generate for(lane=0;lane<4;lane=lane+1) begin: bias_words
        assign biases[lane*48+:48] = {b_out[lane*3+2],b_out[lane*3+1],b_out[lane*3]};
    end endgenerate
    linear_engine core(.clk(clk),.rst_n(rst_n),.clear(clear_pulse),.start(start_pulse),
        .busy(busy),.done(done),.error(compute_error),.cycles(compute_cycles),.mac_count(mac_count),
        .rd_valid(rd_valid),.rd_ready(rd_ready),.x_addr(x_addr),.w_addr(w_addr),.b_addr(b_addr),
        .rsp_valid(mem_rsp_valid),.rsp_ready(mem_rsp_ready),.rsp_error(1'b0),
        .x_data(x_parity ? x_out[1] : x_out[0]),.w_data(weights),.b_data(biases),
        .out_valid(out_valid),.out_ready(out_ready),.out_index(out_index),.out_data(out_data));
    assign done_irq = done || compute_error || protocol_error;
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            start_pulse<=0; clear_pulse<=0; protocol_error<=0; clearing<=1; clear_addr<=0;
            x_words<=0; w_words<=0; b_words<=0; must_clear<=0;
            rsp_valid<=0; rsp_err<=0; rsp_rdata<=0;
        end else begin
            start_pulse<=0; clear_pulse<=0;
            if(clearing) begin
                if(clear_addr==4095) begin clearing<=0; clear_addr<=0; end
                else clear_addr<=clear_addr+1'b1;
            end
            if(rsp_valid && rsp_ready) rsp_valid<=0;
            if(accept) begin
                rsp_valid<=1; rsp_err<=0; rsp_rdata<=0;
                if(cmd_addr[1:0]!=0) begin rsp_err<=1; protocol_error<=1; end
                else if(cmd_read) begin
                    case(cmd_addr)
                        20'h00000: rsp_rdata<={28'b0,clearing,protocol_error||compute_error,done,busy||start_pulse};
                        20'h00004: rsp_rdata<=compute_cycles;
                        20'h00008: rsp_rdata<=mac_count;
                        default: begin rsp_err<=1; protocol_error<=1; end
                    endcase
                end else if(cmd_addr==0 && cmd_wmask==4'hf) begin
                    if(cmd_wdata==2 && !busy && !start_pulse && !clearing) begin
                        clearing<=1; clear_addr<=0; clear_pulse<=1; protocol_error<=0;
                        x_words<=0; w_words<=0; b_words<=0; must_clear<=0;
                    end else if(cmd_wdata==1 && !busy && !start_pulse && !clearing && !must_clear &&
                        x_words==3168 && w_words==8192 && b_words==512 && !protocol_error && !compute_error) begin
                        start_pulse<=1; must_clear<=1;
                    end else begin rsp_err<=1; protocol_error<=1; end
                end else if(x_write) x_words<=x_words+1'b1;
                else if(w_write) w_words<=w_words+1'b1;
                else if(b_write) b_words<=b_words+1'b1;
                else begin rsp_err<=1; protocol_error<=1; end
            end
        end
    end
endmodule
