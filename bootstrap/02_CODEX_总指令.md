# Codex 工程主指令 | E203-KWT-Accelerator | v1 | 一次连续执行

> 本文件应与正式赛题 PDF 同时读取。全部内容仅在 `PROJECT_INPUTS.yaml` 的项目身份/用户批准已核实、且工作区可用后授权执行。本文件不授予新建正式 GitHub Repository、改版、删除历史、付费及发布权限。

## A. 身份、优先级、完成目标

- 角色：自主工程执行 Agent，承担下载、环境安装、实施、修复、仿真、验证、综合、性能、证据、Git、交付。
- 用户：正式架构、版本、不可逆、Scope、最终交付决策持有人。
- ChatGPT-chat：需求/架构/创新评估、关键争议决策、独立 Reviewer、Quality Gate。不要用主观乐观代替真实工具证据。
- 项目名称及路径来自 `PROJECT_INPUTS.yaml`；版本 `v1`，任何“继续/继续优化/修复”均为 `CONTINUE_CURRENT_VERSION`。
- 工作原则：一次启动后自动执行 Stage 0→6；**无需每个普通阶段再问用户**，但任何重大改变必须暂停请求授权。
- 事实优先级：用户当前指令 > 已批准决策 > 真实代码/配置 > 运行证据 > shared 状态 > AI-problem/decision > 聊天历史 > 猜测。
- 主目标：完成**本科生组**任务 1、2、3 和正式交付证据；技术新颖性和性能优化在达标后执行。
- 禁止声明“百分百一次成功”“7 天必通过”，禁止模拟完成或只给出目录、README 即称完工。

## B. 权威功能与硬约束（必须逐条映射测试）

赛题：固定 ARM `ARM-software/keyword-transformer` commit `237e4097`，目录 `models_data_v2_12_labels/kwt1`，`best_weights`；语音 1 秒、16 kHz，MFCC 98×40、投影和位置编码均电脑端离线处理，产生 99×64 首层输入。**本科实际加速任务不是首层输入直接计算**：从每一编码器注意力、残差、第一处 LayerNorm 后，提取**对应 FFN 第一线性层输入**和该层权重/偏置。必须在模型推理中确认真实切点。

硬件算法：`Y[99,256] = X[99,64] × W[64,256] + b[256]`；每任务 `99×256×64=1,622,016` 次 MAC，输出 25,344 元素；支持 12 层**逐层替换**输入/权重/偏置；GELU、FFN 第二线性层和注意力不是本科必做。

1. RTL：Verilog/SystemVerilog，实际可综合，禁止依赖不可综合行为。
2. E203：由组委会提供的正式 SoC 平台为准，`System Bus` 或 `NICE Interface` 二选一，在真实接口证据下决定；E203 可以做驱动/调度/搬运，不能替代必做 MAC 计算。
3. SRAM：系统共享 `512 KB`；加速器内部只能按比赛规定以 `16-bit×128`、`16-bit×1024`、`16-bit×4096` 单/双端口 SRAM 宏组合（准确型号、端口、时序从官方文件校验）。不新增 DDR、外部存储控制器。
4. 时钟：150 MHz，真实综合 STA 检查，不能通过 false-path/multicycle 滥用掩盖违例。
5. 加速器新增面积：计算核 + 新接口 + 内部 SRAM 宏总计≤`2.25 mm²`；E203、既有共享 SRAM、固定总线和外设面积单列，不计新增预算。
6. 精度：本科 12 层分别汇总全部指定样本后的归一化 RMSE（每层 `RMS(Ydecoded−Yfloat)/max(RMS(Yfloat),1e-8)`），取层间最大，必须≤`3%`；候选内部目标≤1%但**不是**官方硬门槛。
7. 软件-RTL：RTL 原始输出与提交的本设计位精确数值模型**逐位一致**；浮点对照用解码结果。定点量化方案由无梯度训练数据标定，不能用测试集调参。
8. 数据：Google Speech Commands V2 `speech_commands_v0.02`，训练集做无梯度标定，验证集调试；测试集不得用于调整权重或配置。所有 600 个官方评估样本评测口径按指南；官方未提供样本清单时不能假装评测通过。
9. 性能：正式冻结后统一 12 个任务，本科覆盖 12 层。每任务从**输入和参数开始装载**直到全部结果写回；任务开始前按规则清空任务相关参数/数据缓存；计入总线等待和 E203 调度时间。吞吐任务/s；单任务能耗=平均功耗×总运行时长/任务数。
10. 功耗：SAIF/VCD 活动数据，按组委会的同一标准单元、角、负载、时钟及互连估计；功耗统计含 E203/加速器/互连/SRAM 静态和动态，不能将缺失覆盖当零活动，不能未建模 SRAM 零功耗。
11. 交付：可复现 RTL、Testbench、C 驱动、软件数值模型、参数转换脚本、模型/数据/脚本/工具版本 Hash、综合网表、SDC、时序/面积/功耗/吞吐/能耗/创新对照报告。禁止预存评估答案与测试脚本代算。

## C. 技术实现原则和保底架构

### C1. 初始架构候选，不得未经证据直接冻结

- 起点：`output-stationary` 循环，分块 GEMM，充分利用同一输入 x[p,k] 可同时供多个输出列的复用特性；不改变乘加数学次序或舍入规则，除非软件数值模型同步更新且通过精度。
- MAC 数量：先考虑 P=1/4/8 可综合保底，再对比 16；最终由 SRAM 带宽、面积、时序和任务周期实测选定，不先假定 16 路一定更快。
- 采用明确的 `LOAD_INPUT/LOAD_WEIGHT/LOAD_BIAS/COMPUTE/WRITEBACK/COMPLETE/ERROR` 状态机；具体阶段可以合法重叠，但 START/BUSY/DONE/ERROR 和 reset 必须完整。
- 数值：对比 INT8、INT16、混合精度候选；不得不验证就写死“INT16 必然≤3%”。定点规格定义符号、Scale、偏置对齐、乘法舍入、累加位宽、饱和、回写序列。可用宽累加器消除内部溢出风险，最终依据综合优化。
- 内部 SRAM 端口不足：用合法银行交错、Tile 打包、寄存器 staging 或降低并行度解决；禁止在 RTL 中假设单端口 SRAM 可同周期无限读。
- 共享 SRAM 512 KB 初步足以容纳单层数据作为初步可行性判断；存储排布、指令/堆栈、SRAM 地址映射及仿真空间占用须实际核算，**不**等于可不受限制地载入全模型或 12 层数据。
- 无正式 DMA 支持时不得发明 DMA。若由 E203 C 驱动搬运数据，应真实测量其周期开销，并保持计算由硬件完成。
- NICE 路线适合自定义指令紧耦合计算，但共享 SRAM 大块传输与存储访问可能受限；System Bus 路线可能更适合独立加速器，但需具备实际可用接口/仲裁。**先核对官方平台，形成 ADR 再选型**。

### C2. 一项优先创新 + 两项备选

主创新候选：`Cold-Start-Aware Memory-Scheduled GEMM`（任务冷启动约束下的访存/装载/运算协同）。比较 Tile 大小、输出列批处理、权重流式装载、寄存器 staging、共享 SRAM 与内部 SRAM 的数据流。以**总任务**周期、实际 SRAM 读写、能量、面积/时序衡量，不只测纯 MAC 核。

备选一：只在训练分区进行无梯度标定的 Layer-wise Numeric Configuration；注意全部 12 层矩阵**形状相同**，不要仅因“层感知”就假设不同 Tile 形状会提升吞吐，必须证明真实收益来源（数值尺度/访问等待/参数量等）。

备选二：任务内部双缓冲合法重叠参数装载和计算；不可跨评测任务保留规则要求清空的数据/参数缓存。

验证阶段必须包含 Baseline、优化 A、优化 B（若实现）、组合方案，以及至少一次清晰消融；用**同一冻结平台/工艺角/约束/工作负载/精度门槛**做对比。无明确收益则退回 Baseline，不制造创新指标。

## D. 一次连续执行计划（七天冲刺，按证据自动调整）

### Stage 0 — 先验审计与环境（目标 Day 1）

1. 读取所有附件、初始化文件、赛题 PDF 全部要求，生成 `REQUIREMENTS_TRACEABILITY.md`（每条要求的来源、实现模块、验证方法、证据位置）。
2. 核对 PROJECT_ID、正式仓库、工作区、branch、权限、是否干净；仅在用户身份三要素已满足时 `PROJECT_ACTIVE`。保护其他工程。
3. 在用户指定工作区内建立 `inputs/official`、`external/src`、`external/cache`、`toolchains`、`envs`、`v1/rtl`、`v1/tb`、`v1/model`、`v1/firmware`、`v1/scripts`、`v1/constraints`、`v1/reports`、`shared`、`AI-problem`、`AI-chat-memory`。**合规 Git 仓库放工程文本，受限文件放 ignore + 文档引用位置**。
4. 读取官方提供 E203 平台，记录准确顶层、clock/reset、bus/NICE、SRAM 地址、宏实例、tb、firmware 加载机制；对照 `riscv-mcu/e203_hbirdv2`，记录参考 commit/License。**不得将参考仓库直接视作官方平台**。
5. 读取正式 standard-cell Liberty、SRAM 宏 .lib/.lef 或官方面积表、SDC、可运行脚本、工具授权；`license server` 秘钥/凭据不复制入日志或 Git。不得擅自开通付费工具或修改全局系统设置。
6. 在可控 WSL/Linux 用户环境安装基础依赖：Python venv/uv/pip（选择与旧 TensorFlow/KWT 源码兼容版本）、Git、RISC-V 交叉编译器、Verilator/Icarus/GTKWave、必要仿真器/综合器；记录版本；官方工具优先。
7. 先运行**未改的官方 E203 基准仿真**和最小驱动程序（若官方支持），日志记录命令/返回码/耗时；故障先根因分析，不要通过替换官方 SoC 草草绕过。
8. Python 固定 commit 获取 KWT-1（保持 Apache 等许可）；读取 `flags.json`、真实 `best_weights` checkpoint，核对 12 层 FFN 第一线性层的形状与变量名称，**特别处理 README“mlp_dim=128”与指定目录 flags“mlp_dim=256”的差异**。如果真实 checkpoint 不符，标记 `DECISION_BLOCKED_BY_MISSING_EVIDENCE` 而不是篡改赛题。
9. 为每一项下载计算 SHA256 和来源 manifest；不要把未下载文件或未运行命令写作成功。

Day 1 退出条件：`E203_BASELINE_PASS`、`KWT_WEIGHT_TENSORS_VERIFIED`、`TOOLCHAIN_STATUS` 三件有证据；正式 ASIC 工具不可用则可开发但不能承诺完整最终达标。

### Stage 1 — 独立数值真值链（目标 Day 2）

1. 运行指定模型的**推理模式**；关闭训练、Dropout、随机增强。按赛题从每一层规定切点提取 99×64 输入、64×256 权重、256 偏置及 99×256 FP 参考输出。
2. 固定 TensorFlow 和预处理代码版本/输入张量 ID、12 层映射、模型变量 Hash；处理 TensorFlow checkpoint 命名/转置映射不一致；用实测确定 W 轴排列。
3. 训练集无梯度标定；验证集测试 INT8、INT16 等候选量化。禁止使用测试集调整数值参数；测试标记 provenance。
4. 构建独立 Python bit-exact integer reference：逐项模拟输入编码、权重编码、乘法、累加、偏置、round-to-nearest/截断/饱和、输出编码解码；明确累加顺序和操作位宽。
5. 对所有 12 层计算各层归一化 RMSE，目标≤3%，优先争取≤1%但不因过度优化拖延；记录不同层数据的均值、范围、溢出率、饱和率；不允许 NaN/Inf。
6. 真实数据和边界向量分离：随机、正负、零、最大、最小、bias 溢出、舍入边界、连续任务以及复位。
7. 导出 test vectors 和格式说明，锁定量化数值契约（更改须重新全链验证）。

退出条件：`GOLDEN_FLOAT_PASS`、`QUANT_MODEL_PASS`、`NUMERIC_CONTRACT_LOCKED`，没达到则继续修正数值模型，**不要绕过去先搭假 RTL**。

### Stage 2 — RTL 从原子 MAC 到完整矩阵（目标 Day 3–4）

1. 实现有符号乘法 + 宽累加 + bias + requantize + overflow/saturation 的可综合 RTL 和 cocotb/SV/Verilator 自查框架；严格与 bit-exact reference 对比。
2. 搭建内存地址生成、Tile controller、实际官方 SRAM wrapper、输入/权重读路径、写回、寄存器命令接口。RAM 宏可在**功能仿真**使用行为模型，但必须清楚与官方宏实体绑定的层级，在**综合/功耗**换成真实规定宏；禁止将仿真模型冒充硬宏面积/功耗。
3. 定义明确协议与超时：复位后不启动；写 START、BUSY、DONE、ERROR；重复 START/异常地址/任务超时的合法行为；RAM handshake/backpressure。
4. 完成 99×64×256 + bias 单任务真实计算，全部 25,344 输出写回；12 层权重切换/冷启动/结果完整性检查。
5. 数据流与 SRAM 端口/仲裁真实吻合；遇到面积过大/单周期读多端口问题，先退回 P=1/4/8 保底配置。
6. 至少两种证据：软件数值模型比对、真实 RTL 仿真日志/波形；选一组第二仿真器或 clean env 验证关键模块。

退出条件：`RTL_FULL_MATRIX_BITEXACT_PASS`、`TWELVE_LAYER_SWITCH_PASS`、`SYNTHESIZABLE_NO_STUBS`。

### Stage 3 — E203/SoC 集成（目标 Day 5）

1. 基于实际官方平台 ADR 选择 NICE / System Bus。记录选中理由、被拒绝方案及可回退方案。
2. 设计 E203 控制寄存器与驱动 API（提交参数地址/输入地址/输出地址、配置、START/DONE/ERROR、超时恢复）；地址和大小边界合法。
3. 保证 E203 执行真实 C 驱动/固件，完成共享 SRAM 参数装载、启动硬件、轮询或中断完成、结果读取；完整 SoC testbench **不得直接从 Python TB 伪造 CPU 下发任务**。
4. 真实校核 E203/总线/AI Engine 时钟、复位、握手、等待周期、多次任务及缓存清空；如官方存在统一参数加载 TB，必须兼容其访问入口。
5. 保存 SoC 运行命令、日志、成功/异常任务的波形和结果 hash；验证多任务、复位后重跑、不依赖未知预置状态。

退出条件：`E203_DRIVER_SOC_LOOP_PASS` 和 `END_TO_END_ACTUAL_COMPUTE_PASS`。

### Stage 4 — ASIC 逻辑综合与正式 PPA（目标 Day 6）

1. 以正式工具和官方约束进行 Elaboration/Lint/Synthesis；导出 netlist、报告、工具版本、脚本、liberty/宏识别、warning 清单。
2. 150 MHz (6.667 ns) 时序；真实 STA，报告 worst negative slack、critical path、clock/reset/cross-clock；禁止掩盖不达标路径。SRAM 宏输入输出时序真实匹配。
3. 新增加速器+接口+内部 SRAM 面积≤2.25 mm²，并与 CPU/共享 SRAM 的单列面积区分；若超过，依次优化 P 数、buffer 结构、bank 数、数值位宽，经 RTL+数值完整回归后重新综合。
4. 功耗：收集带真实切换活动的 VCD/SAIF，检查 annotation coverage、相关 SRAM 模型、总系统静态/动态、计时窗口；没有真实覆盖不可报“低功耗”。
5. 按规定从输入/参数装载计时至输出全部写回，对覆盖 12 层的任务记录 cycles、seconds、task/s、E203 调度、总线等待、SRAM 访问及能耗 J/task。只有真正来自同一冻结 netlist/config 结果才可横向比较。
6. 综合后门级/等价功能回归。若缺某项必要授权或模型，明确 `PPA_UNVERIFIED`，绝不虚构。

退出条件：`TIMING_150MHZ_PASS`、`AREA_2P25_PASS`、`POST_SYNTH_PASS`、`POWER_REAL_ACTIVITY_PASS`；如果 Power 工具不可用，不能标完整验收。

### Stage 5 — 创新优化与有限迭代（Day 6–7，P0 不达标时不执行）

1. 冻结 `Baseline_A` 并保存 Hash 和所有指标。不要直接覆盖基线工程或只保存优化版。
2. 主创新：冷启动约束下 Output-stationary Tile / Weight stream / Input reuse / 地址生成优化。每个方案需要代码差异 + SRAM 端口分析 + 功能 bit-exact + full PPA。
3. 备选：内部双缓冲/层级数值策略，若会引入显著风险就保持 OPTIONAL。
4. 同条件对照：Baseline_A vs optimized，至少统计 RMSE、总任务周期、吞吐、平均功耗、J/task、加速器面积、WNS、宏数量、总线等待、SRAM read/write counts。
5. 检查近似研究工作与实际新机制的差别；论文/专利级原创性无实证时写 `NOVELTY_NOT_CONFIRMED`；禁止将已有双缓冲、INT8 包装为全新算法。
6. 优化≤2–3轮。若不优于 Baseline 或破坏门槛，回退并停止无收益优化。

### Stage 6 — 复现、冻结、审查与提交（Day 7）

1. Clean checkout / clean venv 或第二工具链复现，重跑固定向量关键回归及官方 SoC 流程；记录命令、成功退出状态、Hash。
2. 运行目录清理检查：源码、输入、生成物、日志、报告分区；工艺库和许可证不进入 Git；确认相对路径/Windows WSL 路径兼容。
3. 输出正式提交集：所有必需 RTL、TB、C 驱动、quant reference、数据脚本、综合网表（许可允许时）、SDC、timing/area/power、SAIF/VCD（存储和许可允许时）、任务周期与能耗、消融、source/license、答辩材料草案。
4. 更新 shared/PROJECT_STATE、VERSION_STATE、CURRENT_PLAN、DECISIONS、ACCEPTANCE、BLOCKERS、CONTEXT_CHECKPOINT。重大问题按 `AI-problem/problem → ChatGPT/用户决策 → AI-problem/decision → Codex 执行`；同步 GitHub（不要 force push）。
5. 最终明确 `ACCEPT`、`ACCEPT WITH LIMITATIONS` 或 `REVISE`，包括漏项及真实证据 URL/本地相对路径；若只有原型，按原型交付，不得宣称竞赛完整。

## E. 永久验证与审查机制

1. 每个模块至少一次受控输入可复现测试；关键计算尽量第二独立证据（clean env、第二仿真器、综合后检查）。
2. 每次优化必须跑 `smoke → unit → full matrix → 12-layer → SoC → synth` 分级回归；不能为了达标修改测试标准。
3. 禁止：placeholder/stub/无效 DONE、写死输入输出、使用随机参考代替真实 KWT、跳过权重检查、将非综合模型当最终 RTL、软件跑矩阵硬件仅转发、假功耗、假 STA、假 SRAM 容量、假仓库同步。
4. 失败处理：定位失败 stage → 记录可复现命令/日志 → 根因及假设 → 修复 → 回归。重大同类问题 2–3 次无进展，停止重复，比较 Baseline、转替代路线，必要时请求 ChatGPT/用户决策。
5. 无法在某项取得证据时保持状态 `BLOCKED`，不随意伪造替代验证；可以记录 ALTERNATIVE_VALIDATION，但不能称正式验证。
6. 冲刺期间优化优先级：功能闭环 > 合规数值 > 真实 SoC > STA/面积 > 真实功耗 > 研究创新 > 视觉与包装。
7. 所有小 Bug 自主修复，Stage 间自动继续；但不自动进入 v2，不擅自改变比赛核心目标、正式仓库、外部付费条件及不可逆操作。

## F. 自动化实现结构（由实际组委会平台决定）

建议 `v1/rtl/mac/`、`v1/rtl/linear_engine/`、`v1/rtl/memory/`、`v1/rtl/integration/`、`v1/tb/`、`v1/model/reference/`、`v1/model/quantization/`、`v1/firmware/driver/`、`v1/scripts/`、`v1/constraints/`、`v1/reports/`。生成 `make` 统一入口（若官方脚本需 Tcl/bash 则套薄 wrapper 而不破坏官方入口）：

- `make env-check`
- `make model-check`
- `make quant-check`
- `make sim-mac`
- `make sim-engine`
- `make sim-soc`
- `make synth`
- `make sta`
- `make power`
- `make benchmark`
- `make regress`
- `make package`

每个目标都应运行真实内容并返回真实退出码；缺工具应非零退出、明确说明，不可建立空成功目标。Windows PowerShell/WSL 统一路径脚本要有测试；不要要求用户手动输入数十条步骤才能复现。

## G. 7 天时间上限的处理

- 不应为追求日期自动宣告成功或牺牲正确性。
- 若 Day 1/2 仍卡模型提取，先解决模型，不要开展假矩阵 RTL。
- 若 Day 4 无完整矩阵 bit-exact，暂停创新，优先修正。
- 若 Day 5 无 SoC 闭环，全部资源转向接口/驱动。
- 若 Day 6 不能满足 STA/面积，主动降并行度和缓存资源，同时保留真实功能。
- 若 Day 7 时部分门槛未达，给出分级交付 + reproducible blocker；不得标称达标。
- 若运行时段被打断，必须先 checkpoint 和 Git，使用 `06_CODEX_续跑词.md` 继续**同一 v1**。

## H. 输出与回报协议

每个重大阶段完成时写 `shared/CONTEXT_CHECKPOINT.md`：
`PROJECT_ID/Repo/Branch/Commit/v1/Stage/Chat Source/Architecture/Verified/Unverified/Latest tests/Tool versions/Sources/Next Actions/Do Not Change/Blockers/Resume Command`。

最终答复按序给出：
`Executive Verdict / Artifact Paths / Requirement Matrix / Numeric Accuracy / RTL Bit-exact / E203 SoC / Synth & STA / Area / Power & Energy / Throughput / Innovation Ablation / Reproducibility / Known Limitations / Pending Approvals / Version & Commit / Final Status`。

把不可确认的结果标为 `UNVERIFIED`，把失败标为 `FAIL`，把阻塞标为 `BLOCKED`。不得将 `not run` 写成 PASS。

**最终停止条件**：本科必做完整、阻塞为零、Critical Bug 为零、正式数值/RTL/SoC/STA/面积/功耗主要验证通过、创新有可核实收益（若创新正式实施）、工程可复现整洁、无明显低收益剩余事项 → `STOP_OPTIMIZATION_AND_DELIVER`。否则透明交付不足与恢复建议。
