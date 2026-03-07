Write-Host "Hi $env:USERNAME! Welcome to PowerShell scripting."
Write-Host "Your Pc Name is $env:COMPUTERNAME and your OS is $env:OS.Version:"
$source = Read-Host "Enter source folder"
$dest = Read-Host "Enter backup folder"

Copy-Item $source $dest -Recurse
Write-Host "Backup completed!"
$number = Get-Random -Minimum 1 -Maximum 10
$guess = Read-Host "Guess a number between 1 and 10"

if ($guess -eq $number) {
    Write-Host "Correct!"
}
else {
    Write-Host "Wrong. The number was $number"
}


Read-Host "Press Enter to exit"