Write-Host "Hello, World!"
$name = "Kumar"
$age  = 30
Write-Host "Name: $name, Age: $age"
$greeting = "Hello, $name! You are $age years old."
Write-Host $greeting
$sum = 5 + 10
Write-Host "The sum of 5 and 10 is: $sum"
$numbers = @(1, 2, 3, 4, 5)
Write-Host "Numbers: $($numbers -join ', ')"
$today = Get-Date
Write-Host "Today's date is: $today"
$randomNumber = Get-Random -Minimum 1 -Maximum 100
Write-Host "Random number between 1 and 100: $randomNumber"
$greetingFunction = {
    param($name)
    return "Hello, $name!"
}
$result = & $greetingFunction -name "Kumar"
Write-Host $result  # Output: Hello, Kumar!

