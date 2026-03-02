#!/bin/bash
# Instrucciones para activar protección de rama (post-merge)

cat << 'EOF'
════════════════════════════════════════════════════════════════
ACTIVACIÓN DE PROTECCIÓN DE RAMA
════════════════════════════════════════════════════════════════

⚠️  IMPORTANTE: Ejecutar DESPUÉS de hacer merge del PR

📋 PASO 1: Navegar a Settings
════════════════════════════════════════════════════════════════

Abre en tu navegador:
https://github.com/marketingeducative-eng/Tetris-Metro/settings/branches


📋 PASO 2: Configurar Protección
════════════════════════════════════════════════════════════════

1. Branch name pattern: main

2. Click en "Add branch protection rule" (o "Edit" si ya existe)

3. ACTIVAR estas opciones:
   ☑ Require status checks to pass before merging

4. En "Search for status checks", escribir y seleccionar:
   → pyjnius-smoke
   
   O buscar:
   → "Validate pyjnius+Cython compilation (no APK packaging)"

5. El check debe aparecer como requerido con un ✓


📋 PASO 3: NO Modificar
════════════════════════════════════════════════════════════════

• NO cambiar otros checks existentes
• NO modificar permisos de push/force push
• NO tocar otras settings del repositorio


📋 PASO 4: Guardar
════════════════════════════════════════════════════════════════

Click en "Save changes" (botón verde al final de la página)


📋 PASO 5: Verificar
════════════════════════════════════════════════════════════════

1. Vuelve a: https://github.com/marketingeducative-eng/Tetris-Metro/settings/branches

2. Confirma que en la regla de "main" aparece:
   ● Status checks that are required:
     • pyjnius-smoke


✅ ¿QUÉ CONSEGUIMOS?
════════════════════════════════════════════════════════════════

Después de activar la protección:

✅ Cualquier PR futuro hacia main requerirá que pase el smoke test
✅ No se podrá hacer merge si pyjnius-smoke está en rojo
✅ Garantiza que nunca se merge código que rompa pyjnius compilation
✅ Previene introducción accidental de Cython 3.x incompatible


🎯 RESULTADO FINAL
════════════════════════════════════════════════════════════════

Tu repositorio estará protegido contra el bug histórico:
  "jnius/jnius_utils.pxi:323:37: undeclared name not builtin: long"

Cada cambio en buildozer.spec o workflows pasará por validación
automática de pyjnius compilation (~8-12 min) antes de merge.


════════════════════════════════════════════════════════════════
EOF
