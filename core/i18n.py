"""
Lightweight i18n (internationalization) system for Proxima Parada.

Supports:
- Default language: Catalan ("ca")
- Optional language: English ("en")
- Easy future expansion ("es", "fr", etc.)

Usage:
    from core.i18n import t, set_language, get_language
    
    set_language("en")  # Switch to English
    message = t("app.title")  # Get translated string
    message = t("goal.distance.generic", distance=5)  # With formatting
"""

# ===========================
# TRANSLATIONS DICTIONARY
# ===========================

TRANSLATIONS = {
    "ca": {
        # Application
        "app.title": "PRÒXIMA PARADA",
        "app.subtitle": "Aprèn a moure't pel Metro de Barcelona",
        
        # HUD - Score and stats
        "hud.streak": "Ratxa: {streak}",
        "hud.record": "Rècord: {score}",
        "hud.lives": "Vides: {lives}",
        "hud.errors": "Errors: {errors}",
        "hud.progress": "{current}/{total}",
        
        # HUD - Direction mode
        "hud.direction_title": "➜ Direcció: {station}",
        
        # HUD - Goal mode
        "hud.goal_title": "⭐ Objectiu: {station}",
        
        # Instructions and UI
        "ui.drag_instruction": "Arrossega l'estació correcta fins al cercle verd!",
        "ui.tap_to_start": "Toca o fes clic per començar",
        "ui.tap_to_close": "Toca per tancar",
        
        # Tutorial
        "tutorial.title": "Com es juga",
        "tutorial.step1": "1. Mira la pròxima estació (dalt)",
        "tutorial.step2_direction": "2. Confirma la direcció del tren",
        "tutorial.step2_normal": "2. Arrossega el token correcte",
        "tutorial.step3_direction": "3. Arrossega el token correcte",
        "tutorial.step3_normal": "3. Deixa'l anar sobre el cercle verd",
        "tutorial.step4_direction": "4. Deixa'l anar sobre el cercle verd",
        "tutorial.step4_normal": "4. Fes-ho abans que arribi el tren!",
        "tutorial.step5_direction": "5. Fes-ho abans que arribi el tren!",
        
        # Settings
        "settings.title": "Configuració",
        "settings.language": "Idioma",
        "settings.language_ca": "Català",
        "settings.language_en": "English",
        "settings.practice_mode": "Mode de pràctica",
        "settings.direction_mode": "Mode de direcció",
        "settings.subtitles": "Subtítols",
        "settings.active": "ACTIU",
        "settings.inactive": "INACTIU",
        "settings.close": "Tancar",
        
        # Goal mode
        "goal.reached": "Objectiu arribat!",
        "goal.distance.generic": "Falten {distance} parades per arribar a l'objectiu",
        "goal.distance.close": "Ja només falten {distance} parades",
        
        # Feedback messages
        "feedback.almost_there": "Ja gairebé hi ets!",
        "feedback.next_stop_goal": "La propera parada és l'objectiu!",
        
        # Zone transitions
        "zone.entering": "Entrant a {zone}",
        
        # Line completion
        "line.completed.title": "Línia completada!",
        "line.completed.back_to_lines": "Enrere",
        "line.completed.repeat_line": "Repetir",
        "line.completed.exit": "Sortir",
        
        # First Day mode
        "first_day.title": "🌟 El teu primer dia a Barcelona",
        "first_day.subtitle": "Descobreix el centre històric i el mar",
        "first_day.intro": "Comença un viatge guiat pels llocs més emblemàtics:",
        "first_day.station1": "• Catalunya — El cor de la ciutat",
        "first_day.station2": "• Liceu — La Rambla i el teatre",
        "first_day.station3": "• Jaume I — Entrada al Barri Gòtic",
        "first_day.station4": "• Barceloneta — La platja i el mar",
        "first_day.station5": "• Espanya — Montjuïc i les vistes",
        "first_day.start_button": "Començar el viatge",
        "first_day.completed.title": "Felicitats!",
        "first_day.completed.message": "Has completat el teu primer dia a Barcelona!",
        "first_day.continue": "Continuar",
        
        # Daily Challenge
        "daily_challenge.title": "Repte del dia",
        "daily_challenge.arrive_at": "Arriba fins a {station}",
        "daily_challenge.line": "Línia: [{line_id}]",
        "daily_challenge.completed": "Repte completat avui!",
        "daily_challenge.start": "Començar",
        
        # Line selection
        "line_select.title": "Escull la línia",
        "line_select.back": "Enrere",
        
        # Cover screen
        "menu.play": "Jugar",
        "menu.daily_challenge": "Repte del dia",
        "menu.first_day": "🌟 El teu primer dia a Barcelona",
        "menu.settings": "Configuració",
        "menu.footer": "L3 — Zona Universitària → Trinitat Nova",
    },
    "en": {
        # Application
        "app.title": "NEXT STOP",
        "app.subtitle": "Learn to navigate Barcelona Metro",
        
        # HUD - Score and stats
        "hud.streak": "Streak: {streak}",
        "hud.record": "Record: {score}",
        "hud.lives": "Lives: {lives}",
        "hud.errors": "Errors: {errors}",
        "hud.progress": "{current}/{total}",
        
        # HUD - Direction mode
        "hud.direction_title": "➜ Direction: {station}",
        
        # HUD - Goal mode
        "hud.goal_title": "⭐ Goal: {station}",
        
        # Instructions and UI
        "ui.drag_instruction": "Drag the correct station to the green circle!",
        "ui.tap_to_start": "Tap to start",
        "ui.tap_to_close": "Tap to close",
        
        # Tutorial
        "tutorial.title": "How to play",
        "tutorial.step1": "1. Look at the next station (above)",
        "tutorial.step2_direction": "2. Confirm the train direction",
        "tutorial.step2_normal": "2. Drag the correct token",
        "tutorial.step3_direction": "3. Drag the correct token",
        "tutorial.step3_normal": "3. Drop it on the green circle",
        "tutorial.step4_direction": "4. Drop it on the green circle",
        "tutorial.step4_normal": "4. Do it before the train arrives!",
        "tutorial.step5_direction": "5. Do it before the train arrives!",
        
        # Settings
        "settings.title": "Settings",
        "settings.language": "Language",
        "settings.language_ca": "Català",
        "settings.language_en": "English",
        "settings.practice_mode": "Practice Mode",
        "settings.direction_mode": "Direction Mode",
        "settings.subtitles": "Subtitles",
        "settings.active": "ON",
        "settings.inactive": "OFF",
        "settings.close": "Close",
        
        # Goal mode
        "goal.reached": "Goal reached!",
        "goal.distance.generic": "{distance} stops to the goal",
        "goal.distance.close": "Just {distance} stops left",
        
        # Feedback messages
        "feedback.almost_there": "Almost there!",
        "feedback.next_stop_goal": "Next stop is the goal!",
        
        # Zone transitions
        "zone.entering": "Entering {zone}",
        
        # Line completion
        "line.completed.title": "Line completed!",
        "line.completed.back_to_lines": "Back",
        "line.completed.repeat_line": "Repeat",
        "line.completed.exit": "Exit",
        
        # First Day mode
        "first_day.title": "🌟 Your first day in Barcelona",
        "first_day.subtitle": "Discover the historic center and the sea",
        "first_day.intro": "Start a guided journey through iconic places:",
        "first_day.station1": "• Catalunya — The heart of the city",
        "first_day.station2": "• Liceu — Las Rambla and theatre",
        "first_day.station3": "• Jaume I — Gateway to Gothic Quarter",
        "first_day.station4": "• Barceloneta — The beach and sea",
        "first_day.station5": "• Espanya — Montjuïc and views",
        "first_day.start_button": "Start the journey",
        "first_day.completed.title": "Congratulations!",
        "first_day.completed.message": "You completed your first day in Barcelona!",
        "first_day.continue": "Continue",
        
        # Daily Challenge
        "daily_challenge.title": "Daily Challenge",
        "daily_challenge.arrive_at": "Arrive at {station}",
        "daily_challenge.line": "Line: [{line_id}]",
        "daily_challenge.completed": "Challenge completed today!",
        "daily_challenge.start": "Start",
        
        # Line selection
        "line_select.title": "Choose a line",
        "line_select.back": "Back",
        
        # Cover screen
        "menu.play": "Play",
        "menu.daily_challenge": "Daily Challenge",
        "menu.first_day": "🌟 Your first day in Barcelona",
        "menu.settings": "Settings",
        "menu.footer": "L3 — Zona Universitària → Trinitat Nova",
    }
}


# ===========================
# STATE AND FUNCTIONS
# ===========================

_current_language = "ca"


def normalize_lang(lang: str) -> str:
    """
    Normalize language codes.
    Examples: "ca-ES" -> "ca", "en-US" -> "en"
    """
    if not lang:
        return "ca"
    # Take the first part before hyphen
    normalized = lang.split("-")[0].lower()
    return normalized if normalized in TRANSLATIONS else "ca"


def set_language(lang: str) -> None:
    """Set the active language. Defaults to 'ca' if invalid."""
    global _current_language
    normalized = normalize_lang(lang)
    _current_language = normalized
    print(f"[i18n] Language set to: {_current_language}")


def get_language() -> str:
    """Get the current active language code."""
    return _current_language


def t(key: str, **kwargs) -> str:
    """
    Translate a key with optional formatting.
    
    Args:
        key: Translation key (e.g., "app.title", "hud.streak")
        **kwargs: Format placeholders (e.g., streak=5 for "Ratxa: {streak}")
    
    Returns:
        Translated and formatted string. Falls back to Catalan, then key itself.
    """
    # Try current language
    if _current_language in TRANSLATIONS and key in TRANSLATIONS[_current_language]:
        template = TRANSLATIONS[_current_language][key]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"[i18n] Missing format key in '{key}': {e}")
            return template  # Return unformatted if placeholder missing
    
    # Fallback to Catalan
    if key in TRANSLATIONS["ca"]:
        template = TRANSLATIONS["ca"][key]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"[i18n] Missing format key in Catalan '{key}': {e}")
            return template
    
    # Debug: return key if not found
    print(f"[i18n] WARNING: Missing translation key: {key}")
    return key


def missing_keys_report() -> None:
    """Print missing translation keys for the selected language compared to Catalan."""
    current = TRANSLATIONS.get(_current_language, {})
    catalan = TRANSLATIONS.get("ca", {})
    
    missing = set(catalan.keys()) - set(current.keys())
    
    if missing:
        print(f"\n[i18n] Missing translation keys for '{_current_language}':")
        for key in sorted(missing):
            print(f"  - {key}")
    else:
        print(f"\n[i18n] All keys are translated for '{_current_language}'!")


def get_translations_for_language(lang: str) -> dict:
    """Get all translations for a specific language."""
    normalized = normalize_lang(lang)
    return TRANSLATIONS.get(normalized, {})
