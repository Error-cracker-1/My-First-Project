# Welcome and System Information
Write-Host "Hi $env:USERNAME! Welcome to PowerShell scripting."

# Display PC name and the actual operating system name.
# The `Get-CimInstance Win32_OperatingSystem` cmdlet retrieves detailed OS information.
# Fixed: Added backtick to ensure `n` is interpreted as a newline character.
Write-Host "Your PC Name is $env:COMPUTERNAME and your OS is $(Get-CimInstance Win32_OperatingSystem).Caption`n"

# File Backup Section
# Prompts the user for source and destination paths for a folder backup.
$sourcePath = Read-Host "Please enter the path to the source folder:"
$destinationPath = Read-Host "Please enter the path to the backup destination folder:"

# Attempt to copy items recursively and provide feedback on success or failure.
try {
    Copy-Item -Path $sourcePath -Destination $destinationPath -Recurse -ErrorAction Stop
    Write-Host "Backup completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Backup failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" # Add a newline for spacing before the next section.

# Number Guessing Game Section
# Generates a random number between 1 and 10 for the user to guess.
$randomNumber = Get-Random -Minimum 1 -Maximum 10
$userGuess = Read-Host "Guess a number between 1 and 10"

# Compares the user's guess to the random number.
# PowerShell's -eq operator implicitly handles type conversion for comparison.
if ($userGuess -eq $randomNumber) {
    Write-Host "Correct!" -ForegroundColor Green
}
else {
    Write-Host "Wrong. The number was $randomNumber." -ForegroundColor Red
}

Write-Host "`n" # Add a newline for spacing before the exit prompt.

# Pause script execution until user input to keep the console window open.
Read-Host "Press Enter to exit"