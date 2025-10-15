#!/bin/bash
# Script de gestión del sistema FADE Financiación
# Uso: ./gestionar.sh [comando]

cd ~/fade-financiacion-lite

function mostrar_menu() {
    echo "================================================"
    echo "   FADE - Gestión del Sistema de Financiación"
    echo "================================================"
    echo ""
    echo "Selecciona una opción:"
    echo ""
    echo "1) Ver estado de los servicios"
    echo "2) Ver logs de la aplicación"
    echo "3) Reiniciar la aplicación"
    echo "4) Actualizar desde GitHub"
    echo "5) Hacer backup de datos"
    echo "6) Restaurar backup"
    echo "7) Ver uso de recursos"
    echo "8) Parar todos los servicios"
    echo "9) Iniciar todos los servicios"
    echo "0) Salir"
    echo ""
    read -p "Opción: " opcion
    
    case $opcion in
        1) ver_estado ;;
        2) ver_logs ;;
        3) reiniciar_app ;;
        4) actualizar_github ;;
        5) hacer_backup ;;
        6) restaurar_backup ;;
        7) ver_recursos ;;
        8) parar_servicios ;;
        9) iniciar_servicios ;;
        0) exit 0 ;;
        *) echo "Opción no válida"; sleep 2; mostrar_menu ;;
    esac
}

function ver_estado() {
    echo ""
    echo "📊 Estado de los servicios:"
    echo "=========================="
    docker compose ps
    echo ""
    read -p "Presiona Enter para continuar..."
    mostrar_menu
}

function ver_logs() {
    echo ""
    echo "📋 Últimos logs de la aplicación:"
    echo "================================="
    docker compose logs flask-app --tail=50
    echo ""
    read -p "Presiona Enter para continuar..."
    mostrar_menu
}

function reiniciar_app() {
    echo ""
    echo "🔄 Reiniciando la aplicación..."
    docker compose restart flask-app
    echo "✅ Aplicación reiniciada"
    sleep 2
    mostrar_menu
}

function actualizar_github() {
    echo ""
    echo "📥 Actualizando desde GitHub..."
    echo "==============================="
    
    # Guardar cambios locales si los hay
    if [[ -n $(git status -s) ]]; then
        echo "⚠️  Hay cambios locales. Guardando backup..."
        git stash
    fi
    
    # Actualizar
    git pull origin main
    
    echo ""
    echo "🔨 Reconstruyendo contenedores..."
    docker compose down
    docker compose build flask-app
    docker compose up -d
    
    echo "✅ Actualización completada"
    sleep 3
    mostrar_menu
}

function hacer_backup() {
    echo ""
    echo "💾 Creando backup..."
    echo "==================="
    
    FECHA=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="backups"
    mkdir -p $BACKUP_DIR
    
    # Backup del JSON de programas
    cp data/programas_financiacion.json "$BACKUP_DIR/programas_$FECHA.json"
    
    # Backup de la configuración
    cp .env "$BACKUP_DIR/env_$FECHA.txt" 2>/dev/null
    
    echo "✅ Backup creado en: $BACKUP_DIR/programas_$FECHA.json"
    echo ""
    read -p "Presiona Enter para continuar..."
    mostrar_menu
}

function restaurar_backup() {
    echo ""
    echo "📂 Backups disponibles:"
    echo "======================"
    ls -lh backups/*.json 2>/dev/null || echo "No hay backups disponibles"
    echo ""
    read -p "Nombre del archivo a restaurar (o Enter para cancelar): " archivo
    
    if [ -n "$archivo" ]; then
        if [ -f "backups/$archivo" ]; then
            cp "backups/$archivo" data/programas_financiacion.json
            chmod 666 data/programas_financiacion.json
            echo "✅ Backup restaurado"
            docker compose restart flask-app
        else
            echo "❌ Archivo no encontrado"
        fi
    fi
    
    sleep 2
    mostrar_menu
}

function ver_recursos() {
    echo ""
    echo "💻 Uso de recursos del servidor:"
    echo "================================"
    echo ""
    echo "CPU y Memoria:"
    top -bn1 | head -5
    echo ""
    echo "Espacio en disco:"
    df -h /
    echo ""
    echo "Memoria Docker:"
    docker stats --no-stream
    echo ""
    read -p "Presiona Enter para continuar..."
    mostrar_menu
}

function parar_servicios() {
    echo ""
    echo "⏹️  Parando todos los servicios..."
    docker compose down
    echo "✅ Servicios detenidos"
    sleep 2
    mostrar_menu
}

function iniciar_servicios() {
    echo ""
    echo "▶️  Iniciando servicios..."
    docker compose up -d
    echo "✅ Servicios iniciados"
    sleep 2
    mostrar_menu
}

# Iniciar el menú
mostrar_menu
