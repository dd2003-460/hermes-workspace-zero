#!/usr/bin/env python3
"""LoRA fine-tuning script for persona-align on Qwen3.6-35B-A3B-MLX-6bit.

Uses mlx_lm.lora with the locally cached model weights.
Data format: {prompt, completion} — converted from instruction/output format.

Usage:
    python train_lora.py --model <path> --data <path> --iters <n>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, "/Users/a1-6/D1-automation/mlx-abliteration/.venv_mlx/lib/python3.12/site-packages")

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import mlx_lm
from mlx_lm.lora import linear_to_lora_layers, TrainingArgs
from mlx_lm.tuner.trainer import TrainingCallback


class ScoringCallback(TrainingCallback):
    """Custom callback to score outputs during training."""

    def __init__(self, model, tokenizer, dataset, tokenizer_obj=None):
        self.model = model
        self.tokenizer = tokenizer
        self.dataset = dataset
        self.eval_tokenizer = tokenizer_obj

    def __call__(self, step, log, train_logs):
        if step % 10 == 0:
            print(f"\n[Step {step}] Loss: {log['loss']:.4f} | "
                  f"PPL: {log.get('ppl', 'N/A')}")

        if step % 20 == 0 and self.dataset:
            # Generate a test response
            sample = self.dataset[0]
            prompt = sample["prompt"]
            generated = mlx_lm.generate(
                self.model, self.tokenizer,
                prompt=prompt,
                max_tokens=256,
                temperature=0.5,
            )
            print(f"\n[Step {step}] Test generation:")
            print(f"  Prompt: {prompt[:60]}...")
            print(f"  Output: {generated[:120]}...")
            print()


def main():
    parser = argparse.ArgumentParser(description="LoRA fine-tuning for persona-align")
    parser.add_argument("--model", type=str, default="/Users/a1-6/.lmstudio/models/Youssofal/Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit")
    parser.add_argument("--data", type=str, default="lora_training/dataset")
    parser.add_argument("--iters", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-seq", type=int, default=2048)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-scale", type=float, default=2.0)
    parser.add_argument("--layers", type=int, default=8)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--adapter-file", type=str, default="lora_training/adapters.safetensors")
    args = parser.parse_args()

    # Load model
    print(f"Loading model: {args.model}")
    model, tokenizer = mlx_lm.load(args.model)
    print(f"Model: {type(model).__name__}")
    print(f"Tokenizer: {type(tokenizer).__name__}")

    # Set up LoRA layers
    print(f"\nSetting up LoRA layers (rank={args.lora_rank}, scale={args.lora_scale}, {args.layers} layers)")
    config = {
        "rank": args.lora_rank,
        "scale": args.lora_scale,
        "dropout": args.dropout,
        "weight_decay": 0.0,
    }
    lora_layers = linear_to_lora_layers(model, args.layers, config)
    print(f"LoRA layers attached: {len(lora_layers)}")

    # Set optimizer
    optimizer = optim.AdamW(learning_rate=args.lr)

    # Print trainable params
    total_params = sum(v.size for v in model.parameters())
    trainable_params = sum(v.size for v in lora_layers.parameters())
    print(f"\nTotal params: {total_params:,}")
    print(f"Trainable params: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")

    # Training config
    training_args = TrainingArgs(
        batch_size=args.batch_size,
        iters=args.iters,
        val_batches=2,
        steps_per_report=5,
        steps_per_eval=10,
        steps_per_save=50,
        max_seq_length=args.max_seq,
        adapter_file=args.adapter_file,
        grad_accumulation_steps=1,
    )

    # Start training
    print(f"\nTraining for {args.iters} iterations")
    print(f"Data directory: {args.data}")
    print(f"Batch size: {args.batch_size}")

    import mlx_lm.lora as lora_module
    lora_module.main(vars(args))


if __name__ == "__main__":
    main()
