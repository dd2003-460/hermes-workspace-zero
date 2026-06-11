# Publishing Checklist — IC_K Series

> Created: 2026-04-04 | Quality Gate: PASSED (A-/A range, world-class ready)

---

## Source Files

| File | Description | Path |
|------|-------------|------|
| A2 (LessWrong ready) | "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective" | `../a2_lw_ready_backup_20260404.md` |
| A3 (blog draft v3) | "IC_K ≠ inf IC: When the Infimum Destroys the Answer" | `../a3_blog_draft_v3.md` |
| Twitter Thread | 12-tweet thread, ready to post | `../twitter_thread_ready.md` |

---

## Step 1: A2 — LessWrong Submission

**File:** `a2_lw_ready_backup_20260404.md`  
**Title:** Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective  
**Estimated time:** ~15 min

### Submission Steps

1. Go to [LessWrong](https://www.lesswrong.com) → Log in → "New Post"
2. **Title field:** `Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective`
3. **Body:** Copy the entire content from `a2_lw_ready_backup_20260404.md` (from after the frontmatter YAML block to the end)
   - The file uses standard GitHub-flavored Markdown with `$...$` and `$$...$$` for math — LessWrong's MathJax renderer handles this natively
   - The horizontal rules (`---`) render as section separators on LessWrong
4. **Tags (add these):**
   - `complexity_theory`
   - `information_theory`
   - `kolmogorov_complexity`
   - `communication_complexity`
   - `mathematics`
   *(If a tag doesn't exist exactly, use the closest available — LessWrong will suggest matches as you type)*
5. **Optional but recommended:**
   - Add a brief "sequence" or series link once A3 is also published
   - Set canonical URL blank for now (fill in later if paper goes to arXiv)
6. **Preview** the post — check that:
   - MathJax renders properly (all `$...$` and `$$...$$` display as formulas, not raw text)
   - Code block (the binary search example) renders with monospace formatting
   - Blockquotes (`>`) render correctly
7. **Publish**

### MathJax Rendering Notes

- LessWrong uses KaTeX by default (not MathJax), which supports:
  - Inline math: `$ ... $` — ✅ works
  - Display math: `$$ ... $$` — ✅ works
  - `\text{...}`, `\mid`, `\cdot`, `\Theta`, `\inf`, `\sup` — all standard KaTeX
  - `\_` for escaped underscores — should render fine
- If `_` in variable names doesn't render, the copy-paste-ready file already uses `\_` escapes where needed
- The table using `|---|` markdown syntax will render as a LessWrong table

### Post-Publish

- Save the LessWrong URL
- Note the publication timestamp

---

## Step 2: Twitter/X Thread

**File:** `twitter_thread_ready.md`  
**Estimated time:** ~5 min  
**Recommended timing:** 2–4 hours after A2 LessWrong publication

### Why 2-4 Hours Later

- Gives A2 time to get initial traction on LessWrong
- Thread can reference "I just posted a deep-dive on LessWrong → [link]" in replies
- Maximizes cross-platform visibility without overwhelming either platform

### Posting Steps

1. Open [X/Twitter](https://x.com)
2. Compose a new tweet (Tweet 1/12) — copy from `twitter_thread_ready.md`
3. **Formatting tips:**
   - Each numbered section (1/12 through 12/12) is one tweet
   - The `---` separators in the file mark tweet boundaries — copy content between separators
   - Emojis (🧵, 📌, 🚀) are included inline — keep them
   - The math formulas in the thread use plain Unicode/ASCII notation (no `$` delimiters needed for Twitter)
4. Use the thread feature (click "+") to chain all 12 tweets
5. **Optional additions in final reply tweet (12/12):**
   - "Full deep dive on LessWrong: [link]" — add the A2 LessWrong URL once published
   - "Companion post on IC_K ≠ inf IC coming soon" — teaser for A3
6. **Post**

### Alternative: Schedule via Third-Party Tools

- Typefully, Hypefury, or Buffer can schedule threads
- Upload the thread text as a draft, set publish time to A2_time + 2-4h

---

## Step 3: A3 — LessWrong Submission

**File:** `a3_blog_draft_v3.md`  
**Title:** IC_K ≠ inf IC: When the Infimum Destroys the Answer  
**Subtitle:** Why optimizing over distributions kills your lower bound  
**Recommended timing:** 3–7 days after A2 publication

### Why 3-7 Days Later

- A2 needs time to accumulate readers/comments on LessWrong
- A3 explicitly references A3 as "companion post to" A2 — having A2 live first creates a natural link
- Spacing out posts prevents both from competing for the same audience attention
- Gives time to incorporate any community feedback from A2 into A3 if desired

### Tags

- `complexity_theory`
- `information_theory`
- `kolmogorov_complexity`
- `applied_rationality`
- `optimization`
- *(same core tags as A2 + `applied_rationality` and `optimization` to capture the "when this bites you in practice" audience)*

### Additional Notes

- The footer in A3 already links back to A2: *"This is a companion post to 'Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective.'"*
- Once A2 is published, update that line to be a hyperlink with the actual LessWrong URL
- Consider adding both to a LessWrong sequence titled "IC_K: Kolmogorov Information Complexity"

---

## Pre-Flight Checklist

- [ ] A2 content reviewed and final (file: `a2_lw_ready_backup_20260404.md`)
- [ ] A3 content reviewed and final (file: `a3_blog_draft_v3.md`)
- [ ] Twitter thread reviewed and final (file: `twitter_thread_ready.md`)
- [ ] LessWrong account logged in and active
- [ ] arXiv author name(s) decided (for companion paper attribution)
- [ ] A2 LessWrong posted ✅ (fill in URL: _______________)
- [ ] Twitter thread posted ✅ (time: _______________)
- [ ] A3 LessWrong posted ✅ (time: _______________)
- [ ] Cross-links updated (A2↔A3, Twitter→LessWrong)

---

## Companion Paper Note

The companion paper ("IC_K: Distribution-Free Kolmogorov Information Complexity") is mentioned in both A2 and A3. Before either arXiv submission:

- [ ] Decide on author name(s)
- [ ] Finalize LaTeX formatting
- [ ] Set arXiv primary category (likely `cs.CC` — Computational Complexity)
- [ ] Add arXiv link to LessWrong posts once published
