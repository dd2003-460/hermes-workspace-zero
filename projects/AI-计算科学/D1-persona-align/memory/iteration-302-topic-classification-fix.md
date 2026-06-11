# Iteration 302: Temporal Stability — Topic Classification Fix

## Action
- Fixed `cross_topic_stability()` in `temporal_stability_test.py`
- Root cause: all通用关键词 (贝叶斯, 感知, 认知, 推理, 压缩) appear in 50+ files because they exist in prompt preamble
- Solution: (1) use low-frequency discriminating keywords (2) score all topics and assign best-scoring (3) filter by 2 <= freq <= 15

## Results

### Before (iteration 301)
| Topic | Count |
|-------|-------|
| 信息理论 | 52 |

### After (iteration 302)
| Topic | Count | Avg Score | Min Score |
|-------|-------|-----------|-----------|
| 信息理论 | 22 | 0.7327 | 0.5586 |
| 数学 | 8 | 0.7325 | 0.5613 |
| 生物学 | 4 | 0.7278 | 0.5500 |
| 认知 | 6 | 0.7234 | 0.5383 |
| 社会 | 12 | 0.7222 | 0.5385 |

All 52 files classified. Cross-topic score range: 0.7222-0.7327 (range 0.0105).

## Analysis

1. The topic classification was broken because high-frequency keywords from the prompt preamble matched all files
2. Using discriminating low-frequency keywords gives clean separation
3. Cross-topic stability is excellent — all topics have nearly identical persona scores
4. "社会" and "认知" have slightly lower min scores, possibly because these topics have more diverse content

## Implications

- persona-v3 expresses consistently across different topics
- The topic classification fix is a general improvement applicable to any multi-topic analysis
- Cross-topic stability confirms persona-v3 is not over-optimized for a single topic domain

## Status
Topic classification fixed. Both tests now pass with meaningful results.
