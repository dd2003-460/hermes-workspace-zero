# origin: ai
# Claude 像素形象调研（LMArena agent mode, 2026-10-20）

## 核心发现

Claude 有官方像素角色 **Clawd** 🦀（Claude Code mascot, 2025-09 引入，@trq212 "a new mascot, we call him Clawd 🦀"）。
社区像素艺术几乎都是 Clawd 变体。不需要从 logo 发明。

## 1. 官方视觉识别（三层）

| 层 | 内容 | 有脸？ |
|---|---|---|
| 1. Spark 星芒 | 不规则手绘感放射/风车/星号，terracotta 橙 | 否 |
| 2. Wordmark | "Claude" 暖色 serif + ANTHROP\C 企业标 | 否 |
| 3. **Clawd（角色源）** | 橙色"堆叠方块"生物：宽平顶矩形身体、两个小方形黑眼、无嘴无瞳孔无轮廓、短侧臂、4 短腿 | 是（极简） |

## 2. 官方色板（anthropics/skills brand-guidelines）

| 角色 | Hex | 像素用途 |
|---|---|---|
| **主橙 Crail/Japonica** | **#D97757** | 身体填充（最可识别色） |
| 采样 sprite 橙 | #DA7758 / #DD775B | 逆向后采样值，同族，标准化用 #D97757 |
| 暗/墨 | #141413 | 眼睛/文字（暖近黑，非纯黑） |
| 象牙底 | #FAF9F5 | 默认背景 |
| 燕麦/浅灰 | #F0EEE6 / #E8E6DC | 卡片/微阴影 |
| 中灰 | #B0AEA5 | 次要元素 |
| 点缀（慎用） | 蓝 #6A9BCC / 绿 #788C5D / 深陶 #C6613F | 极小点缀 |
| **鱼身阴影（建议，同族）** | **#C6613F**（深陶）+ #E9A786（浅陶） | 暗鳍/尾 + 高光 |

旧/第三方 #CC785C / #D4A27F 已过时。

## 3. Clawd 核心特征

- **轮廓**：一个宽平顶矩形块（"stacked squares"/矮胖 blob）。宽>高。终端像素 ~2× 高:宽，屏幕更扁。
- **眼睛（识别锚点）**：恰好两个 2×2 黑色方眼，宽距，身体水平 1/3 处。无嘴/瞳孔/轮廓。
- **肢体**：两侧短桩臂（可持旗/道具）+ 4 短直腿/脚（中间两腿间隙更大）。
- **渲染**：完全单色平涂，无轮廓无阴影无抗锯齿无渐变。放大只用 nearest-neighbor。
- **表情**：只靠眼睛交换（blink: – – / happy: ^^ / error: X X）。

## 4. 最佳像素参考（15+ 中找到）

| 参考 | 亮点 |
|---|---|
| **ClawdMoji** ⭐ | 像素完美复刻；原生 12×8 网格（24×16 谐波——所有特征恰好 2px 厚），body #DA7758, eyes #000 |
| **Clawdius** (eqctrl.io/clawdius) ⭐ | 最干净官方 sprite trace + 16 表情/道具共用一个身体。最佳"不变形换表情"参考 |
| **Codrops 逆向** ⭐ | 逐帧重建 4 个官方 @claudeai 动画（walk/flag/gym/confetti）；body 纯 <rect> 构建；最佳动画时间参考 |
| sketchybar-clawd | 18×6 变体：圆头、2 眼、4 脚，blink/dead/sleep 姿态 |
| clawd-on-desk / MyClawd | 精致动画集 + Pillow 绘制工具包 |
| Printables 3D Clawd | 轮廓比例参考 |

负面发现：Dribbble/Behance 基本没有——生态在 GitHub、X(@claudeai)、Reddit。Anthropic 无官方像素资产 repo。

## 5. 像素化关键参数

- **眼睛=识别锚点**：两个 2×2 黑方眼，宽距，身体 1/3 处，无嘴/瞳孔/轮廓
- **全平涂**：一色，无阴影/渐变/抗锯齿；nearest-neighbor 放大
- **网格**：24×16 工作，特征 2px 厚；body ≈20×9
- **Fat-fish 适配**（agent 已原型 sprites/fat_fish_front_28x20.png）：
  - 保持颜色+眼睛+正面视角完全不变
  - body 圆成 fat oval（1-2px 步进）
  - arms→#C6613F 侧鳍
  - legs→底鳍+阶梯尾
  - 可选 Spark 形背鳍
  - **陷阱 1**：浅色 belly 补丁在此尺寸读成嘴→删除
  - **陷阱 2**：侧面鱼丢两眼识别→保持正面

## 6. IP 注意

Clawd 是 Anthropic 商标/IP（"Clawdbot"→Moltbot rename）。公开/商业化视频保持 transformative，不分发 traced sprites。

## 7. 对 render_full_pixel.js 的改造方案

把现有 robot（橙色 #e08a3c, 16×22px, 天线+眼+嘴+腹+腿）替换为 Clawd 风格：
- 色板：robot #e08a3c → **#D97757**；robot2 #c9762f → **#C6613F**；robotEye #12151c → **#141413**
- 轮廓：平顶宽矩形（宽>高），4 短腿（中间间隙更大）
- 眼睛：2 个 2×2 黑方眼，宽距，身体 1/3 处，**无嘴无天线**
- 渲染：单色平涂，无阴影无渐变
- 尺寸：在 320×180 基绘下 ≈20×9px（与现 robot 相当）
