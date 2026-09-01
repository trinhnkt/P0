# Anonymous 4open.science snapshot — files to remove

The live review URL in the manuscript is still:

`https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`

That snapshot **leaks identity** via named JEDM sources. anonymous.4open.science snapshots are not edited in place. Create a **new** snapshot from a tree that does **not** contain the files below, then put the new URL in Data and Code Availability if it changes.

## Delete before re-anonymizing (paths inside `sparse-calibration-kt/`)

- `paper/main_jedm.tex`
- `paper/main_jedm.pdf`
- `jedm_upload_folder/main_jedm.tex`

Keep, if present:

- `paper/main_jedm_anonymous.tex`
- `paper/main_jedm_anonymous.pdf`
- `jedm_upload_folder/main_jedm_anonymous.tex`

Do not include `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx` (named authors). The IJIET blind PDF is `output/main_ijiet_blind.pdf`.

## Overlay copies (this folder)

`IJIET_FINAL_REVISION/anonymous_overlay/` holds a reminder README only. Do **not** copy named JEDM tex into a public snapshot.

## This machine cannot push 4open.science

After you publish a clean snapshot, replace the URL in the Word Data paragraph (zero-width spaces after `/` must be kept for line wrapping) and recompile named + blind PDFs.
