Write-Host "=== Welcome Program ==="

$name = Read-Host "Enter your name"
$age = Read-Host "Enter your age"

if ([int]$age -ge 18) {
    Write-Host "Hello $name, you are an Adult."
}
else {
    Write-Host "Hello $name, you are a Minor."
}

Write-Host "Today's Date:"
Get-Date

Read-Host "Press Enter to exit"