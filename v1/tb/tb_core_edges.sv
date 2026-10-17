`timescale 1ns/1ps
module tb_core_edges;
    reg clk=0; always #5 clk=~clk;
    reg rst_n=0,clear=0,start=0,rd_ready=1,rsp_valid=0,rsp_error=0,out_ready=0;
    reg signed [15:0] x_data=0;
    reg [63:0] w_data=0;
    reg [191:0] b_data=0;
    wire busy,done,error,rd_valid,rsp_ready,out_valid;
    wire [31:0] cycles,mac_count;
    wire [12:0] x_addr;
    wire [11:0] w_addr;
    wire [5:0] b_addr;
    wire [14:0] out_index;
    wire [191:0] out_data;
    reg signed [47:0] expected[0:3];
    reg [191:0] held;
    integer k,l;
    linear_engine dut(.*);
    task new_task;
        begin
            @(negedge clk); clear=1; rsp_valid=0; rsp_error=0;
            @(negedge clk); clear=0; start=1;
            @(negedge clk); start=0;
        end
    endtask
    task respond;
        begin
            while(!rd_valid) @(negedge clk);
            // Stall request, then response, exercising both independent channels.
            rd_ready=0; repeat(2) @(negedge clk); rd_ready=1;
            @(posedge clk); @(negedge clk);
            repeat(2) @(negedge clk);
            rsp_valid=1; @(posedge clk); @(negedge clk); rsp_valid=0;
        end
    endtask
    initial begin
        if($test$plusargs("WAVE")) begin $dumpfile("core_edges.vcd"); $dumpvars(0,tb_core_edges); end
        repeat(3) @(negedge clk); rst_n=1;
        if(busy||done||out_valid) $fatal(1,"Reset unexpectedly starts work");
        x_data=-16'sd32768;
        w_data={16'hffff,16'h0000,16'h8000,16'h7fff};
        b_data={48'h000000000003,48'hfffffffffffc,48'h000000000005,48'hfffffffffff9};
        expected[0]=-48'sd32768*48'sd32767*48'sd64-48'sd7;
        expected[1]=48'sd32768*48'sd32768*48'sd64+48'sd5;
        expected[2]=-48'sd4;
        expected[3]=48'sd32768*48'sd64+48'sd3;
        new_task();
        for(k=0;k<64;k=k+1) respond();
        if(!out_valid||out_index!=0||mac_count!=256) $fatal(1,"Dot length/count incorrect");
        for(l=0;l<4;l=l+1) if(out_data[l*48+:48]!==expected[l]) $fatal(1,"Signed boundary mismatch lane=%0d",l);
        held=out_data;
        repeat(5) begin @(negedge clk); if(!out_valid||out_data!==held) $fatal(1,"Output not held under stall"); end
        // Reset must abort an active task and suppress stale output.
        rst_n=0; @(negedge clk); rst_n=1; @(negedge clk);
        if(busy||done||error||out_valid||mac_count!=0) $fatal(1,"Reset abort failed");
        x_data=1; w_data={4{16'h0001}}; b_data={4{48'h7fffffffffff}};
        new_task(); respond();
        if(!error||busy||done||out_valid) $fatal(1,"Overflow was not detected");
        new_task(); rsp_error=1; respond();
        if(!error||busy||done) $fatal(1,"Memory response error was not detected");
        @(negedge clk); clear=1; @(negedge clk); clear=0;
        if(busy||done||error) $fatal(1,"Error clear failed");
        $display("CORE_EDGES_PASS signed_min_max_bias_zero_lane reset_abort overflow bus_error request_response_output_stalls");
        $finish;
    end
    initial begin #1000000; $fatal(1,"Edge test timeout"); end
endmodule
