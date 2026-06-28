# Welcome and System Information
Write-Host "Hi $env:USERNAME! Welcome to PowerShell scripting."
# Corrected OS version display to show actual operating system name.
Write-Host "Your PC Name is $env:COMPUTERNAME and your OS is $(Get-CimInstance Win32_OperatingSystem).Caption`n"

# File Backup Section
$source = Read-Host "Please enter the path to the source folder:"
$dest = Read-Host "Please enter the path to the backup destination folder:"

# Attempt to copy items and provide feedback on success or failure.
try {
    Copy-Item -Path $source -Destination $dest -Recurse -ErrorAction Stop
    Write-Host "Backup completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Backup failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" # Add a newline for spacing before the next section

# Number Guessing Game Section
$number = Get-Random -Minimum 1 -Maximum 10
$guess = Read-Host "Guess a number between 1 and 10"

# Compare the user's guess to the random number.
# PowerShell's -eq operator can implicitly convert strings to numbers for comparison.
if ($guess -eq $number) {
    Write-Host "Correct!" -ForegroundColor Green
}
else {
    Write-Host "Wrong. The number was $number." -ForegroundColor Red
}

Write-Host "`n" # Add a newline for spacing before the exit prompt

# Pause script execution until user input to keep the console window open.
Read-Host "Press Enter to exit"