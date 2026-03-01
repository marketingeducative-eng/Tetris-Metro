# Barcelona Survival Mode - Quick Integration Guide

## 5-Minute Integration

### Step 1: Import the Mode

```python
from core.modes import SurvivalMode
```

### Step 2: Initialize and Set Mode

```python
# Create survival mode instance
survival_mode = SurvivalMode()

# Set on game engine
engine.set_mode(survival_mode)
```

### Step 3: Handle Scenario Display (in Renderer)

```python
def show_survival_scenario(self):
    """Display current survival scenario"""
    scenario = self.state.mode.get_current_scenario()
    
    if not scenario:
        # Mode complete
        self.show_survival_complete()
        return
    
    # Display narrative (2 lines)
    narrative_text = '\n'.join(scenario['narrative'])
    self.narrative_label.text = narrative_text
    
    # Display question
    self.question_label.text = scenario['question']
    
    # Display choices as tokens/buttons
    for i, choice in enumerate(scenario['choices']):
        token = self.create_choice_token(
            text=choice['text'],
            is_correct=choice['correct'],
            feedback=choice['feedback']
        )
        self.add_token(token)
    
    # Display cultural context (optional, collapsible)
    self.context_label.text = scenario['context']
```

### Step 4: Handle Choice Selection

```python
def on_choice_selected(self, choice):
    """Handle player selecting a choice"""
    # Show feedback
    self.show_feedback(choice['feedback'])
    
    if choice['correct']:
        # Correct answer - advance scenario
        self.state.mode.on_correct(self.state, None)
        
        # Check if mode complete
        if self.state.mode.is_complete():
            self.show_survival_complete()
        else:
            # Show next scenario
            self.schedule_event(self.show_survival_scenario, 2.0)
    else:
        # Wrong answer - track attempt
        self.state.mode.on_wrong(self.state, None)
        
        # Allow retry
        self.show_feedback("Torna-ho a provar!")
```

### Step 5: Handle Completion

```python
def show_survival_complete(self):
    """Show completion overlay with badge"""
    # Load completion data
    import json
    from pathlib import Path
    
    scenarios_path = Path(__file__).parent / "data" / "survival_scenarios_ca.json"
    with open(scenarios_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        completion = data['completion']
    
    # Display completion overlay
    overlay = FloatLayout()
    
    # Title
    title = Label(
        text=f"🎉 {completion['title']}",
        font_size='32sp',
        bold=True
    )
    
    # Message
    message = Label(
        text=completion['message'],
        font_size='24sp',
        color=(0.3, 1.0, 0.5, 1)
    )
    
    # Badge
    badge = Label(
        text=f"🎒 {completion['description']}",
        font_size='18sp'
    )
    
    # Add to overlay
    # ... (your layout code here)
    
    # Unlock badge in progress manager
    if hasattr(self.parent, 'progress_manager'):
        self.parent.progress_manager.unlock_badge('survival_barcelona_1')
```

## Optional: Add Help Button

```python
def add_help_button(self):
    """Add optional English help button"""
    help_btn = Button(
        text="? English Help",
        size_hint=(None, None),
        size=(120, 36),
        pos_hint={'right': 0.98, 'top': 0.98}
    )
    help_btn.bind(on_release=self.show_english_help)
    self.parent.add_widget(help_btn)

def show_english_help(self, *args):
    """Show English translation overlay"""
    scenario = self.state.mode.get_current_scenario()
    
    # Create overlay with English translations
    overlay = FloatLayout()
    
    # Title
    title = Label(text="English Help", font_size='24sp')
    
    # Translations
    translations = Label(
        text=(
            f"SITUATION:\n"
            f"{self._translate_narrative(scenario['narrative'])}\n\n"
            f"QUESTION:\n"
            f"{self._translate_question(scenario['question'])}\n\n"
            f"CONTEXT:\n"
            f"{self._translate_context(scenario['context'])}"
        ),
        halign='left'
    )
    
    # Close button
    close_btn = Button(text="Tancar", on_release=lambda x: self.parent.remove_widget(overlay))
    
    # Add to overlay
    # ... (your layout code)
```

## Progress Tracking

```python
# Get scenario progress
completed, total = engine.mode.get_scenario_progress()
progress_text = f"Escenari {completed+1} de {total}"

# Update progress bar
progress_ratio = completed / total
self.progress_bar.width = self.progress_bar_container.width * progress_ratio

# Check completion
if engine.mode.is_complete():
    print("Survival Mode completed!")
    # Show completion, unlock badge, etc.
```

## Testing Your Integration

```bash
# Run the test file to see the mode in action
python test_survival_mode.py
```

## Common Patterns

### Pattern 1: Scenario Loop

```python
def start_survival_mode(self):
    """Start survival mode gameplay loop"""
    self.show_survival_scenario()

def show_survival_scenario(self):
    scenario = self.state.mode.get_current_scenario()
    if scenario:
        # Display scenario
        self._display_scenario(scenario)
    else:
        # Mode complete
        self.show_survival_complete()

def on_choice_selected(self, choice):
    if choice['correct']:
        self.state.mode.on_correct(self.state, None)
        self.schedule_event(self.show_survival_scenario, 2.0)
    else:
        self.state.mode.on_wrong(self.state, None)
        # Allow retry
```

### Pattern 2: Visual Feedback

```python
def show_choice_feedback(self, choice):
    """Show visual feedback for choice"""
    if choice['correct']:
        # Green flash
        self.flash_color((0.2, 1.0, 0.3, 1))
        # Play success sound
        self.audio.play_success()
    else:
        # Red flash
        self.flash_color((1.0, 0.3, 0.2, 1))
        # Play error sound
        self.audio.play_error()
    
    # Show feedback text
    self.feedback_label.text = choice['feedback']
```

### Pattern 3: Context Expansion

```python
def toggle_context_visibility(self):
    """Toggle cultural context visibility"""
    if self.context_label.opacity == 0:
        # Expand
        Animation(
            opacity=1,
            height=80,
            duration=0.3
        ).start(self.context_label)
    else:
        # Collapse
        Animation(
            opacity=0,
            height=0,
            duration=0.3
        ).start(self.context_label)
```

## Data Structure Reference

### Scenario Object

```python
scenario = {
    'id': 'buy_ticket',                    # Unique identifier
    'title': 'Comprar un bitllet',         # Scenario title
    'narrative': [                         # 2-line emotional setup
        'Estàs a l\'estació.',
        'Necessites comprar un bitllet.'
    ],
    'context': 'Cultural explanation...',  # Educational context
    'task_type': 'choice',                 # Task type (currently only 'choice')
    'question': 'Què has de demanar?',     # Question text
    'choices': [                           # 3 choice options
        {
            'text': 'Un bitllet senzill, si us plau',
            'correct': True,
            'feedback': 'Perfecte! Això et durà un viatge.'
        },
        # ... 2 more choices
    ]
}
```

## Troubleshooting

### Issue: Scenarios not loading

**Check:**
1. File exists: `data/survival_scenarios_ca.json`
2. JSON is valid (no syntax errors)
3. File encoding is UTF-8

**Solution:**
```python
# Add error handling to mode initialization
try:
    survival_mode = SurvivalMode()
    if not survival_mode.scenarios:
        print("ERROR: No scenarios loaded!")
except Exception as e:
    print(f"ERROR loading survival mode: {e}")
```

### Issue: Badge not unlocking

**Check:**
1. Badge defined in `core/badges.py`
2. Badge ID matches: `'survival_barcelona_1'`
3. Progress manager is initialized

**Solution:**
```python
# Verify badge exists
from core.badges import BADGE_DEFINITIONS
if 'survival_barcelona_1' in BADGE_DEFINITIONS:
    print("Badge definition found")
else:
    print("ERROR: Badge not defined!")

# Check progress manager
if hasattr(self.parent, 'progress_manager'):
    print("Progress manager available")
else:
    print("ERROR: No progress manager!")
```

### Issue: Wrong scenario appearing

**Check:**
1. Current scenario index
2. Scenario completion tracking

**Solution:**
```python
# Debug scenario state
mode = engine.mode
print(f"Current index: {mode.current_scenario_index}")
print(f"Completed: {mode.completed_scenarios}")
print(f"Total scenarios: {len(mode.scenarios)}")
```

## Performance Considerations

- **Lazy Loading**: Scenarios loaded once at mode initialization
- **Minimal State**: Only tracks current index and completed set
- **No Heavy Processing**: All logic is simple conditionals
- **Memory**: ~50KB for scenario data (negligible)

## Accessibility

Consider adding:
- Font size controls
- High contrast mode
- Screen reader support
- Keyboard navigation
- Audio narration (TTS)

## Localization

Currently Catalan-only. To add languages:

```python
# Structure scenarios with language keys
{
    'id': 'buy_ticket',
    'title': {
        'ca': 'Comprar un bitllet',
        'en': 'Buy a ticket',
        'es': 'Comprar un billete'
    },
    # ... etc
}
```

## Related Documentation

- Full documentation: [BARCELONA_SURVIVAL_MODE.md](BARCELONA_SURVIVAL_MODE.md)
- Mode implementation: [core/modes.py](core/modes.py)
- Scenarios data: [data/survival_scenarios_ca.json](data/survival_scenarios_ca.json)
- Test suite: [test_survival_mode.py](test_survival_mode.py)

## Support

For questions or issues, check:
1. This quick guide
2. Full documentation (BARCELONA_SURVIVAL_MODE.md)
3. Test file (test_survival_mode.py) for example usage
4. Mode source code (core/modes.py) for implementation details
