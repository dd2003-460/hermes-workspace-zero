# scenario-score.py 完整 12 维度对比（T8 补全）

> origin: ai · 2026-10-23 · goal-f34e1f87 r6
> 脚本：projects/AI-计算科学/D1-persona-align/scripts/scenario-score.py
> 维度：9 基础（avg_sent_len/first_person/question_rate/suoyi_ratio/conf_k/bushi_ershi_kchar/empty_k/numbered_k/cut_k）+ 3 新增（analogy_k/bold_k/hardnum_k）
> 修复：GT 路径从 /tmp/scen/ 改为 S1/S2/S3 子目录内

## 关键发现

1. **AX 公理 > A persona > B generic**（余弦近似度 0.814 > 0.589 > 0.453）：公理驱动的生成比 persona 描述更接近 GT
2. **A persona 硬数字密度偏高**（S1 hardnum_k=11.2 vs GT=0）：persona prompt 倾向生成更多具体数字
3. **B generic 类比密度偏高**（S3 analogy_k=11.5 vs GT=0）：generic 倾向用类比解释
4. **加粗密度全为 0**：三个场景的 GT 和生成文本都没用加粗，该维度无区分度
5. **drift 成璐度**：A=90 | AX=90 | B=83（A 和 AX 持平，B 略低）

## 原始输出


===== S1-消费决策-硬件 =====
指标                        GT   A persona       AX 公理   B generic
chars                    218         625         421         227
n_sents                    6          21          13           4
avg_sent_len            36.3        29.8        32.4        56.8
first_person           0.167       0.429       0.769        0.75
question_rate          0.167       0.333       0.154         0.5
所以_k                    13.8         1.6         4.8         4.4
但是_k                     0.0         0.0         0.0         0.0
suoyi_ratio              3.0         1.0         2.0         1.0
conf_words                 0           5           0           0
conf_k                   0.0         8.0         0.0         0.0
bushi_ershi_kchar        0.0         0.0         0.0         0.0
empty_talk                 0           1           0           0
numbered                   2           4           2           0
numbered_k               9.2         6.4         4.8         0.0
cut                        0           2           0           1
cut_k                    0.0         3.2         0.0         4.4
analogy_k                4.6         0.0         0.0         0.0
bold_k                   0.0         0.0         0.0         0.0
hardnum_k                0.0        11.2         0.0         8.8
余弦 vs GT                           0.486       0.748       0.323
drift 成璐度                             85          95          85  (GT参照 85)

===== S2-量化估算-元评估 =====
指标                        GT   A persona       AX 公理   B generic
chars                    748         673         585         240
n_sents                    9          17          18           7
avg_sent_len            83.1        39.6        32.5        34.3
first_person           0.667       0.529       0.667       0.571
question_rate          0.444       0.176       0.167       0.143
所以_k                     1.3         3.0         1.7         4.2
但是_k                     1.3         0.0         0.0         0.0
suoyi_ratio              0.5         2.0         1.0         1.0
conf_words                 0           7           1           1
conf_k                   0.0        10.4         1.7         4.2
bushi_ershi_kchar        0.0         0.0         0.0         0.0
empty_talk                 0           1           0           1
numbered                   6           6           3           0
numbered_k               8.0         8.9         5.1         0.0
cut                        0           0           0           0
cut_k                    0.0         0.0         0.0         0.0
analogy_k                0.0         0.0         0.0         0.0
bold_k                   0.0         0.0         0.0         0.0
hardnum_k                0.0         1.5         1.7         4.2
余弦 vs GT                            0.74       0.899        0.49
drift 成璐度                             85          95          80  (GT参照 60)

===== S3-ML训练机制-CoT =====
指标                        GT   A persona       AX 公理   B generic
chars                    204         482         281          87
n_sents                    3          15           7           3
avg_sent_len            68.0        32.1        40.1        29.0
first_person             0.0       0.533       0.143       0.333
question_rate          0.667       0.333       0.143         1.0
所以_k                     9.8         4.1         0.0         0.0
但是_k                     9.8         0.0         0.0         0.0
suoyi_ratio             0.67         2.0         0.0         0.0
conf_words                 1           6           2           0
conf_k                   4.9        12.4         7.1         0.0
bushi_ershi_kchar        0.0         0.0         0.0         0.0
empty_talk                 0           0           0           0
numbered                   0           3           0           0
numbered_k               0.0         6.2         0.0         0.0
cut                        0           1           0           0
cut_k                    0.0         2.1         0.0         0.0
analogy_k                0.0         2.1         0.0        11.5
bold_k                   0.0         0.0         0.0         0.0
hardnum_k                0.0         4.1         0.0         0.0
余弦 vs GT                           0.541       0.795       0.545
drift 成璐度                            100          80          85  (GT参照 70)

===== 汇总(3场景均值) =====
余弦近似度: A persona = 0.589 | AX 公理 = 0.814 | B generic = 0.453
  Δ: A-B = +0.136 | AX-B = +0.361 | A-AX = -0.225
drift 成璐度: A = 90 | AX = 90 | B = 83  (Δ: A-B = +7, AX-B = +7)
