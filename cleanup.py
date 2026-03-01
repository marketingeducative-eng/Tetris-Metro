"""
Script de limpieza - Elimina archivos obsoletos de la refactorización
"""
import os
from pathlib import Path

# Archivos obsoletos (versión pre-refactor)
OBSOLETE_FILES = [
    'main_fixed.py',           # Reemplazado por main.py
    'game/board.py',           # Movido a model/board.py
    'game/piece.py',           # Movido a model/piece.py
    'game/tetrominos.py',      # Movido a model/tetrominos.py
    'game/content_manager.py', # Refactorizado como model/metro_content.py
    'game/persistence.py',     # Integrado en game/controller.py
]

def clean_obsolete_files():
    """Elimina archivos obsoletos"""
    root = Path(__file__).parent
    
    print("🧹 Limpiando archivos obsoletos...")
    print("=" * 50)
    
    for file_path in OBSOLETE_FILES:
        full_path = root / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Eliminado: {file_path}")
            except Exception as e:
                print(f"❌ Error eliminando {file_path}: {e}")
        else:
            print(f"⚠️  No encontrado: {file_path}")
    
    print("=" * 50)
    print("✅ Limpieza completada")

if __name__ == '__main__':
    response = input("¿Eliminar archivos obsoletos? (s/n): ")
    if response.lower() == 's':
        clean_obsolete_files()
    else:
        print("❌ Limpieza cancelada")
