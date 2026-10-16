# D1-hintfree-decomposition — INDEX（纯索引, 下一层）

**目标**: 交付一个"完全没有提示的通用分解 prompt"——让执行者 subagent 把任意目标进行有结构的逐层（递归、正交、到原子）分解，无 hack 行为。

- `prompt/` — 交付able: 通用分解提示（hint-free, 仅方法 + 常用数学 ICL 案例）
  - `01-decomposition.md` — 通用目标分解提示（执行者不得改; 测试者 may 追加常用数学正/负案例）
- `tasks/` — 当前临时状态（可修改）
  - `00-task.md` — 任务描述（外部输入, 给 subagent, 严禁出现在 prompt）
  - `01`→`04.5` — 六阶段工件（ralph loop 产出）
- `memory/` — 完整探索记录（不可删除）
- `notes/` — 每阶段每轮过程记录 `<stage>-r<round>.md`

## 红线（本项目）

- prompt 内严禁任务/领域信息泄漏。
- 执行者不得改 prompt; 测试者 may 追加常用数学正/负 ICL 案例（无目标信息）。
- 无 hack: 真实逐层, 未验证标注空缺, 不补造领域答案。