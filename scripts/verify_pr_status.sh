#!/bin/bash
# Verificación del estado del PR y workflow pyjnius-smoke

set -e

REPO="marketingeducative-eng/Tetris-Metro"
BRANCH="ci/activate-pyjnius-smoke"

echo "════════════════════════════════════════════════════════════════"
echo "VERIFICACIÓN DEL PR: $BRANCH"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 1. Verificar que la rama existe remotamente
echo "[1/5] Verificando branch remota..."
if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
    echo "✅ Branch '$BRANCH' existe en origin"
    COMMIT=$(git log --oneline -1 "origin/$BRANCH" | cut -d' ' -f1)
    echo "   Último commit: $COMMIT"
else
    echo "❌ Branch no encontrada en origin"
    exit 1
fi
echo ""

# 2. URLs importantes
echo "[2/5] URLs para verificación manual..."
echo "📋 Ver/Crear PR:"
echo "   https://github.com/$REPO/pull/new/$BRANCH"
echo ""
echo "📋 Lista de PRs abiertos:"
echo "   https://github.com/$REPO/pulls"
echo ""
echo "📋 Actions/Workflows:"
echo "   https://github.com/$REPO/actions"
echo ""
echo "📋 Workflow pyjnius-smoke específico:"
echo "   https://github.com/$REPO/actions/workflows/pyjnius-smoke.yml"
echo ""

# 3. Intentar obtener info del PR via API (sin autenticación)
echo "[3/5] Intentando obtener info del PR via API..."
PR_DATA=$(curl -s "https://api.github.com/repos/$REPO/pulls?head=marketingeducative-eng:$BRANCH&state=all" 2>/dev/null || echo "[]")

if echo "$PR_DATA" | grep -q '"number"'; then
    PR_NUMBER=$(echo "$PR_DATA" | grep -o '"number": [0-9]*' | head -1 | grep -o '[0-9]*')
    PR_TITLE=$(echo "$PR_DATA" | grep -o '"title": "[^"]*"' | head -1 | cut -d'"' -f4)
    PR_STATE=$(echo "$PR_DATA" | grep -o '"state": "[^"]*"' | head -1 | cut -d'"' -f4)
    
    echo "✅ PR encontrado:"
    echo "   Número: #$PR_NUMBER"
    echo "   Título: $PR_TITLE"
    echo "   Estado: $PR_STATE"
    echo ""
    echo "📋 URL directa del PR:"
    echo "   https://github.com/$REPO/pull/$PR_NUMBER"
    echo ""
    
    # 4. Intentar obtener checks del PR
    echo "[4/5] Verificando checks del PR..."
    CHECKS=$(curl -s "https://api.github.com/repos/$REPO/pulls/$PR_NUMBER/checks" 2>/dev/null || echo "{}")
    
    if echo "$CHECKS" | grep -q '"check_runs"'; then
        echo "Checks encontrados:"
        echo "$CHECKS" | grep -E '"name"|"status"|"conclusion"' | paste - - - | head -5
    else
        echo "⚠️  No se pudieron obtener checks (puede requerir autenticación)"
    fi
else
    echo "⚠️  PR no encontrado via API"
    echo "   Esto puede significar:"
    echo "   - El PR aún no se ha creado manualmente"
    echo "   - La API requiere autenticación"
    echo ""
    echo "👉 Acción requerida: Abre la URL para crear/ver el PR:"
    echo "   https://github.com/$REPO/pull/new/$BRANCH"
fi
echo ""

# 5. Verificar archivos locales del workflow
echo "[5/5] Verificando archivos del workflow localmente..."
if [ -f ".github/workflows/pyjnius-smoke.yml" ]; then
    echo "✅ Workflow pyjnius-smoke.yml existe"
    
    # Verificar configuración crítica
    if grep -q "python-version: '3.10'" .github/workflows/pyjnius-smoke.yml; then
        echo "   ✓ Python 3.10 configurado"
    fi
    
    if grep -q "Cython==0.29.36" .github/workflows/pyjnius-smoke.yml; then
        echo "   ✓ Cython==0.29.36 pinado"
    fi
    
    if grep -q "pull_request:" .github/workflows/pyjnius-smoke.yml; then
        echo "   ✓ Trigger 'pull_request' configurado"
    fi
else
    echo "❌ Workflow no encontrado"
fi

if [ -f "scripts/ci_pyjnius_smoke.sh" ]; then
    echo "✅ Script ci_pyjnius_smoke.sh existe"
    
    if grep -q "undeclared name not builtin: long" scripts/ci_pyjnius_smoke.sh; then
        echo "   ✓ Detección de bug histórico configurada"
    fi
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "PRÓXIMOS PASOS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "1. Abre en el navegador:"
echo "   https://github.com/$REPO/pulls"
echo ""
echo "2. Busca el PR 'CI: Fix pyjnius compilation + add smoke test'"
echo ""
echo "3. Verifica en la pestaña 'Checks':"
echo "   ✅ Job: 'pyjnius Smoke Test (Fast Validation)'"
echo "   ✅ Status: En progreso o Passed (verde)"
echo ""
echo "4. En los logs, confirma:"
echo "   ✅ Python 3.10.x"
echo "   ✅ Cython 0.29.36 verificado"
echo "   ✅ NO aparece 'undeclared name not builtin: long'"
echo "   ✅ Mensaje final: '✅ SMOKE TEST PASSED'"
echo ""
echo "5. Si está en verde → Listo para merge"
echo ""
echo "════════════════════════════════════════════════════════════════"
