# A2 Blog Publish Self-Manual — 2026-04-08

**Target**: LessWrong post submission for article "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective"

**Status**: Preflight ✅ | Manual steps ready | Verification checklists included

---

## Preflight Checklist (已完成)

- ✅ Draft file: `projects/写作/a2_blog_draft.md`
- ✅ Payload: `projects/写作/notes/a2_lw_payload_20260408.json` (see reference below)
- ✅ Markdown rendering check: KaTeX formulas render correctly in LW editor preview

---

## Quick Reference: Payload Values

```json
{
  "post": {
    "title": "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective",
    "subtitle": "How the worst-case measure reveals structure that averages hide",
    "tags": [
      "Algorithmic Information Theory",
      "Kolmogorov Complexity",
      "Average-Case Analysis",
      "Worst-Case Complexity"
    ],
    "author_display_name": "Cheng Lu"
  }
}
```

---

## Manual Publish Steps (User Execution)

1. **Login to LessWrong**
   - URL: https://www.lesswrong.com
   - Use your credentials (username/password or SSO)

2. **Navigate to post creation**
   - Click "Create Post" (top right) or go directly to `/post/create`

3. **Paste draft content**
   - Open `projects/写作/a2_blog_draft.md` in your editor
   - Copy **all** content (including LaTeX formulas)
   - Paste into the LW rich-text editor

4. **Fill post metadata**
   - Title: `Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective`
   - Subtitle: `How the worst-case measure reveals structure that averages hide`
   - Tags: `Algorithmic Information Theory`, `Kolmogorov Complexity`, `Average-Case Analysis`, `Worst-Case Complexity` (add each as separate tag)
   - Author display name: `Cheng Lu` (if editable; otherwise default account name)
   - Post type: `post` (not link or question)

5. **Submit**
   - Click "Publish" or "Submit" (depending on LW UI version)
   - Wait for redirect to the new post URL

6. **Record the URL**
   - Copy the browser address bar (format: `https://www.lesswrong.com/posts/...`)
   - Save to: `projects/写作/notes/lw_a2_post_url_20260408.txt`
     - Content should be **just the URL**, no extra text

---

## Post-Publish Verification (Automated or Manual)

Once URL is recorded, perform:

1. **Access check**
   - Visit the URL in incognito/private window
   - Expect HTTP 200 OK (not 404/403)

2. **Content integrity**
   - Title matches exactly
   - Author name correct
   - All 4 tags present
   - Formulas render (KaTeX) — check at least 2 math blocks

3. **Notify completion**
   - Update task status (if using task board)
   - Inform Zero agent that A2 is live → triggers A3 tracking task

---

## Rollback & Edit

LessWrong supports editing any post after publication.
- If you spot an error, click "Edit" on the post
- Make changes and save
- URL remains the same (no need to update reference files)
- No technical rollback required

---

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| "403 Forbidden" | Not logged in or insufficient karma | Ensure you're logged in with an account that can post |
| Tags not recognized | Typo or unavailable tag | Use exact tag names as shown above |
| Math not rendering | Incomplete LaTeX delimiters | Check that formulas use `$$...$$` or `\( ... \)` |
| URL recording failed | File missing or permission denied | Ensure `projects/写作/notes/` exists and is writable |

---

## Notes

- This manual is for **one-time use** only. Once A2 is published, archive this file if desired.
- For **automation**, provide LessWrong API credentials or browser profile to Zero agent to run `browser attach` → user auth session.
- A3 tracking will depend on this URL being saved; ensure step 6 completes.

**Last updated**: 2026-04-08 R124  
**Agent**: Zero Writing Domain (cron:4ca5ec87-c7c9-4f07-bc9b-55277938aac4)
