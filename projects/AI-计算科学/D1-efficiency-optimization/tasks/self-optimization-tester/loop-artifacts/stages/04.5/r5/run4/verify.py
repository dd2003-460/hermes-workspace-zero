#!/usr/bin/env python3
"""R5.2a run4 判定脚本：验证 result.txt 的 SUM 值"""
import sys, os

EXPECTED = 16.50  # 3.50+2.00+5.75+1.25+4.00 = 16.50

result_file = os.path.join(os.path.dirname(__file__), 'result.txt')
if not os.path.exists(result_file):
    print(f"FAIL: {result_file} 不存在")
    sys.exit(1)

with open(result_file) as f:
    content = f.read().strip()

print(f"result.txt 内容: {content}")
print(f"期望值: SUM={EXPECTED:.2f}")

if content == f"SUM={EXPECTED:.2f}":
    print("PASS: 结果正确")
    sys.exit(0)
else:
    print(f"FAIL: 结果不匹配")
    sys.exit(1)
