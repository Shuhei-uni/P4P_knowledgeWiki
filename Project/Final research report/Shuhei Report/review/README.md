# Main-body page proof

**17 October 2026 revision:** The draft now includes the Phase 9 narrative and Figures 19–20, plus the poster film-rate plot as Figure 7 in Methods. This retained proof predates that addition; its 25-page count does not verify the revised draft. Regenerate the proof before assessing the current page count.

[body-page-proof.pdf](body-page-proof.pdf) contains **25 pages**, counted from Introduction through Conclusions. Front matter, references and appendices are excluded. One page is reserved for the final mesh comparison: **20**. This proof meets the 30-page body limit.

The proof uses A4, 12 pt Times New Roman body text, 1.15 body line spacing, 20 mm top/bottom margins and 25 mm side margins. Captions use the template's small type (approximately 11 pt). Paragraph gaps are 4 pt, with compact heading gaps. Those gaps differ from the supplied template; the body type, line spacing and margins are retained.

All current main-body text and scientific images are included. The recipe removes redundant Part headings and uses each explicit numbered caption once. It places the two published Figure 4 panels vertically at 10 cm width and assigns table widths. Figure pixels and scientific data are unchanged. Short tables stay together rather than splitting across pages.

This is a **review proof**, not the submission PDF. The mesh-comparison slot contains no invented results. Replacing them with final evidence can change pagination. In-text references to excluded appendices remain in the body for the review.

Reproduce from the repository root:

```sh
PyAnsys/.venv/bin/python PyAnsys/scripts/analysis/export_final_report_page_proof.py
```

The script needs `pandoc`, `tectonic`, `pdfinfo` and `pdftotext` on PATH and the installed Times New Roman fonts. [page-proof-manifest.json](page-proof-manifest.json) records source/image hashes, display sizes, page count and reserved-page numbers. [body-input.md](body-input.md) preserves the rendered source snapshot; the JSON AST, LaTeX input and render logs preserve the layout recipe.

The report files moved into `Shuhei Report` on 15 October 2026. Links and generation paths were updated. The existing PDF was retained without rendering it again. Manifest source hashes describe the input at the original rendering; they can differ from the current Markdown after the path updates. Image files are unchanged.
