---
title: "IC_K ≠ inf IC: Why Optimizing Over Distributions Kills Your Lower Bound"
subtitle: "Worst-case vs average-case information complexity — and what happens when you confuse the two"
date: 2026-04-03
tags: [information_theory, kolmogorov_complexity, communication_complexity]
series: "IC_K Trilogy"
series_position: 3
prev_post: "/posts/average-case-isnt-enough"
summary: "Two measures share a notation but answer completely different questions. One vanishes for every Boolean function. The other captures structural hardness. The difference between supremum and infimum isn't notation — it's the difference between obligation and possibility."
---

# IC_K ≠ inf IC: When the Infimum Destroys the Answer

*Why optimizing over distributions kills your lower bound*

---

## 1. Why This Distinction Matters

You need a lower bound on how many bits *must* travel between two parties — not on average, but always. You find two variants of information complexity:

- **IC\_K**: worst-case information cost, measured with Kolmogorov complexity.
- **inf IC**: the infimum over all distributions of Shannon information cost.

They share a vocabulary — internal complexity, information leakage, protocol transcripts. Maybe IC\_K is just inf IC done with better tools.

They're not. The difference isn't a technicality — it's the difference between a measure that captures real structural hardness and one that vanishes entirely.

---

## 2. IC_K: Finite, Concrete, Computable in Principle

IC\_K is defined by two operations: **supremum** over input pairs, **minimum** over protocols. Given a function $f$ and a protocol $\pi$, the information cost on input $(x, y)$ is:

$$\text{cost}_\pi(x, y) = K(M_\pi(x, y) \mid y) + K(M_\pi(x, y) \mid x)$$

where $M_\pi(x, y)$ is the transcript — the full record of messages exchanged. The first term asks: given Bob's input $y$, how hard is it to reconstruct the transcript? That captures what the protocol *leaked* about Alice's input $x$. The second term is symmetric.

Then IC\_K takes the worst case:

$$\text{IC}_K(f) = \min_\pi \sup_{(x,y)} \text{cost}_\pi(x, y)$$

Every piece of this is finite. For a fixed input pair and a fixed protocol, the transcript is a concrete string. Its conditional Kolmogorov complexity is a concrete number — the length of the shortest program that reconstructs it. You take the worst input pair (still finite for Boolean functions on finite domains), then the best protocol (also finite — for any fixed communication budget $B$, there are finitely many protocols with transcripts of length ≤ $B$, and the optimum is achieved at some finite $B$). The result is a number.

IC\_K is not *easy* to compute — Kolmogorov complexity is uncomputable in general. But it's **well-defined and finite**. It's a property of the function, not of your modeling choices. There's no distribution to pick, no parameter to tune.

---

## 3. inf IC: A Limit in Disguise

Now look at the Shannon version. Classical information complexity $\text{IC}(f, \mu)$ measures, for a fixed distribution $\mu$ over inputs, the mutual information between the inputs and the protocol transcript. It's a powerful tool — it's given us tight bounds for Disjointness, resolved direct sum questions, and much more.

But it depends on $\mu$. Different distributions give different answers. So the natural instinct is: take the infimum.

$$\text{IC}(f) = \inf_\mu \text{IC}(f, \mu)$$

This looks like it should be a single number — the "distribution-free" information complexity. But it's not a number in the way IC\_K is. It's the output of an optimization over an *infinite space* of distributions, and that optimization has a trivial result:

$$\inf_\mu \text{IC}(f, \mu) = 0, \text{ for every Boolean function } f.$$

Pick the point-mass distribution that concentrates all probability on a single input pair $(a, b)$. Under this distribution, a protocol that hardcodes $f(a, b)$ and communicates nothing is correct with probability 1. Zero leakage. Infimum achieved.

The infimum exists, it's well-defined, and it's useless. The "distribution-free" version of Shannon IC doesn't free you from distributions — it collapses under them.

But the degeneracy is telling you something about the *meaning* of infimum. Semantically, $\inf_\mu$ asks: "Across all possible input distributions, what's the least information the protocol *ever* has to leak?" The answer is always zero, because there's always a distribution that makes the problem trivial.

**Supremum captures obligation. Infimum captures possibility.** Saying "there exists a distribution under which leakage is zero" tells you something is *possible*. Saying "for every input pair, leakage is at least $c$" tells you something is *necessary*.

---

## 4. Why They're Not the Same Object

The surface similarity is seductive. Both measure "how much information the protocol reveals." Both can be framed as inner complexity. But they differ in three structural ways that no clever reparameterization can bridge.

**Different quantifier order.** IC\_K is $\min_\pi \sup_{(x,y)}$. inf IC is $\inf_\mu \min_\pi$. In IC\_K, the adversary picks the hardest input *after* you've committed to a protocol. In inf IC, point-mass distributions can always drive the answer to zero. The minimax theorem doesn't save you, because degenerate distributions require no communication.

**Different complexity measures.** IC\_K uses Kolmogorov complexity — algorithmic, instance-level, no distribution needed. inf IC uses Shannon mutual information — probabilistic, distribution-tied. Kolmogorov complexity measures the *algorithmic content* of a specific string. Shannon entropy measures *average surprise* under a distribution. They agree for large "typical" strings, but protocol transcripts are small and structured — exactly where they diverge.

**Different objects altogether.** IC\_K is a function property: $f \mapsto \text{IC}_K(f)$, a map from functions to numbers. inf IC is the result of a limit process over an infinite family of distribution-dependent quantities. One is a noun. The other is a noun phrase built from a verb ("take the infimum").

### A Concrete Counterexample

Equality on $n$-bit strings makes this vivid.

| Measure | Result | Interpretation |
|---------|--------|---------------|
| $\text{IC}_K(\text{EQ})$ | $\Theta(\log n)$ | Worst-case inputs force the protocol to reveal the mismatch position |
| $\inf_\mu \text{IC}(\text{EQ}, \mu)$ | $0$ | Point mass on any single pair. Always zero. For any $n$. |

Same function. One measure says $\Theta(\log n)$. The other says $0$. They aren't even in the same order of magnitude. If you used inf IC as a lower bound, you'd conclude that Equality requires zero communication — which is trivially wrong.

---

## 5. When This Bites You in Practice

The IC\_K ≠ inf IC distinction isn't a curiosity for theorists. It has concrete engineering consequences whenever you're reasoning about information flow in distributed systems.

**"Average-case secure" isn't secure.** If your protocol's leakage analysis relies on averaging over an assumed input distribution, your guarantee is only as good as that distribution. An adversary who concentrates probability on degenerate cases can break your leakage bound. IC\_K holds for *every* input pair, not just the ones your model predicts.

**Lower bounds that don't transfer.** A lower bound on $\text{IC}(f, \mu)$ under the uniform distribution tells you about *expected* cost under that specific distribution. Use it to set buffer sizes or bandwidth budgets, and you're betting that real inputs look like your distribution. IC\_K lower bounds hold unconditionally.

The pattern is always the same: **if your guarantee can degenerate under a pathological input, the guarantee isn't real.** It's a property of your model, not of the problem.

**Privacy auditing blind spots.** A compliance team audits data leakage from a distributed analytics platform by computing $\text{IC}(f, \mu_{\text{observed}})$ — the information cost under their empirically observed query distribution. The audit clears: average per-query leakage is below the regulatory threshold ε.

But regulators and adversaries don't query like typical users. They submit targeted, rare, edge-case queries: unusual joins between tables, specific attribute combinations that reveal individual records. Under the uniform distribution your model assigns them negligible probability — so they barely appear in the IC calculation. Under these adversarial inputs, the actual information leakage is orders of magnitude larger.

Your audit computed $\text{IC}(f, \mu)$ for one specific $\mu$. What you needed was a bound that holds for *every* input pair — the kind of analysis IC_K provides. The gap between the certified number and the worst case isn't a bug — it's the quantifier gap.

**Composition breaks differently.** When you compose protocols, IC_K composes with at most logarithmic overhead: $\text{IC}_K(f^n) \leq n \cdot \text{IC}_K(f) + O(\log n)$ (up to logarithmic terms in the prefix complexity of the protocol description; composition theorem follows from the Kolmogorov chain rule — see Li & Vitányi, An Introduction to Kolmogorov Complexity and Its Applications, Ch. 2; and Braverman, Interactive Information Complexity, STOC 2012). inf IC composes to zero, because the infimum is already zero. If your architecture relies on "information cost adds up," you need IC\_K's worst-case additivity.

---

## 6. The Takeaway

IC\_K and inf IC live in the same neighborhood of ideas. Both try to measure internal complexity — how much information a protocol must reveal. But IC\_K asks the worst-case question ("what's the hardest input?") with the right tool (Kolmogorov complexity), while inf IC asks the average-case question ("what's the easiest distribution?") and gets a trivial answer.

IC_K and inf IC ask different questions about the same object. One says: "What's the hardest input, across all protocols?" The other says: "What's the easiest distribution?" For Equality on $n$-bit strings, the first answer is $\Theta(\log n)$. The second is $0$. Which one do you bet your security budget on?

The mathematical lesson is structural: quantifier order and complexity measure determine what question you're actually asking. Swap $\sup$ for $\inf$ and you go from capturing hardness to trivializing it. The engineering lesson is simpler: a guarantee that degenerates under pathological inputs isn't a guarantee at all — it's a property of your model.

So when you read a theorem about information complexity, ask: which way are the quantifiers pointing? Because the difference between "there exists an easy case" and "every case is hard" isn't a detail — it's the whole game.

---

*This is a companion post to "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective." That post introduces IC\_K as a distribution-free measure; this post argues that IC\_K and inf IC are not equivalent — and that the distinction matters both mathematically and practically.*
