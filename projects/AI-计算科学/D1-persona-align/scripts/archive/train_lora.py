#!/usr/bin/env python3
"""
train_lora.py — LoRA fine-tuning for persona alignment

Prerequisites:
  pip3 install torch transformers peft accelerate
  (or: pip3 install mlx mlx-lm peft for Apple Silicon)

This script supports two backends:
1. PyTorch + transformers + PEFT (cross-platform)
2. MLX + mlx-lm (Apple Silicon only)

Usage:
  python train_lora.py --config train_config.yaml
  python train_lora.py --train --data raw/lora_data/lora_trainset.jsonl
  python train_lora.py --eval --adapter ./lora_output --test-data raw/lora_data/synthetic_samples_v3.jsonl
  python train_lora.py --infer --prompt "你如何看待AI对齐问题？"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# Configuration
# ============================================================
@dataclass
class TrainConfig:
    """Training configuration."""
    # Model
    model_name: str = "Qwen/Qwen2.5-7B-Instruct"
    adapter_name: str = "persona-align-adapter"

    # Data
    train_data: str = "raw/lora_data/lora_trainset.jsonl"
    eval_data: Optional[str] = None
    max_samples: Optional[int] = None

    # Training
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation: int = 4
    max_length: int = 2048
    warmup_ratio: float = 0.05
    weight_decay: float = 0.01

    # Output
    output_dir: str = "lora_output"
    save_steps: int = 500
    logging_steps: int = 50

    # Backend: "torch" or "mlx"
    backend: str = "torch"


DEFAULT_CONFIG = TrainConfig()


# ============================================================
# Data loading and preparation
# ============================================================
def load_data(path: str, max_samples: Optional[int] = None) -> List[dict]:
    """Load JSONL data file."""
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    if max_samples:
        samples = samples[:max_samples]
    return samples


def format_instruction_sample(sample: dict) -> str:
    """Format a single sample into a chat-style prompt."""
    instruction = sample.get("instruction", "")
    input_text = sample.get("input", "")
    output = sample.get("output", "")

    if input_text:
        full_instruction = f"{instruction}\n\n{input_text}"
    else:
        full_instruction = instruction

    # System message for persona alignment
    system_msg = (
        "你是成璟的思考扩展。用提问推进思考、跨域跳跃(AI↔物理↔社科↔哲学)、"
        "接受质疑并修正。"
    )

    return (
        f"<|im_start|>system\n{system_msg}<|im_end|>\n"
        f"<|im_start|>user\n{full_instruction}<|im_end|>\n"
        f"<|im_start|>assistant\n{output}<|im_end|>"
    )


def format_eval_sample(sample: dict) -> str:
    """Format for evaluation — only the question."""
    return (
        f"<|im_start|>system\n你是成璟的思考扩展。<|im_end|>\n"
        f"<|im_start|>user\n{sample['instruction']}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


# ============================================================
# PyTorch + transformers + PEFT backend
# ============================================================
def train_torch(config: TrainConfig):
    """Train LoRA using PyTorch + transformers + PEFT."""
    try:
        import torch
        from transformers import (
            AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer,
            DataCollatorForSeq2Seq
        )
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError:
        print("ERROR: torch/transformers/peft not installed.")
        print("Install with: pip3 install torch transformers peft accelerate")
        print("Or: pip3 install --break-system-packages torch transformers peft")
        sys.exit(1)

    print("=" * 60)
    print(f"Training with PyTorch (MPS backend)")
    print(f"Model: {config.model_name}")
    print(f"Adapter: {config.adapter_name}")
    print(f"Data: {config.train_data}")
    print(f"LoRA rank: {config.lora_r}, alpha: {config.lora_alpha}")
    print(f"Epochs: {config.num_epochs}, Batch size: {config.batch_size}")
    print("=" * 60)

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model and tokenizer
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        device_map={"": device} if device == "mps" else None,
        trust_remote_code=True,
    )

    # Apply LoRA
    print("Applying LoRA configuration...")
    peft_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.lora_target_modules,
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Load data
    print("Loading training data...")
    samples = load_data(config.train_data, config.max_samples)
    print(f"Loaded {len(samples)} samples")

    if not samples:
        print("ERROR: No training data found.")
        sys.exit(1)

    # Tokenize
    def tokenize_fn(sample):
        prompt = format_instruction_sample(sample)
        inputs = tokenizer(
            prompt,
            truncation=True,
            max_length=config.max_length,
            padding=False,
            return_tensors=None,
        )
        labels = inputs["input_ids"].clone()
        # Mask the instruction part (before assistant message)
        assistant_token = tokenizer.convert_tokens_to_ids("<|im_start|>")
        if assistant_token in labels:
            idx = labels.tolist().index(assistant_token)
            # Set labels to -100 (ignore) up to and including the assistant token
            labels[:idx] = [-100] * idx
        return {"input_ids": labels, "attention_mask": inputs["attention_mask"]}

    # Use simple tokenizer
    def tokenize_fn_v2(sample):
        prompt = format_instruction_sample(sample)
        return tokenizer(
            prompt,
            truncation=True,
            max_length=config.max_length,
            padding=False,
        )

    tokenized_data = [tokenize_fn_v2(s) for s in samples]
    input_ids = [d["input_ids"] for d in tokenized_data]
    attention_mask = [d["attention_mask"] for d in tokenized_data]

    # Create output directory
    os.makedirs(config.output_dir, exist_ok=True)

    # Training args
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=2,
        fp16=device == "mps",
        report_to="none",
        optim="paged_adamw_8bit" if device == "mps" else "adamw_torch",
        bf16=device != "mps",
    )

    # Simple trainer
    class LoRATrainer(Trainer):
        def __init__(self, model, tokenized_data, training_args):
            super().__init__(
                model=model,
                args=training_args,
                train_dataset=tokenized_data,
            )

    trainer = LoRATrainer(model, tokenized_data, training_args)

    print("Starting training...")
    trainer.train()

    # Save adapter
    adapter_path = os.path.join(config.output_dir, "adapter")
    model.save_pretrained(adapter_path)
    print(f"Adapter saved to {adapter_path}")


# ============================================================
# MLX backend (Apple Silicon)
# ============================================================
def train_mlx(config: TrainConfig):
    """Train LoRA using MLX + mlx-lm."""
    try:
        import mlx.core as mx
        import mlx.nn as nn
        from mlx_lm import load, generate
        import mlx_loRA  # pip install mlx-lora
    except ImportError:
        print("ERROR: MLX packages not installed.")
        print("Install with:")
        print("  pip3 install --break-system-packages mlx mlx-lm mlx-lora")
        sys.exit(1)

    print("=" * 60)
    print("Training with MLX (Apple Silicon)")
    print(f"Model: {config.model_name}")
    print("=" * 60)


# ============================================================
# Evaluation
# ============================================================
def evaluate_torch(config: TrainConfig):
    """Evaluate LoRA adapter on test data."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Evaluating on device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(config.model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        device_map={"": device} if device == "mps" else None,
        trust_remote_code=True,
    )

    # Load adapter
    print(f"Loading adapter from {config.output_dir}/adapter...")
    model = PeftModel.from_pretrained(base_model, f"{config.output_dir}/adapter")
    model.eval()

    # Load test data
    eval_file = config.eval_data or config.train_data
    if not os.path.exists(eval_file):
        print(f"Test data not found: {eval_file}")
        return

    samples = load_data(eval_file, 10)  # Evaluate first 10
    print(f"Evaluating {len(samples)} samples...")

    for i, sample in enumerate(samples):
        prompt = format_eval_sample(sample)
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
            )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Strip the prompt prefix
        generated = generated.replace(prompt, "", 1).strip()

        print(f"\n--- Sample {i+1} ---")
        print(f"Q: {sample['instruction'][:100]}...")
        print(f"A: {generated[:200]}...")


# ============================================================
# Interactive inference
# ============================================================
def infer(config: TrainConfig, prompt: str):
    """Interactive inference with the trained model."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(config.model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        torch_dtype=torch.float16,
        device_map={"": device},
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, f"{config.output_dir}/adapter")
    model.eval()

    system_msg = "你是成璟的思考扩展。用提问推进思考、跨域跳跃(AI↔物理↔社科↔哲学)、接受质疑并修正。"
    full_prompt = (
        f"<|im_start|>system\n{system_msg}<|im_end|>\n"
        f"<|im_start|>user\n{prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    result = result.replace(full_prompt, "", 1).strip()
    print(result)


# ============================================================
# Main entry point
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Persona LoRA Fine-tuning")
    parser.add_argument("--config", help="Path to training config YAML")
    parser.add_argument("--train", action="store_true", help="Run training")
    parser.add_argument("--eval", action="store_true", help="Run evaluation")
    parser.add_argument("--infer", action="store_true", help="Run inference")
    parser.add_argument("--prompt", help="Prompt for inference mode")
    parser.add_argument("--data", help="Path to training/eval data (JSONL)")
    parser.add_argument("--adapter", help="Path to adapter directory")
    parser.add_argument("--model", help="Model name (HF Hub)")
    parser.add_argument("--epochs", type=int, help="Number of epochs")
    parser.add_argument("--lr", type=float, help="Learning rate")
    parser.add_argument("--output-dir", help="Output directory")

    args = parser.parse_args()

    # Build config
    config = TrainConfig()
    if args.config:
        print("Config loading: YAML support coming later")

    # Override with CLI args
    if args.data:
        config.train_data = args.data
        config.eval_data = args.data
    if args.model:
        config.model_name = args.model
    if args.adapter:
        config.output_dir = args.adapter
    if args.epochs:
        config.num_epochs = args.epochs
    if args.lr:
        config.learning_rate = args.lr
    if args.output_dir:
        config.output_dir = args.output_dir

    if args.train:
        if config.backend == "mlx":
            train_mlx(config)
        else:
            train_torch(config)
    elif args.eval:
        evaluate_torch(config)
    elif args.infer:
        infer(config, args.prompt or "你如何看待AI对齐问题？")
    else:
        # Default: show status and instructions
        print("=" * 60)
        print("Persona LoRA Fine-tuning Tool")
        print("=" * 60)
        print(f"Model: {config.model_name}")
        print(f"Data: {config.train_data}")
        print(f"Output: {config.output_dir}")
        print()

        if os.path.exists(config.train_data):
            samples = load_data(config.train_data)
            print(f"Training data: {len(samples)} samples")
        else:
            print(f"WARNING: Training data not found: {config.train_data}")
            print("Run first: python synthetic_data_generator_v4.py to generate samples")

        print()
        print("Usage:")
        print("  python train_lora.py --train          # Train LoRA adapter")
        print("  python train_lora.py --eval            # Evaluate adapter")
        print("  python train_lora.py --infer --prompt 'question'  # Inference")
        print()
        print("Prerequisites:")
        print("  pip3 install --break-system-packages torch transformers peft accelerate")


if __name__ == "__main__":
    main()
