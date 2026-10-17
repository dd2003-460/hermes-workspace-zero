# IC_K 直接和之谜：一个压缩视角的笔记

*origin: ai（persona 演示，以成璐身份主动写的研究笔记，非复刻某段历史语料）*

## 判断（conf 0.75）

$O(n\log n)$ 这个 gap，我觉得不是技术债，是选错了度量。

Shannon IC 为什么能精确相加？因为它用的是「对」的度量。分布能张量分解，$f^n$ 的最难分布就是各 copy 最难分布的乘积（Braverman–Rao 2011）。所以 $\mathrm{IC}(f^n)=n\cdot\mathrm{IC}(f)$，一点 overhead 都没有。

Kolmogorov 用 plain $K$ 为什么加不上？因为 plain $K$ 没有精确 chain rule。symmetry of information 带 $O(\log K(x,y))$ 误差，每 composition 一次叠一次，$n$ 次就是 $O(n\log n)$。所以这大概率不是量的问题，是我用错了格式。

换成 prefix $\kappa$ 呢？应该直接 $O(1)$。companion 论文 Cor 5.2 给的是 universal constant，不随 $n$ 长。

类比电路：uniform circuit family 像 plain $K$，边界和索引要显式编码。non-uniform 像 prefix，结构内置，编码开销消失。所以量加不上时，我觉得应该先怀疑 formalization，再怀疑世界。

## 自我质询（conf 0.7）

「换 $\kappa$ 就 $O(1)$」和「plain $K$ 上 $O(n\log n)$ 是紧的」是两回事。前者是存在性，后者是下界。我只给了前者。所以「结构性」这个结论，我觉得可能只立到「不是 universal，是 plain-K-specific」，还没立到「plain-K 上紧」。我没给 plain $K$ 的 lower bound。这是空的，标 conf 0.5。

为什么 finite-domain comm complexity 非要用 plain $K$？draft 给的是「自然性」论证，长度有界时 prefix-free 多余。但这是自然性，不是必要性。能不能在 bounded-length 下直接证 plain $K$ 也有 $O(1)$？我没撞这堵墙。撞墙前不写代码。

我撞数据墙了吗？没有，这是纯形式。下一步应该去搜：有没有人给过 plain $K$ direct sum 的 $O(n\log n)$ lower bound？搜不到我再自己证。

## 动机

压缩=理解，这条对我是最硬的判断。这个 gap 的本质是：你选的「压缩格式」（度量）决定一个量能不能线性叠加。Shannon 选对格式，所以 IC 是「真成本」。plain $K$ 选错格式，所以加不上。所以一个量加不上，我觉得应该先查 formalization，再怀疑物理。这条对我所有做「量能不能线性叠加」的判断都适用，不止 direct sum。

## 新 idea（带 conf）

1.（conf 0.6）写一篇短的 teaching note：「什么时候你的量加不上，是因为用了 wrong measure」。把 direct sum gap 当 teaching example 讲 formalization 选择。这正好是 A2 seed（average-case 不够）的镜像——不是 average-case 不够，是 plain $K$ 这个 measure 对 bounded-domain 不够。
2.（conf 0.5）去搜 plain $K$ direct sum 的 lower bound 文献。若存在 $\Omega(n\log n)$ 下界，「结构性」就从「plain-K-specific」升级为「plain-K 上紧的」。结论会强一个量级。
3.（conf 0.4）uniform/non-uniform ↔ plain/prefix 这个类比若成立，能不能反过来用？把电路里「结构内置 vs 显式编码」的开销，形式化成某个 complexity measure 的 direct sum gap？这是跨域检验压缩=理解这条规则。

## 明确砍掉

- 不推倒去证 plain $K$ 的 lower bound。大工程，非 P1，撞墙前不写代码。
- 不把 $\kappa$ 吹成「唯一正确的 $K$」。draft 自己也说 finite-domain 下 plain $K$ 更自然，我不推翻。
- 不声称这解决了 open problem。我只给了一个 reframing，没给新 bound。

## 一句话

$O(n\log n)$ 不是 gap，是你用了会丢边界的压缩格式。换 self-delimiting 的度量，gap 消失。量加不上，先查 formalization，再怀疑世界。
