# Step 03: 元宝变压器板块会话数据抓取

## 目标
用 ego-login 已登录的 ego-browser 完整抓取元宝会话《A股变压器板块估值与全球对比分析》（含 1.5 万字深度研究报告附件），落盘到变压器子模块 data/ 目录。

## 涉及文件
- `market-alpha/transformer-sector-valuation/data/yuanbao-session-raw.md`（完整会话全文）
- `market-alpha/transformer-sector-valuation/data/report-attachment.md`（深度研究报告附件内容）
- `market-alpha/transformer-sector-valuation/data/README.md`（数据来源说明）

## 做法
1. ego-browser 打开 `https://yb.tencent.com/s/zHbNFn6SIb1H`（已验证可达，标题正确，登录态有效）
2. 抓取页面完整 innerText（会话多轮：初始问题→1.5万字报告→澄清需求讨论→正交分解讨论→贡献因子框架讨论）
3. 定位附件《A股变压器板块深度研究报告.md》：尝试点击下载；若为展开式文本则整段抓取
4. 长内容分段滚动抓取，拼接去重
5. 落盘 + 写 data/README.md（URL、抓取时间、字数统计、完整性）

## 验收标准
- [ ] `yuanbao-session-raw.md` >15KB，含五个核心判断、正交分解讨论、贡献因子对数分解框架
- [ ] `report-attachment.md` 含报告主体（执行摘要/覆盖标的/对标组/估值数据），或标注"附件无法独立下载，正文已抓"
- [ ] 关键数字可提取：思源 -56.1%、金盘 AIDC 订单 55.65 亿、板块 PE 30.72/47.2% 分位（抽样验证）
