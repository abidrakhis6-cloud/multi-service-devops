# ==========================================
# Script de vérification pour Max
# MultiServe - Points 3, 5, 6, 7
# ==========================================

Write-Host "==========================================" -ForegroundColor Green
Write-Host "🔍 VÉRIFICATION DES POINTS POUR MAX" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Point 3 - Services + Monitoring
Write-Host "📊 POINT 3 - Services + Monitoring connectés" -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor Cyan
$compose = Get-Content docker-compose.yml -Raw
$checks = @{
    "Prometheus" = $compose -match "prometheus"
    "Postgres Exporter" = $compose -match "postgres.?exporter|pgexporter"
    "Redis Exporter" = $compose -match "redis.?exporter"
    "Nginx Exporter" = $compose -match "nginx.?exporter"
    "Grafana" = $compose -match "grafana"
    "Alertmanager" = $compose -match "alertmanager"
}
$checks.GetEnumerator() | ForEach-Object {
    $status = if ($_.Value) { "✅ OK" } else { "❌ MANQUANT" }
    Write-Host "  $($_.Key): $status"
}
Write-Host ""

# Point 5 - Alertmanager config
Write-Host "🔔 POINT 5 - Test alerts bout en bout" -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor Cyan
if (Test-Path "monitoring/alertmanager/config.yml") {
    Write-Host "  ✅ Config alertmanager: EXISTE"
    $alerts = Get-Content monitoring/alertmanager/config.yml -Raw
    if ($alerts -match "slack|pagerduty|webhook|email") {
        Write-Host "  ✅ Canaux de notification configurés"
    } else {
        Write-Host "  ⚠️  Aucun canal de notification trouvé"
    }
} elseif (Test-Path "monitoring/alertmanager/alertmanager.yml") {
    Write-Host "  ✅ Config alertmanager: EXISTE (alertmanager.yml)"
} else {
    Write-Host "  ❌ Config alertmanager: MANQUANT"
}
if (Test-Path "monitoring/prometheus/rules/alerts.yml") {
    Write-Host "  ✅ Règles d'alertes Prometheus: EXISTENT"
} else {
    Write-Host "  ❌ Règles d'alertes: MANQUANTES"
}
Write-Host ""

# Point 6 - Branches Git
Write-Host "🌿 POINT 6 - Nettoyage branches Git" -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor Cyan
Write-Host "Branches locales:"
git branch
Write-Host ""
Write-Host "Branches distantes:"
git branch -r
Write-Host ""
Write-Host "⚠️  Branches à nettoyer potentielles:"
$branches = git branch -a
@("develop", "feature/images", "hotfix/pharmacy-images", "master", "staging") | ForEach-Object {
    if ($branches -match $_) {
        Write-Host "  - $_ existe"
    }
}
Write-Host ""

# Point 7 - EKS CIDRs et Secrets
Write-Host "🔒 POINT 7 - EKS CIDRs + Secrets Django" -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor Cyan
if (Test-Path "terraform/eks.tf") {
    $eks = Get-Content terraform/eks.tf -Raw
    if ($eks -match "public_access_cidrs|endpoint_public_access") {
        Write-Host "  ✅ CIDRs EKS configurés"
    } else {
        Write-Host "  ⚠️  CIDRs EKS non trouvés"
    }
} else {
    Write-Host "  ❌ terraform/eks.tf: MANQUANT"
}
if (Test-Path ".env.example") {
    $env = Get-Content .env.example -Raw
    if ($env -match "SECRET_KEY.*CHANGE" -or $env -match "SECRET_KEY.*your-secret") {
        Write-Host "  ⚠️  SECRET_KEY par défaut trouvé - doit être changé en prod!"
    } else {
        Write-Host "  ✅ SECRET_KEY semble configuré"
    }
} else {
    Write-Host "  ❌ .env.example: MANQUANT"
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ VÉRIFICATION TERMINÉE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
