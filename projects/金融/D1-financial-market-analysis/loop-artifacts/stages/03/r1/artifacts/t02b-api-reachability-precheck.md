# origin: ai

# T02b — 交易所 API 可达性预检 (03 阶段补做, 主机 2026-10-17)

> 触发: 副脑"只能改一件事"= Bybit API 04 环境可达性预检。T02 决策 B 默认建立在
> "Bybit API 在 04 环境可达"这一未实证前提上 (02 全程沙箱网络阻断, 无真实 API 响应)。
> 本预检用真实 curl 直接验证。

## 实测结果 (curl, 单一视点=本机)

| 端点 | 域名 | 结果 | rc | 备注 |
|------|------|------|-----|------|
| Bybit v5 /market/time | api.bybit.com | 3/3 全失败 | 35 | TLS 握手 reset by peer |
| Bybit v5 funding-rate | api.bybit.com | 空响应 | 35 | 同上 |
| Bybit v5 open-interest | api.bybit.com | 空响应 | 35 | 同上 |
| Binance spot /ping | api.binance.com | 失败 | 35 | TLS error |
| Binance fapi /ping | fapi.binance.com | 失败 | 28 | 10s timeout |
| **Binance 数据 CDN** | **data.binance.vision** | **200 OK** | 0 | 02 已证可达的批量归档域 |

curl rc 语义: 35=TLS 连接错误, 28=超时, 0=成功。

## 判定

- **规律**: 交易所 **live API 域** (api.bybit.com / api.binance.com / fapi.binance.com)
  全部不可达 (TLS reset 或 timeout); 而 **data.binance.vision (批量归档 CDN)** 可达 (200)。
- **解释** (两种可能, 置信标注):
  1. GFW 对加密交易所 API 域的选择性 TLS 拦截 (高置信, 与 rc=35 的 TLS 层 reset 行为一致,
     且 CDN 域放行符合其放行静态/归档域的经验)
  2. 本环境为沙箱/受限出口, 仅放行白名单域 (中置信)
  - 无论哪种, **对本环境的结论一致**: live 交易所 API 不可用。
- **样本量诚实声明**: Bybit 3 次, Binance spot 1 次, fapi 1 次, CDN 1 次。方向强一致
  (live API 全败 / 归档 CDN 全成), 但非大样本; 不排除瞬时波动。

## 对 T02 决策的影响 (关键)

T02 三选项默认= **B** (Bybit 免费 OI 至 symbol 上线日为主深度源 + Binance 30d 交叉验证)。
本预检证明 B 的**可达性前提在本环境不成立**:

- **B (Bybit OI 主源)**: 依赖 live `api.bybit.com` 拉 OI 历史 → 本环境**不可执行** (TLS 阻断)。
  → 从"默认"降级为"**条件路径**": 仅当 04 环境换成无阻断网络 (或经代理) 时启用。
- **A (仅 funding rate, Binance 批量归档)**: funding rate 主信号取自
  **data.binance.vision** 月度 `fundingRate` 批量文件 → 本环境**可达可执行** (200 已证)。
  → **升为本环境稳健默认**。
- **C (Coinglass $29/mo)**: OI 增强的付费分支, 走 web/app 通道 (非本环境 API), 预注册触发条件不变。

**结论**: 04 实现层在本环境应以 **A (funding-only, data.binance.vision)** 为默认回测路径;
OI 作为增强信号仅在"可连通 live API 的环境"或"经 C 付费源"时叠加。这不推翻 T02 的
A/B/C 结构, 只是把"默认"从 B 改为 A (本环境), B 转为条件路径。

## 下游动作

- T04 (f) 局限性节: 把"Bybit API 可达性未实证"更新为"**已实证: 本环境 live 交易所 API
  全部不可达 (TLS reset/timeout), 仅 data.binance.vision 归档 CDN 可达**"。
- 04 实现: 默认走 A; 任何需要 live API 的代码路径在本环境会失败 (rc=35), 须显式降级到 A。
- 新增开放问题: 04 是否需要代理/无阻断网络以启用 B/C? (路由给 04 决策, 不阻塞 03。)
