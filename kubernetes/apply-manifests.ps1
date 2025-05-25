# PowerShell script to apply Kubernetes manifests
# First, ensure authentication is set up
& "C:\Users\Lenovo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" container clusters get-credentials minitasks-cluster --region=us-central1 --project=cs436-minitasks

# Add gcloud to PATH
$env:PATH += ";C:\Users\Lenovo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# Apply Kubernetes manifests with validation turned off
Write-Host "Applying PersistentVolumeClaim..." -ForegroundColor Green
kubectl apply -f kubernetes/persistent-volume-claim.yaml --validate=false

Write-Host "Applying Deployment..." -ForegroundColor Green
kubectl apply -f kubernetes/deployment.yaml --validate=false

Write-Host "Applying Service..." -ForegroundColor Green
kubectl apply -f kubernetes/service.yaml --validate=false

Write-Host "Applying HorizontalPodAutoscaler..." -ForegroundColor Green
kubectl apply -f kubernetes/hpa.yaml --validate=false

Write-Host "All manifests applied!" -ForegroundColor Green 