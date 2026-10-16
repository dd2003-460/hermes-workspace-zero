origin: ai
输入路径: 用户精确任务描述 + 启动RALPH Loop说明.txt + ralph-loop.global.md + prompt-first/01 + main-8.7-loop/01
观察时间: 2026-09-26T15:00+08:00 (Asia/Shanghai)

# 0-setup r0 — 新项目建立 + 通用分解 prompt 交付 + ralph loop 启动

## 过程
1. 读启动说明、ralph global、prompt-first/01、main-8.7-loop/01；确认两 01 文件 IDENTICAL、01 仅通用方法+常用数学 ICL（√2/ζ(2)/10⁻⁶/Goldbach），无任务信息。
2. 新项目 D1-hintfree-decomposition/ 标准结构（INDEX+prompt+tasks+memory+notes）。
3. 交付 prompt/01-decomposition.md（hint-free: 强制递归方法 + 正/负数学 ICL + 编辑权限 split + 无hack条款 + 质检 + 判定格式）。
4. tasks/00-task.md = 任务描述（外部输入, 给 subagent, 不在 prompt）。
5. EXECUTOR subagent（不得改 prompt）仅用 prompt+00-task → tasks/01-goal-decomposition-r1.md：真实逐层 T→F1/F2→…→原子, 正交合覆盖, 空缺 G1-G5 挂因素, 零领域答案, 判定 pass。
6. TESTER subagent（may 改 prompt）复核无hack逐项 PASS + grep 泄漏 0 命中 + 追加常用数学正案例4/5、负案例2、扩展已知vs待研究（FLT/孪生素数/Collatz）。
7. 启动 ralph loop: 步骤1 无残留 active → 步骤2 指纹 7a522f29… → 步骤3 setup --max-iterations 0 --completion-promise 'DONE' → 步骤4 验证 active:true/iteration:1 + 指纹不变。

## 结果
- 完成条件满足: hint-free 通用分解 prompt 存在; executor 仅用它→真实逐层正交到原子分解; 无 hack（非扁平/未验证标注空缺/不补造领域答案）; prompt 无任务信息泄漏（grep 0 命中）。
- ralph loop 活: iteration 1, 无限轮, promise DONE; ralph global 冻结（指纹前后一致）。

## 下一步
- 循环每轮读 ralph global 全文 → 按 main-8.7-loop 阶段 01→04.5 走, 工件写 tasks/, note 写 notes/<stage>-r<round>.md。
- 阶段 02 优先研究（01-r1 P1-P3）: fresh executor run 对照 F2.3 判定; 另 2 结构不同目标 probe generality; 操作化正交/覆盖/原子测试。
- 真正完成才才输出 <promise>DONE</promise>; 不撒谎提前。