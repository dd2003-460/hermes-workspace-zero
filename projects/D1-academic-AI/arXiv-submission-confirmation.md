# arXiv 提交确认 — 作者审阅清单

**生成日期**：2026-05-11（iteration 42）

---

## 论文 1: D1-grav-waves

### 基本信息
- **标题**：An Extended Functorial QFT Framework for Gravitational-Wave Source Discrimination in Pulsar Timing Arrays
- **作者**：Cheng Lu (Independent Researcher)
- **分类**：gr-qc（主）, hep-th（辅）
- **许可证**：CC BY 4.0
- **tarball**：`D1-grav-waves/D1-grav-waves-arxiv.tar.gz` (128K)
- **本地编译**：✅ 10页, 291KB PDF（pdflatex 通过）
- **参考文献**：24篇，全部内联引用验证通过

### 内容摘要
本文使用扩展代数量子场论框架，将 PTA 中 Hellings-Downs 相关性函数重新表述为局部代数间的自然变换。主要结果：
1. HD 相关性在函子论框架下的几何解释
2. SMBHB 与宇宙学背景源判别预言
3. 各向同性缩放定理

### 提交前确认
- [ ] 作者信息正确
- [ ] 摘要内容正确
- [ ] gr-qc 分类正确（可考虑添加 hep-th）
- [ ] 参考文献无遗漏
- [ ] 图 1（HD 曲线）渲染正确

---

## 论文 2: D40 (AI-Market Precision Tradeoff)

### 基本信息
- **标题**：The Precision-Accessibility Tradeoff in AI Markets
- **作者**：Cheng Lu (Independent Researcher)
- **分类**：cs.AI（主）, cs.CY, stat.AP（辅）
- **许可证**：CC BY 4.0
- **tarball**：`D1-academic-AI/D40-paper-arxiv.tar.gz` (12K)
- **本地编译**：⚠️ CJK 字符导致本地 pdflatex/xelatex 编译失败（arXiv 服务器应可处理）
- **参考文献**：15篇，全部内联引用验证通过（纯文本格式）

### 内容摘要
建立 AI 精度-可访问性权衡理论，证明通用模型的精度退化是信息选择而非信息损失。包含四个定理和四项数值实验验证。

### 提交前确认
- [ ] 作者信息正确
- [ ] 中文内容渲染预期正常
- [ ] cs.AI 分类正确
- [ ] 参考文献无遗漏

---

## 提交流程

1. 访问 https://arxiv.org/submission
2. 选择分类（gr-qc / cs.AI）
3. 上传对应 tarball
4. 填写元数据（标题、摘要、作者、分类）
5. 提交

---

## 工具复用

- `arxiv_tarball.sh` — 自动创建 arXiv 提交包（含引用验证）
- `verify_citations.py` — 验证参考文献内联完整性
- `arxiv_submission_checklist.sh` — arXiv 提交检查清单
- `_extract_title.py` — 从 .tex 文件提取标题

所有工具位于 `/Users/a1-6/Desktop/workspace/scripts/`，各项目中已有副本。
