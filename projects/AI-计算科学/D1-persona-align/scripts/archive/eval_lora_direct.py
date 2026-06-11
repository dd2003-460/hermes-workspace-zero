#!/usr/bin/env python3
"""
Try loading model + LoRA directly using MLX + safetensors + peft.

This attempts to:
1. Load the base model using huggingface transformers (MLX format)
2. Load the LoRA adapter using peft
3. Apply LoRA to the model
4. Test with a few questions
"""

import json
import time

# Try loading with transformers
print("Step 1: Loading model...")
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print("  ✓ transformers loaded")
except ImportError as e:
    print(f"  ✗ transformers import failed: {e}")
    print("  Trying MLX-native loading...")
    try:
        import mlx.core as mx
        import mlx.nn as nn
        print("  ✓ mlx loaded")
    except ImportError as e2:
        print(f"  ✗ mlx also failed: {e2}")
        exit(1)

MODEL_PATH = "/Users/a1-6/.lmstudio/models/Youssofal/Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit"
LORA_PATH = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/lora_training/adapters.safetensors"

# Check LoRA file
print(f"\nStep 0: Checking LoRA file...")
import os
print(f"  LoRA path: {LORA_PATH}")
print(f"  LoRA size: {os.path.getsize(LORA_PATH) / 1024 / 1024:.1f} MB")

# Check config
with open(os.path.join(MODEL_PATH, "config.json")) as f:
    config = json.load(f)
print(f"  Model type: {config.get('model_type', 'unknown')}")
print(f"  architectures: {config.get('architectures', [])}")
print(f"  num_hidden_layers: {config.get('num_hidden_layers')}")
print(f"  hidden_size: {config.get('hidden_size')}")
print(f"  num_attention_heads: {config.get('num_attention_heads')}")
print(f"  num_key_value_heads: {config.get('num_key_value_heads')}")
print(f"  num_experts: {config.get('num_experts', 'N/A')}")
print(f"  moe_intermediate_size: {config.get('moe_intermediate_size', 'N/A')}")
print(f"  quantization: {config.get('quantization', 'N/A')}")
print(f"  dtype (from config): {config.get('torch_dtype', 'N/A')}")

# Try loading with peft
print(f"\nStep 2: Trying PEFT LoRA load...")
try:
    from peft import PeftModel
    print("  ✓ peft loaded")
    
    # Try loading the model
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype="float16",  # Will need to adjust for quantized
        device_map="auto",
    )
    print(f"  Model loaded! Size: {sum(p.numel() for p in model.parameters()) / 1e9:.1f}B params")
    
    # Apply LoRA
    lora_model = PeftModel.from_pretrained(model, LORA_PATH)
    print(f"  LoRA applied! Merge status: {lora_model.peft_config}")
    
    # Test
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    test_input = "你好，请简短回复。"
    inputs = tokenizer(test_input, return_tensors="pt").to(model.device)
    output = lora_model.generate(**inputs, max_new_tokens=50, temperature=0.8)
    print(f"\nTest output: {tokenizer.decode(output[0], skip_special_tokens=True)}")
    
except Exception as e:
    import traceback
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
