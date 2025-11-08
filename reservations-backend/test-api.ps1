# Test-Skript für Reservierungen Backend API
# PowerShell Script zum Testen aller Endpoints

Write-Host "Test Suite - Reservierungen API" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# 1. Health Check
Write-Host "1. Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "[OK] Health Check: $($health.status)" -ForegroundColor Green
    Write-Host "   Timestamp: $($health.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Health Check failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Root Endpoint
Write-Host "2. Testing Root Endpoint..." -ForegroundColor Yellow
try {
    $root = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Write-Host "[OK] Root: $($root.message)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Root endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# 3. Generate Token
Write-Host "3. Generating JWT Token..." -ForegroundColor Yellow
try {
    $tokenResponse = Invoke-RestMethod -Uri "$baseUrl/auth/token?username=testuser" -Method POST
    $token = $tokenResponse.access_token
    Write-Host "[OK] Token generated successfully" -ForegroundColor Green
    Write-Host "   Type: $($tokenResponse.token_type)" -ForegroundColor Gray
    Write-Host "   Expires in: $($tokenResponse.expires_in) seconds" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Token generation failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Headers mit Token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 4. Get All Reservations (initial)
Write-Host "4. Getting all reservations (initial)..." -ForegroundColor Yellow
try {
    $reservations = Invoke-RestMethod -Uri "$baseUrl/reservations/" -Method GET -Headers $headers
    Write-Host "[OK] Found $($reservations.Count) reservation(s)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Get reservations failed: $_" -ForegroundColor Red
}
Write-Host ""

# 5. Create New Reservation
Write-Host "5. Creating new reservation..." -ForegroundColor Yellow
$newReservation = @{
    customer_name = "Max Mustermann"
    customer_email = "max@example.com"
    reservation_date = (Get-Date).AddDays(7).ToString("yyyy-MM-ddTHH:mm:ssZ")
    party_size = 4
    special_requests = "Fensterplatz bitte"
} | ConvertTo-Json

try {
    $created = Invoke-RestMethod -Uri "$baseUrl/reservations/" -Method POST -Headers $headers -Body $newReservation
    $newId = $created.id
    Write-Host "[OK] Reservation created successfully" -ForegroundColor Green
    Write-Host "   ID: $($created.id)" -ForegroundColor Gray
    Write-Host "   Customer: $($created.customer_name)" -ForegroundColor Gray
    Write-Host "   Status: $($created.status)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Create reservation failed: $_" -ForegroundColor Red
    $newId = 1
}
Write-Host ""

# 6. Get Single Reservation
Write-Host "6. Getting single reservation (ID: $newId)..." -ForegroundColor Yellow
try {
    $single = Invoke-RestMethod -Uri "$baseUrl/reservations/$newId" -Method GET -Headers $headers
    Write-Host "[OK] Reservation retrieved" -ForegroundColor Green
    Write-Host "   Customer: $($single.customer_name)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Get single reservation failed: $_" -ForegroundColor Red
}
Write-Host ""

# 7. Update Reservation
Write-Host "7. Updating reservation..." -ForegroundColor Yellow
$updateData = @{
    customer_name = "Max Mustermann"
    customer_email = "max.mustermann@example.com"
    reservation_date = (Get-Date).AddDays(7).ToString("yyyy-MM-ddTHH:mm:ssZ")
    party_size = 6
    special_requests = "Vegetarisches Menü"
} | ConvertTo-Json

try {
    $updated = Invoke-RestMethod -Uri "$baseUrl/reservations/$newId" -Method PUT -Headers $headers -Body $updateData
    Write-Host "[OK] Reservation updated" -ForegroundColor Green
    Write-Host "   Party Size: $($updated.party_size)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Update reservation failed: $_" -ForegroundColor Red
}
Write-Host ""

# 8. Update Status
Write-Host "8. Updating status to confirmed..." -ForegroundColor Yellow
try {
    $statusUpdate = Invoke-RestMethod -Uri "$baseUrl/reservations/$newId/status?new_status=confirmed" -Method PATCH -Headers $headers
    Write-Host "[OK] Status updated to: $($statusUpdate.status)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Status update failed: $_" -ForegroundColor Red
}
Write-Host ""

# 9. Test Invalid Token
Write-Host "9. Testing with invalid token..." -ForegroundColor Yellow
$badHeaders = @{
    "Authorization" = "Bearer invalid-token"
}
try {
    Invoke-RestMethod -Uri "$baseUrl/reservations/" -Method GET -Headers $badHeaders
    Write-Host "[FAIL] Should have rejected invalid token!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Write-Host "[OK] Invalid token correctly rejected (401)" -ForegroundColor Green
    }
}
Write-Host ""

# 10. Delete Reservation
Write-Host "10. Deleting reservation..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/reservations/$newId" -Method DELETE -Headers $headers
    Write-Host "[OK] Reservation deleted" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Delete failed: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "All tests completed!" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
