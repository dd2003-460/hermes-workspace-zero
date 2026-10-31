# origin: ai · 机械脚本留档（无内容价值，仅防重复摸索）

2026-10-31 market-alpha 双阻塞解除时产生的一次性浏览器自动化脚本。归档原因：任务已完成，脚本本身没有复用价值；但其中踩出的坑值得留一句话备忘，避免下次重新摸索 20 轮。

## 关键教训（arena.ai/agent 会话注入指令的正确姿势）

1. **页面初始没有输入框**——只有 recaptcha 隐藏 textarea。必须先点"继续工作"按钮，tiptap 编辑器（`.tiptap.ProseMirror`）才渲染出来。
2. **React 受控组件不吃假输入**——setter + dispatchEvent('input') 填的值 UI 上看得见但发送不出去；必须走 CDP 真实键盘（mouse.click 聚焦 → keyboard.type → Enter）。
3. **长文本多次发送可能触发 reCAPTCHA 安全验证**——卡住需人工过一次。
4. 可用模板：`inject-t3-final.mjs`（改 sid + text 路径即可复用）。

文件清单：probe-*（DOM 探查过程）、inject*（输入尝试，前 9 个是失败迭代）、check-*（发送确认）、click-continue（唤出编辑器）、arena-b8-*（更早的 b8 批次检查/提交）。
