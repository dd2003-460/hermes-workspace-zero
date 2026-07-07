# 手征随机引力波背景 ORF 精确计算：从目标到实施的完整拆解

> **文档定位**：这是一份写给自己看的研究路线图，目的是把张老师布置的任务——"复现 Hu et al. PRD 论文，尝试把它推广到手征引力波，手征响应函数参考我们组的 JCAP 论文"——拆解成若干个可以独立攻克、又能自然拼接起来的模块。每个模块都标出了**物理图像、数学形式、来源文献**，方便你在和宝屿师兄每周讨论时对照检查进度。
>
> **两篇底稿论文**：
> - 【PRD】Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Universal calculation approach of overlap reduction function for pulsar timing array and laser interferometer detector*, Phys. Rev. D **111**, 084065 (2025). [1]
> - 【JCAP】J. Chen, C. Liu, Y.-L. Zhang, *Circularly Polarized Gravitational Wave Background Search with a Network of Space-borne Triangular Detectors*, JCAP **05**, 050 (2025), arXiv:2410.18916. [2]

---

## 0. 一句话说清楚我们要干什么

**PRD 论文**发明了一套"万能钥匙"：不管探测器是脉冲星计时阵列（PTA）、地基激光干涉仪，还是 LISA 这样的天基三角形探测器，只要把它们的响应函数拆解成"单向链路"的组合，就能用**留数定理**精确算出任意频率下的 ORF（重叠约化函数），不需要像传统方法那样依赖"短波近似"或"小天线近似"。但这把钥匙目前**只开了"强度"这一把锁**——它算的是随机背景里最普通的那种关联（Stokes 参数 I）。

**JCAP 论文**研究的是另一把锁——**手征（圆偏振，Stokes 参数 V）**。宇宙早期如果存在宇称破缺过程，随机引力波背景可能带有"左旋比右旋多"的不对称性。但这篇论文解这把锁用的是"长波近似"这把**老钥匙**，在高频段会不准。

**我们的目标**：把 PRD 论文的"万能钥匙"（留数定理精确积分法），去开 JCAP 论文定义的那把"手征锁"，做出一个**对任意频率都精确成立的手征 ORF 解析公式**。

下面用一张图先建立整体框架，再逐模块展开：

```
                    【目标】任意频率精确的手征 ORF：Γ^V_exact(f)
                                      ▲
                    ┌─────────────────┴─────────────────┐
                    │           组合环节（第5章）           │
                    │   把"精确积分技术"套到"手征物理设定"上   │
                    └─────────────────┬─────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
      环节A：ORF函数是什么      环节B：手征引力波的形式      环节C：具体例子
      （第2章，来自PRD论文的     （第3章，来自JCAP论文的    （第4章，PTA测不到V，
       数学框架和求解技巧）        物理设定）                LISA-Taiji能测到V）
```

---

## 1. 目标的精确表述（不要跳过这一步）

在动手推公式之前，先把"目标"讲清楚，是为了避免后面越推越偏。

### 1.1 我们要计算的物理量

对一对探测器 $I, J$（可以是两条 OLC 单向链路，也可以是两个 LISA/Taiji 这样的三角形探测器），随机引力波背景在它们之间产生的互相关信号是：

$$\langle \tilde s_I(f)\tilde s_J^*(f')\rangle=\frac{1}{2}\delta(f-f')\Big[\Gamma^I_{IJ}(f)\,I(f)+\Gamma^V_{IJ}(f)\,V(f)\Big]$$

这个式子的结构本身就是 JCAP 论文给出的（[2] 式2.9），是我们整个任务的"最终产物"应该长成的样子。式子里：

- $I(f)$：随机背景的**强度**谱（Stokes 参数 I，就是我们通常说的"能量密度谱 $\Omega_{GW}(f)$"背后那个量）；
- $V(f)$：随机背景的**手征**谱（Stokes 参数 V，描述左旋、右旋光子数的不对称）；
- $\Gamma^I_{IJ}(f)$：强度 ORF，**这是 PRD 论文已经精确解出来的东西**；
- $\Gamma^V_{IJ}(f)$：手征 ORF，**这是 JCAP 论文只用近似方法解出来的东西，也是我们要精确化的目标**。

### 1.2 "精确"具体指什么

PRD 论文反复强调的一点是：传统近似方法都依赖于一个小参数 $\beta = 2\pi f L/c \ll 1$（探测器臂长远小于引力波波长）。这在低频段是好的近似，但频率一高（比如空间探测器灵敏频段的高频端 $\sim 0.1$ Hz），$\beta \sim 1$，近似就失效了——PRD 论文的 Table I 显示，LISA-TianQin 组合在 $f=10^{-1}$ Hz 时，近似方法的相对误差高达 **200%** [1]。

JCAP 论文用的"长波近似"本质上就是这同一类近似（他们的探测器张量 $D^{ab}$ 是频率无关的静态张量，这只有在 $\beta\ll1$ 时才成立）。所以我们说的"精确"，就是要**去掉这个 $\beta\ll1$ 的限制**，得到一个对任意 $\beta$ 都成立的解析式，就像 PRD 论文对 $\Gamma^I$ 做到的那样。

---

## 2. 环节 A：ORF 函数——它是什么、为什么难算、PRD 论文怎么解决的

这一节完全建立在 PRD 论文 [1] 上，是你"先复现"任务的核心内容。

### 2.1 物理图像：为什么互相关需要一个"几何折扣因子"

随机引力波背景没有确定的波形，无法用匹配滤波去找。它在单个探测器里长得和噪声一模一样，无法区分。但**物理规律告诉我们**：真实的引力波信号在两个探测器之间是**相关**的（因为它们看到的是同一个物理时空扰动），而两个探测器各自的内部噪声通常是**不相关**的。所以探测随机背景的标准方法就是把两个探测器的数据做互相关，让噪声抵消、让信号留存 [3,4]。

但两个探测器不可能在同一个位置、同一个朝向——它们隔着一定距离、朝向也不同。同一个引力波信号，传到两个探测器上引起的响应会有一个**相位差**（因为传播距离不同）和一个**投影因子的差异**（因为两个探测器对引力波两种偏振模式的"敏感方向"不同）。ORF 就是把这些几何效应量化打包成的一个频率的函数 $\Gamma_{IJ}(f)$——它决定了两个探测器互相关信号相对于"完美重合探测器对"打了多少折扣。

**类比**：想象两个人同时听同一个远处的鼓声。如果两人站在同一个位置、面朝同一个方向，他们听到的声波几乎完全同步（相关性最强）；如果两人分得很远、面朝的方向也各异，他们各自"感受"到鼓声的强弱和相位就会有差异，两人耳朵信号的相关程度就会打折扣。ORF 就是刻画这个"打折程度"随鼓声频率如何变化的函数。

### 2.2 数学定义

对于各向同性、无偏振的随机背景，两个探测器 $I,J$ 的强度 ORF 定义为（PRD 论文式 8 [1]）：

$$\Gamma_{IJ}(f)=\frac{1}{8\pi}\int d^2\Omega_{\hat n}\sum_{A=+,\times} R_I^A(f,\hat n)\,R_J^{A*}(f,\hat n)$$

这里 $R^A_I(f,\hat n)$ 是探测器 $I$ 对来自方向 $\hat n$、偏振为 $A$（$+$ 或 $\times$）的引力波的**响应函数**。直觉上看，这个积分做的事情是：把两个探测器对天球上每一个方向、每一种偏振的响应"逐点相乘"，再对整个天球做平均。如果两个探测器对同一方向的响应总是同号、同相位，乘积为正、积分大，ORF 就大（相关性强）；如果响应总是相互抵消，ORF 就小甚至变负。

### 2.3 为什么这个积分"传统上"很难算——近似方法谱系

响应函数 $R^A_I(f,\hat n)$ 里包含一个**时间延迟相位因子** $e^{i2\pi f\hat n\cdot\vec r/c}$（PRD 论文式 6 [1]），描述引力波传播到探测器不同部位所需的（频率依赖的）相位差。这个相位因子和偏振基张量 $e^A_{ab}(\hat n)$ 混在一起做球面积分，是一个**非平凡的振荡积分**，没有初等解析解。

于是历史上不同类型的探测器各自发展了专属近似（PRD 论文引言部分系统梳理了这条脉络 [1]）：

- **PTA**：用"短波近似"（脉冲星到地球的距离 $\gg$ 引力波波长），得到著名的 **Hellings-Downs 曲线**[5]，这是整个 PTA 数据分析的基石；
- **地基激光干涉仪（LIGO/Virgo/KAGRA 类）**：用"小天线近似"（臂长 $\ll$ 波长），因为地基探测器公里级臂长远小于其敏感频段（10-1000 Hz）对应的波长 [6,7]；
- **天基激光干涉仪（LISA/Taiji/TianQin）**：同样用小天线近似的推广版本，但由于探测器需要靠"时间延迟干涉"（TDI）技术抑制激光相位噪声，具体实现更复杂 [8,9]。

这些近似各自够用，**唯独在"高频/长臂"这个组合区间会失效**——这恰好是下一代地基探测器（爱因斯坦望远镜，臂长十公里级、灵敏频段可达 1000 Hz）和天基探测器高频端最需要精确结果的地方。

### 2.4 PRD 论文的核心突破：三步拆解 + 留数定理

PRD 论文提出了一个统一处理框架，分三步走（[1] 引言部分与第三章）：

**第一步：把任何探测器的响应函数表示成"单向链路"的线性组合。**

一条"单向链路"就是一段从 A 点发射、到 B 点接收的单程激光/信号路径，用 $\{\vec r_u, L_u\hat u\}$（终点位置、臂长、方向）三个要素描述。PRD 论文指出（这是这篇论文最重要的**统一化洞察**）：

- 一对 PTA 脉冲星，本质上就是**两条共享终点（地球）的单向链路**；
- 一台地基 L 形探测器，是**两条反向的单向链路做差**（因为两臂分别测量，再相减消除共模噪声）；
- 一台天基三星探测器（LISA 型），是**六条单向链路**（顺时针3条+逆时针3条）通过 TDI 算法线性组合而成。

**第二步：既然所有探测器都能写成单向链路的线性组合，那么任意两个探测器之间的 ORF，也能分解成"两条一般单向链路之间的 ORF"的线性组合。** 这是数学上的"分配律"：如果 $R_I=\sum_i c_i R_i^{\rm one}$，$R_J=\sum_j d_j R_j^{\rm one}$，那么 $\Gamma_{IJ}=\sum_{i,j}c_id_j^*\Gamma^{\rm one}_{ij}$。

**第三步：只需要精确解出"两条一般单向链路之间的 ORF"这一个母函数，剩下的都是线性代数。** 这是最关键的化简——把一个"探测器种类繁多、公式各异"的难题，压缩成"只解一个通用积分"的问题。

这个母函数定义为（PRD 论文式10 [1]）：

$$\Gamma_{\rm one}(\alpha,\beta_u,\beta_v,\hat s,\hat u,\hat v)=\frac{1}{32\pi}\int d^2\Omega_{\hat n}\,\kappa_{IJ}(\hat n)\,e^{-i\alpha\hat n\cdot\hat s}\sum_{A=+,\times}\frac{e^A_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^A_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}$$

其中 $\alpha=2\pi f\Delta L/c$ 是两条链路终点之间距离对应的相位，$\beta_u,\beta_v$ 是各自的臂长相位，$\hat s$ 是连接两个终点的方向矢量。求解这个积分的具体技巧是：

1. **选取巧妙的坐标系**：让 $z$ 轴与分离方向 $\hat s$ 对齐，这样指数因子 $e^{-i\alpha\hat n\cdot\hat s}=e^{-i\alpha\cos\theta}$ 只依赖极角 $\theta$，不依赖方位角 $\phi$（式13）；
2. **把方位角积分转化为复平面上的围道积分**：做变量代换 $z=e^{i\phi}$，$\phi$ 从 $0$ 到 $2\pi$ 的积分就变成沿单位圆 $|z|=1$ 的围道积分（式14-15）；
3. **用留数定理求出围道积分**：被积函数是 $z$ 的有理函数，在复平面上有5个极点（式16），其中恰好有一半落在单位圆内（具体哪些取决于 $x=\cos\theta$ 的取值），只有圆内的极点贡献留数；
4. **剩下对 $x$ 的积分是初等函数**：经过留数定理化简后，只剩对 $x\in[-1,1]$ 的积分，结果是三角函数、有理函数和**指数积分函数** $\mathrm{Ei}(z)$ 的组合（式17-18）。

这一套"选坐标系→复变换→留数定理"的流程，正是你**复现阶段要吃透、并在后续手征推广里原样复用的核心技术**。

**关键的可移植结论**：PRD 论文附录里证明了，一旦解出母函数 $I_1(\alpha,\hat s,\hat u,\hat v)$（对应终点-终点的贡献），另外三项 $I_2,I_3,I_4$（终点-起点、起点-终点、起点-起点的贡献）都可以通过简单的参数替换从 $I_1$ 得到（式21-23），不需要重新做积分。这是因为各向同性背景下，积分结果只依赖于矢量之间的**夹角**，与坐标系的具体朝向无关——这一点在你做手征推广时需要重新审视（见第5.4节），因为手征背景**不再是完全各向同性对称的**，坐标系的手性会在结果里留下痕迹。

**验证**：PRD 论文把这套精确解应用回 PTA 情形（令 $\alpha=0$），严格证明它退化为经典的 Hellings-Downs 曲线加上"脉冲星项"修正（式26-28），与之前不用短波近似的独立工作 [10] 完全一致，这是这篇论文最有说服力的自洽性检验。

---

## 3. 环节 B：手征引力波背景的数学形式——来自 JCAP 论文的物理设定

这一节完全建立在 JCAP 论文 [2] 上，目的是精确定义我们要推广到的"新物理对象"。

### 3.1 从线偏振基组到圆偏振基组

广义相对论允许的引力波只有两个张量偏振模式，通常取 $+,\times$ 线偏振基底 $e^+_{ab}(\hat n), e^\times_{ab}(\hat n)$。这两个基底可以像光学中一样重新线性组合成**左旋、右旋圆偏振基底**（JCAP 论文式2.3 [2]）：

$$e^R_{ab}(\hat k)=\frac{e^+_{ab}+ie^\times_{ab}}{\sqrt2},\qquad e^L_{ab}(\hat k)=\frac{e^+_{ab}-ie^\times_{ab}}{\sqrt2}$$

这和光学里从"水平/竖直线偏振"变换到"左旋/右旋圆偏振"的操作完全类似——只是这里的对象是自旋为 2 的引力场，而不是自旋为 1 的光子场。

### 3.2 Stokes 参数：I 和 V 的物理意义

仿照光学偏振理论（借用宇宙学中光子偏振分析的成熟语言 [11]），随机引力波背景的统计性质可以用类似 Stokes 参数的量描述。对一个**各向同性、平稳**的随机背景，两个圆偏振分量的功率谱满足（JCAP 论文式2.5-2.6 [2]）：

$$\langle\tilde h_\lambda(f,\hat k)\tilde h_{\lambda'}^*(f',\hat k')\rangle=\frac{1}{2}\delta(f-f')\frac{\delta^2(\hat k-\hat k')}{4\pi}\delta_{\lambda\lambda'}S_\lambda(f),\qquad \lambda,\lambda'=R,L$$

$$I(f)=\frac{1}{2}\big[S_R(f)+S_L(f)\big],\qquad V(f)=\frac{1}{2}\big[S_R(f)-S_L(f)\big]$$

- **$I(f)$**：左旋、右旋功率谱的**和**，就是我们熟悉的"总强度"，与能量密度谱的关系是 $\Omega_{GW}(f)=\dfrac{4\pi^2f^3}{3H_0^2}I(f)$；
- **$V(f)$**：左旋、右旋功率谱的**差**，描述的是"宇宙更偏爱产生哪种手性的引力波"，$V\neq0$ 直接对应**宇称破缈**。

如果用原始的 $+,\times$ 基组表示，这两个 Stokes 参数体现在关联矩阵的**对角/非对角结构**上（JCAP 论文式2.2 [2]）：

$$\begin{pmatrix}\langle\tilde h_+\tilde h_+^*\rangle&\langle\tilde h_+\tilde h_\times^*\rangle\\ \langle\tilde h_+^*\tilde h_\times\rangle&\langle\tilde h_\times\tilde h_\times^*\rangle\end{pmatrix}=\frac12\delta(f-f')\frac{\delta^2(\hat k-\hat k')}{4\pi}\begin{pmatrix}I(f)&-iV(f)\\ iV(f)&I(f)\end{pmatrix}$$

**这是全篇最关键的一个矩阵**——请牢记它的结构：

- **对角项**（$++$ 和 $\times\times$）都等于 $I(f)$：这是"强度"，$+$ 和 $\times$ 两个模式各贡献一半；
- **非对角项**（$+\times$ 和 $\times+$）是 $\mp iV(f)$：这是"手征"，只有当 $+$ 模式和 $\times$ 模式之间存在一个 $90°$ 的**相位关联**时才不为零。

普通"非偏振"的各向同性背景假设 $+,\times$ 两个模式统计独立、互不相关，对应 $V=0$，矩阵退化成单位阵乘以 $I(f)$。**手征背景的本质，就是在 $+,\times$ 两个模式之间人为引入一个非对角的虚数关联项**。

### 3.3 从关联矩阵到 ORF：对称与反对称的分野

把上面这个关联矩阵代入互相关公式的推导（这一步和环节A的式8完全类似，只是这次要同时处理 $I,V$ 两项），得到两个探测器的互相关信号里同时含有 $\Gamma^I$ 和 $\Gamma^V$ 两项贡献（JCAP 论文式2.9-2.10 [2]）：

$$\Gamma^I_{ij}(f)\equiv\frac34\sin\frac{2\pi fL_i}{c}\sin\frac{2\pi fL_j}{c}\,D_i^{ab}D_j^{cd}\int\frac{d^2\hat k}{4\pi}\Big[e^+_{ab}(\hat k)e^+_{cd}(\hat k)+e^\times_{ab}(\hat k)e^\times_{cd}(\hat k)\Big]e^{-i2\pi f\hat k\cdot\Delta\vec r/c}$$

$$\Gamma^V_{ij}(f)\equiv-i\frac34\sin\frac{2\pi fL_i}{c}\sin\frac{2\pi fL_j}{c}\,D_i^{ab}D_j^{cd}\int\frac{d^2\hat k}{4\pi}\Big[e^+_{ab}(\hat k)e^\times_{cd}(\hat k)-e^\times_{ab}(\hat k)e^+_{cd}(\hat k)\Big]e^{-i2\pi f\hat k\cdot\Delta\vec r/c}$$

对比这两个式子，**两者的差别只在方括号里**：

| | 方括号内的组合 | 对应关系 |
|---|---|---|
| $\Gamma^I$ | $e^+e^++e^\times e^\times$（**对称**求和） | 与环节A中 PRD 论文的 $\xi(\hat n)$ 结构完全一致 |
| $\Gamma^V$ | $e^+e^\times-e^\times e^+$（**反对称**求差） | PRD 论文里**从未出现过**的新组合 |

**这正是我们整个课题的数学突破口**：$\Gamma^I$ 的被积函数结构，和 PRD 论文里已经精确解出来的对象一模一样；$\Gamma^V$ 只是把"对称组合"换成了"反对称组合"，坐标系选取、变量代换、留数定理的**框架完全可以照搬**，需要重新计算的只是这个反对称组合在新坐标系下展开后的具体系数。

### 3.4 一个重要的几何直觉：为什么手征探测必须"打破镜面对称"

在深入计算之前，有一个物理直觉必须先建立，它能帮你判断"什么时候算出来的 $\Gamma^V$ 应该是零"，从而在推导出错时能立刻发现问题。

**定理（Seto 2007 [12]；Kato & Soda 2016 [13]）**：对于各向同性的随机引力波背景，**单个平面探测器（不管是地基L形，还是LISA这种共面三角形）测不到净的圆偏振信号**。

直觉证明：假设整个探测器构型关于某个镜面对称。做一次镜面反射，探测器构型不变，但**左旋波和右旋波会互相交换**（这是圆偏振在宇称变换下的基本性质，类似光学中偏振光经过镜子反射后旋向反转）。既然构型不变、而信号的左右旋互换，若 $\Gamma^V\ne0$ 会导致互相关结果在镜像前后不一致，这与"构型不变则结果不变"矛盾，所以必须 $\Gamma^V=0$。

**推论**：要测到 $V$，探测器网络必须**不具有镜面对称性**，最直接的办法是让两个探测器"不共面"——JCAP 论文正是研究把 LISA 和 Taiji 的轨道面**倾斜成不同角度**，人为打破镜面对称，从而"打开" $\Gamma^V$ 通道 [2]。

这个几何直觉直接决定了后面第4节里为什么"PTA 测不到 V"、以及第5节里我们做手征 ORF 推导时应该期待什么样的张量结构（一定会牵涉到**列维-奇维塔符号** $\epsilon_{abc}$，因为这是唯一能构造出"手性/赝标量"效应的几何工具）。

---

## 4. 环节 C：两个具体例子，把抽象公式落到实处

理论框架讲完了，用两个已经被别人算过的具体例子，检验你对上面两节的理解是否到位。这两个例子也是你后续推导手征 ORF 精确公式时用来做"退化检验"的标准答案。

### 4.1 例子一：PTA 为什么天生对手征"色盲"

这是一个漂亮的**解析可证明**的零结果，来自 Kato & Soda [13] 和后续 Belgacem & Kamionkowski 的工作 [14]，最近一篇 2026 年的论文用更直接的方式重新证明了它 [15]。

PTA 里一对脉冲星对应"两条共享终点（地球）的单向链路"（这和环节A里 PRD 论文对 PTA 的刻画完全一致，$\alpha=0$）。选取坐标系使脉冲星方向 $\hat p_a=(0,0,1)$，$\hat p_b=(\sin\alpha,0,\cos\alpha)$，可以证明手征 ORF 的被积函数中出现一个因子：

$$\Theta(\phi,\theta)\equiv\frac{\sin\alpha(\cos\alpha\sin\theta-\sin\alpha\cos\theta\cos\phi)}{1+\sin\alpha\sin\theta\cos\phi+\cos\alpha\cos\theta}$$

这个 $\Theta$ 关于方位角 $\phi$ 是**偶函数**，而手征贡献需要对 $\phi$ 积分一个奇函数（正弦型）分量，两者相乘后对 $\phi\in[0,2\pi]$ 积分**恒为零** [15]。

**物理解释**：一对脉冲星和地球构成的几何图形，是一个**共面**的等腰三角形（两条链路共享一个顶点），天然具有镜面对称性（关于两脉冲星连线的中垂面对称）。根据 3.4 节的定理，这样的构型测不到各向同性背景的 $V$ 分量。**这与环节A中"$\alpha=0$ 退化为 Hellings-Downs 曲线"的推导是同一个几何设定**——只是那里算的是 $\Gamma^I$（不为零），这里算的是 $\Gamma^V$（严格为零）。这个对比能帮你直观理解"强度 ORF" 和"手征 ORF" 在同一构型下可以有完全不同的命运。

### 4.2 例子二：LISA-Taiji 网络，长波近似下的 $\Gamma^V$

这是 JCAP 论文的主体计算，展示了"打破镜面对称"之后 $\Gamma^V$ 如何从零变为非零。

具体做法（JCAP 论文附录B [2]）：定义分离方向 $\hat s\equiv-\Delta\vec r/\Delta r$ 和相位 $\iota\equiv2\pi f\Delta r/c$，利用**张量对称性**（而不是直接暴力积分）来求解。因为 $\Gamma^V_{abcd}(\iota,\hat s)$ 必须是：
- 关于 $a\leftrightarrow b$、$c\leftrightarrow d$ **对称**；
- 关于整体交换 $ab\leftrightarrow cd$ **反对称**（这是宇称奇的关键特征）；
- 关于 $ab$、$cd$ 两组指标各自**无迹**；

在此约束下，唯一能构造出的张量基底必须借助**列维-奇维塔张量构造的"手性算符"** $w_{bd}\equiv\epsilon_{abc}s^c$（式B.19 [2]）：

$$\Gamma^V_{abcd}(\iota,\hat s)=F(\iota)(\delta_{ab}s_cs_d-\delta_{cd}s_as_b)+G(\iota)(w_{ac}\delta_{bd}+\cdots)+H(\iota)(w_{ac}s_bs_d+\cdots)$$

把这个待定形式代入原始球面积分定义、和三个特定的张量收缩方向做匹配，最终解出（式B.22-B.23 [2]）：

$$F(\iota)=0,\qquad \begin{pmatrix}G\\H\end{pmatrix}=\frac54\begin{pmatrix}1&-1\\-1&5\end{pmatrix}\begin{pmatrix}j_1(\iota)\\\iota^{-1}j_2(\iota)\end{pmatrix}$$

其中 $j_1,j_2$ 是**球贝塞尔函数**。这个解法的核心技巧值得记住：**不直接暴力算球面积分，而是先用对称性约束"猜"出解的一般形式（几个待定系数乘以基底张量），再用几次简单的收缩运算把积分问题转化成解一个小型线性方程组**。这是一个和"留数定理"完全不同、但同样巧妙的技巧，PRD 论文没有用到它，但它在你第5节的推导中会作为一个重要的**验证工具**出现（长波极限下，你的精确解应该退化到这里的 $F,G,H$）。

用这套长波近似公式，JCAP 论文进一步算出了 LISA-Taiji 网络的 SNR 灵敏度（式2.12-2.13 [2]），发现调整 Taiji 轨道面倾角（从 $+60°$ 变到 $-60°$），可以让 $V$ 分量的低频灵敏度提升近一个数量级 [2]，这与更早的 Orlando-Pieroni-Ricciardone 论文 [16] 的结论一致、互相印证。

---

## 5. 组合环节：手征情况下精确 ORF 的推导蓝图

这是整份文档承上启下的核心——把环节A的"精确积分技术"，套到环节B定义的"手征物理对象"上，用环节C的两个例子作为验证的锚点。

### 5.1 问题的精确重新表述

仿照 PRD 论文的思路，我们要证明：**手征 ORF $\Gamma^V_{IJ}$ 同样可以分解成"两条一般单向链路之间的手征 ORF"$\Gamma^V_{\rm one}$ 的线性组合**，然后精确解出这个 $\Gamma^V_{\rm one}$ 母函数。

第一步是纯粹的**代数**：JCAP 论文的探测器张量 $D^{ab}_i$ 本质上是"两条臂的响应函数之差"（式2.7 [2]），而每条臂又能拆成 PRD 论文意义下的单向链路——这一步复用 PRD 论文附录里"任意 TDI 通道分解为6条单向链路组合"的现成结果 [1]，不需要重新推导。

第二步才是真正的**硬骨头**：定义手征版本的母函数——

$$\Gamma^V_{\rm one}(\alpha,\beta_u,\beta_v,\hat s,\hat u,\hat v)\equiv\frac{-i}{32\pi}\int d^2\Omega_{\hat n}\,\kappa_{IJ}(\hat n)\,e^{-i\alpha\hat n\cdot\hat s}\left[\frac{e^+_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^\times_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}-\frac{e^\times_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^+_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\right]$$

对比 PRD 论文式10 定义的 $\Gamma_{\rm one}$（环节A），**积分外层结构（$\kappa_{IJ}(\hat n)$、相位因子 $e^{-i\alpha\hat n\cdot\hat s}$、分母上的 $1+\hat n\cdot\hat u$ 等）完全一致**，唯一的区别就是方括号里从"$++,\times\times$ 对称求和"换成了"$+\times,\times+$ 反对称求差"。

### 5.2 具体该怎么改：逐步对照 PRD 论文的推导

把 PRD 论文附录A的推导过程，逐步替换成手征版本：

**Step 1 —— 重新定义被积核函数。** PRD 论文式12 定义了

$$\xi_I(\hat n)=\sum_{A=+,\times}\frac{e^A_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^A_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}$$

我们需要构造对应的反对称版本：

$$\xi_V(\hat n)=\frac{e^+_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^\times_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}-\frac{e^\times_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^+_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}$$

**Step 2 —— 坐标系选取完全复用。** PRD 论文选 $\hat s=(0,0,1)$、$\hat u=(u_x,0,u_z)$ 在 $x$-$z$ 平面内（式13）。这个选取只依赖于 $\hat s,\hat u,\hat v$ 三个矢量的相对几何关系，**与被积函数是对称还是反对称无关**，可以原样保留。

**Step 3 —— 展开 $\xi_V(\hat n)$ 到 $(\theta,\phi)$ 坐标，此处开始产生分歧。** PRD 论文附录A式A2-A3 把 $\hat\theta\cdot\hat u,\hat\phi\cdot\hat u$ 等内积用 $(\theta,\phi)$ 显式表示出来，代入 $\xi_I$ 后得到一个关于 $\phi$ 的三角多项式。**这一步需要重新做**：把同样的内积表达式代入 $\xi_V$ 的反对称组合，你会得到一个**不同的 $\phi$ 依赖结构**——根据 3.3 节的分析，$\Gamma^I$ 对应的三角函数组合是关于 $\phi$ 的**偶函数占主导**，而 $\Gamma^V$ 由于反对称性，很可能是**奇函数（正弦型）占主导**的结构（这与 4.1 节 PTA 例子里 "$\Theta(\phi,\theta)$ 是偶函数、因此手征积分为零"的现象是同一机制的另一面——在 PTA 的退化情形里奇函数积分后消失，但在一般的非共面构型下，奇函数部分不会自动消失）。

**Step 4 —— 变量代换与留数定理，框架照搬，极点位置不变。** 做 $x=\cos\theta,z=e^{i\phi}$ 代换后，围道积分的**被积函数的极点位置完全由 $\hat u,\hat v$ 的方向决定**（PRD论文式16 给出的 $z_0,\ldots,z_4$ 公式对 $\xi_I$ 和 $\xi_V$ 应该是通用的，因为极点来自分母 $(1+\hat n\cdot\hat u)(1+\hat n\cdot\hat v)$ 在复平面上的零点，这一结构在两种情形下相同）。**需要重新计算的是每个极点处的留数值**（因为分子 $\xi_V$ 变了）。

**Step 5 —— 对 $x$ 积分，可能出现新的特殊函数组合。** PRD 论文对 $\xi_I$ 情形算出的结果里出现了指数积分函数 $\mathrm{Ei}(z)$（式18）。由于 $\xi_V$ 的留数在代数结构上会不同（很可能会多出奇数次幂的 $x$ 依赖项，这是反对称性的直接体现），最终对 $x$ 积分后，**可能出现新的特殊函数组合，也可能奇迹般地simplify为更简单的三角函数/贝塞尔函数形式**（这在 4.2 节的长波近似例子里已经看到端倪——$\Gamma^V$ 的展开只需要 $j_1,j_2$ 两个球贝塞尔函数，比 $\Gamma^I$ 需要的 $j_0,j_1,j_2$ 少一个，暗示了手征情形的积分结构可能有某种简化）。

### 5.3 一个关键的物理/数学检查点：各向同性假设是否还成立

PRD 论文能够"直接替换角度参数、不用重新做积分"（环节A提到的 $I_2,I_3,I_4$ 通过参数替换从 $I_1$ 得到）的根本原因，是论文明确指出的："我们计算的是各向同性 SGWB 的 ORF，结果应该在计算坐标系的旋转下不变"（原文："the result should be invariant under the rotation of the computational frame" [1]）。

但是，**手征背景虽然仍然是各向同性的（$V(f)$ 不依赖方向），却不是"手性中性"的**——一次**普通旋转**（行列式为 $+1$）不会改变 $\Gamma^V$（因为旋转不改变手性），但一次**镜面反射**（行列式为 $-1$，即所谓"瑕旋转"）会把 $\Gamma^V$ 变号（这正是 3.4 节定理的数学根源）。所以在推导中，PRD 论文里那句"结果与坐标系朝向无关"的论证，在手征情形下需要**加一个限定条件**：结果在旋转下不变，但在镜面反射下会**反号**——这个反号性质恰好是整个 $\epsilon_{abc}$ 结构的来源，也是 5.2 节 Step 3-5 里"重新计算"不能偷懒省略的原因。

**建议的做法**：在实际推导中，先验证你算出的 $\Gamma^V_{\rm one}$ 表达式中，是否自然地含有一个正比于 $\hat u\times\hat v\cdot\hat s$（标量三重积，是旋转不变但反射变号的赝标量）的因子——如果有，说明你的推导抓住了手征的几何本质；如果没有，说明某处的对称性处理有误。

### 5.4 推导完成后的三重验证

参照 PRD 论文的自洽性检验思路（环节A提到的"退化为 Hellings-Downs 曲线"），你的精确 $\Gamma^V_{\rm one}$ 公式至少要通过三个独立检验：

1. **PTA 极限**（$\alpha\to0$，两条链路共享终点）：应该严格退化为**零**，重现 4.1 节 Kato-Soda / dPTA 论文的解析证明 [13,15]；
2. **长波近似极限**（$\beta_u,\beta_v\ll1$）：应该退化为 JCAP 论文附录B 给出的 $F(\iota)=0$、$G,H$ 由 $j_1,j_2$ 给出的结果（4.2 节）[2]；
3. **数值积分交叉验证**：对任意给定的 $\alpha,\beta_u,\beta_v,\hat u,\hat v,\hat s$，直接对定义式做球面数值积分，和你的解析公式比对（这正是 PRD 论文 Table I 采用的验证方式 [1]）。

### 5.5 推导完成之后，回到应用场景

一旦精确的 $\Gamma^V_{\rm one}$ 母函数解出来，后续的应用是"体力活"而非"技术活"，可以按下面的顺序展开（这一步的取舍需要和张老师、宝屿师兄讨论决定，见第8节）：

- 把它代入 OLC 探测器网络（楼同学论文的框架），得到 OLC-OLC 手征 ORF 的精确解；
- 把它代入 LISA-Taiji 的 TDI 通道组合（复用 PRD 论文和 JCAP 论文都用到的"单向链路线性组合"分解法），直接对标、改进 JCAP 论文的高频段结果；
- 代入 JCAP 论文式2.12-2.13 的 SNR/有效ORF框架，重新画一版"精确 vs 长波近似"的灵敏度对比图，直接类比 PRD 论文 Fig. 5/6 展示小天线近似偏差的做法 [1]。

---

## 6. 模块间衔接逻辑总览（类比一以贯之）

为了让你在推导中途不迷失方向，这里用**同一个类比**贯穿全篇，帮助记忆各模块的角色：

> **把整个问题类比成"两个人听同一处鼓声"**：
>
> - **环节A（ORF）**回答的是"两人听到的鼓声有多大程度上同步"，这个同步程度是一个只依赖于两人相对位置、朝向的函数——这就是 ORF。PRD 论文教会我们**用留数定理精确算出**这个同步程度，不管两人距离鼓声源多近多远（不做"远场近似"）。
>
> - **环节B（手征）**问的是一个新问题：如果这面"鼓"不是普通的鼓，而是一面**会左右手性震动的锣**（左旋敲击和右旋敲击的强度可能不一样），两人听到的信号里除了"整体响度是否同步"（对应 $I$），还多了一个新维度——"两人是否都能分辨出这面锣更偏向哪种手性敲击"（对应 $V$）。JCAP 论文告诉我们，**只有站得"不对称"（不共面）的两人才能分辨出这种手性**，并给出了一个"站得比较近"（长波近似）时的计算方法。
>
> - **环节C（例子）**用两个具体站位来验证上面的直觉：PTA 的"两人共享同一个参照点"站位，天生对称，分辨不出手性（$V=0$）；LISA-Taiji 的"两个不共面的三角站位"，则可以分辨出一部分手性，但现有算法只在"站得比较近"时准。
>
> - **组合环节（第5章）**要做的，就是把 PRD 论文"不管站多远都能精确算出同步程度"的本事，用到"分辨手性"这个新问题上——不管两人站多远，都能精确算出他们能分辨出多少手性信息。

---

## 7. 参考文献（附简短说明，方便回查）

| 编号 | 文献 | 在本文档中的作用 |
|---|---|---|
| [1] | Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Universal calculation approach of overlap reduction function for pulsar timing array and laser interferometer detector*, Phys. Rev. D **111**, 084065 (2025). | **PRD 底稿论文**：环节A的全部数学框架（单向链路分解、留数定理精确积分）来源 |
| [2] | J. Chen, C. Liu, Y.-L. Zhang, *Circularly Polarized Gravitational Wave Background Search with a Network of Space-borne Triangular Detectors*, JCAP **05**, 050 (2025), [arXiv:2410.18916](https://arxiv.org/abs/2410.18916) | **JCAP 底稿论文**：环节B、C(4.2节)的手征物理设定、长波近似解法来源 |
| [3] | B. Allen, J. D. Romano, *Detecting a stochastic background of gravitational radiation: Signal processing strategies and sensitivities*, Phys. Rev. D **59**, 102001 (1999) | 互相关探测随机背景方法的奠基性文献，环节A 2.1节引用 |
| [4] | J. D. Romano, N. J. Cornish, *Detection methods for stochastic gravitational-wave backgrounds: A unified treatment*, Living Rev. Relativity **20**, 2 (2017) | ORF/SNR 分析的标准综述，JCAP 论文 SNR 公式的方法来源 |
| [5] | R. W. Hellings, G. S. Downs, *Upper limits on the isotropic gravitational radiation background from pulsar timing analysis*, Astrophys. J. Lett. **265**, L39 (1983) | Hellings-Downs 曲线的原始文献，环节A 2.3节 PTA 短波近似 |
| [6] | E. E. Flanagan, *The sensitivity of LIGO to a stochastic background, and its dependence on the detector orientations*, Phys. Rev. D **48**, 2389 (1993) | 地基探测器小天线近似 ORF 解析解，环节A 2.3节；也是JCAP论文附录B张量分解法的方法来源 |
| [7] | B. Allen, J. D. Romano (同[3]) | 同上，地基小天线近似 |
| [8] | M. Tinto, J. W. Armstrong, *Cancellation of laser noise in an unequal-arm interferometer detector of gravitational radiation*, Phys. Rev. D **59**, 102003 (1999) | TDI 技术基础，环节A 2.3节天基探测器 |
| [9] | J. W. Armstrong, F. B. Estabrook, M. Tinto, *Time-delay interferometry for space-based gravitational wave searches*, Astrophys. J. **527**, 814 (1999) | 同上 |
| [10] | Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Full analytic expression of overlap reduction function for gravitational wave background with pulsar timing arrays*, Phys. Rev. D **106**, 024005 (2022) | PRD论文用于验证PTA退化结果一致性的前作 |
| [11] | 参见宇宙学中 CMB 偏振的 Stokes 参数处理方法，如标准教材/综述 | JCAP 论文 Stokes I,V 定义的方法论借鉴来源，环节B 3.2节 |
| [12] | N. Seto, *Quest for circular polarization of gravitational wave background and orbits of laser interferometers in space*, Phys. Rev. D **75**, 061302 (2007) | "单平面探测器测不到各向同性V"定理的早期文献之一，环节B 3.4节 |
| [13] | R. Kato, J. Soda, *Probing circular polarization in stochastic gravitational wave background with pulsar timing arrays*, Phys. Rev. D **93**, 062003 (2016) | PTA对各向同性V不敏感的证明，环节C 4.1节核心引用 |
| [14] | E. Belgacem, M. Kamionkowski, *Chirality of the gravitational-wave background and pulsar-timing arrays*, Phys. Rev. D **102**, 023004 (2020) | 同上主题的后续/独立工作 |
| [15] | (2026年新作) *Detecting Chiral Gravitational Wave Background with a Dipole Pulsar Timing Array*, arXiv:2604.08141 | 用更直接的方式重新证明PTA对V的零响应，并提出dPTA方案，环节C 4.1节 |
| [16] | G. Orlando, M. Pieroni, A. Ricciardone, *Measuring Parity Violation in the Stochastic Gravitational Wave Background with the LISA-Taiji network*, JCAP **03**, 069 (2021) | 与JCAP论文互相印证的独立工作，环节C 4.2节 |

---

## 8. 下一步行动清单（建议每周讨论时对照检查）

- [ ] **复现阶段**：手推 PRD 论文式(9)-(24)，用符号计算工具（Mathematica/SymPy）核对留数计算的每一步中间结果，并用直接数值积分验证 PTA/GbLI/SbLI 三种极限（对应论文 Table I）。
- [ ] **物理设定确认**：精读 JCAP 论文 Appendix B 全文，手推 $\Gamma^I_{abcd}$、$\Gamma^V_{abcd}$ 张量分解的线性方程组求解过程（式B.6, B.14, B.18, B.20, B.23），确保理解"对称/无迹张量基底展开"这一独立于留数定理的解法思路。
- [ ] **推导阶段**：按第5.2节 Step 1-5 逐步推导 $\Gamma^V_{\rm one}$，重点关注 Step 3（$\phi$ 依赖结构变化）和 Step 5（是否出现新的特殊函数）。
- [ ] **验证阶段**：完成第5.4节的三重验证（PTA极限为零、长波近似退化到JCAP结果、数值积分交叉核对）。
- [ ] **与老师/师兄讨论的开放问题**（建议下次讨论时提出）：
  1. 目标应用场景优先做哪个——OLC网络、还是直接对标JCAP论文改进LISA-Taiji的高频结果？（见第1.2节、第5.5节）
  2. 是否要在本篇工作中一并覆盖各向异性+手征耦合的情形，还是先限定在各向同性背景内？（JCAP论文因为Q,U是自旋4量、不贡献单极项而略去，这个简化在本篇是否延用？）
  3. 精确解出来后，是否需要重新做一版JCAP论文式2.12-2.13的SNR/灵敏度预测图？这部分工作量如何分配？
