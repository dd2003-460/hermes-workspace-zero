# IC_K ≠ inf IC: Why Optimizing Over Distributions Kills Your Lower Bound

*Two objects. Same notation family. Completely different behavior. Confusing them leads to wrong answers about how hard computational problems actually are.*

---

## Hook: A Tale of Two "Zeros"

Alice and Bob want to compute whether their $n$-bit inputs are equal. You're asked to prove a lower bound: how much information *must* leak, no matter what clever protocol they use?

Two researchers tackle this.

**Researcher A** computes the Kolmogorov information cost. She finds $\Theta(\log n)$: the protocol *must* reveal, in the worst case, the position of the first mismatch. There is no way around it.

**Researcher B** takes the infimum of Shannon information cost over all input distributions. She gets zero. Literally zero. Pick any single input pair, concentrate all probability there, and the protocol can hardcode the answer with no communication at all.

Same function. Same notation family. Two answers: $\Theta(\log n)$ and $0$.

At least one of them is asking the wrong question. If you use Researcher B's number as your lower bound, you'll ship a protocol believing its information leakage is negligible — and be wrong by a factor of $\Theta(\log n)$.

This post is about why this isn't a bug in the math. It's a bug in the *question*. And confusing these two objects is one of the most natural mistakes you can make in information complexity — because they look almost identical on the surface, but diverge in a way that has concrete engineering consequences.

---

## 1. Why This Distinction Matters

*This section: IC_K and inf IC are both called "information complexity" and both measure protocol information leakage, but they produce different answers for the same function. I'll show you why this matters before we define anything.*

You need a lower bound on how many bits *must* travel between two parties — not on average, but always. You find two variants of information complexity:

- **IC\_K**: worst-case information cost, measured with Kolmogorov complexity.
- **inf IC**: the infimum over all distributions of Shannon information cost.

They share a vocabulary — internal complexity, information leakage, protocol transcripts. Maybe IC\_K is just inf IC done with better tools.

They're not. The difference isn't a technicality — it's the difference between a measure that captures real structural hardness and one that can vanish entirely.

> **Confusion check.** If your goal is just to know that IC\_K ≠ inf IC, the Equality example above already proves it. But *why* they differ is the interesting part. It has to do with three structural choices — quantifier order, complexity measure, and what kind of guarantee you're actually after — that look like implementation details but aren't. The rest of this post unpacks each one.

*What happens if you treat them as the same?* Let's see, concretely. If you're designing a distributed system and you cite "information complexity lower bounds" from Shannon-style analysis, assuming they hold universally, you've just guaranteed nothing — because the infimum over distributions is always zero. You think you have a lower bound. You don't. You have a guarantee that only works in the easiest case.

---

## 2. IC_K: Finite, Concrete, Computable in Principle

*This section: I'll show that IC_K is well-defined and finite for any Boolean function on a finite domain. The reader should come away with: (a) the precise definition, (b) why every step produces a concrete number, and (c) why "finite" doesn't mean "easy to compute."*

IC\_K is defined by two operations: **supremum** over input pairs, **minimum** over protocols. Given a function $f$ and a protocol $\pi$, the information cost on input $(x, y)$ is:

$$\text{cost}_\pi(x, y) = K(M_\pi(x, y) \mid y) + K(M_\pi(x, y) \mid x)$$

where $M_\pi(x, y)$ is the transcript — the full record of messages exchanged. Let me unpack this before the notation scares you off.

> **Intuition check.** Imagine you're Bob. You know your own input $y$, and you see the transcript $M_\pi(x, y)$. The question "$K(M_\pi(x, y) \mid y)$" asks: how much *additional* information does the transcript contain beyond what you already know? If the transcript is just "yes" or "no" — one bit either way — then you already knew it after running the protocol. But if the transcript also reveals the *position* of a mismatch, that's extra information about Alice's input, and $K(\cdot|y)$ captures it. This term measures what the protocol *leaked* about Alice's input $x$. The second term is symmetric.

Then IC\_K takes the worst case:

$$\text{IC}_K(f) = \min_\pi \sup_{(x,y)} \text{cost}_\pi(x, y)$$

The read order is important: for each protocol $\pi$, find the *hardest* input pair $(x,y)$ — the one that leaks the most. Then, among all protocols, pick the one that leaks the least on its own worst case.

Every piece of this is finite. For a Boolean function on $\{0,1\}^n \times \{0,1\}^n$:

1. There are finitely many (valid) protocols for a given $f$ with bounded communication
2. Each protocol produces a finite string as transcript on each input
3. The conditional Kolmogorov complexity of any finite string is a finite number
4. The supremum over finitely many input pairs is a maximum over finitely many numbers

So IC\_K is a concrete natural number. It's a property of the function, not of your modeling choices.

IC\_K is not *easy* to compute — Kolmogorov complexity is uncomputable in general. But it's **well-defined**. There's no distribution to pick, no parameter to tune. It's the function itself telling you how much information must flow, no matter what.

> **What goes wrong if you treat this as average-case?** Some readers might object: "But worst case is too pessimistic! Real inputs aren't adversarial." That's a fair concern for *some* applications. But for lower bounds — for proving what *must* happen — you want the worst case. If you care about typical inputs, define a different measure. But don't call it the same thing.

---

## 3. inf IC: A Limit in Disguise

*This section: I'll prove that $\inf_\mu \text{IC}(f, \mu) = 0$ for every Boolean function $f$, explain why this isn't a bug, and show what goes wrong if you confuse this "zero" with "the problem is easy."*

Now look at the Shannon version. Classical information complexity $\text{IC}(f, \mu)$ measures, for a fixed distribution $\mu$ over inputs, the mutual information between the inputs and the protocol transcript. It's a powerful tool — it's given us tight bounds for Disjointness, resolved direct sum questions, and much more.

But it depends on $\mu$. Different distributions give different answers. So the natural instinct is: take the infimum.

$$\text{IC}(f) = \inf_\mu \text{IC}(f, \mu)$$

This looks like it should be a single number — the "distribution-free" information complexity. But it's not a number in the way IC\_K is. It's the output of an optimization over an *infinite space* of distributions, and that optimization can behave badly.

### The Proof (It's Really This Short)

For every Boolean function $f$: $\inf_\mu \text{IC}(f, \mu) = 0$.

**Proof.** Pick any input pair $(a, b)$ and let $\mu$ be the point-mass distribution concentrated entirely on $(a, b)$. Under this distribution, a protocol that hardcodes $f(a, b)$ and communicates *nothing* is correct with probability $1$. The mutual information between the inputs (which are now deterministic) and the empty transcript is zero. So $\text{IC}(f, \mu) = 0$. Since the infimum is at most zero and mutual information is non-negative, the infimum is exactly zero. ∎

This deserves more than a one-line proof, because the degeneracy is telling you something about the *meaning* of infimum.

### Why This Isn't a Bug — And Why It Still Breaks Everything

Semantically, $\inf_\mu$ asks: "Across all possible input distributions, what's the *least* information the protocol *ever* has to leak?" The answer is always zero, because there's always a distribution that makes the problem trivial.

But that's the point — the infimum is *designed* to find the easiest case, and it succeeds. It's not a pathological artifact. It's the quantifier doing exactly what it's supposed to do.

The reason this feels wrong is that $\inf$ and $\sup$ are not symmetric in a computational context:

| Quantifier | What it asks | What it captures |
|---|---|---|
| $\sup$ (worst-case) | "What's the hardest case I must handle?" | **Obligation** — a guarantee |
| $\inf$ (easiest) | "What's the best case that exists?" | **Possibility** — no guarantee |

Saying "there exists a distribution under which leakage is zero" tells you something is *possible*. Saying "for every input pair, leakage is at least $c$" tells you something is *necessary*. If your goal is a guarantee — a bound you can rely on — only the necessity claim matters.

> **"But Shannon IC under uniform distribution ≠ 0! That's useful!"**
>
> Absolutely right — and this is the key distinction I need to be crystal clear about. $\text{IC}(f, \mu_{\text{uniform}})$ can be large and informative. That's not what I'm calling useless. What I'm calling useless is $\inf_\mu \text{IC}(f, \mu)$ — the infimum over *all* distributions, which is always zero. The problem isn't Shannon mutual information; it's the $\inf_\mu$ operator. Keep the distribution fixed, and Shannon IC is a powerful tool. Take the infimum, and it collapses.
>
> **What goes wrong if you confuse IC$(f, \mu_{\text{uniform}})$ with IC$_K(f)$?** You get a bound that's real *only if* real inputs look uniform. For Equality on $\{0,1\}^n$, the Shannon IC under uniform distribution depends on the protocol class (deterministic vs.\ randomized, public coin vs.\ private coin), while IC$_K$(EQ) = $\Theta(\log n)$. If you use the Shannon bound to size your system's privacy budget and your inputs aren't actually uniform, your guarantee evaporates. The IC$_K$ bound, in contrast, holds for every single input pair regardless of distribution.

Taking the infimum answers the wrong question not because the math is wrong, but because it's answering the easiest-case question when you need a worst-case guarantee.

---

## 4. Why They're Not the Same Object

*This section: I'll enumerate the three structural differences between IC_K and inf IC — quantifier order, complexity measures, and object type — and show with a concrete example (Equality) that they can diverge by an arbitrarily large factor. The reader should understand that no re-parameterization can make these objects agree.*

The surface similarity is seductive. Both measure "how much information the protocol reveals." Both can be framed as inner complexity. But they differ in three structural ways that no clever reparameterization can bridge.

### (1) Different Quantifier Order

IC\_K is $\min_\pi \sup_{(x,y)}$. inf IC is $\inf_\mu \min_\pi$.

In IC\_K, the adversary picks the hardest input *after* you've committed to a protocol. This is an adversarial model: the protocol must work no matter what. In inf IC, you pick the easiest distribution *before* the protocol, and then optimize. Point-mass distributions can always drive the answer to zero.

The min-max theorem doesn't save you here, because degenerate distributions require no communication. Even if you restrict to non-degenerate distributions, you can make the infimum arbitrarily small by concentrating probability mass on inputs where $f$ happens to be constant.

> **If you confused the quantifiers,** you'd write something like: "Since IC_K takes a minimum over protocols and inf IC also takes a minimum over protocols, they must be comparable." This is wrong because the surrounding quantifiers are different — $\sup_{(x,y)}$ vs $\inf_\mu$ — and those surrounding quantifiers determine whether you're looking at an obligation or a possibility. Two expressions can share sub-structure and still evaluate to completely different things. (Compare: $\max_x \min_y$ vs $\min_y \max_x$.)

### (2) Different Complexity Measures

IC\_K uses Kolmogorov complexity — algorithmic, instance-level, no distribution needed. inf IC uses Shannon mutual information — probabilistic, distribution-tied.

Kolmogorov complexity measures the *algorithmic content* of a specific string: the length of the shortest program that generates it. Shannon entropy measures *average surprise* under a distribution: $H(X) = \sum -p(x)\log p(x)$.

For long random strings, they essentially agree (the source coding theorem). But protocol transcripts are typically short and structured — exactly where they diverge.

> **Concrete illustration.** Consider a transcript that says "position 7 differs." Under Kolmogorov complexity, describing this takes about $\log n$ bits (to specify which position). Under Shannon, the information content depends entirely on your distribution over positions — if position 7 has probability 0.99, it carries almost no Shannon information. If position 7 has probability $1/n$, it carries $\log n$ bits. Kolmogorov complexity doesn't care about your distributional assumptions — position 7 always takes $\log n$ bits to specify.

### (3) Different Objects Altogether

IC\_K is a function property: $f \mapsto \text{IC}_K(f)$, a map from functions to numbers. It's computed directly from the function's truth table and the definition of valid protocols.

inf IC is the result of a limit process over an infinite family of distribution-dependent quantities. It requires you to consider *all possible* distributions and find the one that minimizes information cost.

One is a noun. The other is a noun phrase built from a verb ("take the infimum").

### A Concrete Counterexample

Equality on $n$-bit strings makes this vivid:

| Measure | Value for EQ | Scaling with $n$ |
|---|---|---|
| $\text{IC}_K(\text{EQ})$ | $\Theta(\log n)$ | Grows logarithmically |
| $\inf_\mu \text{IC}(\text{EQ}, \mu)$ | $0$ | Always zero, for any $n$ |

Same function. One measure says $\Theta(\log n)$. The other says $0$. They're not even in the same order of magnitude. More: the ratio diverges as $n \to \infty$. This isn't a discrepancy — it's a chasm.

If you used inf IC as a lower bound for Equality, you'd conclude that Equality requires zero communication. But Equality on $n$-bit strings *does* require communication: if Alice and Bob share no randomness, the deterministic communication complexity of EQ is $n+1$ bits. If they share public randomness, it's $\Theta(\log(1/\epsilon))$ bits for $\epsilon$-error protocols. The inf IC answer ($0$) conflicts with well-established communication complexity bounds. It's not just imprecise — it's *wrong*, as a lower bound on what the problem requires.

---

## 5. When This Bites You in Practice

*This section: The IC_K ≠ inf IC distinction has concrete consequences for distributed system design, security audits, and protocol composition. I'll show three scenarios where using inf IC-style reasoning gives you a false sense of security, and explain how IC_K-style worst-case analysis catches the failure.*

This isn't just theory. The distinction has concrete consequences whenever you reason about information flow in systems that must work reliably, not just typically.

### Scenario 1: "Average-Case Secure" Isn't Secure

If your protocol's leakage analysis relies on averaging over an assumed input distribution, your guarantee is only as good as that distribution. An adversary who concentrates probability on a degenerate case can break your leakage bound. IC\_K holds for *every* input pair, not just the ones your model predicts.

> **The error pattern:** (1) Assume a "typical" input distribution $\mu$. (2) Measure $\text{IC}(f, \mu)$. (3) Conclude "leakage is bounded by $\text{IC}(f, \mu)$." (4) Deploy. Step 3 is the error — you've proven a bound under $\mu$, but nothing prevents inputs *outside* $\mu$'s typical set.

### Scenario 2: Composition Hides the Danger

You compose a protocol $n$ times — say, running authenticated key exchange between $n$ pairs of nodes. Under a fixed distribution, each instance leaks $c$ bits of mutual information. Total expected leakage: $n \cdot c$. Clean, predictable.

But that average case depends on the distribution being "well-behaved" across *all* $n$ compositions. In the worst case, a single bad input pair to any instance can leak significantly more than $c$ — and with $n$ independent compositions, the probability that *at least one* pair is adversarial grows with $n$. IC\_K handles this: $\text{IC}_K(f^n)$ grows at most linearly plus $O(\log n)$ overhead for bookkeeping — a clean, distribution-free bound. inf\_mu IC composes as: $0 \leq n \cdot 0$, which is technically true and completely useless.

### Scenario 3: Protocol Design Decisions

When you compose protocols — compute $f$ on $n$ independent copies, or nest $f$ inside $g$ — IC\_K and inf IC diverge sharply.

- IC\_K composes subadditively: $\text{IC}_K(f^n) \leq n \cdot \text{IC}_K(f) + O(\log n)$. The cost scales linearly with a small logarithmic overhead for the bookkeeping — this follows from the subadditivity of Kolmogorov complexity (up to additive $\log n$ terms, as is standard in algorithmic information theory).
- inf IC composes as: $0 \leq n \cdot 0$. Because the infimum is already zero, composition preserves zero.

This means if you're reasoning about compositional security using inf IC, your analysis will always conclude "no information leakage accumulates across compositions" — the exact opposite of reality. If your architecture relies on "information cost adds up," you need IC\_K's worst-case additivity, not inf IC's degenerate $0 \leq n \cdot 0$.

> **What if uniform IC *is* what you want?** There are legitimate use cases for distribution-specific analysis: capacity planning, expected-latency estimation, average-case mechanism design. Nothing here says "always use worst case." The claim is narrower: when you need a *guarantee* — something that holds no matter what the inputs are — you must use a worst-case measure. IC\_K provides that. inf\_mu IC(a, mu) provably does not. And confusing them is a category error, not a trade-off.

---

## 6. The Takeaway

IC\_K and inf IC live in the same neighborhood of ideas. Both try to measure internal complexity — how much information a protocol must reveal. But IC\_K asks the worst-case question ("what's the hardest input?") with the right tool (Kolmogorov complexity), while $\inf_\mu \text{IC}$ asks the easiest-case question ("what's the best distribution?") and gets a trivial answer.

The mathematical lesson: **quantifier order and complexity measure aren't implementation details — they determine what question you're actually asking.** Swap $\sup$ for $\inf$ and you go from capturing structural hardness to trivializing it. Swap Kolmogorov for Shannon and you go from instance-level guarantees to distribution-dependent averages.

The engineering lesson: if your system's correctness depends on information-theoretic lower bounds, make sure those bounds hold in the worst case. Average-case guarantees are real, but they're not the same thing — and confusing the two is how you end up with a protocol that's "secure in expectation" and broken in practice.

One more thing: this isn't a peculiarity of information complexity. The same structural error — replacing a universal quantifier ("for all inputs") with an existential one ("there exists a distribution") — shows up in cryptography, mechanism design, PAC learning, and anywhere else that "typical case" reasoning gets mistaken for "guaranteed case" reasoning.

So here's the concrete lesson. You have two numbers for the same function. One says $\Theta(\log n)$. The other says $0$. Which one do you bet your security budget on?

**Know exactly which quantifiers your theorem is using. Before you deploy the theorem.**
