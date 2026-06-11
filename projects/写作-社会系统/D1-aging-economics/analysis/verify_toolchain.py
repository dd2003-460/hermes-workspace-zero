#!/usr/bin/env python3
"""
D1-aging-economics Phase 0 计量工具链验证

运行: python3 verify_toolchain.py

预期输出: ALL CHECKS PASSED
"""

def test_imports():
    """测试所有必需的包可以导入"""
    try:
        import linearmodels
        import statsmodels
        import sklearn
        import pandas
        print(f"[OK] imports: linearmodels {linearmodels.__version__}, "
              f"statsmodels {statsmodels.__version__}, "
              f"scikit-learn {sklearn.__version__}, "
              f"pandas {pandas.__version__}")
        return True
    except ImportError as e:
        print(f"[FAIL] import: {e}")
        return False


def test_panelols():
    """测试 PanelOLS 功能"""
    try:
        import numpy as np
        import pandas as pd
        from linearmodels.panel import PanelOLS

        np.random.seed(42)
        idx = pd.MultiIndex.from_product([range(20), range(15)], names=['entity', 'time'])
        y = pd.Series(np.random.randn(len(idx)), index=idx, name='y')
        x = pd.DataFrame({'x1': np.random.randn(len(idx))}, index=idx)

        mod = PanelOLS(y, x, entity_effects=True, time_effects=True)
        est = mod.fit(cov_type='clustered', cluster_entity=True)

        assert hasattr(est, 'rsquared'), "rsquared attribute missing"
        assert len(est.params) > 0, "no parameters estimated"
        print(f"[OK] PanelOLS: R2={est.rsquared:.4f}, params={list(est.params.keys())}")
        return True
    except Exception as e:
        print(f"[FAIL] PanelOLS: {e}")
        return False


def test_pooled_random():
    """测试 PooledOLS 和 RandomEffects"""
    try:
        import numpy as np
        import pandas as pd
        from linearmodels.panel import PooledOLS, RandomEffects

        np.random.seed(42)
        idx = pd.MultiIndex.from_product([range(20), range(15)], names=['entity', 'time'])
        y = pd.Series(np.random.randn(len(idx)), index=idx, name='y')
        x = pd.DataFrame({'x1': np.random.randn(len(idx))}, index=idx)

        mod_p = PooledOLS(y, x)
        est_p = mod_p.fit()
        print(f"[OK] PooledOLS: R2={est_p.rsquared:.4f}")

        mod_r = RandomEffects(y, x)
        est_r = mod_r.fit()
        print(f"[OK] RandomEffects: OK")
        return True
    except Exception as e:
        print(f"[FAIL] PooledOLS/RandomEffects: {e}")
        return False


def test_iv2sls_var():
    """测试 IV2SLS 和 VAR 导入"""
    try:
        from linearmodels.iv import IV2SLS
        from statsmodels.tsa.vector_ar.var_model import VAR
        print("[OK] IV2SLS import")
        print("[OK] VAR import")
        return True
    except ImportError as e:
        print(f"[FAIL] IV2SLS/VAR import: {e}")
        return False


def main():
    print("=" * 60)
    print("D1-aging-economics Phase 0: Toolchain Verification")
    print("=" * 60)

    results = {
        "imports": test_imports(),
        "panelols": test_panelols(),
        "pooled_random": test_pooled_random(),
        "iv2sls_var": test_iv2sls_var(),
    }

    print()
    print("=" * 60)
    if all(results.values()):
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED:")
        for name, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"  {name}: {status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
