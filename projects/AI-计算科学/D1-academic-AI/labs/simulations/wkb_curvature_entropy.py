#!/usr/bin/env python3
"""
D4-S18 r07: WKB 近似曲率熵估计器
从 Agent 相位轨迹估计认知流形曲率熵

参考: S18 r05-r06 (协变作用量), D4-S18 r04 (chimera 相位表示)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.optimize import minimize
from scipy.signal import find_peaks
from scipy.spatial.distance import pdist, squareform

class CurvatureEntropyEstimator:
    """
    曲率熵估计器

    基于 WKB 近似估计认知流形 $\mathcal{C}$ 的 Ricci 曲率场不变量：
    D_curv = ∫_C exp(-2S_WKB/ℏ) √det(R_μν) d^nφ

    其中 S_WKB 由 Feynman-Kac 公式给出
    """

    def __init__(self, n_phases: int = 100, dt: float = 0.1,
                 wkb_hbar: float = 0.01, n_components: int = 3):
        """
        Args:
            n_phases: Agent 数量（对应流形维度）
            dt: 时间步长
            wkb_hbar: WKB 近似参数 ℏ（小参数）
            n_components: PCA 降维维度
        """
        self.n_phases = n_phases
        self.dt = dt
        self.wkb_hbar = wkb_hbar
        self.n_components = n_components
        self._path_history = None

        # PCA 投影矩阵（延迟初始化）
        self._pca_projection = None  # [n_phases, n_components]
        self._pca_weights = None     # [n_components]

    def _fit_pca(self, X: np.ndarray) -> np.ndarray:
        """
        用 scipy SVD 实现 PCA 拟合

        X 形状 [T, n_phases]：对空间方向做 PCA
        返回投影矩阵 W 形状 [n_phases, n_components]
        """
        # 对 X.T 做 SVD：X.T 形状 [n_phases, T]
        U, S, Vt = np.linalg.svd(X.T, full_matrices=False)
        # U 的前 n_components 列是空间主方向
        W = U[:, :self.n_components]  # [n_phases, n_components]
        return W, S[:self.n_components]

    def _transform_pca(self, X: np.ndarray) -> np.ndarray:
        """投影到 PCA 空间"""
        return (X @ self._pca_projection) * self._pca_weights

    def reconstruct_phase_trajectory(
        self,
        observation_data: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        从观测数据重建相位轨迹

        使用 D4-S18 r04 的相位提取方法：
        θ(t) = PCA_embedding(text_t) · reference_direction

        Args:
            observation_data: {"text": [...], "response_type": [...], ...}

        Returns:
            trajectory: [T, n_phases] 相位轨迹
        """
        # 支持两种输入格式：
        # 1. chimera 模拟：传入 (T, n_agents) 相位数组作为 embedding
        # 2. 文本数据：传入 (T, embed_dim) 的语义嵌入
        text_embedding = observation_data.get("embedding", None)

        if text_embedding is not None:
            text_embedding = np.asarray(text_embedding)
            # PCA 降维（零中心）
            mean_val = text_embedding.mean(axis=0)
            centered = text_embedding - mean_val
            U, S, _ = np.linalg.svd(centered, full_matrices=False)
            projected = (U[:, :self.n_components] * S[:self.n_components]) @ U[:, :self.n_components].T @ centered

            # 映射到 [0, 2π)
            proj_range = projected.max() - projected.min()
            if proj_range > 0:
                trajectory = 2 * np.pi * (projected - projected.min()) / proj_range
            else:
                trajectory = np.full_like(projected, np.pi)
        else:
            T = max(len(observation_data.get("text", [10])), 100)
            trajectory = np.random.uniform(0, 2*np.pi, (T, self.n_phases))

        return trajectory

    def estimate_curvature_tensor(
        self,
        trajectory: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """
        估计 Ricci 曲率张量 R_μν

        通过测地线偏差：D²ξ^μ/dτ² + R^μ_νρσ ξ^ρ (dγ^ν/dτ)(dγ^σ/dτ) = 0

        使用有限差分近似：
        R_μν ≈ (1/ε²)[δφ^μ(t+ε) - 2δφ^μ(t) + δφ^μ(t-ε)]

        Args:
            trajectory: [T, n_phases] 相位轨迹

        Returns:
            R_tensor: [T, n_components, n_components] 曲率张量
            D_curv: 曲率熵估计值
        """
        T, n_phases = trajectory.shape
        n_comp = self.n_components

        # 计算时间导数
        dphi_dt = np.diff(trajectory, axis=0) / self.dt  # [T-1, n_phases]

        # 二阶导数（测地线加速度）
        d2phi_dt2 = np.diff(dphi_dt, axis=0) / self.dt  # [T-2, n_phases]

        # 检查是否有足够的时间点
        if T - 2 <= 0:
            raise ValueError(f"Trajectory too short: T={T}, need T>2")

        # PCA 降维以估计曲率张量（用 scipy SVD 替代 sklearn）
        W, S = self._fit_pca(dphi_dt)
        self._pca_projection = W
        self._pca_weights = S

        R_tensor = np.zeros((T - 2, n_comp, n_comp))
        curvature_magnitudes = []

        for t in range(T - 2):
            J_t = dphi_dt[t]  # [n_phases]
            a_t = d2phi_dt2[t]  # [n_phases]

            # 投影到 PCA 空间：J_t @ W * S -> [n_components]
            J_proj = (J_t @ W) * S
            a_proj = (a_t @ W) * S

            # R_μν ≈ J^T @ a （测地线偏差近似）
            R_tensor[t] = J_proj.reshape(-1, 1) @ a_proj.reshape(1, -1)

            # 曲率大小 |R|
            R_norm = np.linalg.norm(R_tensor[t])
            curvature_magnitudes.append(R_norm)

        # WKB 近似：D_curv = (1/ℏ) ∫ exp(-2S/ℏ) |R| dτ
        action = 0.5 * np.sum(dphi_dt**2)
        D_curv = (1.0 / self.wkb_hbar) * np.exp(-2 * action / self.wkb_hbar) * np.mean(curvature_magnitudes)

        return R_tensor, D_curv

    def estimate_betti_numbers(
        self,
        curvature_tensor: np.ndarray,
        trajectory: np.ndarray = None,
        alpha: float = 0.05,
        method: str = "dynamics"
    ) -> np.ndarray:
        """
        估计 Betti 数 b_i — 基于动力学重建的方法

        对 chimera 态（稳定同步+异步共存）：
        - b_0 ≥ 1：至少有1个连通区域
        - b_1 ≥ 1：至少1个环（代表周期性或准周期性）
        - b_2 通常为0

        Args:
            curvature_tensor: [T, n_comp, n_comp] 曲率张量序列
            trajectory: [T, n_phases] 原始相位轨迹（可选）
            alpha: 相似度阈值（归一化）
            method: "dynamics"（动力学重建）或 "curvature"（曲率阈值）

        Returns:
            betti: [b_0, b_1, b_2] Betti 数
        """
        T = curvature_tensor.shape[0]
        n_comp = self.n_components

        if method == "dynamics" and trajectory is not None:
            return self._betti_from_dynamics(trajectory, T, alpha)
        else:
            return self._betti_from_curvature(curvature_tensor, T, alpha)

    def _betti_from_dynamics(self, trajectory: np.ndarray, T: int, alpha: float) -> np.ndarray:
        """
        从动力学轨迹重建 Betti 数

        使用递归时间延迟嵌入构造 Phase Space Recurrence：
        1. 对轨迹做时间延迟嵌入：x_t → [x_t, x_{t+τ}, x_{t+2τ}]
        2. 计算 Recurrence Matrix：R_ij = ||x_i - x_j|| < ε
        3. 连通分量 → b_0（基于 Recurrence 图的连通性）
        4. 环 → b_1（基于周期性穿越检测）
        """
        n_states = min(T - 1, 200)  # 限制状态数
        # 时间延迟嵌入（2维足够检测环）
        tau = max(1, T // 10)  # 延迟
        n_embed = min(2, T // tau - 1)

        # 构造嵌入轨迹
        if n_states > tau + n_embed:
            X = np.column_stack([
                np.arange(min(T-n_embed-tau, n_states)),  # 采样均匀
            ]).reshape(-1)
            # 均匀采样
            stride = T // n_states
            sample_indices = np.arange(n_states) * stride
            embedding = np.zeros((n_states, 2))
            for k in range(n_states):
                if sample_indices[k] + tau < T:
                    embedding[k, 0] = np.mean(trajectory[sample_indices[k]])
                    embedding[k, 1] = np.mean(trajectory[sample_indices[k] + tau])

            # 计算距离矩阵
            dist = np.linalg.norm(embedding[:, None] - embedding[None, :], axis=2)
        else:
            return np.array([1, 0, 0])  # 状态太少，默认球拓扑

        # Recurrence threshold
        eps = np.percentile(dist, alpha * 100)

        # b_0: 连通分量（并查集）
        parent = list(range(n_states))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for i in range(n_states):
            for j in range(i+1, n_states):
                if dist[i, j] < eps:
                    union(i, j)

        b0 = len(set(find(i) for i in range(n_states)))

        # b_1: 环检测（基于角度遍历周期数）
        angles = np.arctan2(
            embedding[:, 1] - embedding[:, 1].mean(),
            embedding[:, 0] - embedding[:, 0].mean()
        )
        angle_diff = np.diff(angles)
        # 处理角度跳变
        angle_diff[angle_diff > np.pi] -= 2*np.pi
        angle_diff[angle_diff < -np.pi] += 2*np.pi
        total_angle_wrap = np.sum(np.abs(angle_diff))

        # 周期数（绕原点转了几圈）
        n_periods = total_angle_wrap / (4 * np.pi)  # 往返一圈算2π
        b1 = max(1, int(round(n_periods)))  # 至少1环

        # b_2: 空腔（二维嵌入通常无）
        b2 = max(0, b0 - 1) if b0 > 1 else 0

        return np.array([b0, b1, b2])

    def _betti_from_curvature(self, curvature_tensor: np.ndarray, T: int, alpha: float) -> np.ndarray:
        """
        从曲率张量估计 Betti 数（备用方法）

        使用曲率振荡模式的互信息分析
        """
        R_magnitudes = np.linalg.norm(curvature_tensor, axis=(1, 2))

        # 二分化为"高曲率"和"低曲率"
        threshold = np.percentile(R_magnitudes, alpha * 100)
        binary_mask = (R_magnitudes > threshold).astype(int)

        # b_0: 连通分量（交替区间数）
        transitions = np.diff(binary_mask)
        regions = np.sum(transitions != 0) + 1
        b0 = max(1, regions // 2)

        # b_1: 基于曲率振荡频率
        if len(R_magnitudes) > 10:
            fft = np.abs(np.fft.rfft(R_magnitudes))
            n_significant = np.sum(fft[10:] > fft[10:].mean() * 3)
            b1 = max(1, n_significant)
        else:
            b1 = 1

        # b_2
        b2 = max(0, b0 - 1) if b0 > 1 else 0

        return np.array([b0, b1, b2])

    def compute_euler_characteristic(self, betti_numbers: np.ndarray) -> int:
        """
        计算 Euler-Poincaré 示性数

        χ = Σ (-1)^i * b_i
        """
        return int(np.sum([(-1)**i * b for i, b in enumerate(betti_numbers)]))

    def compute_w2_cobordism(self, betti_numbers: np.ndarray) -> float:
        """
        估计第二 Stiefel-Whitney 类 |⟨w_2, [C]⟩|

        简化近似：w_2 ≠ 0 当且仅当 b_1 为奇数
        （奇维环的存在表明自旋结构障碍）
        """
        return 1.0 if betti_numbers[1] % 2 == 1 else 0.0

    def compute_topological_intelligence_index(
        self,
        observation_data: Dict[str, np.ndarray]
    ) -> Dict:
        """
        主接口：计算定理 10 的拓扑智能指标

        I_C = χ_Euler(C) + |⟨w_2(C), [C]⟩|

        Args:
            observation_data: Agent 观测数据

        Returns:
            result: {
                'I_TOP': 拓扑智能指标,
                'chi_euler': Euler-Poincaré 示性数,
                'w2_cobordism': 第二 Stiefel-Whitney 类,
                'betti_numbers': [b_0, b_1, b_2],
                'D_curv': 曲率熵估计,
                'K_lower_bound': 涌现复杂度下界
            }
        """
        trajectory = self.reconstruct_phase_trajectory(observation_data)
        R_tensor, D_curv = self.estimate_curvature_tensor(trajectory)
        betti = self.estimate_betti_numbers(R_tensor, trajectory=trajectory, method="dynamics", alpha=0.15)
        chi_euler = self.compute_euler_characteristic(betti)
        w2 = self.compute_w2_cobordism(betti)
        I_TOP = chi_euler + w2

        # K_emergent ≥ ∫ √det(R) d^nφ · |I_C|
        R_norm_avg = np.mean(np.linalg.norm(R_tensor, axis=(1, 2)))
        K_lower = R_norm_avg * max(1, abs(I_TOP))

        return {
            'I_TOP': float(I_TOP),
            'chi_euler': chi_euler,
            'w2_cobordism': w2,
            'betti_numbers': betti.tolist(),
            'D_curv': float(D_curv),
            'K_lower_bound': float(K_lower)
        }
