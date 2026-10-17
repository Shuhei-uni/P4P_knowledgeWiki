# Authorised report export — 18 October 2026

The author requested export of the current Markdown and deferred the DPM follow-up. The existing [LaTeX](../latex/ESB_report_template.tex) and [PDF](../latex/ESB_report_template.pdf) now include the bounded-review revisions. Canonical Markdown, figures and project evidence are unchanged by this export.

The PDF has **30 body pages** (physical pages 12–41), **53 pages overall** and **11,865 body words**. The body is 12 pt Times New Roman with the existing margins and 1.15 spacing. Long-table top/bottom padding changed from 0.4 to 0.2 baselineskip to fit the page limit. Table-column ratios now use eight decimal places to avoid a rounding overflow. Figure sizes are unchanged.

The synchroniser skips the protected opening sections. Independent verification found one stale sentence in the introduction export and a differing title-page draft date. These were aligned exactly with the authoritative Markdown, without changing the Markdown. The copied literature-review export remains unchanged.

[before-export.tar.gz](before-export.tar.gz) and [preservation.json](preservation.json) preserve all pre-export draft, figure and LaTeX files, including untracked files. [previous-annotated-report.pdf](previous-annotated-report.pdf) preserves the prior PDF and its annotations as a directly readable file.

The built-in compile tool was unavailable and no document session was connected. The existing report was compiled with local Tectonic using cached resources. Sandboxed Tectonic failed in macOS system configuration; the approved local compile succeeded. The log has no TeX errors, overfull boxes, missing characters or undefined references. PDF text is extractable. All pages were visually checked; the final appendix page contains one continuation line, a minor layout blemish outside the body-page limit.

[qa.json](qa.json) records hashes, font/page checks and verification status. Fresh verification checks the final export only; it does not start a fourth substantive review cycle. The DPM inputs gap and existing author-completion items remain unresolved; no research conclusions were changed during export.

[Final fresh verification](final-verification.json): **PASS — no material unresolved export issue found**. The verified PDF hash matches the delivered file. Both introduction/date alignment corrections are resolved. All required sections, nine figures and credits, embedded body font, selectable text and 30-page body limit were confirmed. Reviewer exposure to automatically supplied context is disclosed in the record.
