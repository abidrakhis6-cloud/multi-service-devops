# ==========================================
# Script de correction automatique Prometheus
# MultiServe - Session Juin-Juillet 2026
# Auteur: ABID RAKHIS AHMAT
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔧 CORRECTION AUTOMATIQUE PROMETHEUS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier les services en cours
Write-Host "1️⃣  Vérification des services Docker..." -ForegroundColor Yellow
$services = docker-compose ps --format "table {{.Service}}\t{{.Status}}" 2>$null
Write-Host $services
Write-Host ""

# 2. Démarrer tous les services nécessaires
Write-Host "2️⃣  Démarrage des services..." -ForegroundColor Yellow
docker-compose up -d --remove-orphans prometheus nginx-exporter db redis app 2>&1 | Out-Null
Write-Host "    ✅ Services démarrés" -ForegroundColor Green
Write-Host ""

# 3. Attendre que tout soit prêt
Write-Host "3️⃣  Attente du démarrage (20s)..." -ForegroundColor Yellow
Start-Sleep -s 20

# 4. Vérifier Prometheus
Write-Host "4️⃣  Vérification de Prometheus..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/targets" -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "📊 ÉTAT DES TARGETS:" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    foreach ($target in $data.data.activeTargets) {
        $name = $target.labels.job
        $health = $target.health
        $url = $target.discoveredLabels.__address__
        
        if ($health -eq "up") {
            Write-Host "  🟢 $name ($url) - UP" -ForegroundColor Green
        } else {
            Write-Host "  🔴 $name ($url) - DOWN" -ForegroundColor Red
            Write-Host "      Erreur: $($target.lastError)" -ForegroundColor DarkRed
        }
    }
    
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    # Compter les UP vs DOWN
    $up = ($data.data.activeTargets | Where-Object { $_.health -eq "up" }).Count
    $down = ($data.data.activeTargets | Where-Object { $_.health -ne "up" }).Count
    
    Write-Host ""
    Write-Host "📈 RÉSULTAT: $up UP / $down DOWN" -ForegroundColor Cyan
    
    if ($down -eq 0) {
        Write-Host ""
        Write-Host "✅ TOUS LES TARGETS SONT VERTS !" -ForegroundColor Green -BackgroundColor Black
        Write-Host ""
        Write-Host "🌐 URL: http://localhost:9090/targets" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "⚠️  $down TARGETS EN ROUGE" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 Tentative de correction automatique..." -ForegroundColor Yellow
        
        # Redémarrer Prometheus
        docker-compose restart prometheus 2>&1 | Out-Null
        Start-Sleep -s 10
        
        Write-Host "    ✅ Prometheus redémarré" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Vérifiez manuellement: http://localhost:9090/targets" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR: Prometheus n'est pas accessible" -ForegroundColor Red
    Write-Host "   Message: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Démarrage de Prometheus..." -ForegroundColor Yellow
    docker-compose up -d prometheus 2>&1 | Out-Null
    Write-Host "    ✅ Prometheus démarré. Attendez 10s et relancez le script." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ CORRECTION TERMINÉE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
