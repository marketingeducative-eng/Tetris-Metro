# Barcelona Survival Mode

**Status**: ✅ Complete  
**Date**: February 24, 2026  
**Mode Type**: Educational / Language Learning

## Overview

Barcelona Survival Mode transforms the metro game into a practical Catalan survival simulator for Erasmus students and expats arriving in Barcelona. Players learn essential metro vocabulary and phrases through real-life scenarios.

## Objective

Help newcomers to Barcelona survive their first metro experiences by teaching:
- Essential Catalan vocabulary
- Metro navigation phrases
- Cultural context
- Practical communication skills

## Emotional Framing

**Core narrative**: "Acabes d'arribar a Barcelona per primera vegada"  
(You're arriving in Barcelona for the first time)

This creates emotional resonance and practical urgency - players learn what they actually need to know.

## Features

### 1. Real-Life Scenarios

10 essential situations covering:

| Scenario | Teaches | Practical Value |
|----------|---------|----------------|
| Comprar un bitllet | "Un bitllet senzill, si us plau" | Essential for first metro ride |
| Preguntar la direcció | "On és...?" | Navigate to destinations |
| Entendre 'Sortida' | Exit signage | Find your way out |
| Identificar la direcció | Train direction signs | Catch the right train |
| Llegir els cartells | "Enllaç" (connection) | Change metro lines |
| Demanar un cafè | "Un tallat, si us plau" | Social integration |
| Preguntar 'On és...?' | Location questions | General navigation |
| Entendre 'Andana' | Platform vocabulary | Station orientation |
| Ser educat | "Perdona, pots ajudar-me?" | Polite interactions |
| Entendre 'Tancat' | "Tancat" vs "Obert" | Store hours |

### 2. Scenario Structure

Each scenario follows a consistent pattern:

```
1. SHORT NARRATIVE (2 lines max)
   - Sets the emotional context
   - Creates urgency/motivation
   - Example: "Estàs a l'estació. / Necessites comprar un bitllet."

2. MICRO TASK
   - Multiple choice question
   - 3 options: correct Catalan, English, Spanish
   - Example: "Què has de demanar?"

3. IMMEDIATE FEEDBACK
   - In Catalan only
   - Encouraging for correct answers
   - Corrective for wrong answers
   - Example: "Perfecte! Això et durà un viatge."

4. CULTURAL CONTEXT (1 sentence)
   - Explains local usage
   - Adds depth to learning
   - Example: "A Barcelona, pots comprar el 'bitllet senzill' per a un viatge..."
```

### 3. Language Immersion

**No English during gameplay:**
- Questions in Catalan
- Choices in Catalan (except "wrong" choices)
- Feedback in Catalan
- Cultural context in Catalan

**Optional help button:**
- Available but not intrusive
- Shows English translation on demand
- Encourages trying to understand first

### 4. Progression System

**Linear progression:**
- Complete scenario 1 → unlock scenario 2
- Cannot skip ahead
- Reinforces learning sequence

**Completion reward:**
```
Badge: 🎒 Supervivència Barcelona Nivell 1
Message: "Has sobreviscut a Barcelona – Nivell 1"
Description: "Has completat les situacions bàsiques del metro de Barcelona"
```

## Technical Architecture

### Mode Class: `SurvivalMode`

Located in: `core/modes.py`

```python
class SurvivalMode(BaseMode):
    """Barcelona Survival Mode - Learn practical Catalan for metro navigation"""
    
    name = "SURVIVAL"
    
    def __init__(self, scenarios_data=None)
    def get_current_scenario()
    def get_scenario_progress()
    def is_complete()
    def on_round_start(engine, station)
    def on_correct(engine, station)
    def on_wrong(engine, station)
    def get_recommendations(engine)
```

**Attributes:**
- `scenarios`: List of scenario dictionaries
- `current_scenario_index`: Current progress (0-9)
- `completed_scenarios`: Set of completed scenario IDs
- `scenario_attempts`: Dict tracking attempts per scenario

**Lifecycle Hooks:**
- `on_round_start()`: Initialize scenario
- `on_correct()`: Mark complete, advance to next
- `on_wrong()`: Track failed attempts
- `get_recommendations()`: Return scenario-specific choices

### Data File: `survival_scenarios_ca.json`

Located in: `data/survival_scenarios_ca.json`

**Structure:**
```json
{
  "title": "Barcelona Survival Mode - Nivell 1",
  "intro": "Acabes d'arribar a Barcelona...",
  "scenarios": [
    {
      "id": "buy_ticket",
      "title": "Comprar un bitllet",
      "narrative": ["Line 1", "Line 2"],
      "context": "Cultural explanation...",
      "task_type": "choice",
      "question": "Question text?",
      "choices": [
        {
          "text": "Choice text",
          "correct": true/false,
          "feedback": "Feedback text"
        }
      ]
    }
  ],
  "completion": {
    "title": "Enhorabona!",
    "message": "Has sobreviscut a Barcelona – Nivell 1",
    "badge_id": "survival_barcelona_1"
  }
}
```

### Badge Definition

Located in: `core/badges.py`

```python
"survival_barcelona_1": {
    "icon": "🎒",
    "name": "Supervivència Barcelona Nivell 1",
    "description": "Has sobreviscut a Barcelona - Nivell 1",
    "type": "survival",
    "required_count": 1
}
```

## Integration

### Importing the Mode

```python
from core.modes import SurvivalMode

# Initialize mode
survival_mode = SurvivalMode()

# Set mode on engine
engine.set_mode(survival_mode)
```

### Checking Progress

```python
# Get current scenario
current = survival_mode.get_current_scenario()

# Get progress
completed, total = survival_mode.get_scenario_progress()
print(f"Progress: {completed}/{total}")

# Check completion
if survival_mode.is_complete():
    print("Mode completed!")
```

### Handling Events

The mode automatically:
- Advances scenario on `on_correct()`
- Tracks attempts on `on_wrong()`
- Unlocks badge on completion

## User Experience Flow

```
1. MODE START
   ↓
   "Acabes d'arribar a Barcelona per primera vegada"
   ↓
2. SCENARIO 1: Comprar un bitllet
   ↓
   Narrative → Question → Choices → Feedback → Context
   ↓
3. Player selects correct answer
   ↓
   Positive feedback + advance
   ↓
4. SCENARIO 2: Preguntar la direcció
   ↓
   ... continues through 10 scenarios ...
   ↓
5. COMPLETION
   ↓
   "Has sobreviscut a Barcelona – Nivell 1"
   Badge unlocked: 🎒
```

## Testing

### Test File: `test_survival_mode.py`

**Features:**
- Visual scenario browser
- Navigate through all 10 scenarios
- See narrative, choices, feedback, context
- Simulate completion
- View badge unlock

**Run test:**
```bash
python test_survival_mode.py
```

**Console output shows:**
```
======================================================================
BARCELONA SURVIVAL MODE - TEST
======================================================================

Mode Features:
✓ Real-life Catalan language scenarios
✓ Practical metro navigation skills
✓ Cultural context for each situation
✓ Catalan immersion (no English during gameplay)
✓ Optional help button (not shown in this test)
✓ Completion unlocks 'Supervivència Barcelona Nivell 1' badge

Scenarios included:
1. Comprar un bitllet (Buy a ticket)
2. Preguntar la direcció (Ask for directions)
... (10 total scenarios) ...
```

## Future Enhancements

### Nivell 2 (Level 2) - Advanced Scenarios

Potential scenarios:
- Asking about train delays ("Hi ha retards?")
- Understanding announcements ("Propera parada...")
- Buying multi-trip tickets ("T-Casual" vs "T-Dia")
- Asking for help ("Pots ajudar-me?")
- Understanding zone system ("Zona 1", "Títol integrat")
- Metro + bus combinations
- Tourist card navigation
- Emergency situations
- Peak hour etiquette
- Accessibility features

### Audio Integration

- Text-to-speech for Catalan phrases
- Native speaker pronunciation
- Listen before seeing choices
- Pronunciation practice mode

### Adaptive Difficulty

- Track which scenarios are hardest
- Repeat challenging scenarios
- Personalized review sessions

### Social Features

- Share completion status
- Compare progress with friends
- Collaborative scenarios (help another "tourist")

### Real Photo Integration

- Station photos for context
- Metro map integration
- Visual recognition tasks

## Educational Value

### Language Skills Developed

1. **Vocabulary**: 30+ essential metro/daily life words
2. **Phrases**: 10+ practical phrase templates
3. **Cultural awareness**: Barcelona-specific customs
4. **Confidence**: Reduces anxiety about language barriers

### Pedagogical Principles

- **Contextual Learning**: Real situations, not abstract grammar
- **Immediate Feedback**: Reinforcement loops
- **Emotional Anchoring**: "First time in Barcelona" creates memory hooks
- **Cultural Integration**: Not just language, but culture
- **Progressive Difficulty**: Start easy, build confidence
- **Practical Focus**: Only what you actually need

## Design Philosophy

### Core Principles

1. **Respect the Learner**: No condescension, clear explanations
2. **Catalan Immersion**: Build confidence, not dependence on English
3. **Cultural Context**: Language exists in culture
4. **Practical First**: Survival skills before perfection
5. **Emotional Resonance**: The "new in Barcelona" feeling drives engagement

### Why This Works

- **Motivation**: Real need (surviving in Barcelona)
- **Relevance**: Scenarios they'll actually face
- **Confidence**: Small wins build courage to speak
- **Memory**: Emotional context aids retention
- **Integration**: Language + culture = deeper learning

## Related Files

- **Mode Implementation**: `core/modes.py` (SurvivalMode class)
- **Scenarios Data**: `data/survival_scenarios_ca.json`
- **Badge Definition**: `core/badges.py`
- **Test Suite**: `test_survival_mode.py`
- **Documentation**: `BARCELONA_SURVIVAL_MODE.md` (this file)

## Summary

Barcelona Survival Mode addresses a real need: helping newcomers navigate Barcelona's metro system while learning essential Catalan. By focusing on practical scenarios with emotional framing ("arriving for the first time"), the mode creates engaging, memorable learning experiences.

**Key Innovation**: Not just a language lesson, but a survival simulation that respects the player's intelligence and builds genuine communication skills.

**Completion Goal**: "Has sobreviscut a Barcelona – Nivell 1" - You've survived Barcelona, Level 1. Ready for more? 🎒
