---
title: "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective"
date: 2026-04-04
tags: [mathematics, information-theory, complexity-theory, communication-complexity, kolmogorov-complexity]
canonical_url: ""
---

# Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective

*Information complexity is the most refined tool in communication complexity. But if you try to make it distribution-free, it vanishes. This reveals something structural about why average-case analysis can miss the point entirely.*

---

## 1. The Vanishing Act

For every Boolean function in the universe — Disjointness, Equality, Inner Product, every one — the "distribution-free" information complexity is exactly zero.

Not approximately zero. Zero. This is a theorem you can prove in one line, and it removes an entire framework from distribution-free analysis.

The natural fix seems obvious: define $\text{IC}(f) = \inf_\mu \text{IC}(f, \mu)$. Now it's distribution-free. Problem solved? Unfortunately, the infimum over distributions picks the easiest case — and the easiest case for any function is the point mass on a single input pair. Under that distribution, a protocol that just outputs $f(x,y)$ without *any* communication is correct with probability 1. The revealed information is exactly zero.

This isn't a bug in the proof — it's a feature of the quantifier. The infimum operation is doing exactly what it was designed to do: find the minimum. And the minimum, for any problem, is always the one case where nothing is hard.

---

## 2. Why Infimum Is the Wrong Question

The deeper issue is that $\inf$ and $\sup$ are not symmetric in a computational context. When you want to *guarantee* correctness, you need the supremum — "what's the hardest case I must handle?" When you take the infimum — "what's the easiest case?" — you're answering the wrong question for the kind of guarantee you want.

This isn't just a communication-complexity quirk. The same pattern shows up everywhere you try to extract worst-case guarantees from average-case reasoning.

The quantifier gap that kills information complexity isn't a pathology of communication theory — it's a structural feature of any framework that tries to extract worst-case guarantees from average-case reasoning. You've already seen this pattern — you just didn't know it had a name.

In **PAC learning**, memorize the single training example and you get zero training error, but that tells you nothing about generalization. Take a concrete case: learn the parity function on $\{0,1\}^n$ from $m = n+1$ random labeled examples. You can perfectly interpolate — empirical risk zero — but your hypothesis is random noise on the remaining $2^n - m$ inputs, which is nearly all of the domain. The VC dimension isn't cleverer — it flips the quantifier to be worst-case over hypotheses, not average-case over examples. You've *used* this pattern without noticing its shape.

Similarly, **Levin's optimal model** of distributional complexity doesn't minimize over distributions; it maximizes over inputs. Given a search problem, Levin's measure asks: what's the fastest algorithm that works on the worst input? The design choice that makes that theory meaningful is exactly the same sup-over-instances swap that IC_K makes.

And in **generalization theory**, uniform convergence provides the bridge: instead of asking "does the error on these $m$ points approximate the true error?" — which is trivially yes for any fixed hypothesis — you ask "does this hold simultaneously for *all* hypotheses in the class?" The uniform bound depends on the complexity of the entire hypothesis class (VC dimension, Rademacher complexity), not any single point. The hardest distribution in the class is what determines whether you'll generalize to new data.

The pattern is universal: whenever average-case analysis and worst-case guarantees interact, the infimum trivializes and the supremum saves you. Information complexity was the last place this pattern had been named.

---

## 3. The Fix: IC\_K

IC\_K fixes both problems by making **two swaps** that change the character entirely:

**Swap 1: inf → sup.** Instead of minimizing over distributions (finding the easiest case), we maximize over input pairs (finding the hardest case).

**Swap 2: Shannon → Kolmogorov.** Instead of using Shannon mutual information (probabilistic, distribution-dependent), we use conditional Kolmogorov complexity (algorithmic, instance-level).

$$\text{IC}_K(f) = \min_{\pi}\ \sup_{(x,y)} \big[K(M_\pi(x,y) \mid y, \pi) + K(M_\pi(x,y) \mid x, \pi)\big]$$

The question is: given Bob's input $y$ and the protocol description, how hard is it to reconstruct the transcript? That measures what the communication pattern *reveals* about Alice's input. The supremum over input pairs ensures no degenerate distribution can trivialize the measure.

Two things could go wrong with this approach. First, algorithmic mutual information $I_K(x:y)$ is already distribution-free — so why not just use it? Because $I_K$ trivializes for Boolean functions. When the output is one bit, $I_K(f(x,y); x|y) = O(1)$ for *everything* — it can't distinguish functions that require linear communication from ones that need a constant number of bits. Second, why measure the transcript rather than just the protocol output? Because for Boolean functions, the output is one bit — nearly uninformative. The transcript, though — that's where the information flows. IC\_K looks at the **journey** of computation, not the **destination**.

There's a clean duality worth highlighting. Shannon IC and IC\_K differ by their quantifier order:

| Framework | Quantifier order | What it asks |
|-----------|-----------------|--------------|
| Shannon IC | $\sup_\mu \inf_\pi$ | Hardest distribution, best protocol |
| IC\_K | $\inf_\pi \sup_{x,y}$ | Best protocol, hardest input pair |

Swapping quantifiers changes the game. The $\inf_\mu$ in Shannon IC allows degenerate point-mass distributions where no minimax theorem applies. IC\_K's $\sup_{x,y}$ prevents this. The first sanity check is an upper bound: $\text{IC}_K(f) \leq 2D(f) + O(1)$. It's not vacuously large — it's calibrated against the most basic communication measure.

With the definition in hand, the first test is a function we already understand. Equality is the natural candidate: simple to state, tight deterministic bounds known, and sensitive to distributional assumptions in the Shannon framework. If IC\_K is going to be useful, it needs to recover the right answer for Equality — $\Theta(\log n)$ — without any distributional assumptions.

---

## 4. The Concrete Case: Equality at $\Theta(\log n)$

The best way to see IC\_K in action is the Equality function. Alice holds $x \in \{0,1\}^n$, Bob holds $y \in \{0,1\}^n$, and they want to know whether $x = y$.

The optimal deterministic protocol uses binary search. For $n = 8$, say $x = 01101010$ and $y = 01101011$ — they differ only at the last bit:

```
Round 1: x[1..4] = 0110, y[1..4] = 0110  → match
Round 2: x[5..8] = 1010, y[5..8] = 1011  → mismatch (4 bits)
Round 3: x[7..8] = 10,    y[7..8] = 11    → mismatch (2 bits)
```

Three rounds to pinpoint the mismatch. Each round cuts the search space in half: 8 bits → 4 bits → 2 bits → resolved. The transcript records the *path* taken through this binary decision tree — and that path requires $\log n$ bits to describe. For adversarial inputs, every path through the tree is possible, so no compression is available.

Now the IC\_K computation. Bob knows $y = 01101011$ and the protocol $\pi$. Can he predict the transcript $M$? No — because he doesn't know $x$, he can't know *which* halves will match. Reconstructing $M$ given $y$ requires about $\log n$ bits. Same for Alice computing $K(M \mid x)$. So $\text{IC}_K(\text{EQ}) = \Theta(\log n)$.

> **Theorem.** $\text{IC}_K(\text{EQ}) = \Theta(\log n)$.

For input pairs where $x$ and $y$ differ at exactly one adversarial position, the protocol is *forced* to reveal the position — a piece of information requiring $\log n$ bits. No shortcut exists.

Compare with the point-mass case: if $\mu$ concentrates on $x = y = 0^n$, the protocol reveals zero information. $\inf_\mu \text{IC}(\text{EQ}, \mu) = 0$. But IC\_K takes the supremum, so the hard pairs govern. **Same function, two completely different answers.** This is the entire argument for worst-case information measures, compressed into one example.

The Equality example shows IC_K in action for a function whose ordinary information complexity is well-understood. But what about functions where Shannon IC gives trivial bounds? That's where the real test lies.

And that test is already visible in the Disjointness question — a problem where Shannon IC succeeds but requires carefully constructed distributional arguments. A Distribution-Free proof would eliminate the need for those arguments entirely.

---

## 5. Where It Goes Next

**Disjointness.** Shannon IC of DISJ is $\Theta(n)$ under the uniform distribution. Proving $\text{IC}_K(\text{DISJ}) = \Theta(n)$ would establish IC\_K as a practical lower-bound tool for real communication problems, not just Equality. Equality showed the concept works; Disjointness would show it scales to the flagship problem of communication complexity.

Disjointness is the right test: inputs where $x$ and $y$ share no common 1-bit. The communication-theoretic hardness of DISJ — that you essentially need to check all $n$ positions in the worst case — is exactly the kind of structural hardness that $\sup$ over inputs should capture, where $\inf$ over distributions obscures it.

**Randomized IC\_K.** Randomization changes the landscape. For Equality, deterministic IC\_K is $\Theta(\log n)$, but the randomized version drops to $O(1)$. Understanding the precise relationship between $\text{IC}_K^R$ and classical randomized IC remains open. For which functions does randomization compress communication, and by how much?

**Direct sum lower bounds.** We have clean upper bounds: $\text{IC}_K(f^n) \leq n \cdot \text{IC}_K(f) + O(n \log n)$ is proven (companion paper, Theorem 5.1), and using prefix complexity $\kappa$ the overhead tightens to $O(1)$ (Corollary 5.2). The matching lower bound — $\text{IC}_K(f^n) \geq n \cdot \text{IC}_K(f)$ — would complete the picture.

---

## 6. The Takeaway

Information complexity has always been one of the most beautiful tools in communication complexity. Its distribution dependence was a conceptual blemish — not a practical disaster, but a gap between the kind of guarantee we want (distribution-free) and the kind of analysis we have (distribution-dependent). IC\_K closes that gap.

It's not that average-case analysis is wrong. It's that "distribution-free" — when implemented as an infimum over distributions — asks the wrong question. It answers "how easy can this be?" The right question is "how hard must this be?" — and supremum over inputs is the only way to ask it without smuggling in distributional assumptions.

The definitions were the hard part. What remains is the interesting work: using IC\_K to prove bounds we couldn't prove before. A deeper lesson for anyone building guarantees into systems: if your analysis collapses under a pathological distribution, you haven't asked the right question. The right question always quantifies over the hardest case you might face, not the easiest.

This lesson extends far beyond communication complexity. In machine learning, out-of-distribution generalization fails precisely because standard guarantees average over the training distribution — the infimum over a class that excludes the adversarial edge cases your deployed model will encounter. Distribution-free analysis isn't an academic preference. It's the only analysis that doesn't fail when reality diverges from your training set. IC\_K is the communication-complexity version of a lesson ML is learning the hard way.

---

*Based on the paper "IC\_K: Distribution-Free Kolmogorov Information Complexity" (forthcoming). The paper proves: $\text{IC}_K(f) \leq 2D(f) + O(1)$ (Theorem 3.1), $\text{IC}_K(\text{EQ}) = \Theta(\log n)$ (Theorem 4.1), $\text{IC}_K(f^n) \leq n\cdot\text{IC}_K(f) + O(n \log n)$ (Theorem 5.1), and $\text{IC}_\kappa(f^n) \leq n\cdot\text{IC}_\kappa(f) + O(1)$ (Corollary 5.2).*
