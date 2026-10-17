# Bounded report review — 18 October 2026

The revised reading copy is [draft/draft-v1.md](../../draft/draft-v1.md). The six numbered Markdown files remain authoritative; the assembled copy is generated from them. This review used all **three permitted review–revision cycles**, with two fresh reviewers per cycle and the main agent as sole editor. A fresh verifier checked each revision. Final verification status is recorded below.

## Preservation and author limits

[before-review.tar.gz](before-review.tar.gz) preserves the complete original report, including untracked files. [preservation.json](preservation.json) records every original file hash and the archive hash. The initial Git status and tracked patch are retained beside it. No pull, reset, commit, submission, new CFD experiment or change to project evidence was part of this loop.

The introduction/literature Markdown, all existing figure assets/provenance and the LaTeX source/build files remain byte-identical. The PDF changed without a write or export by this loop: it gained four annotations while its extracted text and page-content streams remained identical. The annotated PDF was retained, and the original remains in the backup; see [PDF observation](pdf-change-observation.json). Original objectives, scientific qualifications and figure attribution remain. The official title is unchanged. Current author instruction permits Markdown drafting; LaTeX/PDF export requires a separate request. Confirmed requirements are 30 body pages, 12 pt Times New Roman and the prescribed report sections; the handbook gives 8,000–13,000 words as guidance.

## Review isolation

Every reviewer and verifier was created with `fork_turns="none"`. Both reviewers in each cycle received the same fixed, read-only snapshot: six report parts, figure assets, references and confirmed requirements. Non-printing evidence comments were removed and local evidence-link destinations disabled. No conversation, project summary, previous review or description of edits was supplied. Reviewers were forbidden project records, memories, external links and other reviews, and did not edit files. Snapshot hash manifests verify their inputs.

**Isolation limitation:** automatic bootstrap supplied repository instructions and project-related memory/phase context to the fresh agents. They disclosed this exposure and reported using only the supplied snapshots. These are fresh-conversation reviews, but cannot be described as fully blind. The main agent used project evidence to assess criticisms after each review.

## Decisions and revisions

| Cycle | Material issues and supported correction | Records |
|---|---|---|
| 1 | Added original conceptual Figure 5 and case-specific spatial definitions; explained contact collection and particle mass/momentum interaction; specified inlet-comparison controls and narrowed its endpoint interpretation. The protected literature's efficiency definition was carried forward for source checking. | [Decisions](cycle-01/reviews-and-decisions.json), [revision](cycle-01/revision.diff), [verification](cycle-01/verification.json) |
| 2 | Identified the five matched droplet operating points; added Appendix E with the recovered nine-group inputs; clarified the actual validation scope and dryness/capture distinction outside the protected opening; reconciled the 2014/2015 reference identity. Verification found an existing pressure-definition omission for cycle 3. | [Decisions](cycle-02/reviews-and-decisions.json), [revision](cycle-02/revision.diff), [verification](cycle-02/verification.json) |
| 3 | The CFD examiner returned zero material issues. Explained secondary-phase wall-film accretion and the frozen-bulk limit; defined family-specific static-pressure averages and the historical drift calculation. Recovered monitor samples reproduce 4.611838%, rounding to the reported 4.612%. | [Decisions](cycle-03/reviews-and-decisions.json), [revision](cycle-03/revision.diff), [verification](cycle-03/verification.json) |

The decision files record each substantive criticism, confidence, smallest correction, evidence and accepted/unresolved treatment. No optional stylistic rewrites were retained. Spatial reporting was repaired only as far as verified definitions allowed: missing as-built CAD/design detail was explicitly left unresolved. Figure numbers now run 1–9. Existing figures 1–4 retain their numbers; original Figure 5 is the new schematic; former figures 5–8 are now 6–9. Shuhei's source credits remain on Figures 6 and 7.

## Latest verification and export status

Final fresh-verifier assessment: **both targeted explanations adequate; no material contradiction in the main conclusions**. The verifier inspected all nine figures and accepted the spatial, coupling and comparison-control explanations. It found one existing omission: the interacting-DPM comparisons need their distinct particle-size/release inputs. That criticism is accepted and explicitly unresolved at the three-cycle limit. No failed targeted change required reversal, and no further report edit was made after verification. The latest canonical report matches the final verification snapshot.

Current body: **11,865 words** (Introduction through Conclusions, including headings, captions and tables), counted with the established Pandoc-based report counter. This lies within the handbook word guidance but does not prove page compliance. The unchanged earlier PDF has **29 body pages / 47 total pages** and 11,172 body words. The current Markdown contains additional text and a schematic, so its pagination must be checked at the next authorised export. [qa-current.json](qa-current.json) records the latest content and preservation checks.

## Unresolved limits and author work

- **Final verifier issue C3-V1-1:** the interacting-DPM pairs use a separate seven-bin fine-mist prescription that is not fully stated in the report; Appendix E covers the historical nine-group reconstruction. Source setups confirm the distinction. Add sizes, release rules and matched controls after checking the completed paired settings. This is a reporting omission, not demonstrated incorrect simulation. It remains unresolved at the cycle limit.
- Intended tetrahedral/poly-hexcore geometry equality is not demonstrated: recorded volumes differ. Runtime remains a case comparison, not an isolated mesh-only speedup or cost at equal accuracy.
- Stationary whole-separator conservation, mesh independence and physical performance validation are not established. Local film, collector and simple-duct successes retain their own scopes.
- Particle tracking retains substantial incomplete mass; aggregate escape is not boundary-specific carryover. Original historical binary/tracking cap and physical applicability of the retained drag model remain unqualified.
- Dimensioned as-built blocker/ramp views and complete cross-family CAD parity are not supplied. No geometric design advantage is inferred. Disputed Phase 5 completion and later unverified design endpoints remain excluded.
- Protected literature wording is unchanged. Methods now clarifies its prospective-validation scope and ambiguous efficiency example; any direct revision of the copied section needs author direction. Some bibliographic details remain incomplete.
- Author completion remains for acknowledgements, declaration/signature and AI-use wording. The 30-page PDF check remains for the next explicitly requested export.

[Protocol](protocol.json) identifies agents, snapshots and verification stages. Scientific records remain the evidence owners; this folder records review decisions and report revisions only.

## Later authorised export

After the three-cycle review closed, the author requested export of the current Markdown and deferred the DPM follow-up. The [existing PDF](../latex/ESB_report_template.pdf) now includes these revisions and has **30 body pages / 53 total pages**. The [separate export record](../export-2026-10-18-bounded-review/README.md) preserves the prior annotated PDF and records export-only alignment, layout adjustments and fresh verification. No additional substantive review–revision cycle or CFD work was performed. Earlier status statements above describe the review at its closure.
