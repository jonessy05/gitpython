<#
.SYNOPSIS
  Build and deploy the reservations backend into a local kind cluster (Windows PowerShell)
.DESCRIPTION
  Builds an image with Podman, saves and loads it into kind, applies kustomize, restarts deployment
.NOTES
  Requires: podman, kind, kubectl in PATH. Compatible with Windows PowerShell / PowerShell 5.1.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Run-Cmd {
    param(
        [string]$Cmd,
        [string]$ErrorMsg
    )
    Write-Host "Running: $Cmd" -ForegroundColor Yellow
    iex $Cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host $ErrorMsg -ForegroundColor Red
        throw "Command failed: $Cmd"
    }
}

Push-Location -Path $PSScriptRoot
Write-Host "Working directory: $PWD" -ForegroundColor Cyan

# 1) Build the image
Write-Host '[1/6] Building image...' -ForegroundColor Cyan
Run-Cmd -Cmd 'podman build -t localhost/reservations-backend:local-dev .' -ErrorMsg 'ERROR: podman build failed.'
Write-Host '[1/6] Image built.' -ForegroundColor Green

# 2) Save image archive
Write-Host '[2/6] Saving image to reservations-backend.tar...' -ForegroundColor Cyan
Run-Cmd -Cmd 'podman save localhost/reservations-backend:local-dev --format oci-archive -o reservations-backend.tar' -ErrorMsg 'ERROR: podman save failed.'
Write-Host '[2/6] Image saved.' -ForegroundColor Green

# 3) Load into kind
Write-Host '[3/6] Loading image into kind cluster...' -ForegroundColor Cyan
Run-Cmd -Cmd 'kind load image-archive reservations-backend.tar -n kind-cluster' -ErrorMsg 'ERROR: kind load failed.'
Write-Host '[3/6] Image loaded into kind.' -ForegroundColor Green

# 4) Apply kustomize
Write-Host '[4/6] Applying kustomize...' -ForegroundColor Cyan
Run-Cmd -Cmd 'kubectl apply -k . --prune -l app.kubernetes.io/part-of=biletado -n biletado' -ErrorMsg 'ERROR: kubectl apply failed.'
Write-Host '[4/6] Kustomize applied.' -ForegroundColor Green

# 5) Restart deployment
Write-Host '[5/6] Restarting reservations deployment...' -ForegroundColor Cyan
Run-Cmd -Cmd 'kubectl rollout restart deployment reservations -n biletado' -ErrorMsg 'ERROR: rollout restart failed.'
Write-Host '[5/6] Deployment restarted.' -ForegroundColor Green

# 6) Wait for pods
Write-Host '[6/6] Waiting for pods to become Ready (120s)...' -ForegroundColor Cyan
$waitCmd = 'kubectl wait pods -n biletado -l app.kubernetes.io/component=backend --for condition=Ready --timeout=120s'
try {
    iex $waitCmd
} catch {
    Write-Host 'WARNING: pods did not become ready in time or kubectl wait failed.' -ForegroundColor Yellow
    Write-Host 'You can check logs with: kubectl logs deployment/reservations -n biletado --tail=100' -ForegroundColor Gray
    throw
}

Write-Host '✓ Pods are Ready.' -ForegroundColor Green

Write-Host ''
Write-Host 'Deployment finished. Helpful commands:' -ForegroundColor Cyan
Write-Host '  kubectl logs deployment/reservations -n biletado -f' -ForegroundColor Gray
Write-Host '  kubectl port-forward -n biletado deployment/reservations 8000:8000' -ForegroundColor Gray
Write-Host "  Access proxied API via: http://localhost:9090/api/v3/reservations/status" -ForegroundColor Gray

Pop-Location
