[CmdletBinding()]
param(
    [string]$OutputDirectory = "data/raw/cm_001/stage_a_closure_2010_2018",
    [switch]$Resume
)

$ErrorActionPreference = "Stop"
$researchStart = [datetime]::ParseExact("2010-01-01", "yyyy-MM-dd", $null)
$researchEnd = [datetime]::ParseExact("2018-12-31", "yyyy-MM-dd", $null)
$retrievedAt = [DateTimeOffset]::UtcNow.ToString("o")
$resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputDirectory))

if (Test-Path -LiteralPath $resolvedOutput) {
    $existing = @(Get-ChildItem -LiteralPath $resolvedOutput -Force)
    if ($existing.Count -gt 0 -and -not $Resume) {
        throw "Refusing to overwrite non-empty raw closure directory: $resolvedOutput"
    }
}
New-Item -ItemType Directory -Path $resolvedOutput -Force | Out-Null

function Convert-RocDate {
    param([string]$Value)
    if ($Value -notmatch '^(\d{2,3})年(\d{2})月(\d{2})日$') {
        throw "Unexpected ROC date: $Value"
    }
    $year = [int]$Matches[1] + 1911
    return [datetime]::new($year, [int]$Matches[2], [int]$Matches[3])
}

function Assert-ResearchDate {
    param([datetime]$Value, [string]$Label)
    if ($Value -lt $researchStart -or $Value -gt $researchEnd) {
        throw "$Label crosses Research boundary: $($Value.ToString('yyyy-MM-dd'))"
    }
}

function Save-JsonArtifact {
    param([string]$Stem, [object]$Payload, [hashtable]$RequestMetadata)
    $artifactPath = Join-Path $resolvedOutput "$Stem.json"
    $requestPath = Join-Path $resolvedOutput "$Stem`_request.json"
    if ($Resume -and (Test-Path -LiteralPath $artifactPath) -and (Test-Path -LiteralPath $requestPath)) {
        return
    }
    if ((Test-Path -LiteralPath $artifactPath) -or (Test-Path -LiteralPath $requestPath)) {
        throw "Refusing to overwrite incomplete closure response pair for $Stem"
    }
    [System.IO.File]::WriteAllText(
        $artifactPath,
        ($Payload | ConvertTo-Json -Depth 12 -Compress),
        [System.Text.UTF8Encoding]::new($false)
    )
    $RequestMetadata.retrieved_at_utc = $retrievedAt
    $RequestMetadata.filtered_artifact = "$Stem.json"
    $RequestMetadata.filtered_artifact_bytes = (Get-Item -LiteralPath $artifactPath).Length
    [System.IO.File]::WriteAllText(
        $requestPath,
        ($RequestMetadata | ConvertTo-Json -Depth 8),
        [System.Text.UTF8Encoding]::new($false)
    )
}

function Get-OfficialJson {
    param([string]$Url)
    $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing
    if ([int]$response.StatusCode -ne 200) {
        throw "Official endpoint returned HTTP $($response.StatusCode): $Url"
    }
    return @{
        Response = $response
        Json = ($response.Content | ConvertFrom-Json)
    }
}

# TWT49U obligatorily includes current filing metadata in historical rows. Filter it
# in memory and never persist those post-Research fields or unrelated instruments.
$exRightUrl = "https://www.twse.com.tw/rwd/zh/exRight/TWT49U?startDate=20100101&endDate=20181231&response=json"
$exRightResponse = Get-OfficialJson -Url $exRightUrl
$exRight = $exRightResponse.Json
if ($exRight.stat -ne "OK") { throw "TWT49U status is not OK" }
$codeIndex = [Array]::IndexOf([object[]]$exRight.fields, "股票代號")
$dateIndex = [Array]::IndexOf([object[]]$exRight.fields, "資料日期")
$detailIndex = [Array]::IndexOf([object[]]$exRight.fields, "詳細資料")
if ($codeIndex -lt 0 -or $dateIndex -lt 0 -or $detailIndex -lt 0) {
    throw "TWT49U required fields are missing"
}
$keptFields = @($exRight.fields[0..$detailIndex])
$keptRows = @()
foreach ($row in $exRight.data) {
    if ($row[$codeIndex] -notin @("0052", "0050")) { continue }
    $eventDate = Convert-RocDate -Value ([string]$row[$dateIndex])
    Assert-ResearchDate -Value $eventDate -Label "TWT49U event"
    $keptRows += ,@($row[0..$detailIndex])
}
$filteredExRight = [ordered]@{
    stat = $exRight.stat
    title = $exRight.title
    fields = $keptFields
    data = $keptRows
    acquisition_filter = "Security Code in {0052,0050}; event_date 2010-01-01..2018-12-31; current filing columns discarded before persistence"
    upstream_row_count = @($exRight.data).Count
    filtered_row_count = $keptRows.Count
}
Save-JsonArtifact -Stem "twse_ex_right_2010_2018" -Payload $filteredExRight -RequestMetadata @{
    provider = "Taiwan Stock Exchange"
    dataset = "TWT49U"
    instruments = @("0052", "0050")
    requested_start = "2010-01-01"
    requested_end = "2018-12-31"
    endpoint = $exRightUrl.Split('?')[0]
    request_url = $exRightUrl
    http_status = [int]$exRightResponse.Response.StatusCode
    upstream_post_research_fields_discarded = $true
}

foreach ($instrument in @("0052", "0050")) {
    $dividendUrl = "https://www.twse.com.tw/rwd/zh/ETF/etfDiv?startDate=20100101&endDate=20181231&stkNo=$instrument&response=json"
    $dividendResponse = Get-OfficialJson -Url $dividendUrl
    $dividend = $dividendResponse.Json
    if ($dividend.status -ne "ok") { throw "ETF/etfDiv status is not ok for $instrument" }
    $dividendDateIndex = [Array]::IndexOf([object[]]$dividend.fields, "除息交易日")
    $dividendCodeIndex = [Array]::IndexOf([object[]]$dividend.fields, "證券代號")
    if ($dividendDateIndex -lt 0 -or $dividendCodeIndex -lt 0) {
        throw "ETF/etfDiv required fields are missing for $instrument"
    }
    $filteredDividendRows = @()
    foreach ($row in $dividend.data) {
        if ([string]$row[$dividendCodeIndex] -ne $instrument) { continue }
        $eventDate = Convert-RocDate -Value ([string]$row[$dividendDateIndex])
        Assert-ResearchDate -Value $eventDate -Label "ETF distribution event"
        $filteredDividendRows += ,@($row)
    }
    $filteredDividend = [ordered]@{
        status = $dividend.status
        title = $dividend.title
        fields = $dividend.fields
        data = $filteredDividendRows
        acquisition_filter = "Security Code = $instrument; ex_date 2010-01-01..2018-12-31"
        upstream_row_count = @($dividend.data).Count
        filtered_row_count = $filteredDividendRows.Count
    }
    Save-JsonArtifact -Stem "twse_etf_div_$($instrument)_2010_2018" -Payload $filteredDividend -RequestMetadata @{
        provider = "Taiwan Stock Exchange"
        dataset = "ETF/etfDiv"
        instruments = @($instrument)
        requested_start = "2010-01-01"
        requested_end = "2018-12-31"
        endpoint = $dividendUrl.Split('?')[0]
        request_url = $dividendUrl
        http_status = [int]$dividendResponse.Response.StatusCode
    }
}

# The public halt database begins on 2011-10-03. The endpoint currently ignores
# its stockNo filter when selectType=ALL, so unrelated rows are discarded in memory.
$haltUrl = "https://www.twse.com.tw/rwd/en/afterTrading/TWTAWU?startDate=20111003&endDate=20181231&stockNo=0052&selectType=ALL&response=json"
$haltResponse = Get-OfficialJson -Url $haltUrl
$halt = $haltResponse.Json
if ($halt.stat -ne "OK") { throw "TWTAWU status is not OK" }
$haltCodeIndex = [Array]::IndexOf([object[]]$halt.fields, "Security Code")
$haltDateIndex = [Array]::IndexOf([object[]]$halt.fields, "Trading Halt Date")
$haltRows = @()
foreach ($row in $halt.data) {
    if ([string]$row[$haltCodeIndex] -ne "0052") { continue }
    $haltDate = [datetime]::ParseExact([string]$row[$haltDateIndex], "yyyy/MM/dd", $null)
    Assert-ResearchDate -Value $haltDate -Label "TWTAWU halt"
    $haltRows += ,@($row)
}
$filteredHalt = [ordered]@{
    stat = $halt.stat
    title = $halt.title
    fields = $halt.fields
    data = $haltRows
    acquisition_filter = "Security Code = 0052; available endpoint period 2011-10-03..2018-12-31"
    upstream_row_count = @($halt.data).Count
    filtered_row_count = $haltRows.Count
}
Save-JsonArtifact -Stem "twse_halts_0052_20111003_20181231" -Payload $filteredHalt -RequestMetadata @{
    provider = "Taiwan Stock Exchange"
    dataset = "TWTAWU"
    instruments = @("0052")
    requested_start = "2011-10-03"
    requested_end = "2018-12-31"
    endpoint = $haltUrl.Split('?')[0]
    request_url = $haltUrl
    http_status = [int]$haltResponse.Response.StatusCode
    upstream_filter_ignored = $true
}

# Stratified second-endpoint cross-check: all six non-zero-volume no-OHLC dates
# plus one zero-volume no-OHLC date from every Research year.
$sampleDates = @(
    "20100224", "20110309", "20120104", "20130320", "20140106",
    "20150504", "20160114", "20170103", "20180112",
    "20140603", "20170405", "20170601", "20170720", "20170824", "20171002"
)
foreach ($dateText in $sampleDates) {
    $sampleDate = [datetime]::ParseExact($dateText, "yyyyMMdd", $null)
    Assert-ResearchDate -Value $sampleDate -Label "MI_INDEX sample"
    $dailyUrl = "https://www.twse.com.tw/rwd/en/afterTrading/MI_INDEX?date=$dateText&type=ALL&response=json"
    $dailyResponse = Get-OfficialJson -Url $dailyUrl
    $daily = $dailyResponse.Json
    if ($daily.stat -ne "OK") { throw "MI_INDEX status is not OK for $dateText" }
    $quoteTable = $daily.tables | Where-Object { $_.fields -contains "Security Code" } | Select-Object -First 1
    if ($null -eq $quoteTable) { throw "MI_INDEX quote table is missing for $dateText" }
    $dailyCodeIndex = [Array]::IndexOf([object[]]$quoteTable.fields, "Security Code")
    $dailyRows = @($quoteTable.data | Where-Object { [string]$_[$dailyCodeIndex] -eq "0052" })
    if ($dailyRows.Count -ne 1) { throw "MI_INDEX expected one 0052 row for $dateText, found $($dailyRows.Count)" }
    $filteredDaily = [ordered]@{
        stat = $daily.stat
        requested_date = $sampleDate.ToString("yyyy-MM-dd")
        title = $quoteTable.title
        fields = $quoteTable.fields
        data = @($dailyRows)
        acquisition_filter = "Security Code = 0052; one pre-specified Research date"
        upstream_quote_row_count = @($quoteTable.data).Count
        filtered_row_count = 1
    }
    Save-JsonArtifact -Stem "twse_mi_index_0052_$dateText" -Payload $filteredDaily -RequestMetadata @{
        provider = "Taiwan Stock Exchange"
        dataset = "MI_INDEX Daily Quotes (ALL)"
        instruments = @("0052")
        requested_start = $sampleDate.ToString("yyyy-MM-dd")
        requested_end = $sampleDate.ToString("yyyy-MM-dd")
        endpoint = $dailyUrl.Split('?')[0]
        request_url = $dailyUrl
        http_status = [int]$dailyResponse.Response.StatusCode
    }
}

$manifest = @"
provider = "Taiwan Stock Exchange"
scope = "CM_001 Stage A closure structural audit"
research_start = "2010-01-01"
research_end = "2018-12-31"
retrieved_at_utc = "$retrievedAt"
instruments = ["0052", "0050"]
contains_validation_or_oos_prices = false
acquisition_filtering = "All broad official responses were filtered in memory to Research dates and named instruments before persistence. Current filing metadata returned by TWT49U was discarded."
"@
$manifestPath = Join-Path $resolvedOutput "SOURCE_MANIFEST.toml"
if (-not ($Resume -and (Test-Path -LiteralPath $manifestPath))) {
    [System.IO.File]::WriteAllText($manifestPath, $manifest, [System.Text.UTF8Encoding]::new($false))
}

Write-Output "CM_001 Stage A closure official artifacts written to $resolvedOutput"
