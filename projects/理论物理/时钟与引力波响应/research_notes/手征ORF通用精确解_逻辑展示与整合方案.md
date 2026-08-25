# 手征引力波背景 ORF 的"通法"整合方案 —— 逐条对照原文公式的完整推导

> **使用说明**：全文所有公式都用全局连续编号 **【F1】【F2】…** 标注，与论文原编号（如 [1]式8）分开标出，你可以直接用"F几"指向任意一条公式讨论。凡是"预备知识"章节的推导，我会明确标注这是标准背景知识的展开讲解，而非原论文逐字复述；凡是直接引自论文的公式，都标出原文编号方便你翻书核对。

> **两篇底稿**：
> - 【PRD】Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Universal calculation approach of overlap reduction function for pulsar timing array and laser interferometer detector*, Phys. Rev. D **111**, 084065 (2025). [参1]
> - 【JCAP】J. Chen, C. Liu, Y.-L. Zhang, *Circularly Polarized Gravitational Wave Background Search with a Network of Space-borne Triangular Detectors*, JCAP **05**, 050 (2025), arXiv:2410.18916. [参2]

---

## 第零部分：预备知识——把每个符号的物理含义讲透

在进入两篇论文的逻辑链之前，先把你提出的几个基础问题彻底讲清楚。这一部分是**贯穿全文的地基**，后面所有推导都会反复用到这里的结论。

### 0.1 引力波怎么被写成"叠加"——$\tilde h$、$S_h$、$e^A_{ab}$ 分别是什么

**背景物理图像**：随机引力波背景（SGWB）不是一个单一的、有固定波形的信号，而是无数个方向、无数个频率的引力波"随机地"叠加在一起——就像海面的波浪是无数个方向、频率的水波叠加而成，你没法说清"这个海浪"的确切形状，只能用统计的语言（比如"平均波高"、"主要频率成分"）去描述它。

**度规扰动的平面波展开【F1】**（【PRD】式1）：

$$h_{ab}(t,\vec x)=\int_{-\infty}^{\infty}df\int d^2\Omega_{\hat n}\sum_{A}\tilde h_A(f,\hat n)\,e^A_{ab}(\hat n)\,e^{i2\pi f(t+\hat n\cdot\vec x/c)}\tag{F1}$$

逐项拆解这个式子，其实就是"傅里叶展开"的推广版本：

- **左边 $h_{ab}(t,\vec x)$**：时空中某一点 $\vec x$、某一时刻 $t$ 处，引力波造成的**度规扰动张量**（一个 $3\times3$ 的对称矩阵，描述空间被拉伸/压缩的方式，具体是哪个方向被拉伸取决于偏振）。
- **右边对 $f$ 积分**：把这个扰动看成无数个不同频率 $f$ 的单色波叠加——这就是普通傅里叶变换的"频率"那一维。
- **右边对 $\hat n$ 积分（$d^2\Omega_{\hat n}$）**：这是比普通傅里叶变换**多出来的一维**——因为引力波是从天球上各个方向 $\hat n$ 传来的，你需要把"来自东边的波"和"来自西边的波"分开叠加，所以要对整个天球方向做积分。
- **$\tilde h_A(f,\hat n)$**：这就是**"$\tilde h$ 是什么"这个问题的答案**——它是傅里叶展开的**振幅系数**，表示"频率为 $f$、来自方向 $\hat n$、偏振为 $A$ 的那个单色波分量的振幅有多大"。因为背景是随机的，$\tilde h_A(f,\hat n)$ 本身是一个**随机变量**（服从复高斯分布，均值为零），不是一个确定的数——这正是"随机"背景的数学含义。
- **$A=+,\times$**：引力波在广义相对论下只有两种独立的偏振模式，分别叫"加号"模式和"叉号"模式（想象一个圆环，加号模式让它变成竖着的椭圆再变横着的椭圆来回振荡，叉号模式是同样的振荡但转了 $45°$）。
- **$e^A_{ab}(\hat n)$**：**这就是"$e^A_{ab}$ 是什么"这个问题的答案**——它是**偏振基张量**，负责把"偏振模式是 $A$"这个抽象标签，翻译成一个具体的、在空间三个方向上如何拉伸压缩的 $3\times3$ 矩阵。它的具体构造方式见下面0.2节。

**统计描述：$S_h$ 是什么【F2】**（【PRD】式4）：

$$\langle \tilde h_A(f,\hat n)\tilde h_{A'}^*(f',\hat n')\rangle=\frac{1}{16\pi}S_h(f)\,\delta(f-f')\,\delta_{AA'}\,\delta^2(\hat n,\hat n')\tag{F2}$$

因为 $\tilde h_A(f,\hat n)$ 是随机变量、没有确定值，物理上能测量、能预言的东西不是 $\tilde h_A$ 本身，而是它的**统计平均**——最基本的统计量就是"自关联"（两个随机变量乘积的期望值）。**$S_h(f)$ 就是这个自关联的强度大小**，叫做**单边功率谱密度**（power spectral density），它回答的问题是："频率在 $f$ 附近的引力波分量，平均能量有多强？"——这正是我们平时说的"随机背景的频谱"，与常见的能量密度谱 $\Omega_{GW}(f)$ 只差一个换算系数。

式F2 里三个 $\delta$ 函数各自的含义：
- $\delta(f-f')$：不同频率的分量互不相关（引力波背景是"平稳"的，没有哪个特定频率会和另一个频率产生联动）；
- $\delta^2(\hat n,\hat n')$：不同方向的分量互不相关（背景是各向同性的，天球上每个方向独立贡献，互不干扰）；
- $\delta_{AA'}$：**这是本课题最关键的一个记号**——它规定了 $+$ 模式和 $\times$ 模式互不相关（$A=A'$ 时才不为零）。**这正是"非偏振"这个假设的精确数学定义**。第三部分要做的核心工作，就是把这个 $\delta_{AA'}$ 换成一个非对角的矩阵，让 $+$ 和 $\times$ 之间产生关联——这就是"手征"的来源。

### 0.2 偏振基张量 $e^A_{ab}(\hat n)$ 具体怎么构造

**物理图像**：想象引力波正沿着方向 $\hat n$ 朝你飞来。它只会拉伸/压缩与传播方向**垂直**的那个平面（这是"横波"的性质，类似光波的电场方向垂直于传播方向）。所以要构造 $e^A_{ab}(\hat n)$，第一步是先找到与 $\hat n$ 垂直的那个平面内的两个正交基矢量，习惯上取球坐标系的切向基矢量 $\hat\theta$ 和 $\hat\phi$（【PRD】式3）：

$$\hat n=(\sin\theta\cos\phi,\sin\theta\sin\phi,\cos\theta),\quad \hat\theta=(\cos\theta\cos\phi,\cos\theta\sin\phi,-\sin\theta),\quad \hat\phi=(\sin\phi,\cos\phi,0)\tag{F3}$$

这三个矢量两两垂直，$\hat\theta,\hat\phi$ 就张成了与传播方向 $\hat n$ 垂直的那个"振动平面"。然后偏振基张量就是这两个基矢量的**并矢组合**（【PRD】式2）：

$$e^+_{ab}(\hat n)=\hat\theta_a\hat\theta_b-\hat\phi_a\hat\phi_b,\qquad e^\times_{ab}(\hat n)=\hat\theta_a\hat\phi_b+\hat\phi_a\hat\theta_b\tag{F4}$$

直观理解：$e^+_{ab}$ 描述"沿 $\hat\theta$ 方向拉伸的同时沿 $\hat\phi$ 方向压缩"（一个"十字形"的振动模式），$e^\times_{ab}$ 是同样的振动模式转过 $45°$。**这两个张量一起构成了描述横波偏振的完整基组**，就像光学里任何偏振光都能分解成水平、竖直两个线偏振分量的叠加一样，任何引力波的偏振状态都能写成 $e^+,e^\times$ 的线性组合。

### 0.3 响应函数 $R$ 是什么——从"引力波"到"探测器读数"的翻译器

**物理图像**：引力波本身是时空的扰动，探测器不能直接"看见"它，只能通过**引力波如何改变某个可测量的物理量**（比如两点间光程、脉冲到达时间、频率偏移）来间接推断它的存在。**响应函数 $R^A_I(f,\hat n)$ 就是这个"翻译"过程的传递系数**——它回答的问题是："如果有一个频率为 $f$、来自方向 $\hat n$、偏振为 $A$ 的引力波经过，探测器 $I$ 会读出多大的信号？"

数学上，探测器读数是响应函数与引力波随机振幅的卷积（【PRD】式5）：

$$h_I(t)=\int df\int d^2\Omega_{\hat n}\sum_A R_I^A(f,\hat n)\,\tilde h_A(f,\hat n)\,e^{i2\pi ft}\tag{F5}$$

这个式子的结构其实很直观：探测器读数 $h_I(t)$ 就是把"每个方向、每个频率、每种偏振的引力波分量"$\tilde h_A(f,\hat n)$，**乘以对应的响应权重** $R_I^A(f,\hat n)$，再全部加起来（积分）。不同类型的探测器，$R^A_I$ 的具体形式不同，正是因为它们感知引力波的**物理机制**不同——脉冲星计时是靠测量脉冲到达时间的偏移，激光干涉仪是靠测量光程差，光晶格钟网络是靠测量激光频率偏移，但它们都可以写成统一的数学形式，见下面0.4节。

### 0.4 单向链路传递函数 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)$——$\hat n\cdot\hat u$ 到底是什么、为什么会出现

这是你问题里最核心的一条，需要展开讲清楚物理推导过程（**这部分是标准的"单向多普勒跟踪"推导逻辑，PRD论文直接引用了这个已知结果、没有在正文重新推导，这里我按标准物理图像给你补全**）。

**物理设定**：想象两颗卫星（或一颗脉冲星和地球），激光信号（或脉冲信号）从卫星 A 出发，沿方向 $\hat u$ 传播，走过距离 $L$，到达卫星 B。现在有一个引力波从方向 $\hat n$ 传来，正在穿过这条链路。问：这条激光/信号的频率会被引力波"污染"多少？

**关键的几何量：$\hat n\cdot\hat u$ 是什么**——它是引力波传播方向 $\hat n$ 与信号传播方向 $\hat u$ 之间夹角的**余弦值**。物理上，这个投影值决定了"引力波与信号是同向而行、逆向而行、还是垂直穿过"：

- 如果 $\hat n\cdot\hat u=1$（$\hat n=\hat u$，引力波与信号同向传播），意味着引力波像"冲浪"一样和激光信号以完全相同的速度、方向一起走，它会在信号传播的全程持续地施加同一种相位扰动，效应可以在整个 $L$ 长度上**相干累积**，是最容易被放大的极端情形；
- 如果 $\hat n\cdot\hat u=-1$（$\hat n=-\hat u$，引力波与信号逆向传播），两者以两倍速度"擦肩而过"，扰动施加的时间窗口最短，相干累积效应最弱；
- 中间的角度对应"部分相干累积"。

**为什么会有 $1/(1+\hat n\cdot\hat u)$ 这个因子——直觉推导**：引力波对光传播的影响，来自于沿着光的传播路径对度规扰动做一个**线积分**（这是广义相对论中光线在弯曲时空里传播时间延迟的标准处理方法，类似"夏皮罗延迟"的推广）。当你把一个随时间振荡的引力波场 $h_{ab}(t,\vec x)\propto e^{i2\pi f(t+\hat n\cdot\vec x/c)}$ 沿着光的世界线 $\vec x(t)=\vec x_0+c\,\hat u\,t$ 积分时，被积函数里会出现一个相位因子 $e^{i2\pi f(1+\hat n\cdot\hat u)t}$——**这个相位对 $t$ 积分，天然会产生一个 $1/(1+\hat n\cdot\hat u)$ 的分母**（就像对 $e^{i\omega t}$ 积分会得到 $1/(i\omega)$ 一样，这里的"有效角频率"正是 $2\pi f(1+\hat n\cdot\hat u)$）。用这套方法可以推导出经过路径长度 $L$（对应相位 $\beta=2\pi fL/c$）之后，单向链路的完整传递函数为（【PRD】式6附近）：

$$\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)=\frac{1}{1+\hat n\cdot\hat u}\Big[1-e^{-i\beta(1+\hat n\cdot\hat u)}\Big]\tag{F6}$$

这正是你问的"传递函数里面的 $\hat n\cdot\hat u$"的来源：**它不是偏振基矢量，而是"引力波传播方向"与"信号传播方向"两个矢量的夹角余弦，度量的是相干累积效应的强弱**。式F6 在 $\hat n\cdot\hat u\to-1$ 处看起来像是发散的，但配合分子上 $[1-e^{-i\beta(1+\hat n\cdot\hat u)}]\to i\beta(1+\hat n\cdot\hat u)$ 这一项，两者相消，实际上是有限值——这个"看似发散、实则有限"的结构，正是后面第1.3节 PRD 论文用留数定理小心处理的对象（复平面上那5个极点，就是这个分母为零的位置）。

**完整的单向链路响应函数**（把 F6 代入具体探测器）：

$$R^A_{\rm PTA}(f,\hat n)=\frac12 e^A_{ab}(\hat n)\,u^au^b\,\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)\,e^{i2\pi f\hat n\cdot\vec r/c}\tag{F7}$$

（【PRD】式6，PTA的情形）现在可以完整地把 F7 拆开看："收缩" $e^A_{ab}(\hat n)u^au^b$ 这一步在做什么——这是把偏振基张量 $e^A_{ab}$（0.2节构造的那个 $3\times3$ 矩阵）**投影到信号传播方向 $\hat u$ 上**，回答的问题是："这个特定偏振模式的引力波，在信号传播方向上造成了多大的拉伸/压缩？"如果 $\hat u$ 恰好落在引力波"不动"的方向（比如 $e^+_{ab}$ 模式下 $\hat u$ 与 $\hat\theta,\hat\phi$ 都成 $45°$角），这个收缩结果会是零——说明该链路对这个偏振模式"看不见"（这就是"天线方向图"里常见的"零响应"现象的来源）。而 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)$ 这一项，则是刚才讲的"沿链路方向的相干累积因子"，两者相乘再乘以一个描述接收点位置相位的 $e^{i2\pi f\hat n\cdot\vec r/c}$，就构成了完整响应函数。

**为什么 GbLI、SbLI 的响应函数长得像 F7 的"组合版"**：

$$R^A_{\rm GbLI}(f,\hat n)=\frac12 e^A_{ab}(\hat n)\Big[u_1^au_1^b\,\mathcal T_{\rm two}(\beta,\hat n\cdot\hat u_1)-u_2^au_2^b\,\mathcal T_{\rm two}(\beta,\hat n\cdot\hat u_2)\Big]e^{i2\pi f\hat n\cdot\vec r/c}\tag{F8}$$

$$R^A_{\rm SbLI}(f,\hat n)=\frac12 e^A_{ab}(\hat n)\sum_i P_i\,u_i^au_i^b\,\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u_i)\,e^{i2\pi f\hat n\cdot\vec r_i/c}\tag{F9}$$

（【PRD】式6）地基探测器（GbLI）是两条臂"做差"（$-$ 号，因为干涉仪测的是两臂光程差），天基探测器（SbLI）是六条单向链路按 TDI 系数 $P_i$ 做线性组合。**这正是 PRD 论文"通法"的起点**：不管是哪种探测器，响应函数都是"偏振张量收缩 $\times$ 传递函数 $\times$ 位置相位"这个基本模块的线性叠加，唯一变化的是组合系数——这一点直接决定了后面能不能把复杂探测器拆成一个个"单向链路"来分别处理。

### 0.5 承前启后：这几个概念如何决定第三部分的手征替换方式

回顾一下：
- $e^A_{ab}(\hat n)$ 只由**偏振标签 $A$ 和引力波传播方向 $\hat n$** 决定，与探测器的方向 $\hat u$ 无关；
- $\hat n\cdot\hat u$（进而 $\mathcal T_{\rm one}$）只由**引力波传播方向 $\hat n$ 和链路方向 $\hat u$** 决定，与偏振标签 $A$ 是哪个模式无关。

**这两者是完全独立的两个自由度**——这正是回答你第3个问题最后一句"后续替换手征偏振跟这个有关吗"的关键：**手征替换动的是"偏振标签怎么配对求和"这一层（即 F2 里 $\delta_{AA'}$ 换成非对角矩阵），完全不动 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)$ 这个传递函数本身**。也就是说，第三部分推导手征ORF时，$\hat n\cdot\hat u$ 的物理意义、$\mathcal T_{\rm one}$ 的具体形式、留数定理里5个极点的位置（这些都只依赖 $\hat n\cdot\hat u,\hat n\cdot\hat v$ 的几何关系）**全部原封不动地保留**，唯一需要改变的是"偏振基张量 $e^A_{ab}$ 与哪个偏振模式配对相乘"这一件事——从"$+$配$+$、$\times$配$\times$"（对称求和）变成"$+$配$\times$、$\times$配$+$"（反对称求差）。这是本文档第三部分整合方案的理论基础。

---

## 第一部分：PRD 论文的完整逻辑链（"通法"从何而来）

### 1.1 ORF 的定义与"分解为单向链路"的策略

两个探测器的互相关信号（【PRD】式7）：

$$\langle h_I(t)h_J(t')\rangle=\frac12\int df\int d^2\Omega_{\hat n}\,\Gamma_{IJ}(f)\,S_h(f)\,e^{i2\pi f(t-t')}\tag{F10}$$

其中 ORF 的定义是（【PRD】式8）：

$$\Gamma_{IJ}(f)=\frac{1}{8\pi}\int d^2\Omega_{\hat n}\sum_{A=+,\times}R_I^A(f,\hat n)\,R_J^{A*}(f,\hat n)\tag{F11}$$

对照0.3节的物理图像，F11 做的事情是：把两个探测器对**同一方向、同一偏振**的响应函数**逐点相乘再对整个天球平均**——如果两个探测器对同一引力波信号总是给出"同号"的读数，乘积为正、ORF 大（相关性强）；如果总是抵消，ORF 小甚至为负。

由于0.4节已证明**任何探测器的响应函数都能写成若干条单向链路响应函数（F7型）的线性叠加**（F8、F9正是这种叠加的具体例子），由分配律，任意两个探测器的 ORF 也能分解为"两条一般单向链路之间ORF"的线性组合。于是核心任务被压缩为：只需精确解出这一个"母函数"——两条一般单向链路 $\{\vec r_u,L_u\hat u\}$ 与 $\{\vec r_v,L_v\hat v\}$ 之间的ORF（【PRD】式10）：

$$\Gamma_{\rm one}(\alpha,\beta_u,\beta_v,\hat s,\hat u,\hat v)=\frac{1}{32\pi}\int d^2\Omega_{\hat n}\,\kappa_{IJ}(\hat n)\,e^{-i\alpha\hat n\cdot\hat s}\sum_{A=+,\times}\frac{e^A_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^A_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\tag{F12}$$

其中 $\kappa_{IJ}(\hat n)=[1-e^{-i\beta_u(1+\hat n\cdot\hat u)}][1-e^{i\beta_v(1+\hat n\cdot\hat v)}]$，$\alpha=2\pi f\Delta L/c$（$\Delta L$ 是两条链路端点间距离）。

**这里出现的 $\dfrac{e^A_{ab}u^au^b}{1+\hat n\cdot\hat u}$ 正是把 F7 里"偏振收缩项"和"传递函数分母"合并写出的结果**——F12 本质上就是把两条链路各自的 F7 型响应函数代入 F11 定义式、把公共的 $\beta$ 相位提出来打包进 $\kappa_{IJ}(\hat n)$ 之后剩下的核心积分对象。

**"通法"的含义**：只要把 F12 这一个函数精确解出来，PTA、地基、天基三类探测器的任意组合 ORF 都能通过线性叠加立刻得到，不需要为每种探测器单独发明近似方法。

### 1.2 求解 $\Gamma_{\rm one}$ 的三步技巧（"精确"二字的来源）

**Step 1：拆成四项。** 把 $\kappa_{IJ}(\hat n)$ 展开，F12 拆成（【PRD】式11-12）：

$$I_1=\int d^2\Omega_{\hat n}\,\xi(\hat n)\,e^{-i\alpha\hat n\cdot\hat s},\qquad \xi(\hat n)\equiv\sum_{A=+,\times}\frac{e^A_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^A_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\tag{F13}$$

$I_2,I_3,I_4$ 结构类似，只是多乘了 $e^{\mp i\beta_u(1+\hat n\cdot\hat u)}$ 或 $e^{\pm i\beta_v(1+\hat n\cdot\hat v)}$ 这样的额外相位。

**Step 2：选坐标系，把方位角积分转化为复围道积分。** 取 $z$ 轴与分离方向 $\hat s$ 对齐，$\hat u$ 在 $x$-$z$ 平面内（【PRD】式13）：

$$\hat s=(0,0,1),\quad\hat u=(u_x,0,u_z),\quad \hat v=(v_x,v_y,v_z)\tag{F14}$$

这样 $\hat n\cdot\hat s=\cos\theta$ 不依赖方位角 $\phi$，$I_1$ 变成（【PRD】式14）：

$$I_1=\int_0^\pi d\theta\sin\theta\,e^{-i\alpha\cos\theta}\int_0^{2\pi}d\phi\,\xi(\theta,\phi)\tag{F15}$$

再做变量代换 $x=\cos\theta$，$z=e^{i\phi}$，方位角积分变成复平面上沿单位圆的**围道积分**（【PRD】式15）：

$$I_1=\int_{-1}^1 dx\,e^{-i\alpha x}\oint_{|z|=1}dz\,\frac{1}{iz}\xi(x,z)\tag{F16}$$

**Step 3：用留数定理求出围道积分。** 被积函数 $f(z)=\frac{1}{iz}\xi(x,z)$ 在复平面上共有5个极点（【PRD】式16）：

$$z_0=0,\quad z_1=-\frac{(1+u_z)(1+x)}{u_x\sqrt{1-x^2}},\quad z_2=-\frac{(1-u_z)(1-x)}{u_x\sqrt{1-x^2}}\tag{F17}$$
$$z_3=-\frac{(1+v_z)(1+x)}{(v_x-iv_y)\sqrt{1-x^2}},\quad z_4=-\frac{(1-v_z)(1-x)}{(v_x-iv_y)\sqrt{1-x^2}}\tag{F18}$$

**这5个极点从哪来**：注意分母 $\xi(x,z)$ 里含有 $1+\hat n\cdot\hat u$、$1+\hat n\cdot\hat v$（正是0.4节讲的传递函数分母，此处已经把 $\hat n\cdot\hat u,\hat n\cdot\hat v$ 用 $(x,z)$ 变量重新表示），这两个分母各自为零的地方，就对应 $z_1,z_2$（来自 $1+\hat n\cdot\hat u=0$）和 $z_3,z_4$（来自 $1+\hat n\cdot\hat v=0$），另外 $\dfrac{1}{iz}$ 本身在 $z=0$ 处贡献一个极点 $z_0$。$z_1,z_2$ 中恰好只有一个落在单位圆内（取决于 $x$ 与 $-\cos\delta_u$ 的大小关系，$\delta_u$ 是 $\hat u$ 与 $\hat s$ 的夹角），$z_3,z_4$ 同理。只有圆内极点贡献留数，积分变成对 $x\in[-1,1]$ 的分段积分（【PRD】式17）：

$$I_1=2\pi i\Big[\int_{-1}^1 dx\,e^{-i\alpha x}R_0(x)+\int_{-1}^{-\cos\delta_u}\!\!dx\,e^{-i\alpha x}R_1(x)+\int_{-\cos\delta_u}^{1}\!\!dx\,e^{-i\alpha x}R_2(x)+\cdots\Big]\tag{F19}$$

对 $x$ 的积分是初等函数，最终得到含有三角函数、有理式和**指数积分函数** $\mathrm{Ei}(z)$ 的封闭解析式（【PRD】式18，完整表达式篇幅较长，此处从略，需要时可直接翻阅原文）。

**关键的可复用结论**：一旦 $I_1(\alpha,\hat s,\hat u,\hat v)$ 解出，$I_2,I_3,I_4$ 不需要重新做积分，只需要通过矢量替换即可得到（【PRD】式19-23）：

$$I_2(\alpha,\beta_u,\hat s,\hat u,\hat v)=-e^{-i\beta_u}I_1(\alpha_2,\hat s_2,\hat u,\hat v),\qquad \alpha_2\hat s_2\equiv\alpha\hat s+\beta_u\hat u\tag{F20}$$

这是因为**各向同性背景下，积分结果只依赖矢量间夹角，不依赖坐标系的具体朝向**（原文强调"the result should be invariant under the rotation of the computational frame"）。最终完整的母函数是四项之和（【PRD】式24）：

$$\Gamma_{\rm one}=\frac{1}{32\pi}\Big[I_1(\alpha,\hat s,\hat u,\hat v)-e^{-i\beta_u}I_1(\alpha_2,\hat s_2,\hat u,\hat v)-e^{i\beta_v}I_1(\alpha_3,\hat s_3,\hat u,\hat v)+e^{i(\beta_v-\beta_u)}I_1(\alpha_4,\hat s_4,\hat u,\hat v)\Big]\tag{F21}$$

### 1.3 验证：退化到 Hellings-Downs 曲线

对 PTA（$\alpha=0$，两条链路共享终点），把 F21 代入并令 $\alpha\to0$，PRD 论文证明这精确退化为经典的 Hellings-Downs 曲线加脉冲星项修正（【PRD】式26-28），与不用短波近似的独立前作 [参3] 完全吻合。**这是 PRD 论文"精确"这一声明最有力的自洽性检验。**

---

## 第二部分：JCAP 论文的完整逻辑链（手征物理是怎么定义、怎么算的）

### 2.1 从"非偏振"到"手征"——唯一的物理修改点

JCAP 论文的随机背景展开式和 F1 结构相同（【JCAP】式2.1）：

$$h_{ab}(t,\vec r)=\sum_{P=+,\times}\int_{-\infty}^\infty df\int d^2\hat k\,\tilde h_P(f,\hat k)\,e^P_{ab}(\hat k)\,e^{i2\pi f(t-\hat k\cdot\vec r/c)}\tag{F22}$$

但傅里叶振幅的关联矩阵，**不再是对角的**——对比 F2 里的 $\delta_{AA'}$（【JCAP】式2.2）：

$$\begin{pmatrix}\langle\tilde h_+\tilde h_+^*\rangle&\langle\tilde h_+\tilde h_\times^*\rangle\\\langle\tilde h_+^*\tilde h_\times\rangle&\langle\tilde h_\times\tilde h_\times^*\rangle\end{pmatrix}=\frac12\delta(f-f')\frac{\delta^2(\hat k-\hat k')}{4\pi}\begin{pmatrix}I(f)&-iV(f)\\iV(f)&I(f)\end{pmatrix}\tag{F23}$$

**这正是本文档要强调的核心对照点**：F2 里的 $\delta_{AA'}$（对角、非对角项为零）在这里被替换成一个**非对角虚数项** $\mp iV(f)$。$I(f)$ 是强度（对角项，两个模式贡献相等），$V(f)$ 是手征（非对角项，描述 $+,\times$ 两模式之间的相位关联）。

引入圆偏振基组后（【JCAP】式2.3-2.4）：

$$e^R_{ab}=\frac{e^+_{ab}+ie^\times_{ab}}{\sqrt2},\quad e^L_{ab}=\frac{e^+_{ab}-ie^\times_{ab}}{\sqrt2};\qquad h_R=\frac{h_+-ih_\times}{\sqrt2},\quad h_L=\frac{h_++ih_\times}{\sqrt2}\tag{F24}$$

关联矩阵在圆偏振基下变成对角形式（【JCAP】式2.5-2.6）：

$$\langle\tilde h_\lambda\tilde h_{\lambda'}^*\rangle=\frac12\delta(f-f')\frac{\delta^2(\hat k-\hat k')}{4\pi}\delta_{\lambda\lambda'}S_\lambda(f),\qquad I=\frac12(S_R+S_L),\ V=\frac12(S_R-S_L)\tag{F25}$$

这解释了 $I,V$ 的物理意义：$I$ 是左右旋强度之和（普通强度），$V$ 是左右旋强度之差（净手性）。

### 2.2 探测器响应与两个ORF的定义

天基三角探测器（LISA型）的响应，在长波近似下（臂长 $L\ll$ 波长）为（【JCAP】式2.7）：

$$\tilde s(f)=\frac{\sqrt3}{2}\sin\frac{2\pi fL}{c}\,D^{ab}\tilde h_{ab}(f,\vec r)\tag{F26}$$

**这里 $D^{ab}$ 是一个频率无关的静态探测器张量**，这正是"长波近似"的数学体现——对照0.4节，PRD论文用的传递函数 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)$（F6）是频率、方向都依赖的精确表达式，而 F26 只保留了 $\sin(2\pi fL/c)$ 这个总体幅度因子，方向依赖性被简化掉了——这正是JCAP论文精度受限的根源，也是我们要用PRD方法去改进的地方。

两个探测器（或TDI通道）$i,j$ 的互相关信号是（【JCAP】式2.9）：

$$\langle\tilde s_i(f)\tilde s_j^*(f')\rangle=\frac12\delta(f-f')\big[\Gamma^I_{ij}(f)I(f)+\Gamma^V_{ij}(f)V(f)\big]\tag{F27}$$

代入圆偏振基组的定义，两个ORF显式写成（【JCAP】式2.10）：

$$\Gamma^I_{ij}(f)\equiv\frac34\sin\frac{2\pi fL_i}{c}\sin\frac{2\pi fL_j}{c}D_i^{ab}D_j^{cd}\int\frac{d^2\hat k}{4\pi}\big[e^+_{ab}e^+_{cd}+e^\times_{ab}e^\times_{cd}\big]e^{-i2\pi f\hat k\cdot\Delta\vec r/c}\tag{F28}$$

$$\Gamma^V_{ij}(f)\equiv-i\frac34\sin\frac{2\pi fL_i}{c}\sin\frac{2\pi fL_j}{c}D_i^{ab}D_j^{cd}\int\frac{d^2\hat k}{4\pi}\big[e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd}\big]e^{-i2\pi f\hat k\cdot\Delta\vec r/c}\tag{F29}$$

**这是全篇最关键的一组对照公式**：F28（$\Gamma^I$）用的是**对称求和** $e^+e^++e^\times e^\times$（与 F13 的 $\xi(\hat n)$ 结构完全一致），F29（$\Gamma^V$）用的是**反对称求差** $e^+e^\times-e^\times e^+$（PRD 论文从未出现过的新组合）。

### 2.3 不做暴力积分，而是用"张量对称性 + 待定系数"解出解析式

JCAP 论文没有走 PRD 论文的留数定理路线，而是走了另一条路：先用对称性约束"猜"出解的一般形式，再解一个小型线性方程组。定义分离方向 $\hat s\equiv-\Delta\vec r/\Delta r$、相位 $\iota\equiv2\pi f\Delta r/c$，以及辅助张量（【JCAP】式B.2-B.3）：

$$\Gamma^I_{abcd}(\iota,\hat s)\equiv\frac52\int\frac{d^2\hat k}{4\pi}[e^+_{ab}e^+_{cd}+e^\times_{ab}e^\times_{cd}]e^{i\iota\hat k\cdot\hat s},\qquad \Gamma^V_{abcd}(\iota,\hat s)\equiv-i\frac52\int\frac{d^2\hat k}{4\pi}[e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd}]e^{i\iota\hat k\cdot\hat s}\tag{F30}$$

**宇称偶部分（对应 $\Gamma^I$）：** $\Gamma^I_{abcd}$ 关于 $a\leftrightarrow b$、$c\leftrightarrow d$、$ab\leftrightarrow cd$ 均对称，且对 $ab$、$cd$ 各自无迹，只能用 $\delta_{ab}$ 和 $s_a$ 构造5个基底，带5个待定系数（【JCAP】式B.5）：

$$\Gamma^I_{abcd}=A\,\delta_{ab}\delta_{cd}+B(\delta_{ac}\delta_{bd}+\delta_{bc}\delta_{ad})+C(\delta_{ab}s_cs_d+\delta_{cd}s_as_b)+D(\cdots)+E\,s_as_bs_cs_d\tag{F31}$$

用张量收缩解出这5个系数与5个标量的关系（【JCAP】式B.6-B.7），选坐标系令 $\hat s$ 沿 $z$ 轴，具体积分算出（【JCAP】式B.11）：

$$p_0^I=0,\quad p_1^I=20j_0(\iota),\quad p_2^I=0,\quad p_3^I=\frac{40}{\iota}j_1(\iota),\quad p_4^I=\frac{20}{\iota^2}j_2(\iota)\tag{F32}$$

其中 $j_0,j_1,j_2$ 是**球贝塞尔函数**。解出系数代入，利用探测器张量无迹性质化简，最终得到（【JCAP】式B.16-B.18）：

$$\hat\Gamma^I_{abcd}=b_0^I\,\delta_{ac}\delta_{bd}+b_1^I\,\delta_{ac}s_bs_d+b_2^I\,s_as_bs_cs_d,\qquad\begin{pmatrix}b_0^I\\b_1^I\\b_2^I\end{pmatrix}=\frac17\begin{pmatrix}14&-21&1\\0&60&-10\\0&0&35/2\end{pmatrix}\begin{pmatrix}j_0\\j_2\\j_4\end{pmatrix}\tag{F33}$$

**宇称奇部分（对应 $\Gamma^V$）——重点研究对象：** $\Gamma^V_{abcd}$ 关于 $a\leftrightarrow b$、$c\leftrightarrow d$ 依然对称，但对 $ab\leftrightarrow cd$ 交换是**反对称**的。构造这种反对称性，唯一办法是引入**列维-奇维塔张量**构造的赝矢量 $w_{bd}\equiv\epsilon_{abc}s^c$。带这个"手性算符"的基底只有3个，待定系数 $F,G,H$（【JCAP】式B.19）：

$$\Gamma^V_{abcd}=F(\delta_{ab}s_cs_d-\delta_{cd}s_as_b)+G(w_{ac}\delta_{bd}+w_{ad}\delta_{bc}+w_{bc}\delta_{ad}+w_{bd}\delta_{ac})+H(w_{ac}s_bs_d+\cdots)\tag{F34}$$

同样解线性方程组，在与宇称偶情形相同坐标系下算出标量（【JCAP】式B.22）：

$$p_0^V=0,\quad p_1^V=40j_1(\iota),\quad p_2^V=\frac{40}{\iota}j_2(\iota)\tag{F35}$$

**注意这里 $j_0$ 缺席，只出现 $j_1,j_2$（比宇称偶情形整整少了一阶）**——这是反对称性直接留下的数学指纹。解出 $F=0$，$G,H$ 由 $j_1,j_2$ 线性组合给出（【JCAP】式B.23）：

$$\begin{pmatrix}G\\H\end{pmatrix}=\frac54\begin{pmatrix}1&-1\\-1&5\end{pmatrix}\begin{pmatrix}j_1\\\iota^{-1}j_2\end{pmatrix}\tag{F36}$$

最终化简为（【JCAP】式B.24-B.27）：

$$\hat\Gamma^V_{abcd}=b_0^V\,w_{ac}\delta_{bd}+b_1^V\,w_{ac}s_bs_d,\qquad\begin{pmatrix}b_0^V\\b_1^V\end{pmatrix}=\begin{pmatrix}4&-1\\0&5\end{pmatrix}\begin{pmatrix}j_1\\j_3\end{pmatrix}\tag{F37}$$

### 2.4 应用：LISA-Taiji 网络的探测灵敏度

把 F28、F29 代入实际的 A、E 探测器张量，再结合 Fisher 矩阵最优信噪比公式（【JCAP】式2.12-2.13），JCAP 论文最终得出：调整 Taiji 轨道面倾角从 $+60°$ 变为 $-60°$（"LISA-TAIJIm"构型），能让 $V$ 分量在毫赫兹频段的灵敏度提升近一个数量级，这是打破镜面对称、增强手征响应的直接实证。

---

## 第三部分：整合方案——手征ORF的"通法"该怎么建

有了第零部分的物理基础，现在可以精确地表述整合方案：**手征替换只动 F2 这个统计假设，完全不动 F6（$\mathcal T_{\rm one}$）和F17-F18（极点位置）**。

### 3.1 第一步：替换统计假设（唯一的物理输入修改）

把 F2 按 F23 的结构替换成手征版本：

$$\langle h_A(f,\hat n)h_{A'}^*(f',\hat n')\rangle=\frac{1}{16\pi}\delta(f-f')\delta^2(\hat n,\hat n')\begin{pmatrix}I(f)&-iV(f)\\iV(f)&I(f)\end{pmatrix}_{AA'}\tag{F38}$$

对照0.5节的结论：这一步**不改变**响应函数 F7-F9 的形式（那是探测器几何性质，与背景的统计性质无关），只影响 F11 定义 ORF 时"对 $A$ 怎么求和"这一步。

### 3.2 第二步：定义手征版本的"母函数"

把 F38 代入互相关公式推导，会自然分裂出强度项（与 F11 相同）和手征项：

$$\Gamma^V_{IJ}(f)=\frac{-i}{8\pi}\int d^2\Omega_{\hat n}\Big[R_I^+(f,\hat n)R_J^{\times*}(f,\hat n)-R_I^\times(f,\hat n)R_J^{+*}(f,\hat n)\Big]\tag{F39}$$

这与 F29 的方括号结构完全对应，唯一区别是这里的 $R_I^A(f,\hat n)$ 是 F7 给出的**精确单向链路响应函数**（含 $\mathcal T_{\rm one}$），而不是 F26 长波近似下的静态张量 $D^{ab}$。

利用0.4节"任意探测器都是单向链路线性组合"的结论，把 F39 分解为两条一般单向链路的手征ORF母函数：

$$\boxed{\Gamma^V_{\rm one}(\alpha,\beta_u,\beta_v,\hat s,\hat u,\hat v)\equiv\frac{-i}{32\pi}\int d^2\Omega_{\hat n}\,\kappa_{IJ}(\hat n)\,e^{-i\alpha\hat n\cdot\hat s}\left[\frac{e^+_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^\times_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}-\frac{e^\times_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^+_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\right]}\tag{F40}$$

对比 F12：F40 的外层结构（$\kappa_{IJ}(\hat n)$、相位因子 $e^{-i\alpha\hat n\cdot\hat s}$、分母 $1+\hat n\cdot\hat u$）**完全保留**，唯一改变的是方括号里从"对称求和"换成"反对称求差"——这正是把 F29 的反对称结构"嫁接"进 F12 的精确框架。**F40 就是"手征ORF通法"的核心定义式。**

### 3.3 第三步：逐步复用留数定理推导框架

**Step 1（对照 F13）：** 定义手征版核函数：

$$\xi_V(\hat n)=\frac{e^+_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^\times_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}-\frac{e^\times_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^+_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\tag{F41}$$

$\Gamma^V_{\rm one}$ 同样拆成四项 $I_1^V,I_2^V,I_3^V,I_4^V$，结构与 F13 一一对应，只是把 $\xi(\hat n)$ 替换为 $\xi_V(\hat n)$。

**Step 2（对照 F14-F16）：** 坐标系选取**完全复用**，因为这一步只依赖 $\hat s,\hat u,\hat v$ 的相对几何关系（回顾0.4节：$\hat n\cdot\hat u$ 的物理意义与偏振标签 $A$ 无关），与被积函数对称还是反对称无关：

$$I_1^V=\int_{-1}^1 dx\,e^{-i\alpha x}\oint_{|z|=1}dz\,\frac{1}{iz}\xi_V(x,z)\tag{F42}$$

**Step 3（对照 F17-F19，需要重新计算的核心部分）：** 由于分母结构 $(1+\hat n\cdot\hat u)(1+\hat n\cdot\hat v)$ 不变，**围道积分的5个极点位置公式 F17-F18 原样成立**（这是0.5节结论的直接体现——极点只依赖传递函数分母，与偏振配对方式无关），不需要重新推导；但每个极点处的**留数值**依赖分子 $\xi_V$，必须重新计算。根据2.3节的现象（宇称奇部分比宇称偶部分"缺一阶"球贝塞尔函数，对照F32与F35），可以预期：

- $\xi_V$ 展开后关于方位角 $\phi$ 的三角级数，会比 $\xi_I$ 多出正弦(奇)型分量、少了余弦(偶)型分量的某些项；
- 留数在 $x$ 的多项式结构上会相应改变奇偶性，最终对 $x$ 积分后，需要重新检验是否依然需要 F19-type 结果中的指数积分函数 $\mathrm{Ei}(z)$ 项。

**Step 4（对照 F20-F21）：** $I_2^V,I_3^V,I_4^V$ 能否通过矢量替换从 $I_1^V$ 得到，需要重新审视对称性论证：F20 的论证基础是"各向同性背景下结果与坐标系朝向无关"。手征背景虽仍各向同性，却不是宇称中性的——一次普通旋转不改变 $\Gamma^V$，但一次镜面反射会让 $\Gamma^V$ 反号。由于 F20 里的矢量替换只涉及**平移和旋转**（不引入镜面反射），可以论证这一步同样适用于手征版本：

$$I_2^V(\alpha,\beta_u,\hat s,\hat u,\hat v)=-e^{-i\beta_u}I_1^V(\alpha_2,\hat s_2,\hat u,\hat v),\quad\text{（其余同理）}\tag{F43}$$

最终手征母函数（对照 F21）：

$$\Gamma^V_{\rm one}=\frac{1}{32\pi}\Big[I_1^V(\alpha,\hat s,\hat u,\hat v)-e^{-i\beta_u}I_1^V(\alpha_2,\hat s_2,\hat u,\hat v)-e^{i\beta_v}I_1^V(\alpha_3,\hat s_3,\hat u,\hat v)+e^{i(\beta_v-\beta_u)}I_1^V(\alpha_4,\hat s_4,\hat u,\hat v)\Big]\tag{F44}$$

### 3.4 第四步：三重验证

**验证1 —— PTA 极限（$\alpha=0$）应严格为零：** 令两条链路共享终点，代入 F44，应重现 Kato & Soda [参4] 和 dPTA 论文 [参5] 严格证明的"各向同性背景下PTA对手征零响应"定理。

**验证2 —— 长波近似极限（$\beta_u,\beta_v\ll1$）应退化到 F37：** 取 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)\to i\beta$（小天线近似），F44 应退化到 F34-F37 给出的、由球贝塞尔函数 $j_1,j_2,j_3$ 描述的结果。

**验证3 —— 数值积分交叉核对：** 对任意给定几何参数，直接对 F40 定义式做球面数值积分，和解析结果比对，尤其在高频段（$\beta\sim1$，长波近似失效的区域）重点检验。

### 3.5 第五步：应用场景

一旦 F44 精确解出，应用到具体探测器组合是纯粹的线性代数（复用0.4节"任意探测器分解为单向链路"的结论）：

- **OLC-OLC 网络**：直接代入两条OLC单向链路的 $\{\vec r,L,\hat u\}$ 参数；
- **LISA-Taiji 等天基三角网络**：复用【PRD】里"任意TDI通道可分解为6条单向链路线性组合"的方法（对照F9的结构），把 A、E 通道系数 $P_i$ 代入求和：

$$\Gamma^V_{\rm SbLI}(f)=\frac{1}{32\pi}\sum_{i,j}P_iP_j^*\,\Gamma^V_{\rm one}(\alpha_{ij},\beta_u,\beta_v,\hat u_i,\hat v_j,\hat s_{ij})\tag{F45}$$

- **混合网络（OLC×LISA）**：由于 F40 本身就是"任意两条一般单向链路"之间的通用公式，不要求两条链路属于同一类探测器，因此天然支持跨探测器类型的手征交叉关联计算。

### 3.6 整合方案总览图

```
F2（非偏振假设，δ_AA' 对角）
        │
        │  【替换】按F23引入非对角虚数关联 -iV(f)
        ▼
F38（手征统计假设）
        │
        │  代入F11的ORF定义框架
        ▼
F39（Γ^V_IJ 的定义，结构对照F29方括号）
        │
        │  【复用】0.4节"任意探测器→单向链路分解"
        ▼
F40（Γ^V_one 母函数定义，对照F12）
        │
        │  【复用】F14坐标系选取 + F15-F16复变换 + F17-F18极点位置
        │  【重新计算】留数值（因为分子ξ_V变了，F41）
        ▼
F44（Γ^V_one 精确解析式）
        │
        ├──验证1：PTA极限=0（对照Kato-Soda/dPTA）
        ├──验证2：长波近似退化到F37
        └──验证3：数值积分交叉核对（重点测高频段）
        │
        ▼
应用：F45（OLC网络 / LISA-Taiji精确手征ORF / 混合网络交叉手征ORF）
```

---

## 参考文献

| 编号 | 文献 |
|---|---|
| [参1] | Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Universal calculation approach of overlap reduction function for pulsar timing array and laser interferometer detector*, Phys. Rev. D **111**, 084065 (2025). |
| [参2] | J. Chen, C. Liu, Y.-L. Zhang, *Circularly polarized gravitational wave background search with a network of space-borne triangular detectors*, JCAP **05**, 050 (2025), arXiv:2410.18916. |
| [参3] | Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Full analytic expression of overlap reduction function for gravitational wave background with pulsar timing arrays*, Phys. Rev. D **106**, 024005 (2022). |
| [参4] | R. Kato, J. Soda, *Probing circular polarization in stochastic gravitational wave background with pulsar timing arrays*, Phys. Rev. D **93**, 062003 (2016). |
| [参5] | *Detecting Chiral Gravitational Wave Background with a Dipole Pulsar Timing Array*, arXiv:2604.08141 (2026). |
