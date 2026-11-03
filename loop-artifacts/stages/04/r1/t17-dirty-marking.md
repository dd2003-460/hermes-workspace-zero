# T17 脏数据口径标注（N2 产出）

排除项（excluded-dirty）：
- conv0：检索全空，0/152 正确——stale checkpoint 导致 retrieval 无召回
- conv1：ingestion 残缺（~10 条记录缺失），21/81——Perplexity follow-up 确认 610−152−81−26=351 账目闭合
- conv4：生成全空/超时，0/26

健康子集定义：conv2 + conv3 共 351 题。
口径透明原则：所有对外数字必须同时给官方口径与健康子集口径，单报其一视为不完整。
