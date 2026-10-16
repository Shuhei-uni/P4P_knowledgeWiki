param([Parameter(Mandatory=$true)][string]$ConfigPath)
$ErrorActionPreference = 'Stop'
$config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$shared = $env:OneDriveCommercial
if (-not $shared -or -not (Test-Path -LiteralPath $shared)) {
    $shared = Join-Path $env:USERPROFILE 'OneDrive - The University of Auckland'
}
if (-not (Test-Path -LiteralPath $shared)) { throw 'University OneDrive folder is unavailable' }
$destination = Join-Path $shared $config.destination_relative
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$receiptPath = Join-Path $destination 'copy-verification.json'
$results = @()
try {
    foreach ($file in $config.files) {
        if (-not (Test-Path -LiteralPath $file.source -PathType Leaf)) { throw "Missing source: $($file.source)" }
        $sourceHash = (Get-FileHash -LiteralPath $file.source -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($sourceHash -ne $file.sha256) { throw "Source identity differs: $($file.name)" }
        $target = Join-Path $destination $file.name
        if (Test-Path -LiteralPath $target) {
            if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sourceHash) {
                throw "Refusing to overwrite a different destination: $target"
            }
        } else {
            Copy-Item -LiteralPath $file.source -Destination $target
        }
        $targetHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($targetHash -ne $sourceHash) { throw "Destination hash differs: $($file.name)" }
        $results += [pscustomobject]@{role=$file.role; name=$file.name; destination=$target; sha256=$targetHash; bytes=(Get-Item -LiteralPath $target).Length}
    }
    $config.selected | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $destination 'selected-pairs.json') -Encoding UTF8
    [pscustomobject]@{status='COPIED_SOURCE_AND_DESTINATION_HASH_VERIFIED'; server_id='5'; destination=$destination; files=$results; fluent_solve_load_exit_restart_commands=0} |
        ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
} catch {
    [pscustomobject]@{status='COPY_FAILED'; error=$_.Exception.Message; files=$results} |
        ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
    throw
}
