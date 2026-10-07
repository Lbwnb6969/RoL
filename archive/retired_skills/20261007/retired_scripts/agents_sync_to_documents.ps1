param(
    [string]$Source = "C:\CK3Mods\RoL",
    [string]$Destination = "c:\Users\Falcons的Niko本人的PC\Documents\Paradox Interactive\Crusader Kings III\mod\RoL",
    [switch]$WhatIf
)

Write-Host "[INFO] Source      : $Source"
Write-Host "[INFO] Destination : $Destination"

if (!(Test-Path $Source)) {
    Write-Error "Source not found: $Source"
    exit 2
}

$args = @($Source, $Destination, '/E', '/XD', '.git', '/NFL', '/NDL', '/NJH', '/NJS', '/NC', '/NS', '/NP')
if ($WhatIf) {
    Write-Host "[INFO] WhatIf enabled. No files will be copied."
    $args += '/L'
}

& robocopy @args | Out-Host
$rc = $LASTEXITCODE

if ($rc -le 7) {
    Write-Host "[OK] robocopy completed with exit code $rc"
    exit 0
}

Write-Error "robocopy failed with exit code $rc"
exit $rc
