#!/bin/bash
# GPU 服务器剩余加固措施（需 sudo，在服务器本地终端执行）
# 生成时间：2026-10-27
# 已完成：fstab swap 注释 / 内核参数 APST+ASPM+panic / sysctl min_free+watermark / rsyslog 内核转发 / vLLM 容器 20G 限制
# 剩余：swap unit mask / zram 配置 / hung_task_panic

set -e

echo "=== 1. mask NVMe swap unit（防重启后 systemd-gpt-auto 复活 swap）==="
sudo systemctl mask dev-nvme0n1p2.swap
systemctl is-masked dev-nvme0n1p2.swap && echo "✅ swap unit 已 mask"

echo "=== 2. 配置 zram 6G（swap 替代，压缩换页微秒级）==="
# 清理可能存在的旧 zram
sudo sh -c 'echo 1 > /sys/block/zram0/reset' 2>/dev/null || true
sudo zramctl -s 6G -f /dev/zram0
sudo mkswap /dev/zram0
sudo swapon /dev/zram0
swapon --show
echo "✅ zram 已配置"

# 持久化：写入 /etc/zramswap.conf（zram-tools 格式）
# 如果 zram-tools 的 init 脚本不自动加载，需手动加 systemd unit
cat > /tmp/zram-setup.service << 'EOF'
[Unit]
Description=Setup zram swap
After=systemd-modules-load.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/zramctl -s 6G -f /dev/zram0
ExecStart=/sbin/mkswap /dev/zram0
ExecStart=/sbin/swapon /dev/zram0

[Install]
WantedBy=multi-user.target
EOF
sudo cp /tmp/zram-setup.service /etc/systemd/system/
sudo systemctl enable zram-setup.service
echo "✅ zram 持久化已配置"

echo "=== 3. hung_task_panic=1（D 态冻结→panic→10 秒自动重启）==="
# 已稳定 12 天，APST/ASPM 已修，可以开了
echo 'kernel.hung_task_panic = 1' | sudo tee /etc/sysctl.d/99-hung-task-panic.conf
sudo sysctl -p /etc/sysctl.d/99-hung-task-panic.conf
cat /proc/sys/kernel/hung_task_panic
echo "✅ hung_task_panic 已启用"

echo ""
echo "=== 全部完成 ==="
echo "验证：swapon --show 应只看到 zram0；reboot 后 swap 不会复活"
