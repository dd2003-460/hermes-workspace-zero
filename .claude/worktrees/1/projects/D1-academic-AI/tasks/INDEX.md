# [3.3] tasks/ — 冷待办池

## INDEX.md policy（纯索引，零内容冗余）
本目录只存储冷待办 JSON 文件。INDEX.md 仅列出项目特定任务的引用列表，不重复全局单热任务板 `tasks/single_loop_state.json`。

## Current Tasks（[3.3.*] 编号体系）
- *(empty — awaiting cold task injection)*

## Index Reference Template（每添加一个新任务，按此格式更新）
- `<task_name>.json [3.3.<n>]` — 一行说明任务内容

## Migration Note
每个 D1-*项目的冷待办 JSON 文件，在进入热链路前需先导入 `tasks/single_loop_state.json`。
