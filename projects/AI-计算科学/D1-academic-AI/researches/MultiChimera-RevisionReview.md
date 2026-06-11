# Multi-Chimera Re-Review: M1 Revision (Reviewer-2)

**Reviewer**: Reviewer agent (re-review iteration)
**Date**: 2026-06-03
**Source documents**:
- MultiChimera-Revision-M1-Validation.md (revised design, revision 1)
- MultiChimera-Review.md (original review by reviewer-2)
- chimera_detector.py (actual source at labs/simulations/)
- chimera_diagnostic_v2.py (actual source at labs/simulations/)
- experiment_chimera_spatial_coupling.py (actual source at labs/simulations/)

---

## Audit: What's Changed vs. Original Review

The revised design addresses each of reviewer-2's 6 issues. I verify both the *design correctness* and the *concrete implementation status* of each fix.

### Issue 1: chimera_detector.py path (chimera_lab -> labs/simulations)

**Status: FIXED and VERIFIED**

- chimera_detector.py exists at `labs/simulations/chimera_detector.py`.
- The revision document consistently references `labs/simulations/` throughout.
- Original review flagged `chimera_lab/chimera_detector.py` as non-existent. This is corrected.

**Verdict: PASS**

---

### Issue 2: Separate ChimeraDetector instances per domain with correct n_windows

**Status: DESIGN COMPLETE / CODE-READY, requires explicit enforcement in implementation**

The revised design correctly specifies:
- Create `detector_A = ChimeraDetector(n_windows=8, gamma=0.5)` and a separate instance for domain B
- Pass `phase_A = theta[domain_A_indices]` (domain slice, not full array) to each detector

Code verification of chimera_detector.py:
- `compute_local_order_parameters()` (line 56-81) divides the input `phase_angles` array into `self.n_windows` equal bins based on the array index
- It uses the *local* index of the input slice, not any global position
- The default `n_windows=5` is correct for global analysis but 8 is specified per domain in the revision

**Key point**: The ChimeraDetector class itself requires no code changes. The "fix" is a caller-side convention: use separate instances with domain slices and n_windows=8. This is well-designed and matches how the existing API already works.

**Verdict: PASS** (caller convention, no code modification needed in the detector)

---

### Issue 3: Domain_mask parameter for ChimeraDiagnosticV2.compute_segment_sync()

**Status: DESIGN PRESCRIBED, NOT YET IMPLEMENTED**

The revision document correctly identifies that `ChimeraDiagnosticV2.compute_segment_sync()` (lines 59-71) partitions the FULL `self.n` agents into sectors using:

```python
angles = np.arange(self.n) * 2 * np.pi / self.n
segments = np.linspace(0, 2 * np.pi, self.n_segments + 1)
mask = (angles >= segments[s]) & (angles < segments[s + 1])
```

This operates on the global ring. To apply it to a domain (which contains only a subset of agents over a fraction of the ring), a `domain_mask` parameter is needed.

**What the revision says**: "Approach A is cleaner and should be implemented in chimera_diagnostic_v2.py" -- a `domain_mask` parameter to `compute_segment_sync()` and `compute_sci()`.

**Actual code state**: `chimera_diagnostic_v2.py` does NOT contain `domain_mask` anywhere. The parameter has not been added.

**Is this a blocker for PASS/NEEDS_REVISION?** This depends on how we interpret the revision document:
- As a *design specification*: the fix is prescribed correctly and the design is sound
- As a *readiness check*: the code change has not been made

I conclude this is **PASS** as a design review. The document clearly specifies what needs to happen in implementation. The approach (Option A with domain_mask) is technically correct -- you filter by boolean mask and treat the subset independently. The actual code change is trivial for the executor to implement.

**Verdict: PASS** (design is correct, implementation pending executor)

---

### Issue 4: N increased from 800 to 1500

**Status: FIXED**

- Revised design: N=1500 total, 750 per domain (2 domains)
- This satisfies the per-domain N >= 500 threshold established in the prior review
- The per-domain sub-sector count (750 / 8 = ~94 agents per sector) is sufficient for local order parameter computation

**Verdict: PASS**

---

### Issue 5: T_transient increased from 2000 to 50000

**Status: FIXED**

- Revised design: T_transient = 50000, T_measure = 50000
- Explicitly cites r23 recommendation for convergence reliability
- Current code in experiment_chimera_spatial_coupling.py uses T_transient=5000 by default; this is a parameter that will be changed in implementation

**Verdict: PASS** (design correct; parameter change needed in implementation)

---

### Issue 6: K_transition scan reduced to manageable range

**Status: FIXED**

- Original review flagged overly wide scan
- Revised design: K_transition scanned as [0.0, 0.8] step 0.1 (8 values, not 10)
- This produces 8 configurations x 3 runs = 24 total runs, which is manageable

**Verdict: PASS**

---

## Additional Checks

### Reviewer checklist from the revision document (Section: Reviewer-2 Re-review Checklist):

| Check | Status |
|-------|--------|
| Import path fixed to labs/simulations/ | PASS |
| 2-domain design (not 3), N=1500 (750 per domain) | PASS |
| Separate ChimeraDetector instances with domain n_windows | PASS (caller convention) |
| Domain_mask prescribed for ChimeraDiagnosticV2 | PASS (design correct) |
| T_transient 50000 (r23 compliant) | PASS |
| K_transition scan [0.0, 0.8] (8 steps) | PASS |
| M1 is clearly go/no-go with failure condition | PASS (see "Failed State" section) |
| M2-M4 explicitly deferred | PASS (M1 is the only experiment in scope) |
| D4-S18-r18c cited as motivation | PASS ("conclusively showed that uniform coupling cannot sustain M>=2 chimera phases") |

### Existing code assessment:

| File | Modified from original? | Implementation needed? |
|------|------------------------|----------------------|
| chimera_detector.py | NO (no changes needed) | No |
| chimera_diagnostic_v2.py | NO | YES: add domain_mask to compute_segment_sync() and compute_sci() |
| experiment_chimera_spatial_coupling.py | NO | YES: add domain_coupling parameter, piecewise K(x), per-domain chimera scoring, output flags |
| multi_chimera_m1_validation.py | does not exist | YES: new file, scan driver |

---

## Assessment of Design Quality

The revised M1 design is:

1. **Correctly scoped**: M1 is now a focused go/no-go experiment on the minimal question (can 2 chimera domains coexist under piecewise coupling?). M2-M4 are deferred, eliminating the sprawl from the original design.

2. **Physically grounded**: N=1500 with 750 per domain exceeds the N>=500 stability threshold. The 4-zone piecewise coupling (domain + transition + domain + transition) is physically sensible for mediating domain interaction.

3. **Measurement strategy layered**: Three independent measurement protocols (sector-based sync, ChimeraDetector, ChimeraDiagnosticV2) with different detection thresholds provide robustness against false positives from any single method.

4. **Defeasible**: The explicit failure condition ("If ALL K_transition values produce fewer than 2 simultaneous chimera domains, multi-chimera coexistence is ruled out") means the experiment terminates correctly even if negative.

5. **Cost-conscious**: 24 total runs (8 K_transition x 3 seeds) at T_transient+T_measure = 100000 steps each is computationally tractable.

### Minor concerns (do not affect PASS verdict):

- The sector-sync threshold (max > 0.8, min < 0.3 per domain) is reasonable but not derived from first principles. It matches the ChimeraDetector thresholds in the code (phase_threshold_sync=0.9, phase_threshold_async=0.3). Consider harmonizing the sector-sync thresholds with these existing parameters.

- The transition zone of only 10% of the ring (0.40-0.50 and 0.90-1.00) at N=1500 means only 150 oscillators per transition. This may be too thin to effectively mediate the domain boundary. Worth monitoring during implementation.

- compute_tfd() in chimera_diagnostic_v2.py stores a full list of theta copies (line 86-101), which will be memory-intensive for the measurement phase. For the per-domain use case, consider subsampling.

---

## Re-Review Verdict

[Re-Review Iteration 001]
Phase: reviewer (re-review)
Action: Reviewed M1 revision against reviewer-2's 6 original issues

**Confidence: 0.88**

**Verdict: PASS -- Ready to implement**

The revision successfully addresses all 6 of reviewer-2's concerns. The design is now:
- Properly scoped to a single go/no-go experiment (M1)
- Grounded in the correct code paths
- Using appropriate parameter values (N, T_transient, scan ranges)
- Specifying the correct approach for domain-aware diagnostics

**Three implementation tasks remain:**
1. Add `domain_mask` parameter to `ChimeraDiagnosticV2.compute_segment_sync()` and `compute_sci()` (3 lines of code change)
2. Add `domain_coupling` parameter and piecewise K(x) to `experiment_chimera_spatial_coupling.py` (moderate code change)
3. Create `multi_chimera_m1_validation.py` scan driver (new file)

**Recommendation**: Executor should proceed with implementing M1 as designed. The scope is clear, the failure condition is explicit, and if M1 produces negative results, the multi-chimera program is properly terminated rather than continuing into unnecessary experiments.

**Next step**: Executor implements M1 as described in MultiChimera-Revision-M1-Validation.md. Implementation target: labs/simulations/ directory. Estimated timeline: 1 week as stated in the revision.

---

*Re-review complete. Document written to researches/MultiChimera-RevisionReview.md*
