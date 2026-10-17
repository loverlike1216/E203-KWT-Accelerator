// Functional/synthesis inference model, NOT an official area or power model.
// One synchronous read/write port; read-first when writing.
module sram16_reference #(
    parameter integer AW = 12
)(
    input wire clk, input wire en, input wire we,
    input wire [AW-1:0] addr, input wire [15:0] wdata,
    output reg [15:0] rdata
);
    reg [15:0] mem [0:(1<<AW)-1];
    always @(posedge clk) if(en) begin
        if(we) mem[addr]<=wdata;
        rdata<=mem[addr];
    end
endmodule
