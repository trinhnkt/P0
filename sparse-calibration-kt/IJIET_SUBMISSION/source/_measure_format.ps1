# IJIET format measurement: official template vs filled manuscript.
# Writes UTF-8 reports; does not modify documents.

$ErrorActionPreference = "Stop"
$auditDir = "C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\IJIET_SUBMISSION\audit"
$template = Join-Path $auditDir "IJIET_template.doc"
$ms = "C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\ijiet\Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx"
$out = Join-Path $auditDir "format_measure.txt"

function Dump-Doc($word, $path, $label) {
    $doc = $word.Documents.Open($path, $false, $true)  # ReadOnly
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("===== $label =====")
    [void]$sb.AppendLine("Path: $path")
    [void]$sb.AppendLine("Pages: $($doc.ComputeStatistics(2))  Words: $($doc.ComputeStatistics(0))")
    [void]$sb.AppendLine("Sections: $($doc.Sections.Count)  Tables: $($doc.Tables.Count)  InlineShapes: $($doc.InlineShapes.Count)  Shapes: $($doc.Shapes.Count)")

    for ($s=1; $s -le $doc.Sections.Count; $s++) {
        $sec = $doc.Sections.Item($s)
        $ps = $sec.PageSetup
        $cols = $ps.TextColumns
        $colW = @()
        try {
            if ($cols.Count -ge 1 -and $cols.Count -lt 20) {
                for ($c=1; $c -le $cols.Count; $c++) {
                    $colW += [math]::Round($cols.Item($c).Width, 2)
                }
            }
        } catch {}
        $hdr = ($sec.Headers.Item(1).Range.Text -replace "`r|`a","").Trim()
        $ftr = ($sec.Footers.Item(1).Range.Text -replace "`r|`a","").Trim()
        if ($hdr.Length -gt 160) { $hdr = $hdr.Substring(0,160) }
        if ($ftr.Length -gt 160) { $ftr = $ftr.Substring(0,160) }
        [void]$sb.AppendLine(("Section {0}: paper={1} w={2} h={3} orient={4} start={5}" -f $s, $ps.PaperSize, [math]::Round($ps.PageWidth,2), [math]::Round($ps.PageHeight,2), $ps.Orientation, $ps.SectionStart))
        [void]$sb.AppendLine(("  margins T/B/L/R/Gutter: {0} / {1} / {2} / {3} / {4}  headerDist={5} footerDist={6}" -f [math]::Round($ps.TopMargin,2), [math]::Round($ps.BottomMargin,2), [math]::Round($ps.LeftMargin,2), [math]::Round($ps.RightMargin,2), [math]::Round($ps.Gutter,2), [math]::Round($ps.HeaderDistance,2), [math]::Round($ps.FooterDistance,2)))
        [void]$sb.AppendLine(("  cols={0} spacing={1} even={2} widths={3}" -f $cols.Count, [math]::Round($cols.Spacing,2), $cols.EvenlySpaced, ($colW -join ",")))
        [void]$sb.AppendLine("  HEADER: [$hdr]")
        [void]$sb.AppendLine("  FOOTER: [$ftr]")
        [void]$sb.AppendLine("  DifferentFirstPage=$($ps.DifferentFirstPageHeaderFooter) OddEven=$($ps.OddAndEvenPagesHeaderFooter)")
    }

    [void]$sb.AppendLine("--- key paragraphs ---")
    $n = [Math]::Min(20, $doc.Paragraphs.Count)
    for ($i=1; $i -le $n; $i++) {
        $p = $doc.Paragraphs.Item($i)
        $t = ($p.Range.Text -replace "`r|`a","").Trim()
        if ($t.Length -eq 0) { continue }
        if ($t.Length -gt 90) { $t = $t.Substring(0,90) }
        $pf = $p.Format
        $f = $p.Range.Font
        $list = ""
        try { $list = $p.Range.ListFormat.ListString } catch {}
        [void]$sb.AppendLine(("P{0} style={1} list='{2}' align={3} font={4} size={5} bold={6} italic={7} color={8}" -f $i, $p.Style.NameLocal, $list, $p.Alignment, $f.Name, $f.Size, $f.Bold, $f.Italic, $f.Color))
        [void]$sb.AppendLine(("   spaceB={0} spaceA={1} line={2} lineRule={3} firstInd={4} leftInd={5} afterAuto={6}" -f [math]::Round($pf.SpaceBefore,2), [math]::Round($pf.SpaceAfter,2), [math]::Round($pf.LineSpacing,2), $pf.LineSpacingRule, [math]::Round($pf.FirstLineIndent,2), [math]::Round($pf.LeftIndent,2), $pf.SpaceAfterAuto))
        [void]$sb.AppendLine("   TEXT: $t")
    }

    [void]$sb.AppendLine("--- body sample (first Heading1 Text para) ---")
    $foundBody = $false
    for ($i=1; $i -le $doc.Paragraphs.Count; $i++) {
        $p = $doc.Paragraphs.Item($i)
        if ($p.Style.NameLocal -eq "Text" -and ($p.Range.Text.Trim().Length -gt 80)) {
            $pf = $p.Format
            $f = $p.Range.Font
            $t = ($p.Range.Text -replace "`r|`a","").Trim()
            if ($t.Length -gt 100) { $t = $t.Substring(0,100) }
            [void]$sb.AppendLine(("BODY style=Text font={0} size={1} bold={2} italic={3} align={4}" -f $f.Name, $f.Size, $f.Bold, $f.Italic, $p.Alignment))
            [void]$sb.AppendLine(("   spaceB={0} spaceA={1} line={2} lineRule={3} firstInd={4} leftInd={5}" -f [math]::Round($pf.SpaceBefore,2), [math]::Round($pf.SpaceAfter,2), [math]::Round($pf.LineSpacing,2), $pf.LineSpacingRule, [math]::Round($pf.FirstLineIndent,2), [math]::Round($pf.LeftIndent,2)))
            [void]$sb.AppendLine("   TEXT: $t")
            $foundBody = $true
            break
        }
    }
    if (-not $foundBody) { [void]$sb.AppendLine("NO BODY TEXT PARA FOUND") }

    [void]$sb.AppendLine("--- Heading 1/2 samples ---")
    $h1n=0; $h2n=0
    for ($i=1; $i -le $doc.Paragraphs.Count; $i++) {
        $p = $doc.Paragraphs.Item($i)
        $st = $p.Style.NameLocal
        $t = ($p.Range.Text -replace "`r|`a","").Trim()
        if ($t.Length -eq 0) { continue }
        $list = ""
        try { $list = $p.Range.ListFormat.ListString } catch {}
        $pf = $p.Format
        $f = $p.Range.Font
        if ($st -eq "Heading 1" -and $h1n -lt 3) {
            [void]$sb.AppendLine(("H1 list='{0}' font={1} size={2} bold={3} allcaps={4} align={5} spaceB={6} spaceA={7} | {8}" -f $list, $f.Name, $f.Size, $f.Bold, $f.AllCaps, $p.Alignment, [math]::Round($pf.SpaceBefore,2), [math]::Round($pf.SpaceAfter,2), $t))
            $h1n++
        }
        if ($st -eq "Heading 2" -and $h2n -lt 3) {
            [void]$sb.AppendLine(("H2 list='{0}' font={1} size={2} bold={3} italic={4} align={5} spaceB={6} spaceA={7} | {8}" -f $list, $f.Name, $f.Size, $f.Bold, $f.Italic, $p.Alignment, [math]::Round($pf.SpaceBefore,2), [math]::Round($pf.SpaceAfter,2), $t))
            $h2n++
        }
    }

    [void]$sb.AppendLine("--- captions / equations / refs ---")
    $eq=0; $cap=0; $ref=0; $rh=0
    for ($i=1; $i -le $doc.Paragraphs.Count; $i++) {
        $p = $doc.Paragraphs.Item($i)
        $st = $p.Style.NameLocal
        $t = ($p.Range.Text -replace "`r|`a","").Trim()
        if ($t.Length -eq 0) { continue }
        $f = $p.Range.Font
        $pf = $p.Format
        if ($st -match "figure caption|Figure Caption|Table Title" -and $cap -lt 6) {
            [void]$sb.AppendLine(("CAP style={0} font={1} size={2} bold={3} italic={4} align={5} | {6}" -f $st, $f.Name, $f.Size, $f.Bold, $f.Italic, $p.Alignment, $t.Substring(0,[Math]::Min(120,$t.Length))))
            $cap++
        }
        if ($st -match "Equation|equation" -and $eq -lt 4) {
            [void]$sb.AppendLine(("EQ style={0} font={1} size={2} align={3} | {4}" -f $st, $f.Name, $f.Size, $p.Alignment, $t.Substring(0,[Math]::Min(80,$t.Length))))
            $eq++
        }
        if ($st -eq "Reference Head" -and $rh -lt 8) {
            [void]$sb.AppendLine(("RH font={0} size={1} bold={2} allcaps={3} align={4} | {5}" -f $f.Name, $f.Size, $f.Bold, $f.AllCaps, $p.Alignment, $t))
            $rh++
        }
        if ($st -eq "References" -and $ref -lt 2) {
            $list = ""
            try { $list = $p.Range.ListFormat.ListString } catch {}
            [void]$sb.AppendLine(("REF list='{0}' font={1} size={2} hanging={3} | {4}" -f $list, $f.Name, $f.Size, [math]::Round($pf.FirstLineIndent,2), $t.Substring(0,[Math]::Min(100,$t.Length))))
            $ref++
        }
    }

    [void]$sb.AppendLine("--- figures ---")
    for ($i=1; $i -le $doc.InlineShapes.Count; $i++) {
        $sh = $doc.InlineShapes.Item($i)
        [void]$sb.AppendLine(("Inline {0} type={1} w={2}pt h={3}pt" -f $i, $sh.Type, [math]::Round($sh.Width,2), [math]::Round($sh.Height,2)))
    }
    for ($i=1; $i -le $doc.Shapes.Count; $i++) {
        $sh = $doc.Shapes.Item($i)
        [void]$sb.AppendLine(("Shape {0} type={1} name={2} w={3} h={4}" -f $i, $sh.Type, $sh.Name, [math]::Round($sh.Width,2), [math]::Round($sh.Height,2)))
    }

    [void]$sb.AppendLine("--- keyword hits ---")
    foreach ($n in @("INTERNATIONAL JOURNAL","International Journal of Information","ChatGPT","generative","Grammarly","IRB","GDPR","FERPA","de-identified","public logs","double-blind","anonymous","doi:","10.18178","Manuscript received","Conflict of Interest","Author Contributions","Acknowledgment","Funding","Abstract","Keywords","ECE =","(1)")) {
        $fnd = $doc.Content.Find
        $fnd.ClearFormatting() | Out-Null
        $hit = $fnd.Execute($n)
        [void]$sb.AppendLine("HIT=$hit  $n")
    }

    $doc.Close($false)
    return $sb.ToString()
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $a = Dump-Doc $word $template "OFFICIAL TEMPLATE"
    $b = Dump-Doc $word $ms "CURRENT MANUSCRIPT"
    [System.IO.File]::WriteAllText($out, $a + "`r`n" + $b, [System.Text.Encoding]::UTF8)
    Write-Host "Wrote $out"
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
