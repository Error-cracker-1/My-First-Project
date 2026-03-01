# System Information Dashboard
Write-Host "=== SYSTEM INFORMATION DASHBOARD ===" -ForegroundColor Cyan

# helper: execute a block, warn on failure and return $null instead of stopping
function Get-InfoSafe {
    param(
        [scriptblock]$ScriptBlock
    )
    try {
        & $ScriptBlock -ErrorAction Stop
    }
    catch {
        Write-Warning "Could not retrieve information: $_"
        return $null
    }
}

# retrieve individual pieces; don't abort if one fails
$os = Get-InfoSafe { Get-CimInstance Win32_OperatingSystem }
$cpu = Get-InfoSafe { Get-CimInstance Win32_Processor }
$memory = Get-InfoSafe { Get-CimInstance Win32_ComputerSystem }

Write-Host "`nComputer: $(Get-Content env:COMPUTERNAME)" -ForegroundColor Green
Write-Host "OS: $($os.Caption)" -ForegroundColor Green
if ($cpu) {
    Write-Host "CPU: $($cpu.Name)" -ForegroundColor Green
}
else {
    Write-Host "CPU: <unavailable>" -ForegroundColor DarkYellow
}

if ($os) {
    $usedMemory = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 2)
    $totalMemory = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    Write-Host "Memory: $usedMemory GB / $totalMemory GB" -ForegroundColor Yellow
    $uptime = (Get-Date) - $os.LastBootUpTime
    Write-Host "Uptime: $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m" -ForegroundColor Yellow
}
else {
    Write-Host "Memory: <unavailable>" -ForegroundColor DarkYellow
}

if ($memory) {
    Write-Host "Physical RAM: $([math]::Round($memory.TotalPhysicalMemory / 1GB,2)) GB" -ForegroundColor Yellow
}
else {
    Write-Host "Physical RAM: <unavailable>" -ForegroundColor DarkYellow
}

# disk information for all fixed volumes
Get-Volume | Where-Object DriveType -EQ 'Fixed' | ForEach-Object {
    $percentFree = [math]::Round(($_.SizeRemaining / $_.Size) * 100, 2)
    Write-Host "$($_.DriveLetter): Drive Free Space: $percentFree%" -ForegroundColor $(if ($percentFree -lt 20) { 'Red' } else { 'Green' })
}

# network adapter details
Write-Host "`nNetwork Interfaces:" -ForegroundColor Cyan
Get-NetAdapter -Physical | ForEach-Object {
    $ip = (Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue).IPAddress -join ', '
    Write-Host "  Name: $($_.Name) - Status: $($_.Status) - IP: $ip" -ForegroundColor Green
}

# BIOS/firmware
$bios = Get-InfoSafe { Get-CimInstance Win32_BIOS }
if ($bios) {
    Write-Host "BIOS Version: $($bios.SMBIOSBIOSVersion) ($($bios.Manufacturer))" -ForegroundColor Yellow
}

# installed updates (last 5)
Write-Host "`nRecent Updates:" -ForegroundColor Cyan
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5 | ForEach-Object {
    Write-Host "  $($_.HotFixID) - $($_.InstalledOn.ToShortDateString())" -ForegroundColor Green
}

Write-Host "`nRunning Processes: $($(Get-Process).Count)" -ForegroundColor Magenta
Write-Host "`n================================`n" -ForegroundColor Cyan