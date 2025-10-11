# Script PowerShell para copiar archivos del monolito al proyecto lite
# Ejecutar desde: C:\Users\aleja

Write-Host "=== COPIANDO ARCHIVOS DEL MONOLITO AL PROYECTO LITE ===" -ForegroundColor Green

# Definir rutas
$origen = "C:\Users\aleja\herramienta_deducciones"
$destino = "C:\Users\aleja\fade-financiacion-lite"

# 1. Copiar Templates (3 archivos)
Write-Host "`n1. Copiando templates..." -ForegroundColor Yellow
Copy-Item "$origen\templates\financiacion_dashboard.html" "$destino\templates\" -Force
Copy-Item "$origen\templates\financiacion_gestionar.html" "$destino\templates\" -Force
Copy-Item "$origen\templates\financiacion_adecuacion.html" "$destino\templates\" -Force
Write-Host "   ✓ Templates copiados" -ForegroundColor Green

# 2. Copiar Utils (5 archivos)
Write-Host "`n2. Copiando utils..." -ForegroundColor Yellow
Copy-Item "$origen\utils\financing_dashboard.py" "$destino\utils\" -Force
Copy-Item "$origen\utils\convocatoria_extractor_updated.py" "$destino\utils\" -Force
Copy-Item "$origen\utils\bdns_scraper.py" "$destino\utils\" -Force
Copy-Item "$origen\utils\compatibility_analyzer.py" "$destino\utils\" -Force
Copy-Item "$origen\utils\pdf_processor.py" "$destino\utils\" -Force
Write-Host "   ✓ Utils copiados" -ForegroundColor Green

# 3. Copiar Static (carpeta completa)
Write-Host "`n3. Copiando static..." -ForegroundColor Yellow
if (Test-Path "$destino\static") {
    Remove-Item "$destino\static\*" -Recurse -Force
}
Copy-Item "$origen\static\*" "$destino\static\" -Recurse -Force
Write-Host "   ✓ Static copiado" -ForegroundColor Green

# 4. Copiar Data
Write-Host "`n4. Copiando data..." -ForegroundColor Yellow
Copy-Item "$origen\data\programas_financiacion.json" "$destino\data\" -Force
Write-Host "   ✓ Data copiado" -ForegroundColor Green

Write-Host "`n=== COPIA COMPLETADA ===" -ForegroundColor Green
Write-Host "Archivos copiados exitosamente de:" -ForegroundColor Cyan
Write-Host "  $origen" -ForegroundColor Cyan
Write-Host "A:" -ForegroundColor Cyan
Write-Host "  $destino" -ForegroundColor Cyan

Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
Write-Host "1. Revisa INSTRUCCIONES.md para las adaptaciones necesarias"
Write-Host "2. Crea el archivo .env con tus variables"
Write-Host "3. Adapta bdns_scraper.py y convocatoria_extractor_updated.py"

Read-Host "`nPresiona Enter para cerrar"
