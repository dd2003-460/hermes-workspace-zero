#!/usr/bin/env python3
"""Convert persona-align training data to mlx_lm lora format.

mlx_lm expects: {"prompt": "...", "completion": "..."}
Our data uses: {"instruction": "...", "output": "..."}
"""

import json
import sys
import os
import random

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "raw/lora_data/lora_trainset.jsonl"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "lora_training/dataset"

    # Read training data
    samples = []
    with open(input_path) as f:
        for line in f:
            obj = json.loads(line)
            if obj["metadata"].get("source", "").startswith("hermes"):
                samples.append({
                    "prompt": obj["instruction"],
                    "completion": obj["output"],
                })

    print(f"Loaded {len(samples)} synthetic samples")

    # Shuffle and split
    random.seed(42)
    random.shuffle(samples)

    # 80% train, 10% valid, 10% test
    n = len(samples)
    train = samples[:int(n*0.8)]
    valid = samples[int(n*0.8):int(n*0.9)]
    test = samples[int(n*0.9):]

    os.makedirs(output_dir, exist_ok=True)

    for name, data in [("train", train), ("valid", valid), ("test", test)]:
        path = os.path.join(output_dir, f"{name}.jsonl")
        with open(path, "w") as f:
            for s in data:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        print(f"  {name}.jsonl: {len(data)} samples")

    print(f"\nDataset saved to: {output_dir}")

if __name__ == "__main__":
    main()
