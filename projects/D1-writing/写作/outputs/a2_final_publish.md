---
title: "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective"
date: 2026-04-03
tags: [mathematics, information-theory, complexity-theory, communication-complexity, kolmogorov-complexity]
canonical_url: ""
---

# Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective

*Information complexity is the most refined tool in communication complexity. But if you try to make it distribution-free, it vanishes. This isn't a bug — it reveals something structural about why average-case analysis can miss the point entirely.*

---

## 1. A Measure That Vanishes When You Try to Fix It

Information complexity is often called the "grammar" of communication complexity — the rules that let you say something precise about why a computational problem is hard. While deterministic communication complexity $D(f)$ simply counts the worst-case number of bits exchanged, information complexity asks a deeper question: *how much information about the inputs must the protocol reveal?* This shift from counting bits to measuring information has been remarkably powerful. It's yielded tight bounds on the Disjointness function, resolved the direct sum problem, and become the go-to framework for understanding the *essence* of communication hardness rather than just its combinatorial shell.

So what's the problem? Information complexity has an Achilles' heel: it depends on a **distribution over inputs**. The classical definition $\text{IC}(f, \mu)$ measures the mutual information between inputs $(X, Y) \sim \mu$ and the protocol transcript, and it gives genuinely different answers for different choices of $\mu$. Under the uniform distribution, Equality costs $\Theta(\log n)$ bits of information. Under a biased distribution, the answer shifts. This distribution-dependence feels like a conceptual mismatch — deterministic communication complexity doesn't care about distributions, so why should its information-theoretic refinement?

The natural fix seems obvious: just take the infimum over all distributions. Define $\text{IC}(f) = \inf_\mu \text{IC}(f, \mu)$. Now it's distribution-free. Problem solved?

Unfortunately the answer is: **it vanishes**. Precisely zero.

> **Theorem.** For every Boolean function $f$, $\inf_\mu \text{IC}(f, \mu) = 0$.

Why? Because you can always choose the point-mass distribution — concentrate all probability on a single input pair $(a, b)$. Under this distribution, a protocol that simply outputs $f(a, b)$ without *any* communication is correct with probability 1. The revealed information is exactly zero. Infimum achieved. Game over.

This isn't an approximation to zero, or "small." It's the mathematical equivalent of asking "how hard is this problem?" and getting the answer "zero, if you only consider the one easy case."

This is the problem that motivated IC\_K — and in the process, it reveals something genuinely interesting about average-case analysis in computation.

---

## 2. The 30-Second Version

If you've ever done average-case analysis in machine learning or theoretical CS — and you have — this is about why that tool has blind spots built into its design. Consider the simplest possible communication task: two parties check whether their $n$-bit strings are equal. Measure the information leaked by the optimal protocol, then minimize over all possible input distributions. The answer is always zero. Not because this is an easy problem (it isn't — it requires $\Theta(\log n)$ bits of communication). Because **the averaging operation itself erases structural complexity**. A distribution-free, worst-case version called IC\_K restores the structure that averaging destroyed. This isn't just a technical improvement — it suggests that *any* pure average-case analysis has inherent blind spots, and the worst-case lens recovers information that the average case is structurally incapable of seeing.

---

## 3. Why Averaging Kills Information

Let me make the degeneracy precise and then convince you it's not just a communication-complexity pathology.

### 3.1 Point Mass Degeneracy

The proof that $\inf_\mu \text{IC}(f, \mu) = 0$ is one line: take $\mu = \delta_{(a,b)}$, a single point mass. Then $H(X|Y) = H(Y|X) = 0$ because knowing one input completely determines the other. The conditional mutual information $I(M; X | Y) = H(M|Y) - H(M|X,Y) = 0 - 0 = 0$. Done.

But this one-line proof is actually a four-line philosophical statement in disguise. The infimum operation asks: **"What's the easiest case?"** And the answer to that question is always: "The single point that requires no communication at all." This is what infimum *means*, semantically. It's not a bug in the proof — it's a feature of the quantifier.

The deeper issue is that $\inf$ and $\sup$ are not symmetric in a computational context. When you want to *guarantee* correctness, you need the supremum ("what's the hardest case I must handle?"). When you take the infimum ("what's the easiest case?"), you're answering the wrong question for the kind of guarantee you want. Information complexity is trying to capture *inherent* difficulty — but inf over distributions answers *trivial* difficulty.

### 3.2 This Isn't Unique to Communication Complexity

If this feels familiar from machine learning, that's not coincidence. The same asymmetry shows up everywhere average-case analysis interacts with worst-case guarantees:

In **PAC learning**, you can trivially achieve zero error on any degenerate distribution — just memorize the support. The meaningful guarantees come from uniform convergence arguments that hold across *all* distributions in a class. The VC dimension, for instance, is fundamentally a worst-case combinatorial object masquerading inside an average-case framework.

In **distributional complexity**, Levin's optimal Polynomial Time model takes supremum over inputs, not infimum over distributions. The hardest instances dominate, because a complexity theory built on "easiest case" reasoning would trivialize just like IC does.

In **generalization theory**, pointwise convergence of empirical risk to true risk is trivially satisfied for any fixed distribution. But that tells you nothing about out-of-distribution behavior. Uniform convergence — the supremum version — is what actually guarantees generalization, and what's strictly harder to achieve.

The lesson is consistent: **if your analysis can degenerate under a pathological distribution, the issue isn't that you picked the wrong distribution — it's that your question was the wrong question.** The right question should survive any distribution. Taking supremum rather than infimum is the structural fix, not a distribution-dependent workaround.

---

## 4. The Fix: IC\_K — Worst-Case by Supremum, Distribution-Free by Kolmogorov

### 4.1 Two Swaps

IC\_K fixes both problems simultaneously by making **two swaps** that change the character entirely:

**Swap 1: inf → sup.** Instead of minimizing over distributions (finding the easiest case), we maximize over input pairs (finding the hardest case).

**Swap 2: Shannon → Kolmogorov.** Instead of using Shannon mutual information (probabilistic, distribution-dependent), we use conditional Kolmogorov complexity (algorithmic, instance-level).

The definition:

$$\text{IC}_K(f) = \min_{\pi}\ \sup_{(x,y)} \big[K(M_\pi(x,y) \mid y, \pi) + K(M_\pi(x,y) \mid x, \pi)\big]$$

where $M_\pi(x,y)$ is the protocol transcript. The question is: given Bob's input $y$ and the protocol description, how hard is it to reconstruct the transcript? That measures what the transcript *reveals* about Alice's input. And we take the supremum over all input pairs.

### 4.2 Why This Isn't Just Wordplay

Two things could go wrong. First: algorithmic mutual information $I_K(x : y) = K(x) + K(y) - K(x, y)$ is distribution-free — so why not just use it? Because $I_K$ trivializes for Boolean functions. When the output is one bit, knowing the protocol output constrains $I_K$ to roughly $O(1)$ for everything. The measure can't distinguish functions that require linear communication from ones that need a constant number of bits.

Second: why measure the transcript rather than just the protocol output? Because the output is one bit (for Boolean functions) — it contains almost no information. The transcript, though — that's where the information flows. Measuring $K(M \mid y)$ captures what the communication pattern leaks, not just what it computes.

Put simply: IC\_K looks at the **journey** of information between the parties, not the **destination**. And the supremum ensures the journey is evaluated for the hardest input pair, not the easiest.

### 4.3 The Minimax Duality

There's a clean duality worth highlighting. Shannon information complexity and IC\_K differ by the order of their quantifiers:

| Framework | Quantifier order | Interpretation |
|-----------|-----------------|----------------|
| Shannon IC | $\sup_\mu \inf_\pi$ | Hardest distribution, best protocol |
| IC\_K | $\inf_\pi \sup_{x,y}$ | Best protocol, hardest input pair |

Swapping quantifiers changes the game. In Shannon IC, the adversary picks a distribution first, then you pick the best protocol. In IC\_K, you pick the best protocol first, then the adversary picks a worst-case input pair. This is a genuinely different measure — not minimax-equivalent, because the $\inf_\mu$ in IC allows degenerate (point-mass) distributions where no minimax theorem applies.

Think of it this way: Shannon IC asks "in expectation, how much does the protocol reveal?" IC\_K asks "in the worst case, how much *must* the protocol reveal?" Both are meaningful. But only one of them survives distribution-free analysis.

The first structural result is a sanity check: IC\_K is bounded by deterministic communication:

> **Theorem.** $\text{IC}_K(f) \leq 2D(f) + O(1)$.

The key takeaway: IC\_K is not vacuously large. It's calibrated against the most basic communication measure we have. If $D(f)$ is $n$, IC\_K is at most roughly $2n$.

---

## 5. The Concrete Case: Equality at $\Theta(\log n)$

The best way to see IC\_K in action is the Equality function. Alice holds $x \in \{0,1\}^n$, Bob holds $y \in \{0,1\}^n$, and they want to know whether $x = y$.

The optimal deterministic protocol is a binary search. Alice and Bob iteratively compare halves of their strings, narrowing the interval where the first mismatch could be. For $n = 8$, say $x = 01101010$ and $y = 01101011$ — they differ only at the last bit:

```
Round 1: x[1..4] = 0110, y[1..4] = 0110  → match
Round 2: x[5..8] = 1010, y[5..8] = 1011  → mismatch (4 bits)
Round 3: x[7..8] = 10,    y[7..8] = 11    → mismatch (2 bits)
```

Three rounds. The transcript $M$ records which halves matched and which didn't — roughly $\log n$ bits of information.

Now the IC\_K computation. Bob knows $y = 01101011$ and the protocol $\pi$. Can he predict $M$? No — because he doesn't know $x$, he can't know *which* halves match. Reconstructing $M$ given $y$ requires about $\log n$ bits. The same goes for Alice computing $K(M \mid x)$. So the cost is $\Theta(\log n)$.

> **Theorem.** $\text{IC}_K(\text{EQ}) = \Theta(\log n)$.

The key observation: there always exist input pairs where $x$ and $y$ differ at exactly one adversarial position. For these pairs, the protocol is *forced* to reveal the position of the mismatch — a piece of information that requires $\log n$ bits. No shortcut exists.

Compare with what happens under point mass. If $\mu$ concentrates on $x = y = 0^8$, the protocol reveals zero information. $\inf_\mu \text{IC}(\text{EQ}, \mu) = 0$. But IC\_K takes the supremum, so the hard pairs govern. **Same function, two completely different answers.** This is the entire argument for worst-case information measures, compressed into one example.

---

## 6. Why This Matters

There are three reasons to care, in order of increasing generality.

**New lower-bound tools, without distribution engineering.** Since $\text{IC}_K(f) \leq 2D(f) + O(1)$, any lower bound on IC\_K is automatically a lower bound on deterministic communication. The advantage? You don't need to construct adversarial distributions. The IC\_K bound holds unconditionally. The Equality result is a proof of concept: the right lower bound ($\Theta(\log n)$) falls out of the definition without any distribution assumptions. For harder functions like Disjointness, proving $\text{IC}_K(\text{DISJ}) = \Theta(n)$ would establish IC\_K as a genuinely useful proof technique, not just a conceptual improvement.

**Direct sum and the question of composition.** A central question is whether computing $f$ on $n$ independent copies costs $n$ times the single-instance cost. The IC\_K framework gives a clean answer:

$$\text{IC}_K(f^n) \leq n \cdot \text{IC}_K(f) + O(n \log n)$$

Using prefix Kolmogorov complexity $\kappa$ instead of plain $K$, the overhead tightens to $O(1)$:

$$\text{IC}_\kappa(f^n) \leq n \cdot \text{IC}_\kappa(f) + O(1)$$

This is exactly the kind of clean composition property you want from an information measure. It suggests IC\_K (or its prefix variant) might be the "right" notion for studying composition in communication — questions like the log-rank conjecture or bounds for $f \circ g$, where current techniques are distribution-dependent.

**The general lesson about average-case analysis.** IC isn't wrong. It's just asking the wrong question for distribution-free guarantees. The infimum over distributions asks "what's the minimum leakage, optimized over all distributions?" — and the answer collapses to the trivial case. The supremum over inputs asks "what's the minimum leakage that holds for every input?" — and recovers the function's genuine structural complexity. The difference between these two questions isn't technical. It's the difference between "how easy can this be?" and "how hard can this be?" — and for any guarantee you actually want to rely on, the second question is the only one that matters.

---

## 7. Open Questions

Three concrete targets for where IC\_K could go next:

- **Disjointness.** Shannon IC of DISJ is $\Theta(n)$ under the uniform distribution. We conjecture $\text{IC}_K(\text{DISJ}) = \Theta(n)$ — matching the Shannon result without distributional assumptions. A proof would establish IC\_K as a practical lower-bound tool for real communication problems, not just Equality.

- **Randomized IC\_K vs. randomized Shannon IC.** Randomization changes the information-theoretic landscape in unexpected ways. For Equality, deterministic IC\_K is $\Theta(\log n)$, but the randomized version IC\_K^R drops to $O(1)$. Understanding the precise relationship between IC\_K^R and classical randomized information complexity IC^R remains open. For which functions does randomization compress communication, and by how much?

- **Strong direct sum lower bounds.** We have clean upper bounds on $\text{IC}_K(f^n)$. The matching lower bound — $\text{IC}_K(f^n) \geq n \cdot \text{IC}_K(f)$ up to lower-order terms — would complete the picture. The prefix complexity variant, with its $O(1)$ overhead, is the most promising setting.

---

## 8. The Takeaway

Information complexity has always been one of the most beautiful tools in communication complexity. Its distribution dependence was a conceptual blemish — not a practical disaster, but a mismatch between the kind of guarantee we want (distribution-free) and the kind of analysis we have (distribution-dependent). IC\_K closes that gap. It's not that average-case analysis fails — it's that "taking the infimum over all distributions" asks the wrong question. The supremum-over-inputs approach asks the right one.

The definitions were the hard part. The interesting work — proving tighter bounds, exploring composition, understanding where average-case and worst-case information measures diverge — is just beginning.

---

*Based on the paper "IC_K: Distribution-Free Kolmogorov Information Complexity" (forthcoming). The paper explores both plain Kolmogorov complexity $K$ and prefix complexity $\kappa$ formulations, with the prefix version achieving exact direct sum with $O(1)$ additive error.*
