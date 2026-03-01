"""
Test Barcelona Survival Mode
=============================

This test demonstrates the new Barcelona Survival Mode:
- Real-life Catalan language scenarios
- Practical metro navigation skills
- Cultural context for each situation
- No English during gameplay (Catalan immersion)
- Completion unlocks "Supervivència Barcelona Nivell 1" badge

Run this test to see the survival mode in action.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.modes import SurvivalMode
from pathlib import Path


class SurvivalModeTestApp(App):
    """Test app for Barcelona Survival Mode"""
    
    def build(self):
        manager = ScreenManager()
        
        # Main test screen
        test_screen = Screen(name='test')
        container = FloatLayout()
        
        # Background
        with container.canvas.before:
            Color(0.05, 0.05, 0.08, 1)
            self.bg = container.canvas.before.add(
                RoundedRectangle(pos=container.pos, size=container.size, radius=[0])
            )
        container.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text='Barcelona Survival Mode - Test',
            font_size='28sp',
            bold=True,
            size_hint=(1, None),
            height=60,
            pos_hint={'center_x': 0.5, 'top': 0.98},
            color=(0.3, 0.9, 0.5, 1)
        )
        container.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text='Aprèn el català essencial per sobreviure al metro de Barcelona',
            font_size='16sp',
            italic=True,
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'top': 0.92},
            color=(0.7, 0.8, 0.9, 1)
        )
        container.add_widget(subtitle)
        
        # Initialize survival mode
        self.survival_mode = SurvivalMode()
        self.current_scenario_index = 0
        
        # Scenario display area (scrollable)
        scroll_view = ScrollView(
            size_hint=(0.9, 0.65),
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        
        self.scenario_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[20, 20],
            spacing=15
        )
        self.scenario_layout.bind(minimum_height=self.scenario_layout.setter('height'))
        
        scroll_view.add_widget(self.scenario_layout)
        container.add_widget(scroll_view)
        
        # Progress indicator
        self.progress_label = Label(
            text='',
            font_size='18sp',
            bold=True,
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'y': 0.15},
            color=(1, 0.85, 0.3, 1)
        )
        container.add_widget(self.progress_label)
        
        # Control buttons
        button_box = BoxLayout(
            orientation='horizontal',
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5, 'y': 0.05},
            spacing=15
        )
        
        prev_btn = Button(
            text='← Anterior',
            size_hint=(0.3, 1),
            background_normal="",
            background_color=(0.3, 0.4, 0.5, 1)
        )
        prev_btn.bind(on_release=lambda x: self.show_previous_scenario())
        button_box.add_widget(prev_btn)
        
        next_btn = Button(
            text='Següent →',
            size_hint=(0.3, 1),
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1)
        )
        next_btn.bind(on_release=lambda x: self.show_next_scenario())
        button_box.add_widget(next_btn)
        
        complete_btn = Button(
            text='Completar Mode',
            size_hint=(0.4, 1),
            background_normal="",
            background_color=(1, 0.6, 0.2, 1)
        )
        complete_btn.bind(on_release=lambda x: self.complete_survival_mode())
        button_box.add_widget(complete_btn)
        
        container.add_widget(button_box)
        
        # Load first scenario
        self.show_current_scenario()
        
        test_screen.add_widget(container)
        manager.add_screen(test_screen)
        
        return manager
    
    def _update_bg(self, *args):
        if hasattr(self, 'bg'):
            self.bg.pos = args[0].pos
            self.bg.size = args[0].size
    
    def show_current_scenario(self):
        """Display current scenario"""
        self.scenario_layout.clear_widgets()
        
        if self.current_scenario_index >= len(self.survival_mode.scenarios):
            # All scenarios shown
            completion_label = Label(
                text='Has vist tots els escenaris!\nFes clic a "Completar Mode" per desbloquejar la medalla.',
                font_size='20sp',
                bold=True,
                size_hint_y=None,
                height=100,
                color=(0.3, 1.0, 0.5, 1),
                halign='center'
            )
            completion_label.bind(
                size=lambda instance, value: setattr(instance, 'text_size', (value[0], None))
            )
            self.scenario_layout.add_widget(completion_label)
            self.update_progress()
            return
        
        scenario = self.survival_mode.scenarios[self.current_scenario_index]
        
        # Scenario title
        title = Label(
            text=f"📍 {scenario['title']}",
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=50,
            color=(0.3, 0.9, 0.5, 1),
            halign='left',
            valign='middle'
        )
        title.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        self.scenario_layout.add_widget(title)
        
        # Narrative (emotional framing)
        narrative_text = '\n'.join(scenario['narrative'])
        narrative = Label(
            text=f'[i]{narrative_text}[/i]',
            font_size='18sp',
            size_hint_y=None,
            height=60,
            color=(0.9, 0.9, 1.0, 1),
            markup=True,
            halign='left',
            valign='top'
        )
        narrative.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        self.scenario_layout.add_widget(narrative)
        
        # Question
        question = Label(
            text=f"❓ {scenario['question']}",
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=50,
            color=(1, 0.9, 0.5, 1),
            halign='left',
            valign='middle'
        )
        question.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        self.scenario_layout.add_widget(question)
        
        # Choices
        for i, choice in enumerate(scenario['choices']):
            choice_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=100,
                spacing=5
            )
            
            # Choice button
            choice_btn = Button(
                text=f"{chr(65+i)}) {choice['text']}",
                size_hint=(1, None),
                height=50,
                background_normal="",
                background_color=(0.2, 0.3, 0.4, 1) if not choice['correct'] else (0.2, 0.7, 0.3, 1)
            )
            
            # Feedback label (initially hidden)
            feedback = Label(
                text=f"💬 {choice['feedback']}",
                font_size='15sp',
                size_hint=(1, None),
                height=40,
                color=(0.3, 1.0, 0.5, 1) if choice['correct'] else (1.0, 0.5, 0.3, 1),
                opacity=0,
                italic=True,
                halign='left',
                valign='middle'
            )
            feedback.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.95, None)))
            
            # Bind button to show feedback
            choice_btn.bind(on_release=lambda x, f=feedback: self.show_feedback(f))
            
            choice_container.add_widget(choice_btn)
            choice_container.add_widget(feedback)
            self.scenario_layout.add_widget(choice_container)
        
        # Cultural context (collapsible)
        context_label = Label(
            text=f"ℹ️ Context cultural:\n{scenario['context']}",
            font_size='15sp',
            size_hint_y=None,
            height=80,
            color=(0.6, 0.7, 0.9, 1),
            italic=True,
            halign='left',
            valign='top'
        )
        context_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.95, None)))
        self.scenario_layout.add_widget(context_label)
        
        # Update progress
        self.update_progress()
    
    def show_feedback(self, feedback_label):
        """Show feedback for selected choice"""
        feedback_label.opacity = 1
    
    def show_next_scenario(self):
        """Show next scenario"""
        if self.current_scenario_index < len(self.survival_mode.scenarios) - 1:
            self.current_scenario_index += 1
            self.show_current_scenario()
    
    def show_previous_scenario(self):
        """Show previous scenario"""
        if self.current_scenario_index > 0:
            self.current_scenario_index -= 1
            self.show_current_scenario()
    
    def update_progress(self):
        """Update progress indicator"""
        total = len(self.survival_mode.scenarios)
        current = min(self.current_scenario_index + 1, total)
        self.progress_label.text = f'Escenari {current} de {total}'
    
    def complete_survival_mode(self):
        """Simulate completing survival mode"""
        # Load scenarios data to get completion message
        try:
            scenarios_path = Path(__file__).parent / "data" / "survival_scenarios_ca.json"
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                completion = data.get('completion', {})
        except Exception:
            completion = {
                'title': 'Enhorabona!',
                'message': 'Has sobreviscut a Barcelona – Nivell 1',
                'badge_id': 'survival_barcelona_1'
            }
        
        # Show completion overlay
        overlay = FloatLayout(size_hint=(1, 1))
        with overlay.canvas.before:
            Color(0, 0, 0, 0.9)
            overlay_bg = overlay.canvas.before.add(
                RoundedRectangle(pos=overlay.pos, size=overlay.size, radius=[0])
            )
        
        def update_overlay_bg(*args):
            overlay_bg.pos = overlay.pos
            overlay_bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)
        
        # Completion panel
        panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.7, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=20,
            padding=[30, 30]
        )
        
        with panel.canvas.before:
            Color(0.1, 0.15, 0.2, 1)
            panel_bg = RoundedRectangle(pos=panel.pos, size=panel.size, radius=[20])
            Color(0.3, 0.9, 0.5, 1)
            panel_border = RoundedRectangle(
                pos=(panel.x + 3, panel.y + 3),
                size=(panel.width - 6, panel.height - 6),
                radius=[18]
            )
        
        def update_panel_bg(*args):
            panel_bg.pos = panel.pos
            panel_bg.size = panel.size
            panel_border.pos = (panel.x + 3, panel.y + 3)
            panel_border.size = (panel.width - 6, panel.height - 6)
        panel.bind(pos=update_panel_bg, size=update_panel_bg)
        
        # Title
        title = Label(
            text=f"🎉 {completion['title']}",
            font_size='32sp',
            bold=True,
            size_hint=(1, None),
            height=60,
            color=(1, 0.9, 0.3, 1)
        )
        panel.add_widget(title)
        
        # Message
        message = Label(
            text=completion['message'],
            font_size='24sp',
            size_hint=(1, None),
            height=50,
            color=(0.3, 1.0, 0.5, 1),
            halign='center'
        )
        message.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        panel.add_widget(message)
        
        # Badge
        badge_label = Label(
            text=f"🎒 Medalla desbloquejada:\n{completion.get('description', '')}",
            font_size='18sp',
            size_hint=(1, None),
            height=80,
            color=(0.9, 0.9, 1.0, 1),
            halign='center',
            valign='middle'
        )
        badge_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
        panel.add_widget(badge_label)
        
        # Next level teaser
        next_level = Label(
            text=completion.get('next_level', ''),
            font_size='16sp',
            italic=True,
            size_hint=(1, None),
            height=40,
            color=(0.7, 0.8, 0.9, 1)
        )
        panel.add_widget(next_level)
        
        # Close button
        close_btn = Button(
            text='Tancar',
            size_hint=(0.5, None),
            height=50,
            pos_hint={'center_x': 0.5},
            background_normal="",
            background_color=(0.3, 0.9, 0.5, 1)
        )
        close_btn.bind(on_release=lambda x: self.root.remove_widget(overlay))
        panel.add_widget(close_btn)
        
        overlay.add_widget(panel)
        self.root.add_widget(overlay)


if __name__ == '__main__':
    print("="*70)
    print("BARCELONA SURVIVAL MODE - TEST")
    print("="*70)
    print("\nMode Features:")
    print("✓ Real-life Catalan language scenarios")
    print("✓ Practical metro navigation skills")
    print("✓ Cultural context for each situation")
    print("✓ Catalan immersion (no English during gameplay)")
    print("✓ Optional help button (not shown in this test)")
    print("✓ Completion unlocks 'Supervivència Barcelona Nivell 1' badge")
    print("\nScenarios included:")
    print("1. Comprar un bitllet (Buy a ticket)")
    print("2. Preguntar la direcció (Ask for directions)")
    print("3. Entendre 'Sortida' (Understand 'Exit')")
    print("4. Identificar la direcció (Identify train direction)")
    print("5. Llegir els cartells (Read signage)")
    print("6. Demanar un cafè (Order coffee)")
    print("7. Preguntar 'On és...?' (Ask 'Where is...?')")
    print("8. Entendre 'Andana' (Understand 'Platform')")
    print("9. Ser educat (Be polite)")
    print("10. Entendre 'Tancat' (Understand 'Closed')")
    print("\nEmotional framing:")
    print("→ You're arriving in Barcelona for the first time")
    print("→ The metro is your first challenge")
    print("\n" + "="*70 + "\n")
    
    SurvivalModeTestApp().run()
