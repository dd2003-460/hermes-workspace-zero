# IC_K ≠ inf IC: When the Infimum Destroys the Answer

*Two objects. Same notation family. Completely different behavior. Confusing them leads to wrong answers about how hard computational problems actually are.*

---

## 1. Why This Distinction Matters

You need a lower bound on how many bits *must* travel between two parties — not on average, but always. You find two variants of information complexity:

- **IC\_K**: worst-case information cost, measured with Kolmogorov complexity.
- **inf IC**: the infimum over all distributions of Shannon information cost.

They share a vocabulary — internal complexity, information leakage, protocol transcripts. Maybe IC\_K is just inf IC done with better tools.

They're not. The difference isn't a technicality — it's the difference between a measure that captures real structural hardness and one that vanishes entirely.

This post is about why: the quantifier order, the complexity measure, and what each is actually answering.

---

## 2. IC_K: Finite, Concrete, Computable in Principle

IC\_K is defined by two operations: **supremum** over input pairs, **minimum** over protocols. Given a function $f$ and a protocol $\pi$, the information cost on input $(x, y)$ is:

$$\text{cost}_\pi(x, y) = K(M_\pi(x, y) \mid y) + K(M_\pi(x, y) \mid x)$$

where $M_\pi(x, y)$ is the transcript — the full record of messages exchanged. The first term asks: given Bob's input $y$, how hard is it to reconstruct the transcript? That captures what the protocol *leaked* about Alice's input $x$. The second term is symmetric.

Then IC\_K takes the worst case:

$$\text{IC}_K(f) = \min_\pi \sup_{(x,y)} \text{cost}_\pi(x, y)$$

Every piece of this is finite. For a fixed input pair and a fixed protocol, the transcript is a concrete string. Its conditional Kolmogorov complexity is a concrete number — the length of the shortest program that reconstructs it. You take the worst input pair (still finite for Boolean functions on finite domains), then the best protocol (also finite — there are finitely many). The result is a number.

IC\_K is not *easy* to compute — Kolmogorov complexity is uncomputable in general. But it's **well-defined and finite**. It's a property of the function, not of your modeling choices. There's no distribution to pick, no parameter to tune.

---

## 3. inf IC: A Limit in Disguise

Now look at the Shannon version. Classical information complexity $\text{IC}(f, \mu)$ measures, for a fixed distribution $\mu$ over inputs, the mutual information between the inputs and the protocol transcript. It's a powerful tool — it's given us tight bounds for Disjointness, resolved direct sum questions, and much more.

But it depends on $\mu$. Different distributions give different answers. So the natural instinct is: take the infimum.

$$\text{IC}(f) = \inf_\mu \text{IC}(f, \mu)$$

This looks like it should be a single number — the "distribution-free" information complexity. But it's not a number in the way IC\_K is. It's the output of an optimization over an *infinite space* of distributions, and that optimization has a trivial answer:

$$\inf_\mu \text{IC}(f, \mu) = 0, \text{ for every Boolean function } f.$$

Pick the point-mass distribution that concentrates all probability on a single input pair $(a, b)$. Under this distribution, a protocol that hardcodes $f(a, b)$ and communicates nothing is correct with probability 1. Zero leakage. Infimum achieved.

The infimum exists, it's well-defined, and it's useless. The "distribution-free" version of Shannon IC doesn't free you from distributions — it collapses under them.

But the degeneracy is telling you something about the *meaning* of infimum. Semantically, $\inf_\mu$ asks: "Across all possible input distributions, what's the least information the protocol *ever* has to leak?" The answer is always zero, because there's always a distribution that makes the problem trivial. The infimum is *designed* to find the easiest case. It's not a pathological artifact — it's the quantifier doing what it's supposed to do.

The reason this feels wrong is that $\inf$ and $\sup$ are not symmetric in a computational context. When you want to *guarantee* correctness — to bound resources that must always suffice, to certify leakage that can never exceed — you need the supremum: "what's the hardest case I must handle?"

**Supremum captures obligation. Infimum captures possibility.** Saying "there exists a distribution under which leakage is zero" tells you something is *possible*. Saying "for every input pair, leakage is at least $c$" tells you something is *necessary*. If your goal is a guarantee — a bound you can rely on — only the necessity claim matters. Taking the infimum answers the wrong question not because the math is wrong, but because possibility and necessity are fundamentally different epistemic categories.

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

**Composition breaks differently.** When you compose protocols, IC\_K composes cleanly: $\text{IC}_K(f^n) \leq n \cdot \text{IC}_K(f) + O(\log n)$. inf IC composes to zero, because the infimum is already zero. If your architecture relies on "information cost adds up," you need IC\_K's worst-case additivity.

**Information leakage audits: an engineering scenario.** Imagine you're building an audit framework for a distributed database. Each node processes queries locally and shares aggregated results. You measure leakage under observed traffic — roughly uniform over query patterns — and conclude per-query leakage is bounded by $\epsilon$.

But an adversary doesn't query uniformly. They concentrate on degenerate inputs: repeated identical queries to the same node, targeted at the rarest records, in patterns your model assigns negligible probability to. Under those patterns, the *actual* leakage can be orders of magnitude larger — because your analysis was an average-case bound, and averages hide tails.

The formal parallel to IC is exact. Your audit computed $\text{IC}(f, \mu_{\text{observed}})$ for a fixed $\mu$. The adversary finds an input pair $(a, b)$ that's degenerate under your distribution. If instead the audit had used an IC\_K-style worst-case analysis — bounding leakage for *every* input pair — the adversarial pattern would have been caught from the start.

This isn't hypothetical. Side-channel leakage in cryptographic implementations shows the same structure: timing analysis under uniform inputs gives clean bounds; timing analysis under adversarially chosen inputs reveals leakage that the uniform analysis missed.

The pattern is always the same: **if your guarantee can degenerate under a pathological input, the guarantee isn't real.** It's a property of your model, not of the problem. The fix isn't to find a better distribution — it's to ask a question that doesn't depend on distributions at all.

---

## 6. The Takeaway

IC\_K and inf IC live in the same neighborhood of ideas. Both try to measure internal complexity — how much information a protocol must reveal. But IC\_K asks the worst-case question ("what's the hardest input?") with the right tool (Kolmogorov complexity), while inf IC asks the average-case question ("what's the easiest distribution?") and gets a trivial answer.

The mathematical lesson: **quantifier order and complexity measure aren't implementation details — they determine what question you're actually asking.** Swap $\sup$ for $\inf$ and you go from capturing structural hardness to trivializing it. Swap Kolmogorov for Shannon and you go from instance-level guarantees to distribution-dependent averages.

The engineering lesson: if your system's correctness depends on information-theoretic lower bounds, make sure those bounds hold in the worst case. Average-case guarantees are real, but they're not the same thing — and confusing the two is how you end up with a protocol that's "secure in expectation" and broken in practice.

---

*This is a companion post to "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective." That post introduces IC\_K as a distribution-free measure; this post argues that IC\_K and inf IC are not equivalent — and that the distinction matters both mathematically and practically.*
