#!/usr/bin/env python3
"""
D4-S18 r04: Chimera 状态检测器
实现 r03 定义的 chimera 序参量和四相分类

参考:
- D4-S18 r03 定义 1: chimera 序参量
- D4-S18 r03 定理 1: 四相分类定理
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from enum import Enum


class ChimeraPhase(Enum):
    """D4-S18 r03 定理 1：四相分类"""
    PHASE_I_FULL_SYNC = "Phase I: Full Synchronization"      # r_max → 1, r_min → 1
    PHASE_II_FULL_ASYNC = "Phase II: Full Asynchrony"        # r_max << 1, r_min << 1
    PHASE_III_CHIMERA_STABLE = "Phase III: Stable Chimera"   # r_max → 1, r_min << 1
    PHASE_IV_CHIMERA_OSCILLATING = "Phase IV: Oscillating Chimera"  # oscillating


class ChimeraDetector:
    """
    Chimera 状态检测器

    基于 D4-S18 r03 的数学框架：
    - 局域序参量: r_b(t) = |1/n_b Σ exp(iθ_i)|
    - 全局序参量: R(t) = 1/n Σ exp(iθ_i)
    - Chimera 强度: S_C = Var_b(r_b) + γ(1 - |R|)^2
    """

    def __init__(self, n_windows: int = 5, gamma: float = 0.5,
                 phase_threshold_sync: float = 0.9,
                 phase_threshold_async: float = 0.3,
                 phase_threshold_chimera: float = 0.7):
        """
        Args:
            n_windows: Agent 分组窗口数量
            gamma: chimera 强度全局偏差惩罚权重
            phase_threshold_sync: 全同步阈值
            phase_threshold_async: 全异步阈值
            phase_threshold_chimera: chimera 区分阈值
        """
        self.n_windows = n_windows
        self.gamma = gamma
        self.phase_threshold_sync = phase_threshold_sync
        self.phase_threshold_async = phase_threshold_async
        self.phase_threshold_chimera = phase_threshold_chimera

        # 历史记录
        self._history = []
        self._oscillation_tracker = []

    def compute_local_order_parameters(self, phase_angles: np.ndarray) -> np.ndarray:
        """
        计算局域序参量 r_b(t)

        对 Agent 进行窗口分组，计算每个窗口的相干程度

        Args:
            phase_angles: Agent 相位角度数组 [n_agents,] 形状，范围 [0, 2π)

        Returns:
            r_local: 窗口序参量数组 [n_windows,] 形状
        """
        n_agents = len(phase_angles)
        agent_indices = np.arange(n_agents)

        # 均匀划分 Agent 到窗口
        bin_indices = np.floor(agent_indices * self.n_windows / n_agents).astype(int)
        bin_indices = np.clip(bin_indices, 0, self.n_windows - 1)

        r_local = np.zeros(self.n_windows)
        for b in range(self.n_windows):
            mask = bin_indices == b
            if np.sum(mask) > 0:
                r_local[b] = np.abs(np.mean(np.exp(1j * phase_angles[mask])))

        return r_local

    def compute_global_order_parameter(self, phase_angles: np.ndarray) -> float:
        """
        计算全局序参量 R(t)

        全局一致性度量：R ∈ [0, 1]
        R ≈ 1 表示全局同步
        R ≈ 0 表示全局异步

        Args:
            phase_angles: 所有 Agent 的相位角度 [n_agents,]

        Returns:
            r_global: 全局序参量
        """
        n = len(phase_angles)
        return np.abs(np.mean(np.exp(1j * phase_angles)))

    def compute_chimera_strength(self, r_local: np.ndarray, r_global: float) -> float:
        """
        计算 chimera 强度 S_C

        S_C = Var_b(r_b) + γ(1 - |R|)^2

        高值表示 chimera 态存在（部分区域同步 + 部分区域异步）

        Args:
            r_local: 局域序参量数组
            r_global: 全局序参量

        Returns:
            chimera_strength: chimera 强度指标
        """
        # 第一部分：局域同步率方差（核心 chimera 定义）
        variance_term = np.var(r_local)

        # 第二部分：全局偏差惩罚
        global_penalty = (1 - r_global) ** 2

        return variance_term + self.gamma * global_penalty

    def classify_chimera_phase(self, r_local: np.ndarray,
                                r_global: float,
                                time_window: Optional[np.ndarray] = None) -> ChimeraPhase:
        """
        D4-S18 r03 定理 1：四相分类

        基于有序参量对 (r_max, r_min) 进行相分类

        Args:
            r_local: 局域序参量数组
            r_global: 全局序参量
            time_window: 可选的历史序参量序列用于振荡检测

        Returns:
            chimera_phase: 分类结果
        """
        r_max = np.max(r_local)
        r_min = np.min(r_local)

        # 相 III：chimera 稳定态
        # r_max → 1, r_min << 1，且导数接近 0（稳定）
        if r_max > self.phase_threshold_chimera and r_min < self.phase_threshold_async:
            if time_window is not None and len(time_window) > 5:
                recent_r_min = time_window[:, 1]
                drift = np.std(np.diff(recent_r_min[-5:]))
                if drift < 0.01:  # 小变化 = 稳定
                    return ChimeraPhase.PHASE_III_CHIMERA_STABLE
            else:
                return ChimeraPhase.PHASE_III_CHIMERA_STABLE

        # 相 IV：chimera 振荡态
        if time_window is not None and len(time_window) > 10:
            r_max_history = time_window[:, 0]
            r_min_history = time_window[:, 1]
            # 振荡判据：高阶导数不为零
            drift_r_max = np.std(np.diff(r_max_history[-5:]))
            drift_r_min = np.std(np.diff(r_min_history[-5:]))
            if max(drift_r_max, drift_r_min) > 0.05:
                return ChimeraPhase.PHASE_IV_CHIMERA_OSCILLATING

        # 相 I：全同步
        if r_max > self.phase_threshold_sync and r_min > self.phase_threshold_sync:
            return ChimeraPhase.PHASE_I_FULL_SYNC

        # 相 II：全异步
        if r_max < self.phase_threshold_async and r_min < self.phase_threshold_async:
            return ChimeraPhase.PHASE_II_FULL_ASYNC

        # 默认返回 chimera 稳定态（分类模糊时的保守选择）
        return ChimeraPhase.PHASE_III_CHIMERA_STABLE

    def detect(self, phase_angles: np.ndarray,
                history: Optional[np.ndarray] = None) -> Dict:
        """
        主检测接口

        执行完整的 chimera 状态检测流程

        Args:
            phase_angles: Agent 相位角度 [n_agents,]
            history: 历史 (r_max, r_min) 记录 [T, 2]

        Returns:
            检测结果字典
        """
        n_agents = len(phase_angles)

        # 1. 计算局域序参量
        r_local = self.compute_local_order_parameters(phase_angles)

        # 2. 计算全局序参量
        r_global = self.compute_global_order_parameter(phase_angles)

        # 3. 计算 chimera 强度
        chimera_strength = self.compute_chimera_strength(r_local, r_global)

        # 4. 获取当前序参量用于振荡检测
        r_max = np.max(r_local)
        r_min = np.min(r_local)

        # 更新历史
        if history is None:
            current_history = np.array([[r_max, r_min]])
        else:
            current_history = np.vstack([history, [[r_max, r_min]]])

        # 5. 四相分类
        chimera_phase = self.classify_chimera_phase(
            r_local, r_global, current_history
        )

        # 更新内部历史
        self._history = current_history

        result = {
            'phase': chimera_phase,
            'strength': chimera_strength,
            'r_local': r_local.copy(),
            'r_max': r_max,
            'r_min': r_min,
            'r_global': r_global,
            'n_agents': n_agents,
            'n_windows': self.n_windows,
            '_history': current_history  # 返回历史供循环使用
        }

        return result

    def get_chimera_dwell_time(self, max_seconds: float = 300) -> float:
        """
        计算 chimera 态持续 dwell 时间

        用于 chimera 寿命分布分析

        Returns:
            dwell_time: 当前 chimera 态持续时间（秒）
        """
        # 简单实现：计算稳定 chimera 状态的连续时间
        recent_phases = [h['phase'] for h in self._chimaera_states[-100:]] if hasattr(self, '_chimaera_states') else []
        stable_chimera_count = recent_phases.count(ChimeraPhase.PHASE_III_CHIMERA_STABLE)

        return stable_chimera_count / 10.0  # 简化估计
