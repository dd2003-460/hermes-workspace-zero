# RunPod 云 GPU 使用指南

**所属迭代**: iter42
**创建时间**: 2026-07-15
**任务**: T2
**数据来源**: 1-loop S5 Agent验证 + 内部知识
**置信度**: 0.80

---

## 1. 价格基准

### RTX 4090 定价

| 类型 | 价格 (USD/hr) | 月费估算 | 说明 |
|------|-------------|---------|------|
| RTX 4090 Pod | $0.69/hr | ~$500 | **最推荐**，性价比最高 |
| RTX 4090 Secure Pod | $0.85-1.00/hr | ~$620-730 | 加密存储，适合敏感数据 |
| A6000 Pod | $1.49/hr | ~$1,080 | 48GB VRAM |
| A100 80GB Pod | $2.50/hr | ~$1,825 | 适合 70B+ 模型 |
| H100 Pod | $4.00+/hr | ~$2,920+ | 顶级性能 |

### 盈亏平衡分析

| 自购 vs 云端 | 小时数 | 月数 |
|------------|--------|------|
| RTX 4090 ($2,200) vs RunPod ($0.69/hr) | 226h | ~10周 |
| RTX 5090 ($4,500) vs RunPod ($0.69/hr) | 652h | ~9.5月 |

**结论**: 年使用 < 2000h (约 8 个月/年) 选云端更划算

---

## 2. 注册流程

### Step 1: 创建账号
1. 访问 https://www.runpod.io
2. 点击 "Sign Up"
3. 支持邮箱注册或 Google 登录
4. 验证邮箱

### Step 2: 绑定支付方式
- **支持**: Visa/Mastercard 信用卡, PayPal
- **借记卡**: 部分支持，但信用卡更可靠
- **最低充值**: $25 (首次充值)

### Step 3: 完成 KYC (如需要)
- 部分国家/地区需要额外身份验证
- 准备: 护照/身份证照片
- 通常 24 小时内审核通过

---

## 3. 创建 RTX 4090 Pod

### Step 1: 选择 GPU
1. 进入 "Pods" 页面
2. 点击 "Launch Pod"
3. GPU 选择: RTX 4090
4. 区域选择: 选延迟最低的（通常 US-East 或 EU-West）

### Step 2: 配置 Pod

**推荐配置**:
```
GPU: RTX 4090 (24GB VRAM)
存储: 50GB+ (根据模型大小)
Docker 镜像: nvidia/cuda:12.2.0-devel-ubuntu22.04
            或 runpod/llm-inference:latest
```

**不推荐配置**:
- 不要选择 "Secure Pod" 除非需要加密存储
- 不要选择过多存储（按 GB/月计费）

### Step 3: 启动并连接
1. 点击 "Launch Pod"
2. 等待 Pod 启动（通常 1-3 分钟）
3. 通过 "Connect" → "Jupyter Lab" 访问
4. 首次连接需要 SSH 密钥（自动生成）

### Step 4: 环境配置
```bash
# SSH 连接到 Pod
ssh pod-xxxx.runpod.io

# 进入容器
docker exec -it <container_id> bash

# 安装依赖
pip install torch torchvision torchaudio
pip install transformers
pip install vllm  # 如需 LLM 推理
pip install ollama  # 如需 Ollama
```

---

## 4. 推荐 Docker 镜像

### 4.1 PyTorch 默认镜像
```
nvidia/cuda:12.2.0-devel-ubuntu22.04
```
- 适合: 通用 GPU 计算
- 优点: 官方维护，版本稳定

### 4.2 LLM 推理专用
```
runpod/llm-inference:latest
```
- 适合: LLM 推理
- 已预装 vLLM, Text Generation Inference

### 4.3 Ollama 镜像
```
ollama/ollama:latest
```
- 适合: 快速启动本地 LLM
- 启动后: `ollama run llama3.1 8b`

### 4.4 Jupyter Notebook 镜像
```
jupyter/pytorch:latest
```
- 适合: 开发调试
- 自带 Jupyter Lab

---

## 5. 成本监控

### 设置消费上限
1. 进入 "Settings" → "Billing"
2. 设置 Monthly Budget (建议: $500 起)
3. 启用 Email Alerts

### 监控 Running Cost
1. Pods 页面实时显示运行费用
2. 底部有当前 Pod 的累计费用

### 最佳实践
- **用完即关**: 不需要时立即 Stop Pod
- **不要 Leave 空转**: 忘记关 Pod 会产生持续费用
- **定期清理**: 不再需要的 Pod 直接删除
- **选择合适存储**: 不需要时删除 Volume

### 费用计算示例
```
RTX 4090 Pod 运行 10 小时:
  GPU: 10 × $0.69 = $6.90
  存储: 50GB × $0.05/GB = $2.50
  总计: ~$9.40

运行 100 小时: ~$91.50
运行 1000 小时: ~$915.00
```

---

## 6. 常见问题

### Q1: Pod 启动很慢怎么办?
- 换个区域试试（US-East 通常最快）
- 高峰期可能需要排队
- 考虑预占 Pod (Preemptible Pod)

### Q2: 可以远程桌面连接吗?
- RunPod 主要提供 SSH/Jupyter 访问
- 如需 GUI，可配置 VNC:
  ```bash
  # 在 Pod 内安装 VNC
  apt-get update && apt-get install -y xfce4 vnc4server
  vncserver :1
  ```

### Q3: 支持按小时付费吗?
- 是的，按秒计费，最小单位 1 分钟
- 停止 Pod 后不再计费

### Q4: 数据传输费用?
- 入站: 免费
- 出站: 前 1TB/月免费，超出 $0.05/GB

### Q5: 数据安全性?
- 标准 Pod: 普通共享环境
- Secure Pod: 加密存储，适合敏感数据
- 数据保存在 Volume 中，删除 Pod 不会自动删除

---

## 7. 替代云 GPU 平台

| 平台 | RTX 4090 价格 | 特点 |
|------|-------------|------|
| RunPod | $0.69/hr | 最便宜，易用 |
| Lambda Labs | ~$1.00/hr | 稳定，但经常满员 |
| CoreWeave | ~$0.85/hr | 企业级，API 友好 |
| Vast.ai | $0.40-0.70/hr | 更便宜但可靠性参差 |
| Compass Cloud | ~$0.80/hr | 专注 AI/ML |

**注意**: Vast.ai 可能更便宜但需要自行验机，不适合新手。

---

## 8. 快速上手命令

```bash
# 1. SSH 连接到 Pod
ssh pod-xxxx.runpod.io

# 2. 拉取 PyTorch 镜像
docker pull nvidia/cuda:12.2.0-devel-ubuntu22.04

# 3. 启动容器
docker run -it --gpus all nvidia/cuda:12.2.0-devel-ubuntu22.04 bash

# 4. 安装 PyTorch
pip install torch torchvision torchaudio

# 5. 验证 GPU
python -c "import torch; print(torch.cuda.is_available())"

# 6. 安装 vLLM (LLM 推理)
pip install vllm

# 7. 启动 vLLM 服务
python -m vllm.entrypoints.api_server --model meta-llama/Llama-3.1-8B-Instruct

# 8. 停止 Pod (不再计费)
# 在 RunPod Web UI 中点击 "Stop"
```

---

*本文档基于 1-loop S5 Agent 验证数据 + 执行计划创建。*
*数据来源: RunPod 官方定价 + 1-loop S5 验证 + 内部知识*
