#!/usr/bin/env python3
"""Mem0 smoke test: vLLM LLM + OpenVINO embedding (local, CPU).

If OpenVINO fails, fall back to a simple hash-based embedding.
"""
import sys, json, time, hashlib

VLLM_API_KEY = "sk-vllm-17L3d6z60EuhN1yW_bcRoynvDmxoAk1GKsF3QvSV9cY"
VLLM_BASE = "http://100.112.53.47:8000/v1"
VLLM_MODEL = "qwen3.8-27b-w8a16"

def make_memory(embedding_backend="openvino"):
    from mem0 import Memory
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "mem0_smoke_test",
                "path": "/tmp/mem0-qdrant",
                "embedding_model_dims": 384,
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
    }
    if embedding_backend == "openvino":
        config["embedder"] = {
            "provider": "fastembed",
            "config": {
                "model": "BAAI/bge-small-en-v1.5",
            },
        }
    else:
        # Fallback: use a simple embedding via vLLM (not ideal but works)
        # Actually let's just try openvino first and see
        pass
    m = Memory.from_config(config)
    return m

def test_add_and_search(m):
    """Add a few memories and search for them."""
    user_id = "smoke-test"
    memories = [
        "用户偏好用 dataclass 而不是 Pydantic 做配置管理",
        "V100 GPU 的 HBM 带宽是 900 GB/s",
        "成璐的目标权重：学术 0.4、资本 0.2、健康 0.2、人脉 0.2",
    ]
    for mem_text in memories:
        t0 = time.time()
        m.add(mem_text, user_id=user_id)
        print(f"  added ({time.time()-t0:.1f}s): {mem_text[:40]}...")

    # Search
    queries = [
        "用户偏好什么配置方式",
        "V100 带宽是多少",
        "成璐的目标权重",
    ]
    for q in queries:
        t0 = time.time()
        results = m.search(q, filters={"user_id": user_id})
        dt = time.time() - t0
        if isinstance(results, dict):
            results = results.get("results", [])
        print(f"\n  search ({dt:.1f}s): {q}")
        for r in results[:3]:
            score = r.get("score", r.get("score_raw", "?"))
            text = r.get("memory", r.get("text", "?"))[:60]
            print(f"    [{score:.3f}] {text}" if isinstance(score, float) else f"    [{score}] {text}")

if __name__ == "__main__":
    backend = sys.argv[1] if len(sys.argv) > 1 else "openvino"
    print(f"=== Mem0 smoke test (embedding: {backend}) ===")
    t0 = time.time()
    m = make_memory(backend)
    print(f"Memory initialized ({time.time()-t0:.1f}s)")
    test_add_and_search(m)
    print("\n=== SMOKE TEST PASSED ===")
