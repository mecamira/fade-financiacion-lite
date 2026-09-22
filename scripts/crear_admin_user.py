#!/usr/bin/env python3
"""
Crea o actualiza un usuario administrador con contraseña hasheada.

Uso (dentro del contenedor, para que escriba en el volumen correcto):

    docker compose exec flask-app python scripts/crear_admin_user.py

También sirve para listar o borrar usuarios existentes.
La contraseña se pide con getpass: no se muestra en pantalla ni queda
en el historial de la terminal.
"""

import sys
import os
import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import admin_auth


def listar():
    users = admin_auth.load_users()
    if not users:
        print("No hay usuarios admin configurados todavía.")
        return
    print(f"\nUsuarios admin configurados ({len(users)}):")
    for username, data in users.items():
        print(f"  - {username}  (nombre: {data.get('nombre', username)})")
    print()


def crear():
    username = input("Nombre de usuario (ej: acorderoi): ").strip()
    if not username:
        print("Usuario vacío, cancelado.")
        return
    nombre = input(f"Nombre para mostrar [{username}]: ").strip() or username

    password = getpass.getpass("Contraseña (mínimo 8 caracteres, no se mostrará): ")
    password2 = getpass.getpass("Repite la contraseña: ")

    if password != password2:
        print("❌ Las contraseñas no coinciden. Cancelado.")
        return

    try:
        admin_auth.save_user(username, password, nombre)
        print(f"✅ Usuario '{username}' creado/actualizado correctamente.")
    except ValueError as e:
        print(f"❌ {e}")


def borrar():
    username = input("Nombre de usuario a eliminar: ").strip()
    if admin_auth.delete_user(username):
        print(f"✅ Usuario '{username}' eliminado.")
    else:
        print(f"⚠️  El usuario '{username}' no existía.")


def main():
    print("=" * 50)
    print("Gestión de usuarios administradores — FADE Financiación")
    print("=" * 50)
    listar()
    print("¿Qué quieres hacer?")
    print("  1. Crear o actualizar un usuario")
    print("  2. Eliminar un usuario")
    print("  3. Solo listar (salir)")
    opcion = input("Opción [1]: ").strip() or "1"

    if opcion == "1":
        crear()
    elif opcion == "2":
        borrar()
    else:
        print("Hecho.")


if __name__ == '__main__':
    main()
