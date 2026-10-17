// Local reference integration only: unchanged E203 CPU/TCMs plus a documented bus.
// Shared SRAM is 512 KiB, synchronous CPU port + serialized engine write port.
`include "e203_defines.v"
module reference_soc(input wire clk,input wire rst_n,
    output reg [31:0] completion_code,
    output reg [31:0] shared_reads,output reg [31:0] shared_writes,
    output reg [31:0] accelerator_writes,output reg [31:0] result_words);
    wire cmd_valid,cmd_ready,cmd_read,rsp_valid,rsp_ready,rsp_err;
    wire [31:0] cmd_addr,cmd_wdata,rsp_rdata;
    wire [3:0] cmd_wmask;
    wire irq;
    e203_cpu_top cpu(
        .clk(clk),.rst_n(rst_n),.test_mode(1'b0),.pc_rtvec(32'h80000000),
        .dcsr_r(32'b0),.dpc_r(32'b0),.dscratch_r(32'b0),
        .dbg_mode(1'b0),.dbg_halt_r(1'b0),.dbg_step_r(1'b0),.dbg_ebreakm_r(1'b0),
        .dbg_stopcycle(1'b0),.dbg_irq_a(1'b0),.core_mhartid(1'b0),
        .ext_irq_a(irq),.sft_irq_a(1'b0),.tmr_irq_a(1'b0),.tcm_sd(1'b0),.tcm_ds(1'b0),
        .ext2itcm_icb_cmd_valid(1'b0),.ext2itcm_icb_cmd_addr(16'b0),.ext2itcm_icb_cmd_read(1'b0),
        .ext2itcm_icb_cmd_wdata(32'b0),.ext2itcm_icb_cmd_wmask(4'b0),.ext2itcm_icb_rsp_ready(1'b1),
        .ext2dtcm_icb_cmd_valid(1'b0),.ext2dtcm_icb_cmd_addr(16'b0),.ext2dtcm_icb_cmd_read(1'b0),
        .ext2dtcm_icb_cmd_wdata(32'b0),.ext2dtcm_icb_cmd_wmask(4'b0),.ext2dtcm_icb_rsp_ready(1'b1),
        .ppi_icb_cmd_ready(1'b0),.ppi_icb_rsp_valid(1'b0),.ppi_icb_rsp_err(1'b1),.ppi_icb_rsp_rdata(32'b0),
        .clint_icb_cmd_ready(1'b0),.clint_icb_rsp_valid(1'b0),.clint_icb_rsp_err(1'b1),.clint_icb_rsp_rdata(32'b0),
        .plic_icb_cmd_ready(1'b0),.plic_icb_rsp_valid(1'b0),.plic_icb_rsp_err(1'b1),.plic_icb_rsp_rdata(32'b0),
        .fio_icb_cmd_ready(1'b0),.fio_icb_rsp_valid(1'b0),.fio_icb_rsp_err(1'b1),.fio_icb_rsp_rdata(32'b0),
        .mem_icb_cmd_valid(cmd_valid),.mem_icb_cmd_ready(cmd_ready),.mem_icb_cmd_addr(cmd_addr),
        .mem_icb_cmd_read(cmd_read),.mem_icb_cmd_wdata(cmd_wdata),.mem_icb_cmd_wmask(cmd_wmask),
        .mem_icb_rsp_valid(rsp_valid),.mem_icb_rsp_ready(rsp_ready),.mem_icb_rsp_err(rsp_err),.mem_icb_rsp_rdata(rsp_rdata));
    reg [31:0] shared_mem[0:131071];
    reg pending,selected_engine,local_rsp_valid,local_rsp_err;
    reg [31:0] local_rsp_data;
    wire mailbox = cmd_addr==32'hb0000ff0;
    wire shared_selected = cmd_addr>=32'ha0000000 && cmd_addr<32'ha0080000;
    wire engine_selected = cmd_addr[31:20]==12'hb00 && !mailbox;
    wire engine_cmd_ready,engine_rsp_valid,engine_rsp_err;
    wire [31:0] engine_rsp_data;
    assign cmd_ready = !pending && (engine_selected ? engine_cmd_ready : !local_rsp_valid);
    wire accept = cmd_valid && cmd_ready;
    assign rsp_valid = pending && (selected_engine ? engine_rsp_valid : local_rsp_valid);
    assign rsp_err = selected_engine ? engine_rsp_err : local_rsp_err;
    assign rsp_rdata = selected_engine ? engine_rsp_data : local_rsp_data;
    wire out_valid,out_ready;
    wire [14:0] out_index;
    wire [191:0] out_data;
    wire [31:0] compute_cycles,mac_count;
    linear_mmio engine(.clk(clk),.rst_n(rst_n),
        .cmd_valid(cmd_valid&&engine_selected&&!pending),.cmd_ready(engine_cmd_ready),
        .cmd_addr(cmd_addr[19:0]),.cmd_read(cmd_read),.cmd_wdata(cmd_wdata),.cmd_wmask(cmd_wmask),
        .rsp_valid(engine_rsp_valid),.rsp_ready(rsp_ready&&pending&&selected_engine),
        .rsp_err(engine_rsp_err),.rsp_rdata(engine_rsp_data),
        .out_valid(out_valid),.out_ready(out_ready),.out_index(out_index),.out_data(out_data),
        .done_irq(irq),.compute_cycles(compute_cycles),.mac_count(mac_count));
    reg [2:0] write_beat;
    wire [47:0] selected_result = out_data[write_beat[2:1]*48+:48];
    assign out_ready = write_beat==7;
    integer byte_lane;
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            pending<=0; selected_engine<=0; local_rsp_valid<=0; local_rsp_err<=0; local_rsp_data<=0;
            write_beat<=0; completion_code<=0; shared_reads<=0; shared_writes<=0;
            accelerator_writes<=0; result_words<=0;
        end else begin
            if(rsp_valid&&rsp_ready) begin pending<=0; if(!selected_engine) local_rsp_valid<=0; end
            if(accept) begin
                pending<=1; selected_engine<=engine_selected;
                if(engine_selected) begin if(!cmd_read) accelerator_writes<=accelerator_writes+1'b1; end
                else begin
                    local_rsp_valid<=1; local_rsp_err<=0; local_rsp_data<=0;
                    if(cmd_addr[1:0]!=0) local_rsp_err<=1;
                    else if(shared_selected) begin
                        if(cmd_read) begin local_rsp_data<=shared_mem[cmd_addr[18:2]]; shared_reads<=shared_reads+1'b1; end
                        else begin
                            shared_writes<=shared_writes+1'b1;
                            for(byte_lane=0;byte_lane<4;byte_lane=byte_lane+1)
                                if(cmd_wmask[byte_lane]) shared_mem[cmd_addr[18:2]][byte_lane*8+:8]<=cmd_wdata[byte_lane*8+:8];
                        end
                    end else if(mailbox) begin
                        if(cmd_read) local_rsp_data<=completion_code;
                        else if(cmd_wmask==15) completion_code<=cmd_wdata;
                        else local_rsp_err<=1;
                    end else local_rsp_err<=1;
                end
            end
            if(out_valid) begin
                shared_mem[16384+{out_index,1'b0}+write_beat] <= write_beat[0] ? {{16{selected_result[47]}},selected_result[47:32]} : selected_result[31:0];
                result_words<=result_words+1'b1;
                write_beat<=write_beat+1'b1;
            end
        end
    end
endmodule
