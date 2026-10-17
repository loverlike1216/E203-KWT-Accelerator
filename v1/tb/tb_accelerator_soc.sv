`timescale 1ns/1ps
`include "e203_defines.v"
module tb_accelerator_soc;
    reg clk=0; always #3.333 clk=~clk;
    reg rst_n=0;
    wire [31:0] completion_code,shared_reads,shared_writes,accelerator_writes,result_words;
    reference_soc dut(.*);
    reg [7:0] firmware[0:65535];
    reg [15:0] xs[0:6335],ws[0:16383];
    reg [47:0] bs[0:255],expected[0:25343];
    string firmware_path,vector_dir,path;
    integer n,cycle=0,first_load=-1,last_write=-1,issued=0;
    reg [31:0] expected_checksum;
    always @(posedge clk) begin
        if(rst_n) begin
            cycle<=cycle+1;
            if(dut.cpu.u_e203_cpu.u_e203_core.u_e203_exu.i_valid && dut.cpu.u_e203_cpu.u_e203_core.u_e203_exu.i_ready) issued<=issued+1;
            if(first_load<0 && dut.accept && dut.shared_selected && dut.cmd_read) first_load<=cycle;
            if(dut.out_valid) last_write<=cycle;
            if(cycle%250000==0) begin
                $display("SOC_PROGRESS cycles=%0d pc=%h inputs=%0d weights=%0d bias=%0d busy=%b result_words=%0d",cycle,
                    dut.cpu.inspect_pc,dut.engine.x_words,dut.engine.w_words,dut.engine.b_words,dut.engine.busy,result_words);
                $fflush();
            end
            if(cycle>5000000) $fatal(1,"SoC timeout pc=%h",dut.cpu.inspect_pc);
        end
    end
    initial begin
        if(!$value$plusargs("FIRMWARE=%s",firmware_path)||!$value$plusargs("TASK=%s",vector_dir)) $fatal(1,"Firmware and task required");
        for(n=0;n<65536;n=n+1) firmware[n]=0;
        for(n=0;n<131072;n=n+1) dut.shared_mem[n]=0;
        $readmemh(firmware_path,firmware);
        path={vector_dir,"/x.hex"}; $readmemh(path,xs);
        path={vector_dir,"/w.hex"}; $readmemh(path,ws);
        path={vector_dir,"/b.hex"}; $readmemh(path,bs);
        path={vector_dir,"/y.hex"}; $readmemh(path,expected);
        for(n=0;n<3168;n=n+1) dut.shared_mem[n]={xs[n*2+1],xs[n*2]};
        for(n=0;n<8192;n=n+1) dut.shared_mem[4096+n]={ws[n*2+1],ws[n*2]};
        for(n=0;n<256;n=n+1) begin
            dut.shared_mem[12288+n*2]=bs[n][31:0];
            dut.shared_mem[12289+n*2]={{16{bs[n][47]}},bs[n][47:32]};
        end
        for(n=0;n<8192;n=n+1)
            dut.cpu.u_e203_srams.u_e203_itcm_ram.u_e203_itcm_gnrl_ram.u_sirv_sim_ram.mem_r[n]=
                {firmware[n*8+7],firmware[n*8+6],firmware[n*8+5],firmware[n*8+4],firmware[n*8+3],firmware[n*8+2],firmware[n*8+1],firmware[n*8]};
        repeat(10) @(negedge clk); rst_n=1;
        wait(completion_code!=0); @(negedge clk);
        if(completion_code!=32'h600d0001) $fatal(1,"Firmware failure code=%h pc=%h",completion_code,dut.cpu.inspect_pc);
        expected_checksum=0;
        for(n=0;n<25344;n=n+1) begin
            if(dut.shared_mem[16384+n*2]!==expected[n][31:0] || dut.shared_mem[16385+n*2]!=={{16{expected[n][47]}},expected[n][47:32]})
                $fatal(1,"Actual SoC output mismatch index=%0d",n);
            expected_checksum=expected_checksum^expected[n][31:0]^{{16{expected[n][47]}},expected[n][47:32]};
        end
        if(dut.shared_mem[81920]!==expected_checksum) $fatal(1,"CPU readback checksum mismatch");
        if(shared_reads<62560||accelerator_writes<11874||result_words!=50688||issued==0||dut.mac_count!=1622016)
            $fatal(1,"Missing actual CPU/memory/hardware activity");
        $display("SOC_PASS outputs=25344 issued=%0d shared_reads=%0d accelerator_writes=%0d result_words=%0d macs=%0d task_cycles=%0d total_cycles=%0d checksum=%h",issued,shared_reads,accelerator_writes,result_words,dut.mac_count,last_write-first_load+1,cycle,expected_checksum);
        $finish;
    end
endmodule
