"""
Script de prueba para verificar los nuevos módulos
"""
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Verificar que todos los módulos se pueden importar"""
    print("🔍 Verificando imports...")
    
    try:
        from game.album_store import AlbumStore
        print("✅ AlbumStore importado correctamente")
    except Exception as e:
        print(f"❌ Error importando AlbumStore: {e}")
        return False
    
    try:
        from game.order_track import OrderTrackManager
        print("✅ OrderTrackManager importado correctamente")
    except Exception as e:
        print(f"❌ Error importando OrderTrackManager: {e}")
        return False
    
    try:
        from game.direction_mission import DirectionMission
        print("✅ DirectionMission importado correctamente")
    except Exception as e:
        print(f"❌ Error importando DirectionMission: {e}")
        return False
    
    try:
        from game.controller import GameController, GameState, GameMode
        print("✅ GameController actualizado importado correctamente")
    except Exception as e:
        print(f"❌ Error importando GameController: {e}")
        return False
    
    try:
        from ui.overlays import DirectionMissionOverlay, StationUnlockOverlay
        print("✅ Overlays actualizados importados correctamente")
    except Exception as e:
        print(f"❌ Error importando Overlays: {e}")
        return False
    
    return True


def test_album_store():
    """Probar funcionalidad básica de AlbumStore"""
    print("\n🧪 Probando AlbumStore...")
    
    from game.album_store import AlbumStore
    
    # Crear store temporal
    store = AlbumStore('data/test_album.json')
    
    # Desbloquear estación
    result = store.unlock_station('L1', 'Catalunya')
    print(f"  Desbloquear Catalunya: {'✅ Nueva' if result else '❌ Ya desbloqueada'}")
    
    # Verificar desbloqueo
    is_unlocked = store.is_station_unlocked('L1', 'Catalunya')
    print(f"  Catalunya desbloqueada: {'✅' if is_unlocked else '❌'}")
    
    # Incrementar estadística
    store.increment_station_stat('st_001', correct=True)
    stats = store.get_station_stats('st_001')
    print(f"  Estadísticas st_001: {stats['correct']} correctos, {stats['wrong']} errores")
    
    # Guardar high score
    store.save_high_score(1000)
    high_score = store.get_high_score()
    print(f"  High score guardado: {high_score}")
    
    print("✅ AlbumStore funciona correctamente")
    return True


def test_order_track():
    """Probar funcionalidad básica de OrderTrackManager"""
    print("\n🧪 Probando OrderTrackManager...")
    
    from game.order_track import OrderTrackManager
    from game.album_store import AlbumStore
    from model.metro_content import MetroContentManager
    
    content = MetroContentManager()
    album = AlbumStore('data/test_album.json')
    order_track = OrderTrackManager(content, album)
    
    # Iniciar línea
    success = order_track.start_new_line('L1')
    print(f"  Iniciar L1: {'✅' if success else '❌'}")
    
    if success:
        progress = order_track.get_progress()
        print(f"  Línea: {progress['line_name']}")
        print(f"  Próxima estación: {progress['next_station']}")
        print(f"  Progreso: {progress['next_index']}/{progress['total_stations']}")
        
        # Ver próximas estaciones
        upcoming = order_track.get_upcoming_stations(5)
        print(f"  Próximas 5 estaciones: {[s['name'] for s in upcoming]}")
    
    print("✅ OrderTrackManager funciona correctamente")
    return True


def test_direction_mission():
    """Probar funcionalidad básica de DirectionMission"""
    print("\n🧪 Probando DirectionMission...")
    
    from game.direction_mission import DirectionMission
    from model.metro_content import MetroContentManager
    
    content = MetroContentManager()
    mission = DirectionMission(content)
    
    # Generar misión
    success = mission.start_mission('L1', content.metro_lines)
    print(f"  Generar misión: {'✅' if success else '❌'}")
    
    if success:
        mission_data = mission.get_current_mission()
        if mission_data:
            print(f"  Texto: {mission_data['text']}")
            print(f"  Opciones: {mission_data['options']}")
    
    print("✅ DirectionMission funciona correctamente")
    return True


def test_data_files():
    """Verificar archivos de datos"""
    print("\n📁 Verificando archivos de datos...")
    
    import os
    import json
    
    # Verificar stations.json
    if os.path.exists('data/stations.json'):
        print("✅ stations.json existe")
        try:
            with open('data/stations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                lines = data.get('metro_lines', {})
                stations = data.get('stations_pool', [])
                print(f"  - {len(lines)} líneas de metro")
                print(f"  - {len(stations)} estaciones en pool")
        except Exception as e:
            print(f"❌ Error leyendo stations.json: {e}")
            return False
    else:
        print("❌ stations.json no encontrado")
        return False
    
    # Crear directorio data si no existe
    os.makedirs('data', exist_ok=True)
    print("✅ Directorio data verificado")
    
    return True


def main():
    """Ejecutar todas las pruebas"""
    print("=" * 60)
    print("Metro Tetris - ORDER TRACK Mode")
    print("Script de Verificación")
    print("=" * 60)
    
    results = []
    
    # Test 1: Verificar archivos de datos
    results.append(("Archivos de datos", test_data_files()))
    
    # Test 2: Importar módulos
    results.append(("Imports", test_imports()))
    
    # Test 3: AlbumStore
    try:
        results.append(("AlbumStore", test_album_store()))
    except Exception as e:
        print(f"❌ Error en AlbumStore: {e}")
        results.append(("AlbumStore", False))
    
    # Test 4: OrderTrackManager
    try:
        results.append(("OrderTrackManager", test_order_track()))
    except Exception as e:
        print(f"❌ Error en OrderTrackManager: {e}")
        results.append(("OrderTrackManager", False))
    
    # Test 5: DirectionMission
    try:
        results.append(("DirectionMission", test_direction_mission()))
    except Exception as e:
        print(f"❌ Error en DirectionMission: {e}")
        results.append(("DirectionMission", False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {passed} pasadas, {failed} fallidas")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ¡Todas las pruebas pasaron! El juego está listo.")
        print("\nPara ejecutar:")
        print("  python main_order_track.py")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
