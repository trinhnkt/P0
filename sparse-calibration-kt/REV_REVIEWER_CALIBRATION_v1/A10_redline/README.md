# A10 redline

`latexdiff` is installed but cannot run here (MiKTeX has no Perl script engine).

Tracked copies are unified diffs against `_pre_a10/`:

- `main_jedm.diff`
- `main_jedm_anonymous.diff`
- `sections/*.diff`

Clean manuscript: parent `REV_REVIEWER_CALIBRATION_v1/`.
Pre-A10 snapshot: `REV_REVIEWER_CALIBRATION_v1/_pre_a10/`.

To compile a strikeout/underline PDF later (with Perl):

```
latexdiff _pre_a10/sections/01_introduction.tex sections/01_introduction.tex > A10_redline/sections/01_introduction.tex
```
