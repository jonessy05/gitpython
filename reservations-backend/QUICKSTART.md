# Schnellstart-Anleitung: Reservierungen Backend

## 🚀 Schnellstart (lokal mit Docker)

```powershell
# 1. Backend bauen
cd c:\gitpython\reservations-backend
podman build -t reservations-backend:latest .

# 2. Container starten
podman run -d -p 8000:80 --name reservations-api reservations-backend:latest

# 3. API testen
# Öffne im Browser: http://localhost:8000/docs

# 4. Token generieren (in PowerShell)
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/token?username=testuser" -Method POST
$token = $response.access_token

# 5. Reservierungen abrufen
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/reservations" -Headers $headers
```

## ☸️ Kubernetes Deployment (kind)

### Voraussetzung: kind Cluster

```powershell
# kind Cluster erstellen (falls noch nicht vorhanden)
kind create cluster --name kind-cluster

# Namespace erstellen
kubectl create namespace biletado
kubectl config set-context --current --namespace biletado
```

### Backend deployen

```powershell
cd c:\gitpython\reservations-backend

# 1. Image bauen
podman build -t reservations-backend:latest .

# 2. Image in kind Cluster laden
podman save reservations-backend:latest --format oci-archive -o reservations-backend.tar
kind load image-archive reservations-backend.tar -n kind-cluster

# 3. Mit Kustomize deployen
kubectl apply -k k8s -n biletado

# 4. Warten bis Pods bereit sind
kubectl wait pods -n biletado -l app=reservations-backend --for condition=Ready --timeout=120s

# 5. Status prüfen
kubectl get pods -n biletado -l app=reservations-backend
kubectl get svc -n biletado reservations-backend
```

### API testen (in Kubernetes)

```powershell
# Port-Forwarding einrichten
kubectl port-forward -n biletado service/reservations-backend 8000:8000

# In neuem Terminal/Tab: API testen
# Token generieren
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/token?username=k8suser" -Method POST
$token = $response.access_token

# Reservierungen abrufen
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/reservations" -Headers $headers

# Neue Reservierung erstellen
$body = @{
    customer_name = "Anna Schmidt"
    customer_email = "anna@example.com"
    reservation_date = "2025-12-31T19:00:00Z"
    party_size = 6
    special_requests = "Vegetarisches Menü"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/reservations" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

## 🔄 Nach Code-Änderungen neu deployen

```powershell
cd c:\gitpython\reservations-backend

# Schnell-Update Script
$TAG = "reservations-backend:latest"
podman build -t $TAG .
podman save $TAG --format oci-archive -o reservations-backend.tar
kind load image-archive reservations-backend.tar -n kind-cluster
kubectl rollout restart deployment reservations-backend -n biletado
kubectl rollout status deployment reservations-backend -n biletado
```

## 🧹 Aufräumen

```powershell
# Deployment löschen
kubectl delete -k k8s -n biletado

# Container stoppen (lokal)
podman stop reservations-api
podman rm reservations-api

# kind Cluster löschen (optional)
kind delete cluster --name kind-cluster
```

## 📊 Nützliche Befehle

```powershell
# Logs anzeigen
kubectl logs -n biletado -l app=reservations-backend --tail=50 -f

# In Pod einsteigen
kubectl exec -it -n biletado deployment/reservations-backend -- /bin/bash

# Pods beschreiben
kubectl describe pod -n biletado -l app=reservations-backend

# Service Endpoints anzeigen
kubectl get endpoints -n biletado reservations-backend
```
