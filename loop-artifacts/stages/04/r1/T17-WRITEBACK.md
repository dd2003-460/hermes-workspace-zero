# T17 收口回写（N4 产出）

状态：done（2026-11-04）
关键数字：full01 官方 top_10 overall 45.57% / temporal 38.41%；健康子集(conv2+3, 351题) overall 73.22% / temporal 73.13% ≥ 50% 目标线。
结论：temporal 锚定修复方向有效（smoke01 0% → 73.13%）；官方口径缺口归因于 conv0/1/4 脏数据（178 题）。
诚实边界（引 02.5 validation_records）：① 缺同题前后对照，因果声明不成立 ② 排除标准应预定义而非事后 ③ 诊断(retrieval 全空等)需 log + 干净重跑验证 ④ judge 同模型相关误差。
后续动作（新立项范畴，待成璐决策）：全文塞入对照组(~20h)、异源 judge 抽查、predefined dirty-run criteria 下的干净重跑。
decomp 仓条目同步：decomposition.md 不在本工作区 checkout，T17 条目更新列为 decomp 侧后续动作。
