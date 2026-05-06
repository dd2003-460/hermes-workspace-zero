#!/usr/bin/env python3
"""
Chimera 诊断 v2 — D4-S18-r23 双阶段认证协议

升级内容：
1. 添加梯度锁相排除层
2. 实现空间相干窗口不变量（SCI）
3. 实现时间涨落诊断（TFD）
4. 计算机制纯度指数（MPI）

理论参考：D4-S18-r23-chimera-diagnostic-formalization.md
"""

import numpy as np
import json
from typing import Tuple, Dict, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ChimeraDiagnostic:
    """Chimera 诊断结果"""
    phase: str  # "chimera", "gradient_locking", "mixed", "global", "asynchronous"
    mpi: float
    sci: float
    tfd: float
    confidence: float
    details: Dict


class ChimeraDiagnosticV2:
    """
    基于 D4-S18-r23 的双阶段 chimera 认证协议。
    """
    
    def __init__(self, n: int = 64, dt: float = 0.005,
                 n_segments: int = 4, seed: int = 42):
        self.n = n
        self.dt = dt
        self.n_segments = n_segments
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def kuramoto_step(self, theta: np.ndarray, k: float,
                      g: float, omega: np.ndarray) -> np.ndarray:
        """Kuramoto 耦合振子的一步演化"""
        phase_diff = np.add.outer(theta, theta)
        coupling = k * np.mean(np.sin(phase_diff + np.angle(np.exp(1j * (np.arange(self.n).reshape(-1, 1) - np.arange(self.n).reshape(1, -1)) * 2 * np.pi / self.n) * g)))
        return theta + self.dt * (omega + coupling)
    
    def uniform_kuramoto_step(self, theta: np.ndarray, k: float,
                              omega: np.ndarray) -> np.ndarray:
        """均匀耦合 Kuramoto"""
        N = len(theta)
        r = np.mean(np.exp(1j * theta))
        return theta + self.dt * (omega + k * r.imag * np.ones(N))
    
    def compute_segment_sync(self, theta: np.ndarray) -> np.ndarray:
        """将圆周分为扇区，计算每个扇区的平均同步率"""
        # 按空间位置分扇区
        angles = np.arange(self.n) * 2 * np.pi / self.n
        segments = np.linspace(0, 2 * np.pi, self.n_segments + 1)
        sync = np.zeros(self.n_segments)
        
        for s in range(self.n_segments):
            mask = (angles >= segments[s]) & (angles < segments[s + 1])
            seg_phases = theta[mask]
            if len(seg_phases) > 0:
                sync[s] = abs(np.mean(np.exp(1j * seg_phases)))
        return sync
    
    def compute_sci(self, theta: np.ndarray) -> float:
        """
        空间相干窗口不变量（SCI）。
        
        衡量空间同步率的均匀分布程度。
        SCI ≈ 0.3 表示梯度锁相（均匀分布）
        SCI > 0.8 或 < 0.1 表示真实 chimera（区域化）
        """
        sync = self.compute_segment_sync(theta)
        mu = np.mean(sync)
        sigma = np.std(sync)
        return sigma / (mu + 1e-10)
    
    def compute_tfd(self, theta_history: List[np.ndarray]) -> float:
        """
        时间涨落诊断（TFD）。
        
        衡量同步率场的随时间演化程度。
        TFD ≈ 0 表示梯度锁相（稳态锁定）
        TFD > 0 表示真实 chimera（有动力学涨落）
        """
        if len(theta_history) < 2:
            return 0.0
        
        sync_history = [self.compute_segment_sync(t) for t in theta_history]
        # 计算连续步之间的变化
        diffs = [np.linalg.norm(sync_history[i+1] - sync_history[i]) 
                 for i in range(len(sync_history) - 1)]
        return np.mean(diffs)
    
    def compute_mpi(self, sci: float, tfd: float,
                    sci_lock=0.3, sci_chimera=0.8,
                    tfd_lock=0.0, tfd_chimera=0.1) -> float:
        """
        机制纯度指数（MPI）。

        衡量状态是 chimera 主导还是梯度锁相主导。
        MPI > 0.8: 高置信度 chimera
        MPI < 0.3: 梯度锁相主导
        else: 混合态

        关键设计：
        - chimera: 高 SCI (≠锁定点) + 高 TFD (≠锁定点) → MPI 高
        - gradient_locking: 低 SCI (≈锁定点) + 低 TFD (≈锁定点) → MPI 低
        """
        # 归一化到 chimera 区域（越高越像 chimera）
        sci_to_chimera = max(0.0, (sci - sci_lock) / max(sci_chimera - sci_lock, 1e-10))
        tfd_to_chimera = max(0.0, (tfd - tfd_lock) / max(tfd_chimera - tfd_lock, 1e-10))

        # 归一化到 lock 区域（越高越像 gradient_locking）
        sci_to_lock = max(0.0, 1.0 - sci_to_chimera)
        tfd_to_lock = max(0.0, 1.0 - tfd_to_chimera)

        # 组合：接近 chimera 得高分，接近 lock 得低分
        chimera_score = min(sci_to_chimera, 1.0) * min(tfd_to_chimera, 1.0)
        anti_lock = min(sci_to_lock, 1.0) + min(tfd_to_lock, 1.0)  # 接近 lock 惩罚
        mpi = chimera_score - 0.5 * min(anti_lock, 1.0)
        return max(0.0, min(1.0, mpi))
    
    def classify_phase(self, mpi: float, sci: float) -> str:
        """基于 MPI 和 SCI 的分类"""
        if mpi > 0.8:
            return "chimera"
        elif mpi < 0.3:
            return "gradient_locking"
        else:
            # 检查更细粒度
            if sci > 0.5:
                return "chimera"
            elif sci < 0.15:
                return "chimera"
            return "mixed"
    
    def _prepare_chimera_coupling(self, sigma: float) -> np.ndarray:
        """预计算 chimera 耦合矩阵（固定位置，无需重复计算）"""
        N = self.n
        dpos = np.minimum(np.abs(np.arange(N).reshape(-1, 1) - np.arange(N).reshape(1, -1)),
                          N - np.abs(np.arange(N).reshape(-1, 1) - np.arange(N).reshape(1, -1)))
        # 归一化到 2π
        dpos = dpos * 2 * np.pi / N
        return np.exp(-(dpos ** 2) / (2 * sigma ** 2))

    def chimera_coupling_step(self, theta: np.ndarray, k_local: float,
                              sigma: float, omega: np.ndarray,
                              positions: np.ndarray, coupling_matrix: np.ndarray) -> np.ndarray:
        """
        Chimera 耦合步骤：使用非局部高斯核（Abrams-Strogatz 模型）。

        K(x_i, x_j) = K_local * exp(-(x_i - x_j)^2 / (2*sigma^2))

        理论参考：D4-S18-r19 严格 chimera 条件：0.5 < K0 < 2.0, N >= 500
        """
        N = len(theta)
        dphi = theta.reshape(-1, 1) - theta.reshape(1, -1)  # (N, N)
        dphi = (dphi + np.pi) % (2 * np.pi) - np.pi
        local_coupling = np.sum(coupling_matrix * np.sin(dphi), axis=1)
        r_global = np.mean(np.exp(1j * theta))
        return theta + self.dt * (omega + k_local * local_coupling / N + k_local * 0.1 * r_global.imag)

    def run_diagnostic(self, k: float = 1.0, g: float = 0.05,
                       omega_magnitude: float = 0.5,
                       t_warmup: int = 10000, t_measure: int = 10000,
                       record_interval: int = 10,
                       coupling_mode: str = "global") -> List[ChimeraDiagnostic]:
        """
        运行完整的 chimera 诊断协议。

        参数：
            k: 全局耦合强度 / 局部耦合强度
            g: 空间耦合强度（=0 时为纯空间耦合 chimera 或频率梯度锁相）
            omega_magnitude: 频率梯度幅度
            t_warmup: 预热时间步数
            t_measure: 测量时间步数
            record_interval: 记录间隔
            coupling_mode: "global"（均匀耦合）或 "chimera"（非局部耦合）
        """
        rng = self.rng

        # 初始化
        theta = rng.uniform(0, 2 * np.pi, self.n)
        omega = np.zeros(self.n)
        positions = np.arange(self.n) * 2 * np.pi / self.n

        # 频率梯度（正态分布在圆周上）
        if omega_magnitude > 0:
            omega = omega_magnitude * np.sin(positions)

        # 预热阶段
        coupling_matrix = None
        sigma = self.n * g / 2 / np.pi  # 非局部范围（% of circle）
        if coupling_mode == "chimera":
            coupling_matrix = self._prepare_chimera_coupling(sigma)

        for _ in range(t_warmup):
            if coupling_mode == "chimera":
                theta = self.chimera_coupling_step(theta, k, sigma, omega, positions, coupling_matrix)
            elif g > 0:
                coupling_g = 1.0 + g * np.cos(positions)
                r = np.mean(np.exp(1j * theta))
                theta += self.dt * (omega + k * coupling_g * r.imag)
            else:
                r = np.mean(np.exp(1j * theta))
                theta += self.dt * (omega + k * r.imag)

        # 测量阶段 - 记录时间历史
        theta_history = []
        diagnostics = []

        prev_sync = None
        for t in range(t_measure):
            # 演化一步
            if coupling_mode == "chimera":
                theta = self.chimera_coupling_step(theta, k, sigma, omega, positions, coupling_matrix)
            elif g > 0:
                coupling_g = 1.0 + g * np.cos(positions)
                r = np.mean(np.exp(1j * theta))
                theta += self.dt * (omega + k * coupling_g * r.imag)
            else:
                r = np.mean(np.exp(1j * theta))
                theta += self.dt * (omega + k * r.imag)
            
            # 记录同步历史
            if t % record_interval == 0:
                theta_history.append(theta.copy())
            
            # 只在最后一段记录
            if t >= t_measure - record_interval * 100:
                sci = self.compute_sci(theta)
                tfd = self.compute_tfd(theta_history) if len(theta_history) >= 2 else 0.0
                mpi = self.compute_mpi(sci, tfd)
                phase = self.classify_phase(mpi, sci)
                
                seg_sync = self.compute_segment_sync(theta)
                
                diag = ChimeraDiagnostic(
                    phase=phase, mpi=mpi, sci=sci, tfd=tfd,
                    confidence=min(mpi, 1.0 - mpi) + 0.5,
                    details={
                        "segment_sync": np.round(seg_sync, 4).tolist(),
                        "sync_variance": round(float(np.var(seg_sync)), 6),
                    }
                )
                diagnostics.append(diag)
        
        # 综合结论
        if len(diagnostics) == 0:
            return [ChimeraDiagnostic("unknown", 0, 0, 0, 0, {})]
        
        # 取最后几个诊断的平均
        recent = diagnostics[-5:] if len(diagnostics) >= 5 else diagnostics
        avg_mpi = np.mean([d.mpi for d in recent])
        avg_sci = np.mean([d.sci for d in recent])
        avg_tfd = np.mean([d.tfd for d in recent])
        
        final_phase = self.classify_phase(avg_mpi, avg_sci)
        
        return [ChimeraDiagnostic(
            phase=final_phase, mpi=avg_mpi, sci=avg_sci,
            tfd=avg_tfd, confidence=0.8 if avg_mpi > 0.7 else 0.5,
            details={
                "segment_sync": np.round(self.compute_segment_sync(theta), 4).tolist(),
                "sync_variance": round(float(np.var(self.compute_segment_sync(theta))), 6),
                "n_samples": len(diagnostics),
                "final_sync": self.compute_segment_sync(theta).tolist(),
            }
        )]


def run_parameter_scan() -> Dict:
    """
    运行 r23 推荐的多配置诊断扫描。
    """
    results = {}
    
    configurations = [
        ("true_chimera",       1.0, 0.3, 0.0,  "非局部耦合 chimera（Abrams-Strogatz）"),
        ("freq_gradient",      1.0, 0.0, 0.5,  "纯频率梯度锁相（global coupling）"),
        ("global_uniform",     1.0, 0.0, 0.0,  "纯均匀耦合（全局同步）"),
        ("mixed_chimera",      1.5, 0.3, 0.3,  "混合 chimera + 频率梯度"),
    ]
    
    for name, k, g, omega_mag, desc in configurations:
        print(f"\n{'='*60}")
        print(f"配置: {name} — {desc}")
        print(f"  k={k}, g={g}, omega_mag={omega_mag}")
        
        # 确定耦合模式
        coupling_mode = "chimera" if "chimera" in name else "global"
        # 简化：统一 N=256，chimera 模式也能显示区域化模式
        n_particles = 256

        diag = ChimeraDiagnosticV2(n=n_particles, dt=0.005, seed=42)
        # Chimera 需要更少步骤即可收敛到可观察模式
        t_warmup = 10000 if "chimera" in name else 20000
        t_measure = 15000 if "chimera" in name else 30000
        result = diag.run_diagnostic(
            k=k, g=g, omega_magnitude=omega_mag,
            t_warmup=t_warmup, t_measure=t_measure,
            record_interval=50,
            coupling_mode=coupling_mode
        )
        
        d = result[0]
        results[name] = {
            "description": desc,
            "k": k, "g": g, "omega_magnitude": omega_mag,
            "phase": d.phase,
            "mpi": d.mpi,
            "sci": d.sci,
            "tfd": d.tfd,
            "confidence": d.confidence,
            "segment_sync": d.details.get("segment_sync", []),
            "sync_variance": d.details.get("sync_variance", 0),
        }
        
        status_markers = {
            "chimera": "✓ CHIMERA",
            "gradient_locking": "→ GRADIENT LOCKING",
            "mixed": "~ MIXED",
            "unknown": "? UNKNOWN",
        }
        print(f"\n  诊断结果: {status_markers.get(d.phase, d.phase)}")
        print(f"  MPI: {d.mpi:.4f}  SCI: {d.sci:.4f}  TFD: {d.tfd:.6f}")
        print(f"  段同步: {d.details.get('segment_sync', [])}")
    
    return results


if __name__ == "__main__":
    import sys
    
    output_file = Path("labs/simulations/chimera_diagnostic_results_v2.json")
    
    results = run_parameter_scan()
    
    # 汇总
    summary = {
        "theory_reference": "D4-S18-r23-chimera-diagnostic-formalization.md",
        "protocol": "D4-S18-r23-P1: 双阶段 chimera 认证",
        "n_runs": len(results),
        "chimera_count": sum(1 for r in results.values() if r["phase"] in ["chimera", "mixed" and "mixed"]) > 0,
        "gradient_locking_count": sum(1 for r in results.values() if r["phase"] == "gradient_locking"),
    }
    
    # 简化汇总
    for phase in ["chimera", "gradient_locking", "mixed"]:
        count = sum(1 for r in results.values() if r["phase"] == phase)
        if count > 0:
            summary[f"{phase}_count"] = count
    
    final = {
        "configurations": results,
        "summary": {k: v for k, v in summary.items() if k != "n_runs"},
    }
    
    with open(output_file, "w") as f:
        json.dump(final, f, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
