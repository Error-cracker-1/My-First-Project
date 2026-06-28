# System Information Dashboard Script
# This script gathers and displays various system information
# such as OS details, CPU, memory, disk, network, BIOS, and recent updates.

# Defines a helper function to safely execute a script block.
# If the script block encounters an error, a warning is displayed,
# and $null is returned, preventing the main script from stopping.
function Get-InfoSafe {
    param(
        [scriptblock]$ScriptToExecute # The script block to execute.
    )
    try {
        # Execute the script block, forcing errors to be terminating.
        & $ScriptToExecute -ErrorAction Stop
    }
    catch {
        # Catch any terminating errors and display a warning with the error message.
        Write-Warning "Failed to retrieve information: $($_.Exception.Message)"
        return $null # Return $null to indicate failure.
    }
}

# --- Dashboard Header ---
Write-Host "=== SYSTEM INFORMATION DASHBOARD ===" -ForegroundColor Cyan
Write-Host "" # Add an empty line for better spacing

# --- Retrieve Core System Information ---
# Using Get-InfoSafe to prevent script termination if a command fails.
$os = Get-InfoSafe { Get-CimInstance Win32_OperatingSystem }
$cpu = Get-InfoSafe { Get-CimInstance Win32_Processor }
$computerSystem = Get-InfoSafe { Get-CimInstance Win32_ComputerSystem }

# --- Display General System Details ---
Write-Host "Computer Name: $(Get-Content env:COMPUTERNAME)" -ForegroundColor Green

if ($os) {
    Write-Host "Operating System: $($os.Caption) (Build $($os.BuildNumber))" -ForegroundColor Green
    $uptime = (Get-Date) - $os.LastBootUpTime
    Write-Host "System Uptime: $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m $($uptime.Seconds)s" -ForegroundColor Yellow
}
else {
    Write-Host "Operating System: <unavailable>" -ForegroundColor DarkYellow
    Write-Host "System Uptime: <unavailable>" -ForegroundColor DarkYellow
}

if ($cpu) {
    Write-Host "CPU: $($cpu.Name) (Cores: $($cpu.NumberOfCores), Logical Processors: $($cpu.NumberOfLogicalProcessors))" -ForegroundColor Green
}
else {
    Write-Host "CPU: <unavailable>" -ForegroundColor DarkYellow
}

# --- Display Memory Information ---
if ($os -and $computerSystem) {
    # Memory usage reported by the operating system
    $usedMemoryGB = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1GB, 2)
    $totalMemoryOSGB = [math]::Round($os.TotalVisibleMemorySize / 1GB, 2)
    Write-Host "Memory Usage: $usedMemoryGB GB / $totalMemoryOSGB GB" -ForegroundColor Yellow

    # Total physical RAM installed in the system
    $totalPhysicalRAMGB = [math]::Round($computerSystem.TotalPhysicalMemory / 1GB, 2)
    Write-Host "Installed RAM: $totalPhysicalRAMGB GB" -ForegroundColor Yellow
}
elseif ($os) {
     # If only OS info is available, still report memory usage
    $usedMemoryGB = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1GB, 2)
    $totalMemoryOSGB = [math]::Round($os.TotalVisibleMemorySize / 1GB, 2)
    Write-Host "Memory Usage: $usedMemoryGB GB / $totalMemoryOSGB GB" -ForegroundColor Yellow
    Write-Host "Installed RAM: <unavailable>" -ForegroundColor DarkYellow
}
else {
    Write-Host "Memory Usage: <unavailable>" -ForegroundColor DarkYellow
    Write-Host "Installed RAM: <unavailable>" -ForegroundColor DarkYellow
}

Write-Host "" # Add an empty line for better spacing

# --- Display Disk Information for Fixed Volumes ---
Write-Host "--- Disk Information (Fixed Drives) ---" -ForegroundColor Cyan
Get-Volume | Where-Object DriveType -EQ 'Fixed' | ForEach-Object {
    $percentFree = [math]::Round(($_.SizeRemaining / $_.Size) * 100, 2)
    Write-Host "  $($_.DriveLetter): $($_.FileSystemLabel) ($_.FileSystem): Total $([math]::Round($_.Size / 1GB, 2)) GB, Free $([math]::Round($_.SizeRemaining / 1GB, 2)) GB ($percentFree% free)" -ForegroundColor $(if ($percentFree -lt 15) { 'Red' } elseif ($percentFree -lt 30) { 'DarkYellow' } else { 'Green' })
}

Write-Host "" # Add an empty line for better spacing

# --- Display Network Interface Details ---
Write-Host "--- Network Interfaces ---" -ForegroundColor Cyan
Get-NetAdapter -Physical | ForEach-Object {
    $ipAddresses = (Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue).IPAddress
    $macAddress = $_.MacAddress # Get MAC address
    $speedGBPS = [math]::Round($_.LinkSpeed / 1Gb, 2) # Convert LinkSpeed to GBps

    $ipString = if ($ipAddresses) { $ipAddresses -join ', ' } else { "<none>" }

    Write-Host "  Name: $($_.Name)" -ForegroundColor Green
    Write-Host "    Status: $($_.Status) - Link Speed: $speedGBPS Gbps" -ForegroundColor Yellow
    Write-Host "    MAC Address: $macAddress" -ForegroundColor Yellow
    Write-Host "    IPv4: $ipString" -ForegroundColor Yellow
}

Write-Host "" # Add an empty line for better spacing

# --- Display BIOS/Firmware Information ---
Write-Host "--- BIOS Information ---" -ForegroundColor Cyan
$bios = Get-InfoSafe { Get-CimInstance Win32_BIOS }
if ($bios) {
    Write-Host "  Version: $($bios.SMBIOSBIOSVersion)" -ForegroundColor Yellow
    Write-Host "  Manufacturer: $($bios.Manufacturer)" -ForegroundColor Yellow
    Write-Host "  Release Date: $($bios.ReleaseDate)" -ForegroundColor Yellow
}
else {
    Write-Host "  BIOS Information: <unavailable>" -ForegroundColor DarkYellow
}

Write-Host "" # Add an empty line for better spacing

# --- Display Recently Installed Updates (Last 5) ---
Write-Host "--- Recent Windows Updates ---" -ForegroundColor Cyan
$hotfixes = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5
if ($hotfixes.Count -gt 0) {
    $hotfixes | ForEach-Object {
        Write-Host "  $($_.HotFixID) - $($_.Description) - $($_.InstalledOn.ToShortDateString())" -ForegroundColor Green
    }
}
else {
    Write-Host "  No recent updates found." -ForegroundColor DarkYellow
}

Write-Host "" # Add an empty line for better spacing

# --- Display Running Processes Count ---
Write-Host "Running Processes: $((Get-Process).Count)" -ForegroundColor Magenta

# --- Dashboard Footer ---
Write-Host "" # Add an empty line for better spacing
Write-Host "================================`n" -ForegroundColor Cyan
Read-Host "Press Enter to exit"