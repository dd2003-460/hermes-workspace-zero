#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
GW_ORF_研究项目 —— 环境依赖检查与自检脚本
================================================================================
用途：在本地新环境部署本项目前，运行一遍这个脚本，它会：
  1. 检查 Python 版本是否满足要求
  2. 检查/报告所需第三方库（numpy, scipy, sympy, mpmath）是否已安装、版本是否可用
  3. 对每个库的关键功能做一次"冒烟测试"（不只是import成功，还要跑一个真实小计算）
  4. 从项目内随机抽取几个关键脚本实际跑一遍，确认整条依赖链路真的可用
  5. 给出清晰的"下一步该做什么"提示（如果有问题）

用法：
    python3 setup_check.py            # 只检查，不自动安装
    python3 setup_check.py --install  # 检查后，自动用pip安装缺失/版本过低的库

不需要任何命令行参数也可以直接运行，脚本本身不会修改系统环境（除非显式传 --install）。
================================================================================
"""
import sys
import subprocess
import importlib
import os

# ---- 项目要求的最低版本 (基于开发时实际使用的版本，留了向下兼容的余量) ----
REQUIRED_PACKAGES = {
    "numpy":  "1.20",
    "scipy":  "1.7",
    "sympy":  "1.10",
    "mpmath": "1.2",
}
REQUIRED_PYTHON = (3, 8)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def color(text, c):
    # 部分终端(比如某些Windows cmd)不支持颜色转义，出错也不影响功能，直接try
    try:
        return f"{c}{text}{RESET}"
    except Exception:
        return text


def print_header(title):
    print("\n" + "=" * 78)
    print(BOLD + title + RESET)
    print("=" * 78)


def check_python_version():
    print_header("第1步：检查 Python 版本")
    v = sys.version_info
    print(f"当前 Python 版本: {v.major}.{v.minor}.{v.micro}")
    if (v.major, v.minor) >= REQUIRED_PYTHON:
        print(color(f"  ✅ 满足最低要求 (>= {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]})", GREEN))
        return True
    else:
        print(color(f"  ❌ 版本过低，项目要求 Python >= {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}", RED))
        print("     请安装更新版本的 Python 后重试。")
        return False


def parse_version(vstr):
    """把版本字符串解析成可比较的tuple，容错处理非标准版本号"""
    parts = []
    for p in vstr.split("."):
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def check_package(name, min_version):
    """返回 (是否已安装, 是否版本满足, 已安装版本字符串或None)"""
    try:
        mod = importlib.import_module(name)
        installed_version = getattr(mod, "__version__", "未知")
        if installed_version == "未知":
            return True, True, installed_version  # 装了但拿不到版本号，姑且放行
        ok = parse_version(installed_version) >= parse_version(min_version)
        return True, ok, installed_version
    except ImportError:
        return False, False, None


def check_all_packages():
    print_header("第2步：检查第三方库")
    missing = []
    outdated = []
    for name, min_v in REQUIRED_PACKAGES.items():
        installed, ok, version = check_package(name, min_v)
        if not installed:
            print(color(f"  ❌ {name:10s}  未安装  (需要 >= {min_v})", RED))
            missing.append(name)
        elif not ok:
            print(color(f"  ⚠️  {name:10s}  已安装 {version}，低于要求的 {min_v}", YELLOW))
            outdated.append(name)
        else:
            print(color(f"  ✅ {name:10s}  已安装 {version}", GREEN))
    return missing, outdated


def install_packages(pkg_list):
    if not pkg_list:
        return True
    print_header(f"正在自动安装/升级: {', '.join(pkg_list)}")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + pkg_list
    print("执行命令:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(color("  ✅ 安装/升级完成", GREEN))
        return True
    else:
        print(color("  ❌ 安装失败，请检查网络连接或pip配置，也可尝试手动运行上面的命令", RED))
        return False


def smoke_test_numpy():
    import numpy as np
    a = np.array([1.0, 2.0, 3.0])
    assert abs(np.sum(a) - 6.0) < 1e-10
    z = np.exp(1j * np.pi)
    assert abs(z - (-1.0)) < 1e-10


def smoke_test_scipy():
    from scipy import integrate
    val, _ = integrate.quad(lambda x: x**2, 0, 1)
    assert abs(val - 1/3) < 1e-8


def smoke_test_sympy():
    import sympy as sp
    x = sp.symbols('x')
    expr = sp.expand((x + 1)**2)
    assert expr == x**2 + 2*x + 1
    # 测试项目里大量用到的 residue（留数）功能是否可用
    z = sp.symbols('z')
    res = sp.residue(1/z, z, 0)
    assert res == 1


def smoke_test_mpmath():
    import mpmath
    val = mpmath.ei(1.0)
    assert abs(float(val) - 1.8951178163559366) < 1e-6


def run_smoke_tests():
    print_header("第3步：功能冒烟测试（不只检查是否装了，还要跑一遍真实计算）")
    tests = [
        ("numpy 基础运算 + 复数指数", smoke_test_numpy),
        ("scipy 数值积分 (integrate.quad)", smoke_test_scipy),
        ("sympy 符号运算 + 留数计算 (residue)", smoke_test_sympy),
        ("mpmath 指数积分函数 (ei)", smoke_test_mpmath),
    ]
    all_pass = True
    for name, func in tests:
        try:
            func()
            print(color(f"  ✅ {name}", GREEN))
        except Exception as e:
            print(color(f"  ❌ {name}  —— 出错: {e}", RED))
            all_pass = False
    return all_pass


# ---- 抽取几个有代表性、跑得快的关键脚本，实际运行一遍确认整条链路可用 ----
SAMPLE_SCRIPTS = [
    "手征ORF计算_主线/阶段1_单向链路ORF核心积分/组件A_基础设施_坐标系与被积核/推导/01_坐标变换公式_PRD附录A复现.py",
    "手征ORF计算_主线/阶段1_单向链路ORF核心积分/组件B_I1积分的留数分量/R0/具体计算/01_用sympy_residue求解三阶极点留数.py",
    "手征ORF计算_主线/阶段1_单向链路ORF核心积分/组件E_核心发现与跨组件规律/01_核心发现_z1z2处的minus_i比例关系.py",
    "PRD强度ORF复现_副本/阶段2_ORF组装_GammaOne/组件A_强度版GammaOneI/具体计算/01_PTA极限退化为HellingsDowns曲线.py",
]


def run_sample_scripts():
    print_header("第4步：实际运行几个代表性脚本（验证整条依赖链路真的能跑通）")
    project_root = os.path.dirname(os.path.abspath(__file__))
    all_ok = True
    for rel_path in SAMPLE_SCRIPTS:
        full_path = os.path.join(project_root, rel_path)
        script_dir = os.path.dirname(full_path)
        script_name = os.path.basename(full_path)
        if not os.path.exists(full_path):
            print(color(f"  ⚠️  跳过（文件不存在，可能是路径变化）: {rel_path}", YELLOW))
            continue
        print(f"  运行: {rel_path}")
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(color(f"    ✅ 成功退出 (耗时正常)", GREEN))
        else:
            print(color(f"    ❌ 运行出错 (退出码 {result.returncode})", RED))
            print("    ---- 错误输出 ----")
            print("    " + result.stderr.strip().replace("\n", "\n    ")[-800:])
            all_ok = False
    return all_ok


def main():
    do_install = "--install" in sys.argv

    print(BOLD + "\n" + "#" * 78)
    print("#  GW_ORF_研究项目 环境自检脚本")
    print("#" * 78 + RESET)

    py_ok = check_python_version()
    if not py_ok:
        print(color("\n❌ Python 版本不满足要求，无法继续。请先升级 Python。", RED))
        sys.exit(1)

    missing, outdated = check_all_packages()

    if (missing or outdated) and do_install:
        install_packages(missing + outdated)
        print("\n重新检查安装结果:")
        missing, outdated = check_all_packages()

    if missing or outdated:
        print_header("检测到缺失/版本过低的依赖")
        need = missing + outdated
        print(color(f"  以下库需要安装或升级: {', '.join(need)}", YELLOW))
        print(f"  请运行:  pip install --upgrade {' '.join(need)}")
        print(f"  或者直接重新运行本脚本并加上 --install 参数:")
        print(f"      python3 setup_check.py --install")
        print(color("\n⚠️  依赖不完整，跳过后续冒烟测试和脚本运行环节。", YELLOW))
        sys.exit(1)

    smoke_ok = run_smoke_tests()
    if not smoke_ok:
        print(color("\n❌ 部分库的功能测试未通过，环境可能存在异常（比如损坏的安装），"
                     "请尝试重新安装对应的库。", RED))
        sys.exit(1)

    scripts_ok = run_sample_scripts()

    print_header("检查结果汇总")
    if scripts_ok:
        print(color("🎉 全部检查通过！环境已就绪，可以运行本项目下的全部脚本。", GREEN))
        print("\n提示：")
        print("  - 各脚本都是自包含的，进入对应文件夹后直接 `python3 脚本名.py` 即可运行")
        print("  - 建议按 阶段 → 组件 → (推导/具体计算/数值验证) 的顺序阅读/运行")
        print("  - 总入口文档: README.md，各组件说明见对应文件夹下的 说明.md")
        sys.exit(0)
    else:
        print(color("⚠️  依赖库本身没问题，但部分示例脚本运行时出错，请查看上面的错误详情。", YELLOW))
        print("  常见原因：某些脚本依赖同目录下的.pkl中间文件，若单独复制脚本到别处"
              "运行可能会找不到文件——请保持完整目录结构。")
        sys.exit(2)


if __name__ == "__main__":
    main()
