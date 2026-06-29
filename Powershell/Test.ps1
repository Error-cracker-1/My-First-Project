# Script: Test.ps1
# Description: A simple PowerShell program to greet the user, determine age status, and display the current date.

Write-Host "=== Welcome Program ==="
Write-Host ""

# Prompt user for their name
$name = Read-Host "Enter your name"

# Prompt user for their age
$ageInput = Read-Host "Enter your age"

# Attempt to convert age input to an integer and determine age status
try {
    $age = [int]$ageInput
    if ($age -ge 18) {
        Write-Host "Hello $name, you are an Adult."
    }
    else {
        Write-Host "Hello $name, you are a Minor."
    }
}
catch {
    # Handle cases where the age input is not a valid number
    Write-Host "Hello $name. The age you entered ('$ageInput') is not a valid number. Unable to determine if you are an Adult or Minor."
}

Write-Host ""
Write-Host "Today's Date:"
Get-Date

Write-Host ""
# Keep the console window open until the user presses Enter
Read-Host "Press Enter to exit"