# D1-browser-auto 任务计划

## 🔴 当前 Focus

### 浏览器自动化 + 大模型对话

| 任务 | 状态 | 说明 |
|------|------|------|
| 项目初始化 | ✅ 已完成 | 创建 D1-browser-auto 项目，存放方案文档 |
| 方案研究 | ✅ 已完成 | 持久化登录方案（launchPersistentContext + storageState） |
| Playwright 环境安装 | 📋 待开始 | `pip install playwright && playwright install chromium` |
| 手动登录保存 Profile | 📋 待开始 | 运行 step1 脚本，手动登录 ChatGPT/Claude/Kimi |
| 自动化对话脚本 | 📋 待开始 | 实现 step2 AI 驱动对话循环 |
| 反自动化加固 | 📋 待开始 | 隐藏 webdriver 特征、模拟人类行为 |
| 本地 AI 对接 | 📋 待开始 | 对接本地模型（Ollama/MLX 等）作为决策层 |
| 多轮对话稳定性测试 | 📋 待开始 | 验证长期运行的可靠性 |

---

## 技术要点

- **持久化登录**：`launchPersistentContext`（推荐）或 `storageState`
- **反自动化检测**：隐藏 `navigator.webdriver`、随机化操作节奏
- **本地 AI 决策**：接收页面状态 → 输出下一步操作
- **会话管理**：定时保活、过期重新登录机制
