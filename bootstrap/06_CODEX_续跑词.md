# Codex 续跑词（仅在会话/上下文中断后使用）

继续当前项目，不升级版本：`CONTINUE_CURRENT_VERSION`。你接管的是此前已授权的 E203-KWT-1 本科芯片设计竞赛 v1 工程，绝对不能因为“继续”而建 v2，也不要从零重做。

1. 从 `bootstrap/PROJECT_INPUTS.yaml` 再次核实 PROJECT_ID、正式 repo、工作区、branch；通过 `git status/log` 获取最新真实提交。不要将聊天推断当作当前工程事实。
2. 顺序读取 `README.md`, `AGENTS.md`, `shared/PROJECT_STATE.md`, `shared/VERSION_STATE.md`, `shared/CONTEXT_CHECKPOINT.md`, `shared/CURRENT_PLAN.md`, `shared/DECISIONS.md`, `shared/ACCEPTANCE.md`, `shared/BLOCKERS.md`, `AI-problem/problem/`, `AI-problem/decision/`、最新仿真/数值/综合/STA/功耗/CI 证据与 `bootstrap/02_CODEX_总指令.md`。
3. 若状态与代码/日志矛盾，以用户批准的决策、代码、真实工具证据优先并指出冲突；恢复本次 v1 的**未完成 Stage**，不擅自改变 Scope。
4. 优先修复 P0：数值与 bit-exact → 全矩阵与 12 层 → E203 真闭环 → 150 MHz、2.25 mm²、功耗正式证据。普通 Bug 自主闭环；重大问题 2–3 轮无进展，形成问题证据并请求决策。
5. 所有修复复跑适当完整回归，逐阶段 checkpoint/Git。禁止 fake success、测试降标、软件代算、假 PPA。
6. 继续执行直至真正满足全部 Quality Gates 或达到明确阻塞，并诚实输出 `ACCEPT / ACCEPT WITH LIMITATIONS / REVISE`，附真实路径、命令、哈希和剩余限制。
