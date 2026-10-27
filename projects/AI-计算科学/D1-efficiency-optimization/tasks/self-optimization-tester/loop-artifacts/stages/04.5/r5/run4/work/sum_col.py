#!/usr/bin/env python3
"""origin: ai — R5 run4: sum a named CSV column (stdlib only).

Usage: sum_col.py <csv path> <column name>
Prints the column sum to stdout with 2 decimal places.
Missing column -> stderr message + non-zero exit.
"""
import csv
import sys


def main(argv):
    if len(argv) != 3:
        print("usage: sum_col.py <csv path> <column name>", file=sys.stderr)
        return 2
    path, col = argv[1], argv[2]
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                print(f"error: empty csv file: {path}", file=sys.stderr)
                return 1
            if col not in header:
                print(f"error: column {col!r} not found (available: {', '.join(header)})", file=sys.stderr)
                return 1
            idx = header.index(col)
            total = 0.0
            for row in reader:
                if idx >= len(row):
                    continue
                v = row[idx].strip()
                if not v:
                    continue
                total += float(v)
        print(f"{total:.2f}")
        return 0
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1
    except ValueError:
        print(f"error: non-numeric value in column {col!r}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
