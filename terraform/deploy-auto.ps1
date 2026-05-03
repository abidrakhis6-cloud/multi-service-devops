# ==========================================
# Script de Déploiement Automatique Complet
# MultiServe sur AWS EC2
# ==========================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "🚀 DÉPLOIEMENT AUTOMATIQUE MULTISERVE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Vérifier Terraform
if (-not (Test-Path ".\terraform.exe")) {
    Write-Host "📥 Téléchargement de Terraform..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://releases.hashicorp.com/terraform/1.7.4/terraform_1.7.4_windows_amd64.zip" -OutFile "terraform.zip"
    Expand-Archive -Path "terraform.zip" -DestinationPath "." -Force
    Remove-Item terraform.zip
    Write-Host "✅ Terraform installé" -ForegroundColor Green
}

# Initialiser Terraform
Write-Host ""
Write-Host "🔧 Initialisation de Terraform..." -ForegroundColor Yellow
.\terraform.exe init

# Plan
Write-Host ""
Write-Host "📋 Planification du déploiement..." -ForegroundColor Yellow
.\terraform.exe plan -out=tfplan

# Appliquer
Write-Host ""
Write-Host "🚀 LANCEMENT DU DÉPLOIEMENT..." -ForegroundColor Green
$confirm = Read-Host "Confirmer le déploiement? (oui/non)"

if ($confirm -eq "oui" -or $confirm -eq "o" -or $confirm -eq "yes" -or $confirm -eq "y") {
    .\terraform.exe apply -auto-approve tfplan
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ DÉPLOIEMENT INITIÉ !" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ Attendre 5-10 minutes que l'installation se termine..." -ForegroundColor Yellow
    Write-Host ""
    
    # Afficher les outputs
    .\terraform.exe output
} else {
    Write-Host "❌ Déploiement annulé" -ForegroundColor Red
}

Write-Host ""
Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
