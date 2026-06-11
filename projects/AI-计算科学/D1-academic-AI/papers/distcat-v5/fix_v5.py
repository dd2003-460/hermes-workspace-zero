#!/usr/bin/env python3
import sys

tex_path = sys.argv[1]

with open(tex_path, 'r') as f:
    lines = f.readlines()

# Fix \n on line 67 (0-indexed 66)
lines[66] = lines[66].replace('\\n\\usepackage{tikz-cd}', '\n')

# Replace Chinese full stops and Unicode
for i, line in enumerate(lines):
    line = line.replace('。', '.')
    line = line.replace('∞', '\\infty')
    line = line.replace('α', '\\alpha')
    line = line.replace('θ', '\\theta')
    line = line.replace('≈', '\\approx')
    lines[i] = line

# Replace tikzcd
result = []
skip = False
tikzcd_repl = [
    '\\[\n',
    '\\begin{array}{ccc}\n',
    '\\zeta_M(w_i, w_j) ',
    '& \\xrightarrow{\\;\\eta_\\phi\\;} ',
    '& \\zeta_{M}(\\phi(w_i), \\phi(w_j)) \\\\' + '\n',
    '\\downarrow & & \\downarrow\n',
    '\\text{state}(\\omega_M) ',
    '& \\xrightarrow{\\;\\phi^*\\;} ',
    "& \\text{state}(\\omega_{M'})" + '\n',
    '\\end{array}\n',
    '\\]\n',
]
for line in lines:
    if '\\begin{tikzcd}' in line:
        result.extend(tikzcd_repl)
        skip = True
        continue
    if skip and '\\end{tikzcd}' in line:
        skip = False
        continue
    result.append(line)

with open(tex_path, 'w') as f:
    f.writelines(result)

print(f"Basic fixes applied. {len(result)} lines")
