`timescale 1ns/1ps
module tb_engine;
    reg clk=0; always #3.333 clk=~clk;
    reg rst_n=0, cmd_valid=0, cmd_read=0, rsp_ready=0;
    reg [19:0] cmd_addr=0;
    reg [31:0] cmd_wdata=0;
    reg [3:0] cmd_wmask=15;
    wire cmd_ready, rsp_valid, rsp_err;
    wire [31:0] rsp_rdata, compute_cycles, mac_count;
    wire out_valid, done_irq;
    wire [14:0] out_index;
    wire [191:0] out_data;
    integer cycle=0, written=0, layer_id, n, lane, timeout_count;
    reg checking=0;
    reg [31:0] status_word;
    reg [15:0] xs[0:6335], ws[0:16383];
    reg [47:0] bs[0:255], expected[0:25343];
    string vector_root, path;
    wire out_ready = cycle%17 != 0 && cycle%19 != 0;
    linear_mmio dut(.*);
    always @(posedge clk) begin
        cycle<=cycle+1;
        if(out_valid && out_ready) begin
            if(!checking) $fatal(1,"Unexpected output before legal START");
            if(out_index != written) $fatal(1,"Missing/duplicated output index %0d expected %0d",out_index,written);
            for(lane=0;lane<4;lane=lane+1)
                if(out_data[lane*48+:48] !== expected[out_index+lane])
                    $fatal(1,"Mismatch layer=%0d index=%0d got=%h expected=%h",layer_id,out_index+lane,out_data[lane*48+:48],expected[out_index+lane]);
            written<=written+4;
        end
    end
    task bus_op(input reg read_op,input reg [19:0] address,input reg [31:0] data,input reg expect_error);
        reg [31:0] held_data;
        reg held_error;
        begin
            @(negedge clk); cmd_valid=1; cmd_read=read_op; cmd_addr=address; cmd_wdata=data; rsp_ready=0;
            @(posedge clk); while(!cmd_ready) @(posedge clk);
            @(negedge clk); cmd_valid=0;
            while(!rsp_valid) @(negedge clk);
            held_data=rsp_rdata; held_error=rsp_err;
            repeat(2) begin
                @(negedge clk);
                if(!rsp_valid || rsp_rdata!==held_data || rsp_err!==held_error)
                    $fatal(1,"Response changed under backpressure");
            end
            status_word=rsp_rdata;
            if(rsp_err!==expect_error) $fatal(1,"Unexpected bus error addr=%h read=%b err=%b",address,read_op,rsp_err);
            rsp_ready=1;
            @(posedge clk); @(negedge clk); rsp_ready=0;
        end
    endtask
    initial begin
        if(!$value$plusargs("VECTORS=%s",vector_root)) $fatal(1,"VECTORS is required");
        if($test$plusargs("WAVE")) begin $dumpfile("engine.vcd"); $dumpvars(0,tb_engine.dut.core); end
        repeat(4) @(negedge clk); rst_n=1;
        repeat(4100) @(negedge clk);
        bus_op(0,0,1,1); // START without any operands must fail.
        bus_op(0,20'h10004,0,1); // Out of order / incomplete load must fail.
        bus_op(1,20'h00003,0,1); // Unaligned address must fail.
        bus_op(0,0,2,0);
        repeat(4100) @(negedge clk);
        for(layer_id=1;layer_id<=12;layer_id=layer_id+1) begin
            bus_op(0,0,2,0);
            repeat(4100) @(negedge clk);
            bus_op(1,0,0,0);
            if(status_word!==0) $fatal(1,"Clear did not reset state");
            path=$sformatf("%s/layer%02d/x.hex",vector_root,layer_id); $readmemh(path,xs);
            path=$sformatf("%s/layer%02d/w.hex",vector_root,layer_id); $readmemh(path,ws);
            path=$sformatf("%s/layer%02d/b.hex",vector_root,layer_id); $readmemh(path,bs);
            path=$sformatf("%s/layer%02d/y.hex",vector_root,layer_id); $readmemh(path,expected);
            for(n=0;n<3168;n=n+1) bus_op(0,20'h10000+n*4,{xs[n*2+1],xs[n*2]},0);
            for(n=0;n<8192;n=n+1) bus_op(0,20'h20000+n*4,{ws[n*2+1],ws[n*2]},0);
            for(n=0;n<256;n=n+1) begin
                bus_op(0,20'h30000+n*8,bs[n][31:0],0);
                bus_op(0,20'h30004+n*8,{{16{bs[n][47]}},bs[n][47:32]},0);
            end
            written=0; checking=1;
            bus_op(0,0,1,0);
            if(layer_id==12) bus_op(0,0,1,1); // Repeated START cannot corrupt active computation.
            timeout_count=0;
            while(!dut.done) begin
                @(negedge clk); timeout_count=timeout_count+1;
                if(timeout_count>1000000 || dut.compute_error) $fatal(1,"Compute failure or timeout");
            end
            @(negedge clk); checking=0;
            if(written!=25344 || mac_count!=1622016) $fatal(1,"Incomplete matrix/MAC count");
            bus_op(1,0,0,0);
            if(!status_word[1] || status_word[0]) $fatal(1,"Invalid completion state");
            if(status_word[2] != (layer_id==12)) $fatal(1,"Protocol error latch behavior incorrect");
            $display("LAYER_PASS layer=%0d outputs=%0d macs=%0d compute_cycles=%0d",layer_id,written,mac_count,compute_cycles);
        end
        bus_op(0,0,2,0); repeat(4100) @(negedge clk);
        bus_op(1,0,0,0); if(status_word!==0) $fatal(1,"Error recovery failed");
        $display("ENGINE_PASS layers=12 checked_outputs=304128 cold_clear=physical_zero_reload response_and_output_backpressure=PASS");
        $finish;
    end
    initial begin #1000000000; $fatal(1,"Global timeout"); end
endmodule
