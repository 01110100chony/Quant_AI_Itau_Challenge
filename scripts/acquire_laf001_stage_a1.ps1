[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$symbols = @("SPY", "QQQ", "IWM", "DIA", "MDY")
$endpoint = "https://query1.finance.yahoo.com/v8/finance/chart"
$period1 = 1041379200
$period2 = 1483228800
$parserVersion = "laf-stage-a1-v1"
$provider = "Yahoo Finance Chart API"
$parameters = [ordered]@{
    interval = "1d"
    period1 = $period1
    period2 = $period2
    events = "div,splits,capitalGains"
    includeAdjustedClose = "true"
    includePrePost = "false"
}

if ([DateTimeOffset]::FromUnixTimeSeconds($period1).UtcDateTime.ToString("o") -notlike "2003-01-01T00:00:00*") {
    throw "period1 does not resolve to 2003-01-01T00:00:00Z"
}
if ([DateTimeOffset]::FromUnixTimeSeconds($period2).UtcDateTime.ToString("o") -notlike "2017-01-01T00:00:00*") {
    throw "period2 does not resolve to 2017-01-01T00:00:00Z"
}

Push-Location $repoRoot
try {
    $branch = (git branch --show-current).Trim()
    if ($branch -ne "research/laf-001") {
        throw "collector requires branch research/laf-001; observed $branch"
    }
    $dirty = @(git status --porcelain)
    if ($dirty.Count -ne 0) {
        throw "collector requires a clean worktree after H0-A1"
    }
    $h0A1Commit = (git rev-parse HEAD).Trim()

    $rawParent = Join-Path $repoRoot "data\raw\laf_001\research"
    if (Test-Path -LiteralPath $rawParent) {
        $existing = @(Get-ChildItem -LiteralPath $rawParent -Force)
        if ($existing.Count -ne 0) {
            throw "a LAF_001 raw retrieval already exists; refusing a second acquisition"
        }
    }

    $retrievalId = [DateTimeOffset]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
    $rawDir = Join-Path $rawParent $retrievalId
    New-Item -ItemType Directory -Path $rawDir -ErrorAction Stop | Out-Null

    function Write-NewUtf8 {
        param([string]$Path, [string]$Text)
        $encoding = [System.Text.UTF8Encoding]::new($false)
        $bytes = $encoding.GetBytes($Text)
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
    }

    function Write-NewBytes {
        param([string]$Path, [byte[]]$Bytes)
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try { $stream.Write($Bytes, 0, $Bytes.Length) } finally { $stream.Dispose() }
    }

    function Get-Sha256 {
        param([byte[]]$Bytes)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            return ([System.BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace("-", "").ToLowerInvariant()
        } finally {
            $sha.Dispose()
        }
    }

    Add-Type -AssemblyName System.Net.Http
    $handler = [System.Net.Http.HttpClientHandler]::new()
    $client = [System.Net.Http.HttpClient]::new($handler)
    $client.DefaultRequestHeaders.UserAgent.ParseAdd("Quant-AI-Itau-LAF001-StageA1/1.0")
    $receipts = [System.Collections.Generic.List[object]]::new()

    try {
        foreach ($symbol in $symbols) {
            $query = "interval=1d&period1=1041379200&period2=1483228800&events=div%2Csplits%2CcapitalGains&includeAdjustedClose=true&includePrePost=false"
            $url = "$endpoint/$symbol`?$query"
            $requestRecord = [ordered]@{
                provider = $provider
                symbol = $symbol
                endpoint = $endpoint
                url = $url
                parameters = $parameters
                retrieval_id = $retrievalId
                h0_a1_commit = $h0A1Commit
                parser_version = $parserVersion
            }
            Write-NewUtf8 -Path (Join-Path $rawDir "${symbol}_request.json") -Text (($requestRecord | ConvertTo-Json -Depth 8) + "`n")

            $success = $false
            for ($attempt = 1; $attempt -le 2 -and -not $success; $attempt++) {
                $attemptStarted = [DateTimeOffset]::UtcNow.ToString("o")
                $response = $null
                $payload = $null
                $transportError = $null
                try {
                    $response = $client.GetAsync($url).GetAwaiter().GetResult()
                    $payload = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
                } catch {
                    $transportError = $_.Exception.Message
                }

                $httpStatus = if ($null -ne $response) { [int]$response.StatusCode } else { $null }
                $contentType = if ($null -ne $response -and $null -ne $response.Content.Headers.ContentType) {
                    $response.Content.Headers.ContentType.ToString()
                } else { $null }
                $payloadSize = if ($null -ne $payload) { $payload.Length } else { 0 }
                $retryable = ($null -ne $transportError) -or ($null -eq $response) -or (-not $response.IsSuccessStatusCode) -or ($payloadSize -eq 0)

                if ($retryable) {
                    $failurePayloadFile = $null
                    $failureSha = $null
                    if ($payloadSize -gt 0) {
                        $failurePayloadFile = "${symbol}_attempt_${attempt}_response.json"
                        Write-NewBytes -Path (Join-Path $rawDir $failurePayloadFile) -Bytes $payload
                        $failureSha = Get-Sha256 -Bytes $payload
                    }
                    $failureReceipt = [ordered]@{
                        provider = $provider
                        symbol = $symbol
                        url = $url
                        parameters = $parameters
                        attempt = $attempt
                        acquired_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
                        attempt_started_at_utc = $attemptStarted
                        http_status = $httpStatus
                        content_type = $contentType
                        payload_size_bytes = $payloadSize
                        payload_sha256 = $failureSha
                        raw_payload_file = $failurePayloadFile
                        parser_version = $parserVersion
                        transport_error = $transportError
                        retry_reason = if ($null -ne $transportError) { "TRANSPORT" } elseif ($payloadSize -eq 0) { "EMPTY_PAYLOAD" } else { "HTTP" }
                    }
                    Write-NewUtf8 -Path (Join-Path $rawDir "${symbol}_attempt_${attempt}_receipt.json") -Text (($failureReceipt | ConvertTo-Json -Depth 8) + "`n")
                    $receipts.Add($failureReceipt)
                    if ($attempt -eq 2) {
                        throw "acquisition failed twice for $symbol; raw failure receipts were preserved"
                    }
                    continue
                }

                $payloadFile = "${symbol}_response.json"
                Write-NewBytes -Path (Join-Path $rawDir $payloadFile) -Bytes $payload
                $payloadSha = Get-Sha256 -Bytes $payload
                $payloadText = [System.Text.Encoding]::UTF8.GetString($payload)
                try {
                    $json = $payloadText | ConvertFrom-Json -Depth 100
                } catch {
                    $contentReceipt = [ordered]@{
                        provider = $provider
                        symbol = $symbol
                        url = $url
                        parameters = $parameters
                        attempt = $attempt
                        acquired_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
                        http_status = $httpStatus
                        content_type = $contentType
                        payload_size_bytes = $payloadSize
                        payload_sha256 = $payloadSha
                        raw_payload_file = $payloadFile
                        parser_version = $parserVersion
                        content_error = $_.Exception.Message
                    }
                    Write-NewUtf8 -Path (Join-Path $rawDir "${symbol}_receipt.json") -Text (($contentReceipt | ConvertTo-Json -Depth 8) + "`n")
                    throw "content failure for $symbol; payload preserved and no retry permitted"
                }

                $chartError = $json.chart.error
                $result = if ($null -ne $json.chart.result -and $json.chart.result.Count -eq 1) { $json.chart.result[0] } else { $null }
                $meta = if ($null -ne $result) { $result.meta } else { $null }
                $timestamps = if ($null -ne $result) { @($result.timestamp) } else { @() }
                $firstTimestamp = if ($timestamps.Count -gt 0) { [Int64]$timestamps[0] } else { $null }
                $lastTimestamp = if ($timestamps.Count -gt 0) { [Int64]$timestamps[-1] } else { $null }
                $receipt = [ordered]@{
                    provider = $provider
                    symbol = $symbol
                    url = $url
                    parameters = $parameters
                    attempt = $attempt
                    acquired_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
                    attempt_started_at_utc = $attemptStarted
                    http_status = $httpStatus
                    content_type = $contentType
                    payload_size_bytes = $payloadSize
                    payload_sha256 = $payloadSha
                    raw_payload_file = $payloadFile
                    parser_version = $parserVersion
                    provider_timezone = if ($null -ne $meta) { $meta.exchangeTimezoneName } else { $null }
                    provider_exchange = if ($null -ne $meta) { $meta.exchangeName } else { $null }
                    first_timestamp = $firstTimestamp
                    last_timestamp = $lastTimestamp
                    chart_error = $chartError
                    transport_error = $null
                }
                Write-NewUtf8 -Path (Join-Path $rawDir "${symbol}_receipt.json") -Text (($receipt | ConvertTo-Json -Depth 8) + "`n")
                $receipts.Add($receipt)
                if ($null -ne $chartError -or $null -eq $result) {
                    throw "schema/content failure for $symbol; payload preserved and no retry permitted"
                }
                $success = $true
            }
        }
    } finally {
        $client.Dispose()
        $handler.Dispose()
    }

    $retrievalRecord = [ordered]@{
        experiment_id = "LAF_001"
        retrieval_id = $retrievalId
        created_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
        provider = $provider
        symbols = $symbols
        endpoint = $endpoint
        parameters = $parameters
        period1_utc = "2003-01-01T00:00:00Z"
        period2_utc_exclusive = "2017-01-01T00:00:00Z"
        parser_version = $parserVersion
        h0_a1_commit = $h0A1Commit
        receipts = @($receipts)
    }
    Write-NewUtf8 -Path (Join-Path $rawDir "retrieval_manifest.json") -Text (($retrievalRecord | ConvertTo-Json -Depth 10) + "`n")
    Write-Output "RETRIEVAL_ID=$retrievalId"
} finally {
    Pop-Location
}
