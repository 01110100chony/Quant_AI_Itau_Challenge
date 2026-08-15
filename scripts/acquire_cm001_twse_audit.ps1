[CmdletBinding()]
param(
    [string]$OutputDirectory = "data/raw/cm_001/twse_official_audit_2007_2018",
    [switch]$Resume
)

$ErrorActionPreference = "Stop"
$resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputDirectory))
if (Test-Path -LiteralPath $resolvedOutput) {
    $existing = @(Get-ChildItem -LiteralPath $resolvedOutput -Force)
    if ($existing.Count -gt 0 -and -not $Resume) {
        throw "Refusing to overwrite non-empty raw audit directory: $resolvedOutput"
    }
}
New-Item -ItemType Directory -Path $resolvedOutput -Force | Out-Null
$collectedAt = [DateTimeOffset]::UtcNow.ToString("o")

function Save-RawResponse {
    param(
        [string]$Url,
        [string]$Stem,
        [string]$Dataset,
        [string]$Instrument,
        [string]$RequestedMonth
    )
    $rawPath = Join-Path $resolvedOutput "$Stem.json"
    $metadataPath = Join-Path $resolvedOutput "$Stem`_request.json"
    if ($Resume -and (Test-Path -LiteralPath $rawPath) -and (Test-Path -LiteralPath $metadataPath)) {
        return
    }
    if ((Test-Path -LiteralPath $rawPath) -or (Test-Path -LiteralPath $metadataPath)) {
        throw "Refusing to overwrite incomplete response pair for $Stem"
    }
    $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing
    [System.IO.File]::WriteAllText($rawPath, $response.Content, [System.Text.UTF8Encoding]::new($false))
    $metadata = [ordered]@{
        provider = "Taiwan Stock Exchange"
        dataset = $Dataset
        instrument = $Instrument
        requested_month = $RequestedMonth
        acquired_at_utc = $collectedAt
        http_status = [int]$response.StatusCode
        content_type = [string]$response.Headers.'Content-Type'
        raw_response_file = "$Stem.json"
        raw_response_bytes = (Get-Item -LiteralPath $rawPath).Length
        endpoint = $Url.Split('?')[0]
    }
    $metadata | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $metadataPath -Encoding utf8
}

for ($year = 2007; $year -le 2018; $year++) {
    for ($month = 1; $month -le 12; $month++) {
        $monthText = "{0:D4}{1:D2}01" -f $year, $month
        $url = "https://www.twse.com.tw/rwd/en/TAIEX/MI_5MINS_HIST?date=$monthText&response=json"
        Save-RawResponse -Url $url -Stem "TAIEX_$monthText" -Dataset "MI_5MINS_HIST" -Instrument "TAIEX" -RequestedMonth $monthText
        Start-Sleep -Milliseconds 100
    }
}

foreach ($instrument in @("0052", "0050")) {
    foreach ($year in 2010..2018) {
        foreach ($month in 1..12) {
            $monthText = "{0:D4}{1:D2}01" -f $year, $month
            $url = "https://www.twse.com.tw/rwd/en/afterTrading/STOCK_DAY?date=$monthText&stockNo=$instrument&response=json"
            Save-RawResponse -Url $url -Stem "$($instrument)_$monthText" -Dataset "STOCK_DAY" -Instrument $instrument -RequestedMonth $monthText
            Start-Sleep -Milliseconds 100
        }
    }
}

Write-Output "CM_001 Stage A TWSE raw provider-audit responses written to $resolvedOutput"
