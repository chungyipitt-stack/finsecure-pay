<#
.SYNOPSIS
  Generates FinSecure Pay traffic. Use -RejectRatio 0.8 to deliberately trigger
  the FinSecurePayHighRejectionRate alert (> 50% rejected for 1 minute).

.EXAMPLE
  .\scripts\load-test.ps1 -BaseUrl http://<elb-host> -ApiKey $env:FINSECURE_API_KEY -DurationSeconds 300 -RejectRatio 0.8
#>
param(
    [Parameter(Mandatory = $true)] [string] $BaseUrl,
    [string] $ApiKey = "",
    [int]    $DurationSeconds = 180,
    [double] $RejectRatio = 0.2,
    [int]    $RequestsPerSecond = 5
)

$headers = @{ "Content-Type" = "application/json" }
if ($ApiKey) { $headers["X-API-Key"] = $ApiKey }

$end = (Get-Date).AddSeconds($DurationSeconds)
$stats = @{ approved = 0; rejected = 0; error = 0 }
$i = 0
Write-Host "Sending traffic to $BaseUrl/validate for $DurationSeconds s (reject ratio $RejectRatio)..."

while ((Get-Date) -lt $end) {
    for ($n = 0; $n -lt $RequestsPerSecond; $n++) {
        $i++
        $reject = (Get-Random -Minimum 0.0 -Maximum 1.0) -lt $RejectRatio
        $body = if ($reject) {
            # Exceeds limit + unsupported currency -> REJECTED
            @{ transactionId = "TXN-LOAD-$i"; sourceAccount = "1234567890"; destinationAccount = "9876543210";
               amount = 25000.00; currency = "JPY" }
        } else {
            @{ transactionId = "TXN-LOAD-$i"; sourceAccount = "1234567890"; destinationAccount = "9876543210";
               amount = [math]::Round((Get-Random -Minimum 1 -Maximum 9000) + 0.5, 2); currency = "SGD" }
        }
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$BaseUrl/validate" -Headers $headers `
                 -Body ($body | ConvertTo-Json) -TimeoutSec 5
            $stats.approved++
        } catch {
            if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 422) { $stats.rejected++ }
            else { $stats.error++ }
        }
    }
    Write-Host ("`r approved={0} rejected={1} errors={2}" -f $stats.approved, $stats.rejected, $stats.error) -NoNewline
    Start-Sleep -Seconds 1
}
Write-Host "`nDone."
