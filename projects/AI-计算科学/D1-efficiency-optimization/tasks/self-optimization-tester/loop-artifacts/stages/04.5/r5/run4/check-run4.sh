#!/usr/bin/env bash
# R5 run4 终态判定脚本（判定标准事先写死；执行者禁改；Lead 执行后复验 sha256）
# 用例: case1 求和 6.75 / case2 负数 9.00 / case3 浮点 0.60 / case4 缺列非零退出
set -u
WORK="$(cd "$(dirname "$0")/work" && pwd)"
SOL="$WORK/sum_col.py"
FAIL=0
if [ ! -f "$SOL" ]; then echo "FAIL: sum_col.py missing"; exit 2; fi
T=$(mktemp -d)
cat > "$T/c1.csv" <<'EOF'
a,b,c
1,x,1.5
2,y,2.25
3,z,3
EOF
cat > "$T/c2.csv" <<'EOF'
p,q
10,r
-4,s
3,t
EOF
cat > "$T/c3.csv" <<'EOF'
u
0.1
0.2
0.3
EOF
o1=$(python3 "$SOL" "$T/c1.csv" c 2>&1); r1=$?
o2=$(python3 "$SOL" "$T/c2.csv" p 2>&1); r2=$?
o3=$(python3 "$SOL" "$T/c3.csv" u 2>&1); r3=$?
o4=$(python3 "$SOL" "$T/c1.csv" z 2>&1); r4=$?
check() { if [ "$1" -eq 0 ] && [ "$2" = "$3" ]; then echo "PASS case$4 ($2)"; else echo "FAIL case$4 (got[$2] want[$3] rc=$1)"; FAIL=1; fi; }
check "$r1" "$o1" "6.75" 1
check "$r2" "$o2" "9.00" 2
check "$r3" "$o3" "0.60" 3
if [ "$r4" -ne 0 ]; then echo "PASS case4 (rc=$r4 nonzero as expected)"; else echo "FAIL case4 (expected nonzero rc, got 0)"; FAIL=1; fi
rm -rf "$T"
exit "$FAIL"
