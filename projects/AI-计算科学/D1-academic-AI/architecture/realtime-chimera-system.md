# System Architecture: Real-Time Chimera Detection and Analysis Platform

**Date**: 2026-05-01  
**Reference**: D4-S18 r07 theory, UNIFIED-FRAMEWORK.md (Theorems 1-10)

## 1. System Overview

A distributed real-time system for detecting chimera states in coupled Kuramoto oscillators, computing topological intelligence metrics (Theorem 10), and enabling multi-agent cognitive flow management.

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONTROL & ORCHESTRATION                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐  │
│  │   Master     │  │   Config     │  │   Health Check  │  │   Auto-Scaling    │  │
│  │   Node (1)   │  │   Manager    │  │   Server        │  │   Service         │  │
│  └─────────────┘  └──────────────┘  └─────────────────┘  └──────────────────┘  │
│                              ↓ Kafka Producer                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT SIMULATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ... (N)   │
│  │  Agent i     │  │  Agent j     │  │  Agent k     │  │  Agent m     │           │
│  │  (Kuramoto)  │  │  (Kuramoto)  │  │  (Kuramoto)  │  │  (Kuramoto)  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │
│        ↓                ↓                ↓                ↓                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┤
│  │                         Agent Aggregation Service                            │
│  └───────────────────────────────────────────────────────────────────────────────┘
│                              ↓ (topic: agent-sequences)                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DETECTION & ANALYSIS PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────────────┐
│  │                    Message Broker: Apache Kafka                                │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  │ agent-sequences │  │ chimera-phases  │  │ topology-events │                │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│  └───────────────────────────────────────────────────────────────────────────────┘
│                              ↓ Consume                                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │  Phase Detector │    │ Curvature       │    │ Betti Number    │                  │
│  │  Service        │    │ Entropy Est.    │    │ Estimator       │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│       ↓ Chimera State         ↓ D_curv              ↓ I_TOP                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         STORAGE & VISUALIZATION LAYER                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Zabbix /       │  │   PostgreSQL    │  │   Dashboard     │                  │
│  │   InfluxDB       │  │   (topology)    │  │   Service       │                  │
│  │   (metrics)      │  │                 │  │   (Web)         │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Agent Simulation Service

**Purpose**: Simulate N Kuramoto oscillators with configurable chimera conditions

**Interface**:
```python
class AgentSimulatorService:
    """
    Implements:
    - N coupled Kuramoto oscillators
    - Environmental coupling (for multi-chimera scenarios)
    - Caching for checkpoint restoration
    """
    
    @staticmethod
    def create_agents(n_agents: int, initial_coupling: float = 1.0) -> AgentSimulator
    @staticmethod
    def get_kuramoto_phases(n_agents: int, n_windows: int) -> AgentSimulator
```

**Kafka Producer Interface**:
```python
class AgentDataProducer:
    """
    Publishes agent phase snapshots to Kafka
    Topic: agent-sequences
    Schema: json with phase angles [θ₀, θ₁, ..., θₙ₋₁]
    """
    TOPIC = "agent-sequences"
    SCHEMA_VERSION = "v1"
    
    def publish_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Publish phase snapshot with timestamp"""
        self.producer.send(
            self.TOPIC,
            value=json.dumps({
                "timestamp": time.time_ns(),
                "schema_version": self.SCHEMA_VERSION,
                "n_agents": len(snapshot["phases"]),
                "phases": snapshot["phases"],
                "window_partition": snapshot.get("window_partition", [])
            })
        )
```

---

### 2.2 Phase Detector Service

**Purpose**: Real-time classification of chimera phases (D4-S18 r03)

**Interface**:
```python
class PhaseDetectorService:
    """
    Implements theorem 1 from D4-S18 r03:
    Phase I: Full Synchronization (r_max → 1, r_min → 1)
    Phase II: Full Asynchrony (r_max << 1, r_min << 1)
    Phase III: Stable Chimera (r_max → 1, r_min << 1)
    Phase IV: Oscillating Chimera (oscillating)
    """
    
    # Published to: chimera-phases
    TOPIC = "chimera-phases"
    
    def classify_phase(self, window_r: np.ndarray, 
                      global_r: float) -> Dict[str, Any]:
        """
        Returns:
        - phase: ChimeraPhase enum
        - phase_score: float (confidence)
        - metrics: {r_max, r_min, variance}
        """
```

---

### 2.3 Topological Intelligence Service

**Purpose**: Compute I_C = χ_Euler + |⟨w₂, [C]⟩| for phase detector outputs

**Interface**:
```python
class TopologicalIntelligenceService:
    """
    Computes Theorem 10: Topological intelligence metrics
    from chimera phase sequences.
    
    Components:
    - χ_Euler: Euler-Poincaré characteristic (Betti-based)
    - |⟨w₂, [C]⟩|: Second Stiefel-Whitney class estimation
    """
    
    TOPIC = "topology-events"
    
    def compute_i_top(self, phase_sequence: List[ChimeraPhase],
                     b0: int, b1: int, b2: int) -> Dict[str, Any]:
        """
        Returns:
        - I_TOP: int (topological intelligence index)
        - chi_euler: int (Euler-Poincaré characteristic)
        - w2_cobordism: float (Stiefel-Whitney class)
        """
```

---

### 2.4 Monitoring and Alerting Service

**Purpose**: Real-time monitoring with alarm rules

**Interface**:
```python
class MonitoringService:
    """
    Integrates with Zabbix for metric collection.
    Publishes alerts via WebSocket or email/webhook.
    """
    
    def monitor_phase_stability(self, phase: ChimeraPhase, 
                              stability_metric: float) -> bool:
        """Returns True if phase is stable"""
        return abs(self._compute_stability(phase)) > self.stability_threshold
    
    def check_i_top_threshold(self, i_top: float, 
                            threshold: float) -> Dict[str, Any]:
        """Returns alert if I_TOP exceeds or falls below threshold"""
```

**Alert Configuration**:
```yaml
alerts:
  - name: "chimera_phase_transition"
    condition: "new_phase_detected AND not_oscillating"
    severity: "warning"
    action: "log_and_alert"
  
  - name: "i_top_threshold_exceeded"
    condition: "i_top > CONFIG.slow_mode_threshold"
    severity: "critical"
    action: "trigger_recovery_mode"
```

---

## 3. Technology Stack Decisions

| Component | Choice | Justification |
|-----------|--------|---------------|
| Message Broker | Apache Kafka | High throughput, persistent queues, exactly-once semantics |
| Database (Telemetry) | InfluxDB | Time-series optimized, native flux queries for chimera metrics |
| Database (Topology) | PostgreSQL | ACID compliance, pgvector for Betti number embeddings |
| Monitoring | Zabbix | Built-in alerting, health checks, performance monitoring |
| Orchestration | Docker Compose | Lightweight deployment for prototype |

---

## 4. Implementation Considerations

### 4.1 Betti Number Estimation Pipeline
```
Phase Snapshot → Recurrence Plot → Graph G(V,E) → Mapper Algorithm → Betti(b₀, b₁, b₂)
```

### 4.2 Performance Targets
- Agent simulation: **1000 agents** minimum
- Phase detection latency: **<10ms** per snapshot
- Topological calculation: **<100ms** per 1000-timestep window
- Kafka throughput: **10,000 messages/sec** (agent snapshots)

---
