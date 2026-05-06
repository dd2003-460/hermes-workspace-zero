# IC_K 论文 Author 信息填充 Manual Fallback

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**原因**: 自动化流程因飞书凭证缺失而阻塞，需用户手动提供 author 信息

---

## 任务目标
填充 `projects/写作/notes/ic_k_paper_draft.tex` 中的 `\\author` 块，确保包含：
- 作者姓名 (Name)
- 所属机构 (Affiliation)
- 邮箱 (Email)
- ORCID (可选但推荐)

## 需要的用户信息
请提供以下信息（或确认以下默认值）：

| 字段 | 当前值 | 说明 |
|------|--------|------|
| 姓名 | 成璐 | 从 USER.md 提取，请确认或修改 |
| 机构 | [待填写] | 例如：清华大学、北京大学等 |
| 邮箱 | [待填写] | 常用学术邮箱 |
| ORCID | [待填写] | 如无则留空或删除字段 |

## LaTeX 示例格式
\author{
  {\large Cheng Lu\\[0.5em]
  \texttt{chenglu@example.edu}\\[0.2em]
  \small Affiliation Name\\
  \small \href{https://orcid.org/XXXX-XXXX-XXXX-XXXX}{ORCID: XXXX-XXXX-XXXX-XXXX}
  }
}

## 操作步骤
1. 打开 `projects/写作/notes/ic_k_paper_draft.tex`
2. 找到 `\begin{author}` 或 `\author{...}` 部分（通常在 `\begin{document}` 前）
3. 替换为上述格式，填入你的实际信息
4. 保存文件并重新编译（`pdflatex` 或 `xelatex`）
5. 检查 PDF 中的 author 块显示是否正确

## 验证方法
- 编译后查看 PDF 首页的 author 信息
- 确保无编译错误（如 undefined control sequence）
- 如果编译失败，检查 LaTeX 语法（大括号匹配、特殊字符转义）

## 后续
完成后，请回复"IC_K author 已填充"，系统将自动验证编译并进入下一步（会议选择）。

---
*本文件由副脑循环自动生成，Red Line 0 保持*
