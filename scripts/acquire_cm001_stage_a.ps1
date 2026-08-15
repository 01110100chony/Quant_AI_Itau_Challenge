[CmdletBinding()]
param(
    [string]$OutputDirectory = "data/raw/cm_001/yahoo_chart_2007_2018_v2"
)

$ErrorActionPreference = "Stop"

$researchStart = [DateTimeOffset]::new(2007, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
$researchEndExclusive = [DateTimeOffset]::new(2019, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
$period1 = $researchStart.ToUnixTimeSeconds()
$period2 = $researchEndExclusive.ToUnixTimeSeconds()
$collectedAt = [DateTimeOffset]::UtcNow.ToString("o")

$assets = @(
    [PSCustomObject]@{ asset = "XSD"; vendor_symbol = "XSD"; expected_timezone = "America/New_York" },
    [PSCustomObject]@{ asset = "QQQ"; vendor_symbol = "QQQ"; expected_timezone = "America/New_York" },
    [PSCustomObject]@{ asset = "SPY"; vendor_symbol = "SPY"; expected_timezone = "America/New_York" },
    [PSCustomObject]@{ asset = "0052"; vendor_symbol = "0052.TW"; expected_timezone = "Asia/Taipei" },
    [PSCustomObject]@{ asset = "TAIEX"; vendor_symbol = "^TWII"; expected_timezone = "Asia/Taipei" },
    [PSCustomObject]@{ asset = "0050"; vendor_symbol = "0050.TW"; expected_timezone = "Asia/Taipei" }
)

$resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputDirectory))
if (Test-Path -LiteralPath $resolvedOutput) {
    $existing = @(Get-ChildItem -LiteralPath $resolvedOutput -Force)
    if ($existing.Count -gt 0) {
        throw "Refusing to overwrite non-empty raw snapshot directory: $resolvedOutput"
    }
}
New-Item -ItemType Directory -Path $resolvedOutput -Force | Out-Null

foreach ($assetSpec in $assets) {
    $escapedSymbol = [Uri]::EscapeDataString($assetSpec.vendor_symbol)
    $url = "https://query1.finance.yahoo.com/v8/finance/chart/$escapedSymbol" +
        "?period1=$period1&period2=$period2&interval=1d" +
        "&events=div%2Csplits%2CcapitalGains&includeAdjustedClose=true"

    $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing
    $rawPath = Join-Path $resolvedOutput "$($assetSpec.asset)_response.json"
    [System.IO.File]::WriteAllText($rawPath, $response.Content, [System.Text.UTF8Encoding]::new($false))

    $requestMetadata = [ordered]@{
        provider = "Yahoo Finance chart API"
        endpoint = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        asset = $assetSpec.asset
        provider_symbol = $assetSpec.vendor_symbol
        requested_start = "2007-01-01"
        requested_end_exclusive = "2019-01-01"
        interval = "1d"
        events = @("dividends", "splits", "capitalGains")
        include_adjusted_close = $true
        expected_timezone = $assetSpec.expected_timezone
        acquired_at_utc = $collectedAt
        http_status = [int]$response.StatusCode
        raw_response_file = "$($assetSpec.asset)_response.json"
        raw_response_bytes = (Get-Item -LiteralPath $rawPath).Length
    }
    $metadataPath = Join-Path $resolvedOutput "$($assetSpec.asset)_request.json"
    $requestMetadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding utf8
}

Write-Output "CM_001 Stage A immutable raw HTTP responses written to $resolvedOutput"
