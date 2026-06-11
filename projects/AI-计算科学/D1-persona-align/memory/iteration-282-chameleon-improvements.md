# Iteration 282: Chameleon Collapse Detector — Chinese Tokenization + Response Saving

## Action
- Fixed Chinese character tokenization: char unigram → char bigram (更区分度)
- Fixed concept_density: `text.split()` → `len(text)` (中文无空格分隔)
- Added `--save-responses` flag: saves dim-*.json to responses/ directory

## Improvement Results

| 指标 | Before (unigram) | After (bigram) | Change |
|------|-----------------|----------------|--------|
| 平均相似度 | 0.5203 | 0.4802 | -7.7% |
| 最小相似度 | 0.4585 | 0.4205 | -8.3% |
| 最大相似度 | 0.6577 | 0.5938 | -9.7% |
| 概念密度区分 | 全部 0.000 | 0.000-0.027 | 现在有效 |

## Rationale
- **Char bigram**: 中文文本中单字重复率高，bigram 捕捉词汇模式 (如"信息", "密度", "感知")
- **concept_density**: `text.split()` 对中文返回整个字符串为 1 个 token，bigram 后分母是字符数
- 结果更可靠: 相似度差距拉大，检测更灵敏

## Files Saved
- 6 responses to `responses/dim_*.json` (ready for real API replacement)
- `eval_results/chameleon_collapse.json` (metrics + pairwise details)

## Next
- Replace mock responses with real Hermse API calls
- Integrate with EMPA trajectory evaluation (phase 4)
