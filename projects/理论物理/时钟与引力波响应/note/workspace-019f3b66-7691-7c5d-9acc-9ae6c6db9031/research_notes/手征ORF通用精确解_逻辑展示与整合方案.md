# 手征引力波背景 ORF 的"通法"整合方案 —— 逐条对照原文公式的完整推导

> **本文档的目的**：把 PRD 论文（Hu et al. 2025, [1]）和 JCAP 论文（Chen, Liu, Zhang 2025, [2]）各自的完整逻辑链条摊开、逐一标出原文公式编号，然后在此基础上给出把两者拼接成"手征ORF通法"的具体整合方案。所有公式后面括号内的 `(式X)` 均指对应论文里的原始编号，方便你直接翻书/翻PDF核对。

---

## 第一部分：PRD 论文的完整逻辑链（"通法"从何而来）

### 1.1 出发点：随机背景如何在探测器里产生信号

PRD 论文从最基础的度规扰动展开式出发。任意随机引力波背景可以写成对所有方向、所有频率平面波的叠加（[1] 式1）：

$$h_{ab}(t,\vec x)=\int_{-\infty}^{\infty}df\int d^2\Omega_{\hat n}\sum_A \tilde h_A(f,\hat n)\,e^A_{ab}(\hat n)\,e^{i2\pi f(t+\hat n\cdot\vec x/c)}$$

对于**各向同性、无偏振、平稳**的背景，傅里叶振幅的自关联满足（[1] 式4）：

$$\langle h_A(f,\hat n)h_{A'}^*(f',\hat n')\rangle=\frac{1}{16\pi}S_h(f)\,\delta(f-f')\,\delta_{AA'}\,\delta^2(\hat n,\hat n')$$

**这里请特别记住这个 $\delta_{AA'}$**——它规定了 $+$ 模式和 $\times$ 模式之间统计独立、互不相关。这是"非偏振"假设的数学定义，也是本文档第三部分要突破的关键点。

探测器对该背景的响应，是响应函数 $R^A_I(f,\hat n)$ 与随机振幅的卷积（[1] 式5）：

$$h_I(t)=\int df\int d^2\Omega_{\hat n}\sum_A R_I^A(f,\hat n)\,\tilde h_A(f,\hat n)\,e^{i2\pi ft}$$

三类探测器（PTA、地基GbLI、天基SbLI）的响应函数被统一写成同一种数学结构（[1] 式6）：

$$R_{\rm PTA}^A(f,\hat n)=\frac12 e^A_{ab}(\hat n)u^au^b\,\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)\,e^{i2\pi f\hat n\cdot\vec r/c}$$
$$R_{\rm GbLI}^A(f,\hat n)=\frac12 e^A_{ab}(\hat n)\big[u_1^au_1^b\,\mathcal T_{\rm two}(\beta,\hat n\cdot\hat u_1)-u_2^au_2^b\,\mathcal T_{\rm two}(\beta,\hat n\cdot\hat u_2)\big]\,e^{i2\pi f\hat n\cdot\vec r/c}$$
$$R_{\rm SbLI}^A(f,\hat n)=\frac12 e^A_{ab}(\hat n)\sum_i P_i\,u_i^au_i^b\,\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u_i)\,e^{i2\pi f\hat n\cdot\vec r_i/c}$$

其中单向链路传递函数是（[1] 式6附近）：

$$\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)=\frac{1}{1+\hat n\cdot\hat u}\big[1-e^{-i\beta(1+\hat n\cdot\hat u)}\big],\qquad \beta=2\pi fL/c$$

**这一步是全篇论文最关键的洞察**：不管是脉冲星（PTA）、地基探测器（GbLI）还是天基三角探测器（SbLI），它们的响应函数**在数学结构上完全相同**——都是"某个方向向量 $\hat u$ 与偏振基张量收缩、再乘以一个和传递函数相关的相位因子"的线性组合，区别只在于组合系数（$1$、$\pm1$、或 TDI 系数 $P_i$）和传递函数是单程还是往返。

### 1.2 ORF 的定义与"分解为单向链路"的策略

两个探测器的互相关信号由（[1] 式7）：

$$\langle h_I(t)h_J(t')\rangle=\frac12\int df\int d^2\Omega_{\hat n}\,\Gamma_{IJ}(f)\,S_h(f)\,e^{i2\pi f(t-t')}$$

给出，其中 ORF 的定义是（[1] 式8）：

$$\Gamma_{IJ}(f)=\frac{1}{8\pi}\int d^2\Omega_{\hat n}\sum_{A=+,\times}R_I^A(f,\hat n)\,R_J^{A*}(f,\hat n)$$

由于第1.1节已经证明**任何探测器的响应函数都能写成若干条"单向链路" $\{\vec r_u, L_u\hat u\}$ 响应函数的线性叠加**，那么由分配律，任意两个探测器的 ORF 也能分解为"两条一般单向链路之间ORF"的线性组合。所以**核心任务被压缩为：只需要精确解出这一个"母函数"**——两条一般单向链路 $\{\vec r_u,L_u\hat u\}$ 与 $\{\vec r_v,L_v\hat v\}$ 之间的ORF：

$$\Gamma_{\rm one}(\alpha,\beta_u,\beta_v,\hat s,\hat u,\hat v)=\frac{1}{32\pi}\int d^2\Omega_{\hat n}\,\kappa_{IJ}(\hat n)\,e^{-i\alpha\hat n\cdot\hat s}\sum_{A=+,\times}\frac{e^A_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^A_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\tag{[1]式10}$$

其中 $\kappa_{IJ}(\hat n)=[1-e^{-i\beta_u(1+\hat n\cdot\hat u)}][1-e^{i\beta_v(1+\hat n\cdot\hat v)}]$，$\alpha=2\pi f\Delta L/c$（[1] 式10附近）。

**这是"通法"这个词的确切含义**：只要把 $\Gamma_{\rm one}$ 这一个函数精确解出来，PTA、地基、天基三类探测器的任意组合 ORF 都能通过线性叠加立刻得到，不需要为每种探测器单独发明近似方法。

### 1.3 求解 $\Gamma_{\rm one}$ 的三步技巧（这是"精确"二字的来源）

**Step 1：拆成四个积分。** 把 $\kappa_{IJ}(\hat n)$ 展开后，$\Gamma_{\rm one}$ 拆成四项 $I_1,I_2,I_3,I_4$（[1] 式11）：

$$I_1=\int d^2\Omega_{\hat n}\,\xi(\hat n)\,e^{-i\alpha\hat n\cdot\hat s},\qquad \xi(\hat n)\equiv\sum_{A=+,\times}\frac{e^A_{ab}u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^A_{cd}v^cv^d}{1+\hat n\cdot\hat v}\tag{[1]式12}$$

$I_2,I_3,I_4$ 结构类似，只是多乘了 $e^{\mp i\beta_u(1+\hat n\cdot\hat u)}$ 或 $e^{\pm i\beta_v(1+\hat n\cdot\hat v)}$ 这样的额外相位（[1] 式11）。

**Step 2：选坐标系，把方位角积分转化为复围道积分。** 取 $z$ 轴与分离方向 $\hat s$ 对齐，$\hat u$ 在 $x$-$z$ 平面内（[1] 式13）：

$$\hat s=(0,0,1),\quad\hat u=(u_x,0,u_z),\quad \hat v=(v_x,v_y,v_z)$$

这样 $\hat n\cdot\hat s=\cos\theta$ 不依赖方位角 $\phi$，$I_1$ 变成（[1] 式14）：

$$I_1=\int_0^\pi d\theta\sin\theta\,e^{-i\alpha\cos\theta}\int_0^{2\pi}d\phi\,\xi(\theta,\phi)$$

再做变量代换 $x=\cos\theta$，$z=e^{i\phi}$，方位角积分变成复平面上**沿单位圆的围道积分**（[1] 式15）：

$$I_1=\int_{-1}^1 dx\,e^{-i\alpha x}\oint_{|z|=1}dz\,\frac{1}{iz}\xi(x,z)$$

**Step 3：用留数定理求出围道积分。** 被积函数 $f(z)=\frac{1}{iz}\xi(x,z)$ 在复平面上共有5个极点（[1] 式16）：

$$z_0=0,\quad z_1=-\frac{(1+u_z)(1+x)}{u_x\sqrt{1-x^2}},\quad z_2=-\frac{(1-u_z)(1-x)}{u_x\sqrt{1-x^2}}$$
$$z_3=-\frac{(1+v_z)(1+x)}{(v_x-iv_y)\sqrt{1-x^2}},\quad z_4=-\frac{(1-v_z)(1-x)}{(v_x-iv_y)\sqrt{1-x^2}}$$

其中 $z_1,z_2$ 中恰好只有一个落在单位圆内（取决于 $x$ 与 $-\cos\delta_u$ 的大小关系），$z_3,z_4$ 同理（[1] 式16附近）。只有圆内极点贡献留数，积分变成对 $x\in[-1,1]$ 的**分段积分**（[1] 式17）：

$$I_1=2\pi i\Big[\int_{-1}^1 dx\,e^{-i\alpha x}R_0(x)+\int_{-1}^{-\cos\delta_u}\!\!dx\,e^{-i\alpha x}R_1(x)+\int_{-\cos\delta_u}^{1}\!\!dx\,e^{-i\alpha x}R_2(x)+\cdots\Big]$$

对 $x$ 的积分是初等函数，最终得到含有**三角函数、有理式和指数积分函数 $\mathrm{Ei}(z)$** 的封闭解析式（[1] 式18，完整表达式见原文，此处从略）。

**关键的可复用结论**：一旦 $I_1(\alpha,\hat s,\hat u,\hat v)$ 解出，$I_2,I_3,I_4$ 不需要重新做积分，只需要通过矢量替换即可得到（[1] 式19-23）：

$$I_2(\alpha,\beta_u,\hat s,\hat u,\hat v)=-e^{-i\beta_u}I_1(\alpha_2,\hat s_2,\hat u,\hat v),\quad \alpha_2\hat s_2\equiv\alpha\hat s+\beta_u\hat u$$

这是因为**各向同性背景下，积分结果只依赖矢量间夹角，不依赖坐标系的具体朝向**（[1] 原文明确写道"the result should be invariant under the rotation of the computational frame"）。最终完整的母函数是四项之和（[1] 式24）：

$$\Gamma_{\rm one}=\frac{1}{32\pi}\Big[I_1(\alpha,\hat s,\hat u,\hat v)-e^{-i\beta_u}I_1(\alpha_2,\hat s_2,\hat u,\hat v)-e^{i\beta_v}I_1(\alpha_3,\hat s_3,\hat u,\hat v)+e^{i(\beta_v-\beta_u)}I_1(\alpha_4,\hat s_4,\hat u,\hat v)\Big]$$

### 1.4 验证：退化到 Hellings-Downs 曲线

对 PTA（$\alpha=0$，两条链路共享终点），把式24代入并令 $\alpha\to0$，PRD 论文证明这精确退化为经典的 Hellings-Downs 曲线加脉冲星项修正（[1] 式26-28），与不用短波近似的独立前作 [3] 完全吻合。**这是 PRD 论文"精确"这一声明最有力的自洽性检验。**

---

## 第二部分：JCAP 论文的完整逻辑链（手征物理是怎么定义、怎么算的）

### 2.1 从"非偏振"假设到"手征"假设——唯一的物理修改点

JCAP 论文的随机背景展开式和 PRD 论文式1 结构相同（[2] 式2.1）：

$$h_{ab}(t,\vec r)=\sum_{P=+,\times}\int_{-\infty}^\infty df\int d^2\hat k\,\tilde h_P(f,\hat k)\,e^P_{ab}(\hat k)\,e^{i2\pi f(t-\hat k\cdot\vec r/c)}$$

但傅里叶振幅的关联矩阵，**不再是对角的**（[2] 式2.2）：

$$\begin{pmatrix}\langle\tilde h_+\tilde h_+^*\rangle&\langle\tilde h_+\tilde h_\times^*\rangle\\\langle\tilde h_+^*\tilde h_\times\rangle&\langle\tilde h_\times\tilde h_\times^*\rangle\end{pmatrix}=\frac12\delta(f-f')\frac{\delta^2(\hat k-\hat k')}{4\pi}\begin{pmatrix}I(f)&-iV(f)\\iV(f)&I(f)\end{pmatrix}$$

**这正是本文档要强调的核心对照点**：PRD 论文式4 里那个 $\delta_{AA'}$（对角、非对角项为零）在 JCAP 论文里被替换成一个**非对角虚数项** $\mp iV(f)$。$I(f)$ 是强度（对角项，两个模式贡献相等），$V(f)$ 是手征（非对角项，描述 $+,\times$ 两模式之间的相位关联）。

引入圆偏振基组后（[2] 式2.3-2.4）：

$$e^R_{ab}=\frac{e^+_{ab}+ie^\times_{ab}}{\sqrt2},\quad e^L_{ab}=\frac{e^+_{ab}-ie^\times_{ab}}{\sqrt2};\qquad h_R=\frac{h_+-ih_\times}{\sqrt2},\quad h_L=\frac{h_++ih_\times}{\sqrt2}$$

关联矩阵在圆偏振基下变成对角形式（[2] 式2.5-2.6）：

$$\langle\tilde h_\lambda\tilde h_{\lambda'}^*\rangle=\frac12\delta(f-f')\frac{\delta^2(\hat k-\hat k')}{4\pi}\delta_{\lambda\lambda'}S_\lambda(f),\quad I=\frac12(S_R+S_L),\ V=\frac12(S_R-S_L)$$

这解释了 $I,V$ 的物理意义：$I$ 是左右旋强度之和（普通强度），$V$ 是左右旋强度之差（净手性）。

### 2.2 探测器响应与两个ORF的定义

天基三角探测器（LISA型）的响应（在长波近似下，臂长 $L\ll$ 波长）为（[2] 式2.7）：

$$\tilde s(f)=\frac{\sqrt3}{2}\sin\frac{2\pi fL}{c}\,D^{ab}\tilde h_{ab}(f,\vec r)$$

**注意**：这里 $D^{ab}$ 是一个**频率无关的静态探测器张量**（附录A给出具体形式），这正是"长波近似"的数学体现——PRD论文用的传递函数 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)$ 是频率、方向都依赖的精确表达式，而这里只保留了 $\sin(2\pi fL/c)$ 这个总体幅度因子，方向依赖性被简化掉了。

两个探测器（或TDI通道）$i,j$ 的互相关信号是（[2] 式2.9）：

$$\langle\tilde s_i(f)\tilde s_j^*(f')\rangle=\frac12\delta(f-f')\big[\Gamma^I_{ij}(f)I(f)+\Gamma^V_{ij}(f)V(f)\big]$$

代入圆偏振基组的定义，两个ORF显式写成（[2] 式2.10）：

$$\Gamma^I_{ij}(f)\equiv\frac34\sin\frac{2\pi fL_i}{c}\sin\frac{2\pi fL_j}{c}D_i^{ab}D_j^{cd}\int\frac{d^2\hat k}{4\pi}\big[e^+_{ab}e^+_{cd}+e^\times_{ab}e^\times_{cd}\big]e^{-i2\pi f\hat k\cdot\Delta\vec r/c}$$

$$\Gamma^V_{ij}(f)\equiv-i\frac34\sin\frac{2\pi fL_i}{c}\sin\frac{2\pi fL_j}{c}D_i^{ab}D_j^{cd}\int\frac{d^2\hat k}{4\pi}\big[e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd}\big]e^{-i2\pi f\hat k\cdot\Delta\vec r/c}$$

**这是全篇最关键的一组对照公式**：$\Gamma^I$ 用的是**对称求和** $e^+e^++e^\times e^\times$（与 PRD 论文式12 的 $\xi(\hat n)$ 结构完全一致），$\Gamma^V$ 用的是**反对称求差** $e^+e^\times-e^\times e^+$（PRD 论文从未出现过的新组合）。

### 2.3 不做暴力积分，而是用"张量对称性 + 待定系数"解出解析式

JCAP 论文没有走 PRD 论文的留数定理路线，而是走了另一条巧妙的路：**先用对称性约束"猜"出解的一般形式，再解一个小型线性方程组**。定义分离方向 $\hat s\equiv-\Delta\vec r/\Delta r$、相位 $\iota\equiv2\pi f\Delta r/c$（[2] 式B.2），以及辅助张量（[2] 式B.3）：

$$\Gamma^I_{abcd}(\iota,\hat s)\equiv\frac52\int\frac{d^2\hat k}{4\pi}[e^+_{ab}e^+_{cd}+e^\times_{ab}e^\times_{cd}]e^{i\iota\hat k\cdot\hat s},\quad \Gamma^V_{abcd}(\iota,\hat s)\equiv-i\frac52\int\frac{d^2\hat k}{4\pi}[e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd}]e^{i\iota\hat k\cdot\hat s}$$

**"宇称偶"部分（对应 $\Gamma^I$）的推导：**

$\Gamma^I_{abcd}$ 关于 $a\leftrightarrow b$、$c\leftrightarrow d$、$ab\leftrightarrow cd$ 均对称，且对 $ab$、$cd$ 各自无迹。这样的张量只能用 $\delta_{ab}$ 和 $s_a$ 构造出5个基底，带5个待定系数 $A,B,C,D,E$（[2] 式B.5）：

$$\Gamma^I_{abcd}=A\,\delta_{ab}\delta_{cd}+B(\delta_{ac}\delta_{bd}+\delta_{bc}\delta_{ad})+C(\delta_{ab}s_cs_d+\delta_{cd}s_as_b)+D(\cdots)+E\,s_as_bs_cs_d$$

用张量收缩把这5个系数和5个可直接积分求出的标量 $p_0^I,\ldots,p_4^I$ 联系起来，解一个 $5\times5$ 线性方程组（[2] 式B.6-B.7）。选坐标系令 $\hat s$ 沿 $z$ 轴（[2] 式B.9-B.10），把积分具体算出来（[2] 式B.11）：

$$p_0^I=0,\quad p_1^I=20j_0(\iota),\quad p_2^I=0,\quad p_3^I=\frac{40}{\iota}j_1(\iota),\quad p_4^I=\frac{20}{\iota^2}j_2(\iota)$$

其中 $j_0,j_1,j_2$ 是**球贝塞尔函数**（[2] 式B.12）。解出系数后代入，利用探测器张量无迹的性质化简，最终得到（[2] 式B.16-B.18）：

$$\hat\Gamma^I_{abcd}=b_0^I\,\delta_{ac}\delta_{bd}+b_1^I\,\delta_{ac}s_bs_d+b_2^I\,s_as_bs_cs_d,\qquad \begin{pmatrix}b_0^I\\b_1^I\\b_2^I\end{pmatrix}=\frac17\begin{pmatrix}14&-21&1\\0&60&-10\\0&0&35/2\end{pmatrix}\begin{pmatrix}j_0\\j_2\\j_4\end{pmatrix}$$

**"宇称奇"部分（对应 $\Gamma^V$）的推导——这是我们最需要重点研究的部分：**

$\Gamma^V_{abcd}$ 关于 $a\leftrightarrow b$、$c\leftrightarrow d$ 依然对称，但对 $ab\leftrightarrow cd$ 交换是**反对称**的。要构造出这种反对称性，唯一的办法是引入**列维-奇维塔张量**构造的赝矢量 $w_{bd}\equiv\epsilon_{abc}s^c$（[2] 式B.19 之前的定义）。带这个"手性算符"的基底只有3个，待定系数 $F,G,H$（[2] 式B.19）：

$$\Gamma^V_{abcd}=F(\delta_{ab}s_cs_d-\delta_{cd}s_as_b)+G(w_{ac}\delta_{bd}+w_{ad}\delta_{bc}+w_{bc}\delta_{ad}+w_{bd}\delta_{ac})+H(w_{ac}s_bs_d+\cdots)$$

同样解线性方程组（[2] 式B.20-B.21），在与宇称偶情形**相同的坐标系**下算出标量（[2] 式B.22）：

$$p_0^V=0,\quad p_1^V=40j_1(\iota),\quad p_2^V=\frac{40}{\iota}j_2(\iota)$$

**注意这里 $j_0$ 缺席、只出现 $j_1,j_2$（比宇称偶情形整整少了一阶）**——这是反对称性直接留下的数学指纹。解出 $F=0$（第一个基底系数恒为零），$G,H$ 由 $j_1,j_2$ 线性组合给出（[2] 式B.23）：

$$\begin{pmatrix}G\\H\end{pmatrix}=\frac54\begin{pmatrix}1&-1\\-1&5\end{pmatrix}\begin{pmatrix}j_1\\\iota^{-1}j_2\end{pmatrix}$$

最终化简为（[2] 式B.24-B.27）：

$$\hat\Gamma^V_{abcd}=b_0^V\,w_{ac}\delta_{bd}+b_1^V\,w_{ac}s_bs_d,\qquad\begin{pmatrix}b_0^V\\b_1^V\end{pmatrix}=\begin{pmatrix}4&-1\\0&5\end{pmatrix}\begin{pmatrix}j_1\\j_3\end{pmatrix}$$

### 2.4 应用：LISA-Taiji 网络的探测灵敏度

把这套 $\Gamma^I,\Gamma^V$ 公式（[2] 式2.14-2.16）代入实际的 A、E 探测器张量（附录A给出，[2] 式A.8），再结合 Fisher 矩阵最优信噪比公式（[2] 式2.12-2.13），JCAP 论文最终得出：调整 Taiji 轨道面倾角从 $+60°$ 变为 $-60°$（即"LISA-TAIJIm"构型），能让 $V$ 分量在毫赫兹频段的灵敏度提升近一个数量级（[2] 图3-图7及结论部分），这是打破镜面对称、增强手征响应的直接实证。

---

## 第三部分：整合方案——手征ORF的"通法"该怎么建

对照完两篇论文的完整逻辑后，整合方案的骨架已经非常清晰。核心思路是：**把 PRD 论文"分解为单向链路→精确留数解法"这套通法的物理输入，从"非偏振各向同性假设"换成"手征各向同性假设"**，重新走一遍整个推导流程。下面按照"输入替换→中间推导→输出验证"三段给出详细方案。

### 3.1 第一步：替换统计假设（唯一的物理修改）

PRD 论文式4 的各向同性、非偏振假设是：

$$\langle h_A(f,\hat n)h_{A'}^*(f',\hat n')\rangle=\frac{1}{16\pi}S_h(f)\,\delta(f-f')\,\delta_{AA'}\,\delta^2(\hat n,\hat n')$$

**整合方案的第一步，是把这个假设按照 JCAP 论文式2.2 的结构替换成手征版本**：

$$\langle h_A(f,\hat n)h_{A'}^*(f',\hat n')\rangle=\frac{1}{16\pi}\delta(f-f')\delta^2(\hat n,\hat n')\begin{pmatrix}I(f)&-iV(f)\\iV(f)&I(f)\end{pmatrix}_{AA'}$$

这一步不改变 PRD 论文关于"探测器响应可分解为单向链路"的第1.1节结论（那是探测器几何性质，与随机背景的统计性质无关），**只影响 ORF 定义式（[1]式8）里对 $A$ 求和的方式**。

### 3.2 第二步：定义手征版本的"母函数"

仿照 PRD 论文式8 定义 $\Gamma_{IJ}$ 的方式，把新的关联矩阵代入互相关公式的推导，会自然分裂出两项——强度项 $\Gamma^I_{IJ}$（与原PRD论文式8完全相同）和手征项 $\Gamma^V_{IJ}$（新增）：

$$\Gamma^V_{IJ}(f)=\frac{-i}{8\pi}\int d^2\Omega_{\hat n}\Big[R_I^+(f,\hat n)R_J^{\times*}(f,\hat n)-R_I^\times(f,\hat n)R_J^{+*}(f,\hat n)\Big]$$

这个式子与 JCAP 论文式2.10 定义 $\Gamma^V_{ij}$ 的方括号结构**完全对应**，唯一区别是这里的 $R_I^A(f,\hat n)$ 是 PRD 论文式6 给出的**精确单向链路响应函数**（含 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)$），而不是 JCAP 论文式2.7 长波近似下的静态探测器张量 $D^{ab}$。

由于 PRD 论文第1.1节已经证明任意探测器的响应函数都是单向链路的线性组合，这里同样可以把 $\Gamma^V_{IJ}$ 分解为"两条一般单向链路的手征ORF母函数"：

$$\boxed{\Gamma^V_{\rm one}(\alpha,\beta_u,\beta_v,\hat s,\hat u,\hat v)\equiv\frac{-i}{32\pi}\int d^2\Omega_{\hat n}\,\kappa_{IJ}(\hat n)\,e^{-i\alpha\hat n\cdot\hat s}\left[\frac{e^+_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^\times_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}-\frac{e^\times_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^+_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}\right]}$$

这个式子和 PRD 论文式10 定义 $\Gamma_{\rm one}$（对照 [1]式10）**外层结构完全一致**（$\kappa_{IJ}(\hat n)$、相位因子 $e^{-i\alpha\hat n\cdot\hat s}$、分母 $1+\hat n\cdot\hat u$ 都原样保留），唯一改变的是方括号里从"对称求和"换成"反对称求差"——这正是把 JCAP 论文式2.10 的反对称结构"嫁接"进 PRD 论文式10 的精确框架。这就是**"手征ORF通法"的核心定义式**。

### 3.3 第三步：逐步复用留数定理推导框架

按照 PRD 论文第1.3节 Step1-3 的顺序，逐步替换：

**Step 1（对应 [1]式11-12）：** 把 $\xi(\hat n)$ 换成手征版本：

$$\xi_V(\hat n)=\frac{e^+_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^\times_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}-\frac{e^\times_{ab}(\hat n)u^au^b}{1+\hat n\cdot\hat u}\cdot\frac{e^+_{cd}(\hat n)v^cv^d}{1+\hat n\cdot\hat v}$$

$\Gamma^V_{\rm one}$ 同样拆成四项 $I_1^V,I_2^V,I_3^V,I_4^V$，结构与 [1]式11 一一对应，只是把 $\xi(\hat n)$ 全部替换为 $\xi_V(\hat n)$。

**Step 2（对应 [1]式13-15）：** 坐标系选取（$\hat s$ 沿 $z$ 轴，$\hat u$ 在 $xz$ 平面）**完全复用**，因为这一步只依赖 $\hat s,\hat u,\hat v$ 的相对几何关系，与被积函数是否反对称无关。方位角积分同样可以用 $z=e^{i\phi}$ 转化为围道积分：

$$I_1^V=\int_{-1}^1 dx\,e^{-i\alpha x}\oint_{|z|=1}dz\,\frac{1}{iz}\xi_V(x,z)$$

**Step 3（对应 [1]式16-18，这是需要重新计算的核心部分）：** 由于分母结构 $(1+\hat n\cdot\hat u)(1+\hat n\cdot\hat v)$ 不变，**围道积分的5个极点位置公式（[1]式16）原样成立**，不需要重新推导；但每个极点处的**留数值**依赖分子 $\xi_V$，必须重新计算。根据第2.3节 JCAP 论文长波近似解法中观察到的现象（宇称奇部分比宇称偶部分"缺一阶"球贝塞尔函数），可以预期：

- $\xi_V$ 展开后关于方位角 $\phi$ 的三角级数，会比 $\xi_I$ **多出正弦(奇)型分量、少了余弦(偶)型分量的某些项**（因为反对称组合本质上提取的是 $\mathrm{Im}$ 部分而非 $\mathrm{Re}$ 部分）；
- 留数在 $x$ 的多项式结构上会相应改变奇偶性，最终对 $x$ 积分后，**很可能不再需要 PRD 论文式18 里那两个复杂的指数积分函数 $\mathrm{Ei}(z)$ 项**（因为 JCAP 长波近似结果里 $\Gamma^V$ 不需要 $j_0$，暗示手征情形的积分结构可能有对称性简化，具体需展开验证）。

**Step 4（对应 [1]式19-23）：** $I_2^V,I_3^V,I_4^V$ 是否依然能通过"矢量替换"从 $I_1^V$ 得到，需要重新审视。PRD 论文这一步的论证基础是"各向同性背景下结果与坐标系朝向无关"。但**手征背景虽仍各向同性，却不是宇称中性的**：一次普通旋转（$\det=+1$）不改变 $\Gamma^V$，但一次镜面反射（$\det=-1$）会让 $\Gamma^V$ 反号。由于 PRD 论文原本的矢量替换只涉及**平移和旋转**（$\alpha\hat s+\beta_u\hat u$ 这类操作不引入镜面反射），可以论证**这一步的矢量替换规则同样适用于手征版本**，$I_2^V,I_3^V,I_4^V$ 依然可以由 $I_1^V$ 通过同样的参数代换得到：

$$I_2^V(\alpha,\beta_u,\hat s,\hat u,\hat v)=-e^{-i\beta_u}I_1^V(\alpha_2,\hat s_2,\hat u,\hat v),\quad\text{（其余同理）}$$

最终手征母函数：

$$\Gamma^V_{\rm one}=\frac{1}{32\pi}\Big[I_1^V(\alpha,\hat s,\hat u,\hat v)-e^{-i\beta_u}I_1^V(\alpha_2,\hat s_2,\hat u,\hat v)-e^{i\beta_v}I_1^V(\alpha_3,\hat s_3,\hat u,\hat v)+e^{i(\beta_v-\beta_u)}I_1^V(\alpha_4,\hat s_4,\hat u,\hat v)\Big]$$

这个式子的结构与 [1]式24 完全一致，只是每一处 $I_1$ 换成 $I_1^V$。

### 3.4 第四步：三重验证（比照 PRD 论文的自洽性检验方法）

**验证1 —— PTA 极限（$\alpha=0$）应严格为零：** 令两条链路共享终点（脉冲星-地球型退化几何），代入 $\Gamma^V_{\rm one}$，应该重现 Kato & Soda [4] 和最新 dPTA 论文 [5] 严格证明的"各向同性背景下PTA对手征零响应"定理。这对应把第1.4节的验证方法平移到手征情形。

**验证2 —— 长波近似极限（$\beta_u,\beta_v\ll1$）应退化到 JCAP 论文结果：** 取 PRD 精确传递函数 $\mathcal T_{\rm one}(\beta,\hat n\cdot\hat u)\to i\beta$（小天线近似），$\Gamma^V_{\rm one}$ 应该退化到 JCAP 论文式B.19-B.27 给出的、由球贝塞尔函数 $j_1,j_2,j_3$ 描述的结果。这一步直接检验第3.3节 Step3 的预期是否正确。

**验证3 —— 数值积分交叉核对：** 对任意给定的几何参数，直接对 $\Gamma^V_{\rm one}$ 定义式做球面数值积分，和解析结果比对，仿照 PRD 论文 Table I 的验证方式，尤其要在**高频段**（$\beta\sim1$，长波近似失效的区域）重点检验，这正是"精确方法"相对"JCAP长波近似"的核心改进点所在。

### 3.5 第五步：应用场景——组装成实际探测器的手征ORF

一旦 $\Gamma^V_{\rm one}$ 精确解出，应用到具体探测器组合是纯粹的线性代数（复用 PRD 论文第1.1节"任意探测器分解为单向链路"的现成结果）：

- **OLC-OLC 网络**：直接代入两条OLC单向链路的 $\{\vec r,L,\hat u\}$ 参数，得到精确的OLC网络手征ORF；
- **LISA-Taiji 等天基三角网络**：利用 PRD 论文里"任意TDI通道可分解为6条单向链路线性组合"的方法（对应 [1]式37-38 附近内容），把 A、E 通道的系数 $P_i$ 代入 $\Gamma^V_{\rm one}$ 的求和公式，直接对标改进 JCAP 论文的高频段结果：

$$\Gamma^V_{\rm SbLI}(f)=\frac{1}{32\pi}\sum_{i,j}P_iP_j^*\,\Gamma^V_{\rm one}(\alpha_{ij},\beta_u,\beta_v,\hat u_i,\hat v_j,\hat s_{ij})$$

- **混合网络（OLC×LISA）**：由于 $\Gamma^V_{\rm one}$ 本身就是"任意两条一般单向链路"之间的通用公式，不要求两条链路属于同一类探测器，因此这个母函数天然支持跨探测器类型的手征交叉关联计算，一并解决了此前讨论过的"混合网络"空白问题。

### 3.6 整合方案总览图

```
PRD论文式4（非偏振假设，δ_AA' 对角）
        │
        │  【替换】按JCAP式2.2引入非对角虚数关联 -iV(f)
        ▼
新的手征统计假设（3.1节）
        │
        │  代入PRD式8的ORF定义框架
        ▼
Γ^V_IJ 的定义（3.2节，结构对照JCAP式2.10方括号）
        │
        │  【复用】PRD第1.1节"任意探测器→单向链路分解"
        ▼
Γ^V_one 母函数定义（3.2节方框公式，对照PRD式10）
        │
        │  【复用】PRD式13坐标系选取 + 式14-15复变换
        │  【重新计算】式16-18留数值（因为分子ξ_V变了）
        ▼
Γ^V_one 精确解析式（3.3节）
        │
        ├──验证1：PTA极限=0（对照Kato-Soda/dPTA）
        ├──验证2：长波近似退化到JCAP式B.19-B.27
        └──验证3：数值积分交叉核对（重点测高频段）
        │
        ▼
应用：OLC网络 / LISA-Taiji精确手征ORF / 混合网络交叉手征ORF
```

---

## 参考文献

| 编号 | 文献 |
|---|---|
| [1] | Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Universal calculation approach of overlap reduction function for pulsar timing array and laser interferometer detector*, Phys. Rev. D **111**, 084065 (2025). |
| [2] | J. Chen, C. Liu, Y.-L. Zhang, *Circularly polarized gravitational wave background search with a network of space-borne triangular detectors*, JCAP **05**, 050 (2025), arXiv:2410.18916. |
| [3] | Y. Hu, P.-P. Wang, Y.-J. Tan, C.-G. Shao, *Full analytic expression of overlap reduction function for gravitational wave background with pulsar timing arrays*, Phys. Rev. D **106**, 024005 (2022). |
| [4] | R. Kato, J. Soda, *Probing circular polarization in stochastic gravitational wave background with pulsar timing arrays*, Phys. Rev. D **93**, 062003 (2016). |
| [5] | *Detecting Chiral Gravitational Wave Background with a Dipole Pulsar Timing Array*, arXiv:2604.08141 (2026). |
