import numpy as np

def compute_M_rem(M_ZAMS, Z):
    """
    根据附录C中的公式计算最终致密残留物质量 M_rem
    
    参数：
    M_ZAMS : float
        零龄主序质量（以太阳质量为单位）
    Z : float
        金属丰度
    
    返回：
    float
        致密残留物质量 M_rem（以太阳质量为单位）
    """
    
    # 1. 首先计算 M_CO 作为 M_ZAMS 和 Z 的函数
    def compute_M_CO(M_ZAMS, Z):
        def g(x, y, delta):
            return 0.5 / (1 + 10**((x - M_ZAMS) * delta))
        
        # 选择系数
        if Z > 4.0e-3:
            B1 = 59.63 - 2.969e3 * Z + 4.988e4 * Z**2
            K1 = 45.04 - 2.176e3 * Z + 3.806e4 * Z**2
            K2 = 1.389e2 - 4.664e3 * Z + 5.106e4 * Z**2
            delta1 = 2.790e-2 - 1.780e-2 * Z + 77.05 * Z**2
            delta2 = 6.730e-3 + 2.690 * Z - 52.39 * Z**2
        elif 1.0e-3 <= Z <= 4.0e-3:
            B1 = 40.98 + 3.415e4 * Z - 8.064e6 * Z**2
            K1 = 35.17 + 1.548e4 * Z - 3.759e6 * Z**2
            K2 = 20.36 + 1.162e5 * Z - 2.276e7 * Z**2
            delta1 = 2.500e-2 - 4.346 * Z + 1.340e3 * Z**2
            delta2 = 1.750e-2 + 11.39 * Z - 2.902e3 * Z**2
        else:  # Z < 1.0e-3
            B1 = 67.07
            K1 = 46.89
            K2 = 1.138e2
            delta1 = 2.199e-2
            delta2 = 2.602e-2
        
        # 计算 M_CO
        g1 = g(K1, delta1, delta1)
        g2 = g(K2, delta2, delta2)
        M_CO = -2.0 + (B1 + 2.0) * (g1 + g2)
        return M_CO
    
    # 2. 计算 M_rem
    M_CO = compute_M_CO(M_ZAMS, Z)
    
    if Z <= 5.0e-4:
        # 公式 C1-C3
        def p(M_CO):
            return -2.333 + 0.1559 * M_CO + 0.2700 * M_CO**2
        
        def f(M_CO, Z):
            m = -6.476e2 * Z + 1.911
            q = 2.300e3 * Z + 11.67
            return m * M_CO + q
        
        if M_CO <= 5.0:
            M_rem = max(p(M_CO), 1.27)
        elif 5.0 < M_CO < 10.0:
            M_rem = p(M_CO)
        else:  # M_CO >= 10.0
            M_rem = min(p(M_CO), f(M_CO, Z))

    else: # Z > 5e-4
        # 公式 C4-C10
        def h(M_CO, Z):
            if Z >= 1.0e-3:
                A1 = 1.340 - 29.46 / (1 + (Z / 1.110e-3)**2.361)
                A2 = 80.22 - 74.73 * (Z**0.965) / (2.720e-3 + Z**0.965)
                L = 5.683 + 3.533 / (1 + (Z / 7.430e-3)**1.993)
                eta = 1.066 - 1.121 / (1 + (Z / 2.558e-2)**0.609)
            else: # Z < 1e-3
                A1 = 1.105e5 * Z - 1.258e2
                A2 = 91.56 - 1.957e4 * Z - 1.558e7 * Z**2
                L = 1.134e4 * Z - 2.143
                eta = 3.090e-2 - 22.30 * Z + 7.363e4 * Z**2
            
            return A1 + (A2 - A1) / (1 + 10**((L - M_CO) * eta))
        
        def f(M_CO, Z):
            if Z >= 2.0e-3:
                m = 1.217
                q = 1.061
            elif 1.0e-3 <= Z < 2.0e-3:
                m = -43.82 * Z + 1.304
                q = -1.296e4 * Z + 26.98
            else:  # 5.0e-4 < Z < 1.0e-3
                m = -6.476e2 * Z + 1.911
                q = 2.300e3 * Z + 11.67
            
            return m * M_CO + q
        
        if M_CO <= 5.0:
            M_rem = max(h(M_CO, Z), 1.27)
        elif 5.0 < M_CO < 10.0:
            M_rem = h(M_CO, Z)
        else:  # M_CO >= 10.0
            M_rem = max(h(M_CO, Z), f(M_CO, Z))
    
    return M_rem

# 示例使用
if __name__ == "__main__":
    # 测试不同参数
    test_cases = [
        (20.0, 0.02),  # M_ZAMS=20太阳质量, Z=0.02
        (30.0, 0.002), # M_ZAMS=30太阳质量, Z=0.002
        (50.0, 0.0002),# M_ZAMS=50太阳质量, Z=0.0002
        (100.0, 0.0001)# M_ZAMS=100太阳质量, Z=0.0001
    ]
    
    for M_ZAMS, Z in test_cases:
        M_rem = compute_M_rem(M_ZAMS, Z)
        print(f"M_ZAMS={M_ZAMS} M☉, Z={Z:.4f} => M_rem={M_rem:.2f} M☉")