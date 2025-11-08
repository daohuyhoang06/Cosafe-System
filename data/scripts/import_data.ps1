# Import data to Elasticsearch using PowerShell
param(
    [string]$ESHost = "http://localhost:9200",
    [string]$IndexName = "cs_products_data"
)

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  COSAFE SYSTEM - ELASTICSEARCH DATA IMPORT" -ForegroundColor Yellow
Write-Host ("=" * 71) -ForegroundColor Cyan

# Test Elasticsearch connection
Write-Host "`n[1/3] Kiem tra ket noi Elasticsearch..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri $ESHost -Method Get -ErrorAction Stop
    Write-Host "      OK - Elasticsearch dang chay (version: $($response.version.number))" -ForegroundColor Green
}
catch {
    Write-Host "      FAILED - Khong the ket noi toi Elasticsearch!" -ForegroundColor Red
    Write-Host "      Hay chac chan Docker dang chay: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Delete and create index
Write-Host "`n[2/3] Tao index '$IndexName'..." -ForegroundColor Cyan

# Check if index exists and delete it
try {
    Invoke-RestMethod -Uri "$ESHost/$IndexName" -Method Head -ErrorAction Stop | Out-Null
    Write-Host "      Index da ton tai, dang xoa..." -ForegroundColor Yellow
    Invoke-RestMethod -Uri "$ESHost/$IndexName" -Method Delete | Out-Null
}
catch {
    # Index doesn't exist, that's fine
}

# Create index with mapping
$mapping = @{
    mappings = @{
        properties = @{
            name        = @{
                type   = "text"
                fields = @{
                    keyword = @{ type = "keyword" }
                }
            }
            score       = @{ type = "integer" }
            link_image  = @{ type = "text" }
            brand       = @{
                type   = "text"
                fields = @{
                    keyword = @{ type = "keyword" }
                }
            }
            category    = @{
                type   = "text"
                fields = @{
                    keyword = @{ type = "keyword" }
                }
            }
            ingredients = @{
                type    = "object"
                enabled = $true
            }
        }
    }
    settings = @{
        number_of_shards   = 1
        number_of_replicas = 0
        index              = @{
            max_result_window = 50000
        }
    }
} | ConvertTo-Json -Depth 10

try {
    Invoke-RestMethod -Uri "$ESHost/$IndexName" -Method Put -Body $mapping -ContentType "application/json" | Out-Null
    Write-Host "      OK - Index da duoc tao" -ForegroundColor Green
}
catch {
    Write-Host "      FAILED - Khong the tao index: $_" -ForegroundColor Red
    exit 1
}

# Import data files
Write-Host "`n[3/3] Import du lieu..." -ForegroundColor Cyan

# Updated path - now relative to data/scripts/ folder
$dataDir = "..\data_elasticsearch"
$files = Get-ChildItem -Path $dataDir -Filter "part_*.ndjson" | Sort-Object Name

if ($files.Count -eq 0) {
    Write-Host "      FAILED - Khong tim thay file du lieu!" -ForegroundColor Red
    exit 1
}

Write-Host "      Tim thay $($files.Count) files du lieu" -ForegroundColor Yellow

$totalDocs = 0
$fileCount = 0

foreach ($file in $files) {
    $fileCount++
    Write-Host "`n      [$fileCount/$($files.Count)] Dang import $($file.Name)..." -ForegroundColor White
    
    # Read file content (already in bulk format)
    $bulkData = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Replace old index name with new one
    $bulkData = $bulkData -replace '"_index":\s*"products"', "`"_index`": `"$IndexName`""
    
    # Ensure ends with newline
    if (-not $bulkData.EndsWith("`n")) {
        $bulkData += "`n"
    }
    
    # Count documents (every 2 lines = 1 document in bulk format)
    $lineCount = (($bulkData -split "`n" | Where-Object { $_.Trim() -ne "" }).Count) / 2
    
    if ($lineCount -gt 0) {
        try {
            $result = Invoke-RestMethod -Uri "$ESHost/_bulk" -Method Post -Body $bulkData -ContentType "application/x-ndjson"
            
            if ($result.errors) {
                $errorCount = ($result.items | Where-Object { $_.index.error } | Measure-Object).Count
                Write-Host "              $lineCount docs, $errorCount loi" -ForegroundColor Yellow
            }
            else {
                Write-Host "              OK - $lineCount documents" -ForegroundColor Green
            }
            
            $totalDocs += $lineCount
        }
        catch {
            Write-Host "              FAILED - Loi khi import: $_" -ForegroundColor Red
        }
    }
}

# Refresh index
Write-Host "`n      Dang refresh index..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$ESHost/$IndexName/_refresh" -Method Post | Out-Null

# Get final count
$countResult = Invoke-RestMethod -Uri "$ESHost/$IndexName/_count" -Method Get
$finalCount = $countResult.count

Write-Host "`n" -NoNewline
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host "  HOAN TAT!" -ForegroundColor Green
Write-Host "  Tong so documents da import: $totalDocs" -ForegroundColor Yellow
Write-Host "  Tong so documents trong index: $finalCount" -ForegroundColor Yellow
Write-Host ("=" * 71) -ForegroundColor Cyan

Write-Host "`nBan co the chay backend va frontend:" -ForegroundColor White
Write-Host "  Backend:  " -NoNewline -ForegroundColor Cyan
Write-Host "python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "  Frontend: " -NoNewline -ForegroundColor Cyan
Write-Host "cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
