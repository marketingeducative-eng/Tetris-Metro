# Barcelona Civic Institutional Layer

## Overview

The civic institutional layer subtly reinforces the Barcelona City Council's positioning of *Pròxima Parada* as a **digital civic welcome tool** for newcomers, students, and residents learning to navigate Barcelona while integrating through Catalan.

**Design Philosophy:**
- **Civic**: Official but approachable
- **Welcoming**: Warm, inclusive, educational
- **Non-political**: Focused on practical civic life, not political messaging
- **Elegant**: Premium, respectful, institutionally credible

---

## Implementation Components

### 1. Civic Footer Credit

**Location:** `game_proxima_parada.py` (lines 660-668)

**Purpose:** Subtle attribution reinforcing institutional connection to Barcelona's public transport network.

**Implementation:**
```python
self.civic_footer = Label(
    text="Inspirat en la xarxa de transport públic de Barcelona",
    font_size='11sp',
    size_hint=(1, None),
    height=20,
    pos_hint={'center_x': 0.5, 'y': 0.005},
    color=(0.45, 0.5, 0.55, 0.7),
    italic=True
)
```

**Characteristics:**
- Small 11sp font (unobtrusive)
- Italic styling (elegant, credit-like)
- 70% opacity (subtle, not distracting)
- Position at bottom (y: 0.005)
- Catalan text maintaining game language consistency

---

### 2. Civic Splash Overlay

**Location:** `game_proxima_parada.py` (lines 1709-1825)

**Purpose:** Opening splash screen welcoming users to Barcelona with civic subtext.

**Method:** `show_civic_splash(on_dismiss_callback=None)`

**Content:**
- **Main text:** "Benvingut a Barcelona" (38sp, bold, elegant green)
- **Subtitle:** "Una experiència per descobrir la ciutat i viure-la en català" (18sp, italic)
- **Call to action:** "Toca per començar" (15sp, subtle)

**Behavior:**
- Auto-dismisses after 4 seconds
- Touch anywhere to dismiss immediately
- Fade in/out animations (0.8s / 0.5s)
- Deep elegant background (0.02, 0.03, 0.05, 0.98 opacity)
- Rounded panel (22px radius) with subtle green accent border

**Trigger Logic:**
- Shown once per session in `GameScreen.on_pre_enter()`
- Only after onboarding is completed
- Not shown in First Day Mode (has its own intro)
- Uses class variable `GameScreen._civic_splash_shown` to track

**Code:**
```python
# In ui/screens.py GameScreen.on_pre_enter()
if not GameScreen._civic_splash_shown and not self.first_day_mode:
    settings_manager = SettingsManager()
    if settings_manager.get("has_completed_onboarding", False):
        GameScreen._civic_splash_shown = True
        if self.game_widget and hasattr(self.game_widget, "show_civic_splash"):
            Clock.schedule_once(lambda dt: self.game_widget.show_civic_splash(), 0.5)
```

---

### 3. "Descobreix Barcelona" Info Overlay

**Location (Game):** `game_proxima_parada.py` (lines 1830-2015)
**Location (Menu):** `ui/screens.py` (lines 1093-1278) - CoverScreen method

**Purpose:** Educational micro-info about Barcelona civic life, culture, and language.

**Method:** `show_descobreix_barcelona()`

**Content Sections:**

1. **🚇 Què és TMB?**
   - Explains Transports Metropolitans de Barcelona
   - Founded 1997, public enterprise managing metro and buses
   - Connects Barcelona and metropolitan area

2. **🏘️ Què és un barri?**
   - Explains neighborhood/district concept
   - Each has unique personality, history, community
   - Examples: Gràcia, Barceloneta, Gòtic, Eixample

3. **💬 Per què el català importa?**
   - Official language of Catalunya
   - Essential part of cultural identity
   - Facilitates daily life and shows respect
   - Helps integration into community

4. **🤝 Respecte per la llengua local**
   - Both Catalan and Spanish are official
   - Many speak both languages
   - Effort to speak Catalan is valued
   - Don't fear mistakes - trying matters

**UI Design:**
- Title: "🏛️ Descobreix Barcelona" (30sp, civic green)
- Scrollable content (620x520px panel)
- Dark panel (0.10, 0.13, 0.18) with rounded corners (20px)
- Each section has bold icon + title + detailed text
- Close button at bottom (green, "Tancar")
- Touch outside panel to dismiss

**Integration Points:**
1. **Main Menu Button:** 
   - Added to CoverScreen button box
   - Green background (0.28, 0.72, 0.48)
   - Text: "🏛️ Descobreix Barcelona"
   - Positioned between "El teu primer dia" and "Configuració"

2. **Game Widget Access:**
   - Available via `game_widget.show_descobreix_barcelona()`
   - Can be called programmatically during gameplay

---

### 4. Optional City Branding Flag

**Location:** `game_proxima_parada.py` (line 192)

**Purpose:** Allow institutional logo/branding when officially positioned by Barcelona City Council.

**Implementation:**
```python
# Civic mode flag (institutional layer)
self.enable_city_mode = False  # Set to True to show Barcelona City Council branding
```

**Usage Scenarios:**
- `False` (default): Clean civic tone without official logos
- `True`: Can display Barcelona City Council logo/branding for official deployments
- Future enhancement: Logo in splash overlay, watermark, official endorsement text

---

## Overlay Lifecycle Management

All civic overlays follow the hardened lifecycle pattern:

1. **Duplicate Prevention:**
```python
if self.civic_splash_overlay:
    self._log_overlay("Already showing", "civic_splash_overlay")
    return
```

2. **Creation & Tracking:**
```python
self._log_overlay("Show", "civic_splash_overlay")
overlay = FloatLayout(...)
self.civic_splash_overlay = overlay
self.parent.add_widget(overlay)
```

3. **Cleanup:**
```python
def _dismiss_civic_splash(self, callback=None):
    self._cleanup_overlay('civic_splash_overlay')
    if callback:
        callback()
```

4. **Centralized Cleanup Method:**
```python
def _cleanup_overlay(self, overlay_name):
    overlay = getattr(self, overlay_name, None)
    if overlay and overlay in self.parent.children:
        self.parent.remove_widget(overlay)
    setattr(self, overlay_name, None)
    self._log_overlay("Cleanup", overlay_name)
```

---

## User Experience Flow

### First Launch (After Onboarding)
1. User completes narrative onboarding
2. User selects "Jugar" from CoverScreen
3. GameScreen loads → `on_pre_enter()` triggers
4. **Civic splash displays:** "Benvingut a Barcelona"
5. Auto-dismisses after 4s (or user touches)
6. Game begins normally

### Subsequent Launches
- Civic splash does **not** repeat (session-tracked)
- Civic footer remains visible in all games
- "Descobreix Barcelona" button always available in menu

### Accessing Civic Info
1. User on CoverScreen
2. Clicks "🏛️ Descobreix Barcelona" button
3. Info overlay displays with 4 civic topics
4. User scrolls to read, clicks "Tancar" or touches outside

---

## Technical Details

### Files Modified

**game_proxima_parada.py:**
- Lines 186-193: Added overlay tracking attributes
- Lines 660-668: Added civic footer label
- Lines 1709-1825: `show_civic_splash()` method
- Lines 1826-1829: `_dismiss_civic_splash()` method
- Lines 1830-2015: `show_descobreix_barcelona()` method
- Lines 2016-2018: `_dismiss_descobreix()` method

**ui/screens.py:**
- Line 697: Increased button_box height to 280 (5 buttons)
- Lines 717-725: Added `descobreix_button` definition
- Line 739: Added button to button_box
- Line 773: Bound button to `_show_descobreix_info` handler
- Lines 1093-1278: Added `_show_descobreix_info()` method
- Lines 1287-1289: Added `_civic_splash_shown` class variable
- Lines 1304-1312: Added civic splash trigger in `on_pre_enter()`

### Dependencies

**Kivy Imports (already present):**
- `FloatLayout`, `BoxLayout`, `Widget`
- `Label`, `Button`
- `ScrollView`
- `Animation`, `Clock`
- `Color`, `Rectangle`, `RoundedRectangle`

**Project Imports:**
- `SettingsManager` (core.settings)
- `ProximaParadaGame` (game_proxima_parada)

---

## Testing

### Manual Test: Civic Footer
1. Run game: `python main.py`
2. Start any game
3. Look at bottom of screen
4. Verify: "Inspirat en la xarxa de transport públic de Barcelona" is visible but subtle

### Manual Test: Civic Splash
1. Delete or reset settings (to clear `_civic_splash_shown` flag)
2. Complete onboarding
3. Click "Jugar"
4. Verify: Splash appears with "Benvingut a Barcelona"
5. Wait 4s or touch screen
6. Verify: Splash fades out smoothly

### Manual Test: Descobreix Button
1. From main menu (CoverScreen)
2. Click "🏛️ Descobreix Barcelona" button
3. Verify: Info overlay opens with 4 sections
4. Scroll through content
5. Click "Tancar" or touch outside
6. Verify: Overlay dismisses cleanly

### Automated Test
Run: `python test_civic_layer.py`

Tests:
- Civic footer presence and styling
- `show_civic_splash()` method availability
- `show_descobreix_barcelona()` method availability
- No Python errors in civic layer code

---

## Tone Guidelines

### ✅ Civic & Welcoming
- "Benvingut a Barcelona" - warm institutional greeting
- "Una experiència per descobrir la ciutat" - inviting, exploratory
- Educational without being preachy

### ✅ Non-Political
- Focuses on **practical civic life** (TMB, barris, language)
- No political parties, movements, or controversial topics
- Cultural respect presented as practical integration advice

### ✅ Institutionally Elegant
- Premium typography (38sp bold titles, 18sp subtitles)
- Elegant color palette (deep backgrounds, subtle greens)
- Rounded corners, smooth animations
- Italian styling for credits (subtle, respectful)

### ❌ Avoid
- Political messaging or partisan content
- Heavy-handed institutional presence
- Intrusive permanent branding (unless `enable_city_mode=True`)
- Patronizing or condescending language
- Cultural chauvinism (respect multilingualism)

---

## Future Enhancements

### Optional City Branding (`enable_city_mode=True`)
- Barcelona City Council logo in splash overlay
- Watermark in game corner
- "Official civic tool" endorsement text
- Custom color scheme matching city branding

### Additional Civic Content
- "Què és un districte?" (districts vs barris)
- "Com funciona el transport públic?" (tickets, zones, integrated system)
- "Recursos per a nous habitants" (links to city services)
- "Història de Barcelona" (brief timeline)

### Accessibility
- Text-to-speech for civic splash content
- High contrast mode for civic footer
- Adjustable font sizes
- Multiple language support (maintaining Catalan primary)

### Analytics (Privacy-Respecting)
- Track if users engage with "Descobreix Barcelona"
- Measure civic splash dismissal time (interest indicator)
- Identify most popular civic info topics
- **No personal data collection**

---

## Integration Status

✅ **COMPLETED:**
- Civic footer added and visible
- Civic splash overlay implemented
- "Descobreix Barcelona" info overlay created
- Menu button integration in CoverScreen
- Overlay lifecycle hardening
- Session-based splash tracking
- Test suite created

⚠️ **OPTIONAL (Future):**
- `enable_city_mode=True` logo display
- Additional civic content sections
- Analytics integration
- Text-to-speech support

---

## Maintenance Notes

### Adding New Civic Content Sections
Edit the `sections` list in `show_descobreix_barcelona()`:
```python
sections = [
    {
        'icon': '🏛️',
        'title': 'New Section Title',
        'text': (
            "Content here in Catalan. "
            "Multiple paragraphs supported."
        )
    }
]
```

### Adjusting Civic Footer Visibility
Edit `civic_footer` Label in `game_proxima_parada.py`:
```python
self.civic_footer = Label(
    text="Your new text",
    font_size='11sp',  # Adjust size
    color=(0.45, 0.5, 0.55, 0.7),  # Adjust color/opacity
    ...
)
```

### Changing Splash Auto-Dismiss Time
Edit `Clock.schedule_once()` in `show_civic_splash()`:
```python
Clock.schedule_once(auto_dismiss, 4.0)  # Change 4.0 to desired seconds
```

---

## Conclusion

The Barcelona civic institutional layer successfully positions *Pròxima Parada* as a **digital civic welcome tool**, providing:

1. **Subtle Institutional Presence:** Footer credit without intrusion
2. **Welcoming Entry Point:** Elegant splash greeting newcomers
3. **Educational Value:** Practical civic information for integration
4. **Cultural Respect:** Catalan language emphasis, multilingual acknowledgment
5. **Institutional Credibility:** Premium, elegant, non-political tone

**Result:** A game that feels like an **official civic resource** while remaining approachable, educational, and respectful.

---

**Documentation Version:** 1.0  
**Last Updated:** Phase 3 Implementation Complete  
**Status:** ✅ Production Ready
