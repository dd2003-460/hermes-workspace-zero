# v3 定稿 Checklist — P2 第一个数到达后执行

# origin: ai

> v3 升级条件（骨架 v2）：P2 拿到第一个数。本 checklist 让定稿动作从"想到做"变成"按单执行"。

## 前置（P2 实验完成）

- [ ] 信念变化率 ≥40 分（10 分制，后测比前测多 4 分）
- [ ] 读完率 ≥50%（判死线）
- [ ] 3 月留存率 ≥30%（判死线）
- [ ] 数据记录落盘（p2-experiment-plan.md 同目录，p2-results.md）

## 定稿动作

### 1. 全书一致性终检
- [ ] 15 章 drift-check 全跑一遍（cd projects/AI-计算科学/D1-persona-align && python3 scripts/drift-check.py <每章路径> = 100）
- [ ] 交叉引用终检（v3-readthrough-notes.md 的 A1-A4/B1-B2 修复项无回退）
- [ ] P1-P8 前提表与骨架一致（memory/book-skeleton.md vs 各章引用）

### 2. gate 数字回填
- [ ] ch14 gate（40 分设计值）→ 回填 P2 实测值
- [ ] ch15 三线 gate（书/课/社群）→ 书线 gate 回填 P2 实测值
- [ ] assetization-path.md gate 数字与 ch14/15 对齐

### 3. 版本升级
- [ ] memory/book-skeleton.md：v2 → v3（v3 条件行标记"已达成"）
- [ ] state.md #9 备注：v3 正式定稿完成
- [ ] loop-state.json：iteration+1, current_task 更新, blocker 清除
- [ ] tasks/decomposition.md：T5 标记完成，新增 T7（P2 执行）

### 4. git 收口
- [ ] git add projects/写作-社会系统/D2-efficient-propagation-book/
- [ ] git commit -m "D2 v3 定稿: P2 第一个数回填 + 全书终检"
- [ ] git -c http.version=HTTP/1.1 push origin codex/ralph-field-runtime

## 定稿后（可选）

- [ ] 资产化路径 v2（assetization-path.md 更新，课/社群线 gate 激活）
- [ ] 书发布（渠道待成璐拍板）
- [ ] 课/社群线启动评估（gate 过了才动）
