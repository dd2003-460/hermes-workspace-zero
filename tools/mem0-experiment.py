#!/usr/bin/env python3
"""Mem0 3-condition A/B/C experiment.

Phase 1: Ingest — feed the 10 memory files into Mem0 (LLM extracts facts).
Phase 2: Query — run 5 questions, retrieve top-k memories, inject into prompt.
Phase 3: Score — compare with no-memory (5.3/10) and md-tree (10/10).

Usage:
  python mem0-experiment.py ingest   # Phase 1
  python mem0-experiment.py query    # Phase 2+3
"""
import sys, json, time, os, glob

VLLM_API_KEY = "sk-vllm-17L3d6z60EuhN1yW_bcRoynvDmxoAk1GKsF3QvSV9cY"
VLLM_BASE = "http://100.112.53.47:8000/v1"
VLLM_MODEL = "qwen3.8-27b-w8a16"
USER_ID = "decomp-experiment"
MEM_DIR = os.path.join(os.path.dirname(__file__), "..", "projects", "decomp", "memory")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "projects", "decomp", "memory-baseline", "mem0")

def make_memory():
    from mem0 import Memory
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "mem0_decomp_zh",
                "path": "/tmp/mem0-qdrant-decomp-zh",
                "embedding_model_dims": 512,
            },
        },
        "llm": {
            "provider": "openai",
            "config": {
                "model": VLLM_MODEL,
                "openai_base_url": VLLM_BASE,
                "api_key": VLLM_API_KEY,
                "temperature": 0.1,
            },
        },
        "embedder": {
            "provider": "fastembed",
            "config": {
                "model": "BAAI/bge-small-zh-v1.5",
            },
        },
    }
    return Memory.from_config(config)

def phase_ingest():
    """Feed all memory files into Mem0."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    m = make_memory()
    files = sorted(glob.glob(os.path.join(MEM_DIR, "*.md")))
    # Skip INDEX.md (it's just a table of contents)
    files = [f for f in files if not os.path.basename(f).upper() == "INDEX.MD"]
    print(f"Ingesting {len(files)} files into Mem0...")
    log = []
    for f in files:
        with open(f, "r") as fh:
            content = fh.read()
        t0 = time.time()
        result = m.add(content, user_id=USER_ID)
        dt = time.time() - t0
        fname = os.path.basename(f)
        log.append({"file": fname, "time_s": round(dt, 1), "result": str(result)[:200]})
        print(f"  {fname}: {dt:.1f}s")
    # Save ingestion log
    with open(os.path.join(RESULTS_DIR, "ingest-log.json"), "w") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)
    # List all stored memories
    all_mems = m.get_all(filters={"user_id": USER_ID})
    if isinstance(all_mems, dict):
        all_mems = all_mems.get("results", [])
    print(f"\nTotal memories stored: {len(all_mems)}")
    for i, mem in enumerate(all_mems):
        text = mem.get("memory", mem.get("text", "?"))[:80]
        print(f"  [{i+1}] {text}")
    with open(os.path.join(RESULTS_DIR, "all-memories.json"), "w") as fh:
        json.dump(all_mems, fh, indent=2, ensure_ascii=False)

QUESTIONS = [
    {"id": "Q1", "text": "成璐偏好用什么做配置管理？", "expected": "dataclass"},
    {"id": "Q2", "text": "V100 GPU 的 HBM 带宽是多少？", "expected": "900 GB/s"},
    {"id": "Q3", "text": "成璐的目标权重是怎么分配的？", "expected": "学术0.4 资本0.2 健康0.2 人脉0.2"},
    {"id": "Q4", "text": "当前项目 P1 的进度是什么？下一步做什么？", "expected": "T4/T5 相关"},
    {"id": "Q5", "text": "AGENTS.md 里有哪些红线？", "expected": "红线列表"},
]

def phase_query():
    """Run 5 questions, retrieve memories, build augmented prompt."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    m = make_memory()
    results = []
    for q in QUESTIONS:
        t0 = time.time()
        retrieved = m.search(q["text"], filters={"user_id": USER_ID})
        if isinstance(retrieved, dict):
            retrieved = retrieved.get("results", [])
        dt = time.time() - t0
        # Build memory context
        mem_lines = []
        for r in retrieved[:5]:
            score = r.get("score", 0)
            text = r.get("memory", r.get("text", ""))
            mem_lines.append(f"  [{score:.3f}] {text}")
        mem_context = "\n".join(mem_lines) if mem_lines else "  (no memories retrieved)"
        results.append({
            "id": q["id"],
            "question": q["text"],
            "expected": q["expected"],
            "retrieval_time_s": round(dt, 2),
            "num_retrieved": len(retrieved),
            "retrieved": mem_context,
        })
        print(f"\n{q['id']}: {q['text']}")
        print(f"  retrieved {len(retrieved)} memories in {dt:.2f}s")
        print(mem_context)
    with open(os.path.join(RESULTS_DIR, "query-results.json"), "w") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"\nSaved to {RESULTS_DIR}/query-results.json")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "ingest":
        phase_ingest()
    elif sys.argv[1] == "query":
        phase_query()
    elif sys.argv[1] == "all":
        phase_ingest()
        phase_query()
    else:
        print("Usage: mem0-experiment.py [ingest|query|all]")
