origin: ai
输入路径: tasks/04-spec-matrix-r2.md (N1) + tasks/04-boundary-notes-r2.md (N2)
观察时间: 2026-09-25T15:30+08:00 (Asia/Shanghai)

# 阶段 04 节点 N3 执行：合并证据包（join N1+N2）

## 合并内容
N1 已验证规格矩阵 + N2 边界清单 = 完整证据包（已验证数值 + 显边界）。

## 已验证数值（可安全）
- H200: 141GB HBM3e / 4.8TB/s (C1,C2)
- B200: 180GB/卡 SXM (C3), FP4 144/72 8卡DGX (C5), NVLink5 1.8TB/s (C6)
- MI300X: 192GB HBM3 / 5.3TB/s (r1,C9)
- MI350X: 288GB / 8TB/s FP4/MXFP (C13 一手MI350页)
- vLLM 支持 H100/H200/B200/MI300X, 0.30.0 (C9)
- 候选集合存在+获取路径: NVIDIA 6 + AMD 4 + Groq/Cerebras (C12,C13,C14)
- 分层方法论: 单GPU≠rack; 通用≠专用 (C15)

## 显边界（不能用于数值决策）
- B1 MI325X 精确、B2 专用栈通用性、B3 库存、B5 价格时点、B6 TDP、B7 近7天吞吐、B8 适用边界。

## 反向追溯
- 每已验证数值 → N1 → 02.5 一手来源 ID ✓。
- 每边界 → N2 → 02.5 开放项 ✓。

## 验收
- 数值无来源? 无（已验证项引用一手ID）✓。
- 合并完成 ✓。