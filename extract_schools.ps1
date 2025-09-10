# PowerShell script to extract unique school information from Excel file
param(
    [string]$ExcelFile = "Visit Report_2025-02-12_2025-08-19.xlsx",
    [string]$OutputFile = "unique_schools.csv"
)

try {
    # Create Excel COM object
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    
    # Open the workbook
    $workbook = $excel.Workbooks.Open((Resolve-Path $ExcelFile).Path)
    $worksheet = $workbook.Worksheets.Item(1)
    
    # Get the used range
    $usedRange = $worksheet.UsedRange
    $rowCount = $usedRange.Rows.Count
    $colCount = $usedRange.Columns.Count
    
    Write-Host "Excel file loaded successfully"
    Write-Host "Rows: $rowCount, Columns: $colCount"
    
    # Get header row
    $headers = @()
    for ($col = 1; $col -le $colCount; $col++) {
        $headers += $worksheet.Cells.Item(1, $col).Text
    }
    
    Write-Host "`nColumn headers:"
    for ($i = 0; $i -lt $headers.Count; $i++) {
        Write-Host "$($i + 1): $($headers[$i])"
    }
    
    # Find relevant columns
    $smnameCol = -1
    $customerCol = -1
    $phoneCol = -1
    
    for ($i = 0; $i -lt $headers.Count; $i++) {
        $header = $headers[$i].ToLower()
        if ($header -like "*sm*" -and $header -like "*name*") {
            $smnameCol = $i + 1
        }
        elseif ($header -like "*customer*" -and $header -like "*name*") {
            $customerCol = $i + 1
        }
        elseif ($header -like "*phone*") {
            $phoneCol = $i + 1
        }
    }
    
    Write-Host "`nIdentified columns:"
    Write-Host "SM Name Column: $smnameCol ($($headers[$smnameCol-1]))"
    Write-Host "Customer Name Column: $customerCol ($($headers[$customerCol-1]))"
    Write-Host "Phone Column: $phoneCol ($($headers[$phoneCol-1]))"
    
    if ($smnameCol -gt 0 -and $customerCol -gt 0 -and $phoneCol -gt 0) {
        # Extract data
        $schools = @{}
        
        for ($row = 2; $row -le $rowCount; $row++) {
            $smname = $worksheet.Cells.Item($row, $smnameCol).Text.Trim()
            $customer = $worksheet.Cells.Item($row, $customerCol).Text.Trim()
            $phone = $worksheet.Cells.Item($row, $phoneCol).Text.Trim()
            
            # Skip empty rows
            if ($smname -ne "" -and $customer -ne "" -and $phone -ne "") {
                # Use combination as key to ensure uniqueness
                $key = "$smname|$customer|$phone"
                if (-not $schools.ContainsKey($key)) {
                    $schools[$key] = @{
                        SMName = $smname
                        CustomerName = $customer
                        PhoneNumber = $phone
                    }
                }
            }
        }
        
        Write-Host "`nFound $($schools.Count) unique schools"
        
        # Create CSV content
        $csvContent = "SM_Name,Customer_Name,Phone_Number`n"
        foreach ($school in $schools.Values) {
            $csvContent += "`"$($school.SMName)`",`"$($school.CustomerName)`",`"$($school.PhoneNumber)`"`n"
        }
        
        # Save to CSV file
        $csvContent | Out-File -FilePath $OutputFile -Encoding UTF8
        
        Write-Host "`nUnique schools data saved to: $OutputFile"
        Write-Host "`nFirst few entries:"
        $schools.Values | Select-Object -First 5 | Format-Table -AutoSize
        
    } else {
        Write-Host "`nCould not identify all required columns. Please check the column names."
        Write-Host "Available columns:"
        for ($i = 0; $i -lt $headers.Count; $i++) {
            Write-Host "  $($i + 1): $($headers[$i])"
        }
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    # Clean up
    if ($workbook) { $workbook.Close($false) }
    if ($excel) { $excel.Quit() }
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}


