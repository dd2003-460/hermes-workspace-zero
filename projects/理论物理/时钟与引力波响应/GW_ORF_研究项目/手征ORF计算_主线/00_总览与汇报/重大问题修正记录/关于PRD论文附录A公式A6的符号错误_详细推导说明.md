# 重大问题修正记录：PRD论文附录A式(A6)中 v̂ 相关内积公式的符号错误

**编号**: BUG-001
**发现时间**: 本轮工作（在前一模型工作基础上做独立复核时发现）
**严重程度**: 高——已污染此前标记为"✅完成"的 R1V, R2V 计算结果
**状态**: 已定位、已通过双重独立方法证实、修正方案已给出，下面开始逐脚本修复

---

## 0. 先说结论（TL;DR）

**前一模型给出的"极点符号错误"结论是错的，需要撤销。** 真正的错误不在极点公式 $z_3,z_4$（PRD论文 Eq.16/A7 打印的 $z_3=-\dfrac{(1+v_z)(1+x)}{(v_x-iv_y)\sqrt{1-x^2}}$ 是**完全正确**的），而在**论文附录A式(A6)里印刷的三个含 $\hat v$ 的内积公式**中，$v_y$ 项前面的虚数符号是**反的**：

| 量 | PRD论文Eq(A6)原文打印 | 正确应为（本次独立验证） |
|---|---|---|
| $\hat\theta\cdot\hat u$ | $\dfrac{u_xx(1+z^2)}{2z}-u_z\sqrt{1-x^2}$ | ✅ 与打印一致，无误 |
| $\hat\phi\cdot\hat u$ | $i\dfrac{u_x(z^2-1)}{2z}$ | ✅ 与打印一致，无误 |
| $\hat\theta\cdot\hat v$ | $\dfrac{v_xx(1+z^2)}{2z}+i\dfrac{v_yx(z^2-1)}{2z}-v_z\sqrt{1-x^2}$ | ❌ 中间项应为 $-i\dfrac{v_yx(z^2-1)}{2z}$（**符号相反**） |
| $\hat\phi\cdot\hat v$ | $i\dfrac{v_x(z^2-1)}{2z}+\dfrac{v_y(1+z^2)}{2z}$ | ✅ 与打印一致，无误 |
| $\hat n\cdot\hat u$ | $\dfrac{u_x\sqrt{1-x^2}(1+z^2)}{2z}+u_zx$ | ✅ 与打印一致，无误 |
| $\hat n\cdot\hat v$ | $\dfrac{\sqrt{1-x^2}}{2z}\big(v_x(1+z^2)+iv_y(z^2-1)\big)+v_zx$ | ❌ 应为 $\dfrac{\sqrt{1-x^2}}{2z}\big(v_x(1+z^2)-iv_y(z^2-1)\big)+v_zx$（**符号相反**） |

**规律**：6个内积公式中，凡是**不含 $v_y$**的（$\hat\theta\cdot\hat u,\hat\phi\cdot\hat u,\hat n\cdot\hat u,\hat\phi\cdot\hat v$）全部正确；凡是**含 $v_y$** 且是"$\theta$型或$n$型"（即含 $\cos\phi$ 一侧结构，非 $\phi$ 型）的两个公式（$\hat\theta\cdot\hat v,\hat n\cdot\hat v$）符号都反了。

而极点公式 $z_3,z_4$（Eq.16/A7，分母为 $v_x-iv_y$）本身与真实几何**完全自洽**，不需要改动，前一模型把它改成 $v_x+iv_y$ 是**错上加错**（详见第3节"为什么会产生虚假验证通过"）。

---

## 1. 怎么发现的：三层独立交叉验证

### 第一层：从最基本定义直接重推 (theta,phi)→(x,z) 变换

球坐标下三个标准正交基矢量的定义（与论文无关，教科书公式）：
$$\hat n=(\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta),\quad
\hat\theta=(\cos\theta\cos\phi,\ \cos\theta\sin\phi,\ -\sin\theta),\quad
\hat\phi=(-\sin\phi,\ \cos\phi,\ 0)$$

令 $z=e^{i\phi}$（论文自己声明的变量代换约定），欧拉公式给出：
$$\cos\phi=\frac{z^2+1}{2z},\qquad \sin\phi=\frac{z-z^{-1}}{2i}=-\,i\,\frac{z^2-1}{2z}$$

**这是本次修正的核心**：$\sin\phi$ 用 $z$ 表示时，系数是 $-i$，不是 $+i$。这一点可以用最基础的方式验证：

$$\sin\phi=\frac{e^{i\phi}-e^{-i\phi}}{2i}=\frac{z-1/z}{2i}=\frac{z^2-1}{2iz}=\frac{-i(z^2-1)}{2z}$$

（因为 $1/i=-i$）

把这两个代换代入 $\hat n\cdot\hat v=v_x\sin\theta\cos\phi+v_y\sin\theta\sin\phi+v_z\cos\theta$（论文式A3，无争议），得到

$$\hat n\cdot\hat v=\frac{\sqrt{1-x^2}}{2z}\Big[v_x(1+z^2)\ \underbrace{-\,i\,v_y(z^2-1)}_{\text{此项符号}}\Big]+v_zx$$

而论文Eq(A6)打印的是 $+iv_y(z^2-1)$，符号相反。$\hat\theta\cdot\hat v$ 同理。

（对比之下 $\hat n\cdot\hat u,\hat\theta\cdot\hat u$ 不含 $v_y$（因为规范选取 $\hat u=(u_x,0,u_z)$，$u_y=0$），所以不受这个符号问题影响，这也是为什么"两个含v_y的式子错、两个不含v_y的公式对"这条规律的原因。$\hat\phi\cdot\hat v=v_y\cos\phi-v_x\sin\phi$ 里 $v_y$ 项系数是 $\cos\phi\to(z^2+1)/2z$，不涉及虚数符号问题，所以碰巧没有错。）

用 sympy 把上述差值做严格符号化简（`F-code-1`，见 `推导/03_严格符号级证明_附录A式A6符号错误.py`）：
$$\Delta(\hat\theta\cdot\hat v)=\text{Eq(A6)打印值}-\text{正确值}=\frac{iv_y(1-z^2)\cos\theta}{z}\ne0$$
$$\Delta(\hat n\cdot\hat v)=\frac{iv_y(1-z^2)\sin\theta}{z}\ne0$$

这是**严格符号代数恒等式级别**的证明，不依赖任何数值抽样。

### 第二层：数值抽样交叉核对（3D笛卡尔矢量点积 vs (x,z)代数公式）

直接构造真实的 $\hat n,\hat\theta,\hat\phi,\hat u,\hat v$ 三维笛卡尔矢量，在 $|z|=1$（即$\phi$为实数）时算出真实点积，与论文Eq(A6)打印公式代入 $z=e^{i\phi}$ 后的值比较：

| 量 | 5组随机测试的典型误差 |
|---|---|
| $\hat\theta\cdot\hat u,\hat\phi\cdot\hat u,\hat n\cdot\hat u,\hat\phi\cdot\hat v$ | $\sim10^{-16}$（机器精度，完全吻合）|
| $\hat\theta\cdot\hat v,\hat n\cdot\hat v$ | $0.03\sim1.6$（O(1)量级，明显不吻合）|

### 第三层：判决性检验——用留数定理算出的极点残数，对照论文自己给出的封闭解公式Eq(A8)-(A12)

这是最有说服力的一步：PRD论文本身给出了 $R_0,R_1,R_2,R_3,R_4$（强度版，非手征版）的**显式封闭解**（式A8-A12，用 $\delta_u,\delta_v,\gamma,\sigma^\pm$ 参数表示，不含 $z$）。这些封闭解是论文作者独立算出来发表的，可信度最高。

用"完全独立的3D构造 → (x,z)代数延拓（$\sin\phi\to-i(z^2-1)/(2z)$的**正确**版本）→ 数值围道积分求留数"这条链路，与论文Eq(A8)-(A12)的封闭解对比（8组随机几何参数 $\times$ R1,R2,R3,R4 共32次独立检验）：

- 用**修正后**的 $(x,z)$ 内积公式（$\hat\theta\cdot\hat v,\hat n\cdot\hat v$ 里 $v_y$ 项为 $-i$）+ **论文原文未改动**的极点 $z_3,z_4$（分母 $v_x-iv_y$）：
  **32组全部通过，最大相对误差 $\sim10^{-12}$**（唯有个别测试点因 $x+\sigma^\pm$ 分母接近零导致数值不稳定除外，属预期的病态点，非算法错误）。

具体数据见 `数值验证/04_判决性检验_用论文自己的R1R4封闭解反查符号约定.py`，例如：
```
trial0 R1: numerical=-0.99147+0.42479j  paper_formula=-0.99147+0.42479j  rel_err=3.6e-14  ✅
trial0 R3: numerical=-0.073825-0.069841j  paper_formula=-0.073825-0.069841j  rel_err=6.3e-15  ✅
```

这就证明：**极点公式 $z_3,z_4$ 是对的，问题出在 Eq(A6) 里 $\hat\theta\cdot\hat v,\hat n\cdot\hat v$ 的印刷公式**。

---

## 2. 这是论文本身的错误，还是我们转录/理解有误？

已排除的可能：
1. **不是我们抄录PDF时抄错**——本次工作直接用 `PyMuPDF` 从原始PDF裁出高清截图（见 `page12_crop_nv_line.png` 等），逐字符核对确认转录准确无误，论文原文打印的的确是 $+iv_y$。
2. **不是变量约定反了（如论文实际用 $z=e^{-i\phi}$）**——若整体反转 $\phi\to-\phi$（即 $z\to1/z$），$\hat\phi\cdot\hat u,\hat\phi\cdot\hat v$ 也会同时出问题，但数值检验显示这两个量本身是对的，只有 $\hat\theta\cdot\hat v,\hat n\cdot\hat v$ 错，所以不是整体约定反了，而是这两个具体公式在推导/排版过程中单独出的错。
3. **不是"两个负负得正"的巧合**——用严格符号计算（sympy `simplify` 到底），差值就是 $\propto v_y$ 的非零表达式，不是数值噪声。

**结论**：这是 PRD 论文 Hu, Wang, Tan, Shao (2025) 附录A式(A6)本身的一处印刷/推导错误（$\hat\theta\cdot\hat v$ 和 $\hat n\cdot\hat v$ 两处 $v_y$ 项符号）。考虑到该论文最终给出的封闭解公式(A8)-(A12)、以及正文Eq(18)的最终结果，**都不显式依赖这个中间的$(x,z)$内积公式**（它们是用$\delta_u,\delta_v,\gamma,\sigma^\pm$等"角度不变量"表达的），所以**这个印刷错误不影响论文正文的最终结论**，只是这份论文附录A的一个中间推导步骤笔误，属于"人畜无害"但会误导后来者独立复现符号推导的那种错误。

---

## 3. 为什么前一模型的"验证"会产生"虚假通过"的假象

前一模型的排错逻辑是：
1. 用论文Eq(A6)打印的 $\hat n\cdot\hat v$ 公式（$+iv_y$，本身有误）去检验论文Eq(A7)打印的 $z_3,z_4$（分母 $v_x-iv_y$，本身无误）；
2. 因为第1步的公式有错，代入后 $(1+\hat n\cdot\hat v)$ 不为零，得出"$z_3,z_4$ 有误"的错误结论；
3. 于是把 $z_3,z_4$ 的分母也改成 $v_x+iv_y$，凑出了"$(1+\hat n\cdot\hat v)=0$"的假象——因为**两个独立的符号错误（错误的$\hat n\cdot\hat v$ + 错误的$z_3,z_4$）在这个特定的检验方式下恰好互相抵消**，制造了"验证通过"的假象。

这是一个值得记录的方法论教训：**当用来做验证的"金标准"本身包含错误时，被检验对象即便是对的也会显示"不通过"；如果因此去修改被检验对象凑出"通过"，反而会引入新的错误，而且这种"两个错误抵消"式的虚假通过特别难以自我发现**，因为它在这次特定的检验里表现完美（sympy化简严格得0），必须换一个完全独立的、不依赖同一条推导链路的检验方式（比如本文档第3层用的"论文自己发表的R1-R4封闭解"）才能揭穿。

---

## 4. 受影响范围评估

### 完全不受影响（可以直接信任）
- `组件A/推导/01_坐标变换公式_PRD附录A复现.py` 中的 $\hat\theta\cdot\hat u,\hat\phi\cdot\hat u,\hat n\cdot\hat u$ —— 不含 $v_y$，无误。
- 所有仅依赖 $z_1,z_2$（对 $\hat u$ 的极点）的**极点位置本身**——无误。
- 前一模型对 $z_1-z_2$ 符号分支的修正（Bug修正#2）——与本问题无关，独立正确。

### 受污染，需要重新计算（本次工作接下来要做的）
- `组件A/推导/02_构造对称核xiI与反对称核xiV.py` 中的 `theta_dot_v, n_dot_v` 定义——需改用正确符号。
- **R0V, R1V, R2V 全部三个"已验证✅"的留数结果实际上是错的**，因为它们的计算都要用到 $\hat\theta\cdot\hat v$ 或 $\hat n\cdot\hat v$ 在 $z_1,z_2$（或原点）处的取值。用错误公式算出的"数值验证通过"，是因为验证脚本本身用的是同一套（错误的）内积公式做黄金标准围道积分——即前一模型的"独立数值验证"其实并不独立，验证代码和被验证代码共享了同一个错误的输入公式，属于同源污染，无法互相纠错。
- R3V, R4V（虽未获得符号解，但数值探索用的也是错误公式，结论——包括"互为共轭"的发现——需要重新核实）。
- 组件E的核心发现 $R_1^V=-iR_1^I,R_2^V=+iR_2^I$——这个恒等式的推导逻辑（"z1,z2处 eCross_uu/ePlus_uu = ±i"）只涉及 $\hat u$ 相关内积，不直接依赖 $\hat v$ 的错误公式，**但R1V,R2V本身的数值需要重算，这个比例关系是否仍然成立需要用修正后的公式重新验证**。

下一步工作计划见同目录 `修复计划与进度追踪.md`。
