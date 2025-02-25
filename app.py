import streamlit as st
import random
import pandas as pd
import numpy as np
import altair as alt
import time

# Set page configuration
st.set_page_config(
    page_title="Technology vs. Complexity",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Game logic class
class TechProgressGame:
    def __init__(self):
        # Game state
        self.turn = 0
        self.research_points = 100
        self.complexity = 10
        
        # Technology domains with different characteristics
        self.technologies = {
            'AI & Automation': {
                'level': 0, 
                'complexity_factor': 1.8,
                'description': 'Increases efficiency but creates high complexity through societal disruption',
                'research_bonus': 0.1,  # Increases research points per turn
                'icon': '🤖'
            },
            'Biotechnology': {
                'level': 0, 
                'complexity_factor': 1.5,
                'description': 'Provides health benefits but introduces ethical and safety challenges',
                'crisis_resistance': 0.1,  # Reduces crisis severity
                'icon': '🧬'
            },
            'Clean Energy': {
                'level': 0, 
                'complexity_factor': 0.8,
                'description': 'Reduces environmental complexity but requires new infrastructure',
                'complexity_reduction': 0.05,  # Reduces complexity growth rate
                'icon': '🌱'
            },
            'Information Systems': {
                'level': 0, 
                'complexity_factor': 1.3,
                'description': 'Helps manage complexity but introduces new vulnerabilities',
                'capacity_bonus': 0.1,  # Increases effectiveness of institutions
                'icon': '💾'
            }
        }
        
        # Social institutions with specific effects
        self.institutions = {
            'Education System': {
                'level': 1, 
                'capacity_factor': 1.8, 
                'cost': 15,
                'description': 'Increases public understanding and adaptation to new technologies',
                'icon': '🎓'
            },
            'Regulatory Framework': {
                'level': 1, 
                'capacity_factor': 1.5, 
                'cost': 18,
                'description': 'Manages technological risks and provides safety guidelines',
                'icon': '⚖️'
            },
            'Scientific Community': {
                'level': 1, 
                'capacity_factor': 1.7, 
                'cost': 20,
                'description': 'Assesses technologies and builds shared knowledge',
                'icon': '🔬'
            },
            'Social Safety Net': {
                'level': 1, 
                'capacity_factor': 1.4, 
                'cost': 12,
                'description': 'Protects people from disruption and helps adaptation',
                'icon': '🏥'
            }
        }
        
        # Game progression parameters
        self.complexity_growth_rate = 1.08  # 8% base increase per turn
        self.research_points_per_turn = 50
        self.crisis_threshold = 0.2  # Crisis happens when complexity exceeds capacity by this ratio
        self.complexity_components = {}  # For analysis
        
        # Game history tracking
        self.history = {
            'turns': [0],
            'complexity': [self.calculate_total_complexity()],
            'capacity': [self.calculate_total_social_capacity()],
            'research_points': [self.research_points],
            'crisis_events': [None]
        }
    
    def calculate_total_social_capacity(self):
        # Base capacity from institutions
        total_capacity = 0
        for inst, data in self.institutions.items():
            total_capacity += data['level'] * data['capacity_factor']
        
        # Add bonus from Information Systems if developed
        info_sys_level = self.technologies['Information Systems']['level']
        info_sys_bonus = info_sys_level * self.technologies['Information Systems']['capacity_bonus']
        capacity_multiplier = 1 + info_sys_bonus
        
        return total_capacity * capacity_multiplier
    
    def calculate_complexity_growth_modifier(self):
        # Determine if Clean Energy is reducing complexity growth
        energy_level = self.technologies['Clean Energy']['level']
        energy_reduction = energy_level * self.technologies['Clean Energy']['complexity_reduction']
        
        # More tech generally accelerates complexity
        tech_levels_sum = sum(tech['level'] for tech in self.technologies.values())
        tech_acceleration = 1 + (tech_levels_sum * 0.01)  # Each tech level increases growth by 1%
        
        # Final modifier (Clean Energy counteracts general acceleration)
        return tech_acceleration * (1 - energy_reduction)
    
    def calculate_total_complexity(self):
        # Base complexity
        base_complexity = self.complexity
        
        # Direct complexity from technologies
        tech_complexity = 0
        for tech, data in self.technologies.items():
            tech_complexity += data['level'] * data['complexity_factor']
        
        # Interaction effects between technologies (more technologies = more interaction complexity)
        tech_interaction = 0
        active_techs = [tech for tech, data in self.technologies.items() if data['level'] > 0]
        if len(active_techs) > 1:
            # The more different technologies at high levels, the more interaction complexity
            active_tech_data = [self.technologies[tech] for tech in active_techs]
            interaction_level = sum(tech['level'] for tech in active_tech_data) / len(active_techs)
            tech_interaction = (len(active_techs) - 1) * interaction_level * 0.5
        
        # Total complexity
        total = base_complexity + tech_complexity + tech_interaction
        
        # Store components for analysis
        self.complexity_components = {
            'base': base_complexity,
            'tech_direct': tech_complexity,
            'tech_interaction': tech_interaction,
            'total': total
        }
        
        return total
    
    def invest_in_technology(self, tech_name, amount):
        if tech_name not in self.technologies:
            return False, f"{tech_name} is not a valid technology domain"
        
        if amount > self.research_points:
            return False, "Not enough research points"
        
        # Calculate how many levels this buys (costs increase with level)
        current_level = self.technologies[tech_name]['level']
        cost_per_level = 10 + (current_level * 2)  # Increasing costs for higher levels
        levels_gained = amount // cost_per_level
        
        if levels_gained < 1:
            return False, f"Need at least {cost_per_level} points for one level"
        
        # Invest in technology
        self.technologies[tech_name]['level'] += levels_gained
        actual_cost = levels_gained * cost_per_level
        self.research_points -= actual_cost
        
        return True, f"Invested {actual_cost} points in {tech_name}, new level: {self.technologies[tech_name]['level']} (+{levels_gained})"
    
    def invest_in_institution(self, inst_name):
        if inst_name not in self.institutions:
            return False, f"{inst_name} is not a valid institution"
        
        inst = self.institutions[inst_name]
        cost = inst['cost'] * inst['level']  # Increasing costs for higher levels
        
        if cost > self.research_points:
            return False, f"Need {cost} points to upgrade {inst_name}, but only have {self.research_points}"
        
        # Invest in institution
        self.institutions[inst_name]['level'] += 1
        self.research_points -= cost
        
        return True, f"Upgraded {inst_name}, new level: {self.institutions[inst_name]['level']} (cost: {cost})"
    
    def next_turn(self):
        self.turn += 1
        
        # Calculate current complexity and capacity
        current_complexity = self.calculate_total_complexity()
        current_capacity = self.calculate_total_social_capacity()
        complexity_growth_modifier = self.calculate_complexity_growth_modifier()
        
        # Check for crisis
        crisis_event = None
        if current_complexity > current_capacity * (1 + self.crisis_threshold):
            # Crisis happens, severity based on how much complexity exceeds capacity
            severity = (current_complexity - current_capacity) / current_capacity
            crisis_event = self.trigger_crisis(severity)
        
        # Calculate research points bonus from AI & Automation
        ai_level = self.technologies['AI & Automation']['level']
        research_multiplier = 1 + (ai_level * self.technologies['AI & Automation']['research_bonus'])
        
        # Award new research points
        self.research_points += int(self.research_points_per_turn * research_multiplier)
        
        # Increase base complexity (representing advancing global technology)
        self.complexity *= self.complexity_growth_rate * complexity_growth_modifier
        
        # Update history
        self.history['turns'].append(self.turn)
        self.history['complexity'].append(current_complexity)
        self.history['capacity'].append(current_capacity)
        self.history['research_points'].append(self.research_points)
        self.history['crisis_events'].append(crisis_event)
        
        # Return turn summary
        return {
            'turn': self.turn,
            'research_points': self.research_points,
            'complexity': current_complexity,
            'capacity': current_capacity,
            'balance': current_capacity - current_complexity,
            'complexity_growth': f"{(self.complexity_growth_rate * complexity_growth_modifier - 1) * 100:.1f}%",
            'research_bonus': f"{(research_multiplier - 1) * 100:.1f}%",
            'crisis_event': crisis_event
        }
    
    def trigger_crisis(self, severity):
        crisis_events = [
            {
                "name": "Public Backlash", 
                "effect": "Research slowed",
                "description": "Public fear of technology leads to funding cuts and protests",
                "icon": "🗣️"
            },
            {
                "name": "Technological Accident", 
                "effect": "Complexity increased",
                "description": "An unforeseen interaction between technologies creates new risks",
                "icon": "💥"
            },
            {
                "name": "Institutional Failure", 
                "effect": "Capacity decreased",
                "description": "A key social institution proves unable to handle the pace of change",
                "icon": "🏚️"
            },
            {
                "name": "Resource Shortage", 
                "effect": "Research points reduced",
                "description": "Critical resources are depleted or misallocated amid complexity",
                "icon": "📉"
            }
        ]
        
        # Select a crisis based on severity
        crisis = random.choice(crisis_events)
        
        # Reduce severity if Biotechnology is advanced (better crisis management)
        biotech_level = self.technologies['Biotechnology']['level']
        crisis_resistance = biotech_level * self.technologies['Biotechnology']['crisis_resistance']
        adjusted_severity = severity * (1 - crisis_resistance)
        
        # Apply crisis effects
        if crisis["name"] == "Public Backlash":
            self.research_points_per_turn = max(10, int(self.research_points_per_turn * (1 - adjusted_severity/2)))
            message = f"Public backlash against technology reduced research funding. Points per turn now: {self.research_points_per_turn}"
        
        elif crisis["name"] == "Technological Accident":
            complexity_increase = int(self.complexity * adjusted_severity)
            self.complexity += complexity_increase
            message = f"A technological accident increased complexity by {complexity_increase}"
        
        elif crisis["name"] == "Institutional Failure":
            # Reduce a random institution's effectiveness
            institution = random.choice(list(self.institutions.keys()))
            level_reduction = max(1, int(self.institutions[institution]['level'] * adjusted_severity))
            self.institutions[institution]['level'] = max(1, self.institutions[institution]['level'] - level_reduction)
            message = f"{institution} suffered a setback, losing {level_reduction} levels"
        
        elif crisis["name"] == "Resource Shortage":
            loss = int(self.research_points * adjusted_severity)
            self.research_points = max(0, self.research_points - loss)
            message = f"Resource shortage resulted in the loss of {loss} research points"
        
        return {
            "name": crisis["name"],
            "description": crisis["description"],
            "message": message,
            "severity": severity,
            "adjusted_severity": adjusted_severity,
            "icon": crisis["icon"]
        }
    
    def game_status(self):
        # Check if game is over
        current_complexity = self.calculate_total_complexity()
        current_capacity = self.calculate_total_social_capacity()
        
        if current_complexity > current_capacity * 3:
            return "GAME OVER: Complexity catastrophically overwhelmed society's capacity"
        
        if self.turn >= 30:
            if current_capacity > current_complexity * 1.1:
                return "VICTORY: Achieved sustainable technological progress"
            elif current_capacity > current_complexity:
                return "PARTIAL VICTORY: Barely managing complexity"
            else:
                return "GAME OVER: Failed to manage complexity in the allotted time"
        
        return "ONGOING"

# Function to create progress charts
def create_history_chart(game):
    # Prepare the data
    chart_data = pd.DataFrame({
        'Turn': game.history['turns'],
        'Complexity': game.history['complexity'],
        'Absorption Capacity': game.history['capacity']
    })
    
    # Reshape for Altair
    chart_data_long = pd.melt(
        chart_data, 
        id_vars=['Turn'], 
        value_vars=['Complexity', 'Absorption Capacity'],
        var_name='Metric', 
        value_name='Value'
    )
    
    # Create and return the chart
    chart = alt.Chart(chart_data_long).mark_line(point=True).encode(
        x=alt.X('Turn:Q', title='Turn'),
        y=alt.Y('Value:Q', title='Level'),
        color=alt.Color('Metric:N', scale=alt.Scale(
            domain=['Complexity', 'Absorption Capacity'],
            range=['#FF6347', '#2E8B57']
        )),
        tooltip=['Turn', 'Metric', 'Value']
    ).properties(
        title='Progress Over Time',
        width=600,
        height=300
    ).interactive()
    
    return chart

# Function to create complexity breakdown chart
def create_complexity_chart(game):
    # Prepare data
    data = {
        'Source': ['Base Complexity', 'Technology Direct', 'Technology Interactions'],
        'Value': [
            game.complexity_components['base'],
            game.complexity_components['tech_direct'],
            game.complexity_components['tech_interaction']
        ]
    }
    chart_data = pd.DataFrame(data)
    
    # Create and return the chart
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Source:N', title=None),
        y=alt.Y('Value:Q', title='Complexity Contribution'),
        color=alt.Color('Source:N', scale=alt.Scale(
            domain=['Base Complexity', 'Technology Direct', 'Technology Interactions'],
            range=['#FFA07A', '#FF6347', '#8B0000']
        )),
        tooltip=['Source', 'Value']
    ).properties(
        title='Complexity Sources',
        width=300,
        height=200
    )
    
    return chart

# Function to create capacity breakdown chart
def create_capacity_chart(game):
    # Prepare data
    data = []
    for inst, inst_data in game.institutions.items():
        inst_capacity = inst_data['level'] * inst_data['capacity_factor']
        data.append({
            'Institution': inst,
            'Value': inst_capacity,
            'Icon': inst_data['icon']
        })
    
    chart_data = pd.DataFrame(data)
    
    # Create and return the chart
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Institution:N', title=None, sort='-y'),
        y=alt.Y('Value:Q', title='Capacity Contribution'),
        color=alt.Color('Institution:N', scale=alt.Scale(
            range=['#66CDAA', '#3CB371', '#2E8B57', '#006400']
        )),
        tooltip=['Institution', 'Value']
    ).properties(
        title='Capacity Sources',
        width=300,
        height=200
    )
    
    return chart

# Initialize the Streamlit session state
def init_session_state():
    if 'game' not in st.session_state:
        st.session_state.game = TechProgressGame()
        st.session_state.game_status = "ONGOING"
        st.session_state.message = ""
        st.session_state.turn_summary = None
        st.session_state.show_analysis = False
        st.session_state.tech_amount = 0
        st.session_state.selected_tech = None
        st.session_state.selected_inst = None
        st.session_state.actions_taken = 0
        st.session_state.max_actions = 2
        st.session_state.game_over = False
        st.session_state.restart = False

# Main Streamlit app
def main():
    # Initialize session state
    init_session_state()
    
    # Check for game restart
    if st.session_state.restart:
        st.session_state.game = TechProgressGame()
        st.session_state.game_status = "ONGOING"
        st.session_state.message = ""
        st.session_state.turn_summary = None
        st.session_state.show_analysis = False
        st.session_state.tech_amount = 0
        st.session_state.selected_tech = None
        st.session_state.selected_inst = None
        st.session_state.actions_taken = 0
        st.session_state.max_actions = 2
        st.session_state.game_over = False
        st.session_state.restart = False
    
    # Page title and introduction
    st.title("🧪 Technology vs. Complexity: Society's Balancing Act")
    
    # Sidebar with game information
    with st.sidebar:
        st.header("Game Information")
        st.markdown("""
        ### How to Play
        
        In this simulation, you manage society's technological development while building social capacity to handle complexity.
        
        **Key Concepts:**
        - Technologies advance capabilities but increase complexity
        - Social institutions help absorb and manage complexity
        - When complexity exceeds capacity, crises occur
        - The goal is sustainable progress, not just maximum technology
        
        **Game Rules:**
        - You have 2 actions per turn
        - You can invest in technologies or upgrade institutions
        - After each turn, complexity grows naturally
        - Game ends after 30 turns or if complexity overwhelms capacity
        """)
        
        # Only show restart button if game has started
        if st.session_state.turn_summary or st.session_state.game_over:
            if st.button("Restart Game"):
                st.session_state.restart = True
                st.experimental_rerun()
    
    # Game over screen
    if st.session_state.game_over:
        show_game_over()
        return
    
    # Game status indicators
    game = st.session_state.game
    
    # Main game area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Show turn information
        st.header(f"Turn {game.turn}/30")
        
        # Resource indicators
        col_rp, col_comp, col_cap = st.columns(3)
        with col_rp:
            st.metric("Research Points", f"{game.research_points}")
        
        current_complexity = game.calculate_total_complexity()
        current_capacity = game.calculate_total_social_capacity()
        balance = current_capacity - current_complexity
        
        with col_comp:
            st.metric("Complexity", f"{current_complexity:.1f}")
        
        with col_cap:
            st.metric("Absorption Capacity", f"{current_capacity:.1f}", 
                     delta=f"{balance:.1f}", 
                     delta_color="inverse")
        
        # System status
        if balance < 0:
            deficit_percent = abs(balance) / current_capacity * 100 if current_capacity > 0 else 100
            st.error(f"⚠️ WARNING: Complexity exceeds capacity by {deficit_percent:.1f}%")
            st.warning("Crisis risk is HIGH. Consider investing in social institutions.")
        elif balance < current_complexity * 0.1:
            st.warning("⚠️ System balance is CONCERNING. Complexity is rising faster than capacity.")
        else:
            st.success("✅ System balance is STABLE. Society is managing complexity well.")
        
        # Display historical chart
        st.altair_chart(create_history_chart(game), use_container_width=True)
        
        # Display message
        if st.session_state.message:
            st.info(st.session_state.message)
            
        # Display crisis alert
        if st.session_state.turn_summary and st.session_state.turn_summary.get('crisis_event'):
            crisis = st.session_state.turn_summary['crisis_event']
            st.error(f"### {crisis['icon']} CRISIS: {crisis['name']}")
            st.write(f"**What happened**: {crisis['description']}")
            st.write(f"**Impact**: {crisis['message']}")
            
            if game.technologies['Biotechnology']['level'] > 0:
                reduction = (crisis['severity'] - crisis['adjusted_severity']) / crisis['severity'] * 100
                st.info(f"🧬 Biotechnology reduced crisis severity by {reduction:.1f}%")
    
    with col2:
        # Actions section
        st.subheader(f"Actions ({st.session_state.actions_taken}/{st.session_state.max_actions} used)")
        
        # Available actions
        action_options = ["Select Action", "Invest in Technology", "Upgrade Institution", "View System Analysis", "End Turn"]
        
        # Disable options if max actions reached
        if st.session_state.actions_taken >= st.session_state.max_actions:
            action_options = ["Select Action", "View System Analysis", "End Turn"]
            
        action = st.selectbox("Choose an action:", action_options)
        
        if action == "Invest in Technology":
            st.write("##### Available Technologies")
            
            tech_options = []
            for tech, data in game.technologies.items():
                current_level = data['level']
                cost_per_level = 10 + (current_level * 2)
                tech_options.append(f"{data['icon']} {tech} (Cost: {cost_per_level} per level)")
            
            selected_tech_display = st.selectbox("Select technology:", tech_options)
            
            if selected_tech_display:
                # Extract tech name from display string
                tech_name = selected_tech_display.split(" (")[0]
                tech_name = tech_name[2:]  # Remove icon
                st.session_state.selected_tech = tech_name
                
                # Show tech details
                data = game.technologies[tech_name]
                current_level = data['level']
                cost_per_level = 10 + (current_level * 2)
                
                st.write(f"**Current Level**: {current_level}")
                st.write(f"**Cost per level**: {cost_per_level}")
                st.write(f"**Description**: {data['description']}")
                
                # Special effect
                if 'research_bonus' in data:
                    bonus = data['level'] * data['research_bonus'] * 100
                    st.write(f"**Research Bonus**: +{bonus:.1f}%")
                elif 'crisis_resistance' in data:
                    resist = data['level'] * data['crisis_resistance'] * 100
                    st.write(f"**Crisis Resistance**: +{resist:.1f}%")
                elif 'complexity_reduction' in data:
                    reduction = data['level'] * data['complexity_reduction'] * 100
                    st.write(f"**Complexity Growth Reduction**: -{reduction:.1f}%")
                elif 'capacity_bonus' in data:
                    cap_bonus = data['level'] * data['capacity_bonus'] * 100
                    st.write(f"**Capacity Effectiveness**: +{cap_bonus:.1f}%")
                
                # Amount input
                max_amount = game.research_points
                max_levels = max_amount // cost_per_level
                st.write(f"You can afford up to {max_levels} levels")
                
                amount = st.slider("Research points to invest:", 
                                 min_value=0, 
                                 max_value=max_amount, 
                                 value=min(cost_per_level, max_amount),
                                 step=cost_per_level)
                
                if st.button("Invest"):
                    success, message = game.invest_in_technology(tech_name, amount)
                    st.session_state.message = message
                    
                    if success:
                        st.session_state.actions_taken += 1
                    
                    st.experimental_rerun()
        
        elif action == "Upgrade Institution":
            st.write("##### Available Institutions")
            
            # Use institution keys directly from the dictionary
            inst_options = list(game.institutions.keys())
            
            # Format function to display institutions with icons and costs
            def format_institution(inst_key):
                data = game.institutions[inst_key]
                cost = data['cost'] * data['level']
                return f"{data['icon']} {inst_key} (Cost: {cost})"
            
            # Use the direct key selection with a formatter
            selected_inst = st.selectbox("Select institution:", inst_options, format_func=format_institution)
            
            if selected_inst:
                # Now we can safely access the institution data using the selected key
                data = game.institutions[selected_inst]
                current_level = data['level']
                cost = data['cost'] * current_level
                
                st.write(f"**Current Level**: {current_level}")
                st.write(f"**Upgrade cost**: {cost}")
                st.write(f"**Description**: {data['description']}")
                
                if game.research_points < cost:
                    st.error(f"You don't have enough research points for this upgrade")
                    can_upgrade = False
                else:
                    can_upgrade = True
                
                if st.button("Upgrade", disabled=not can_upgrade):
                    success, message = game.invest_in_institution(selected_inst)
                    st.session_state.message = message
                    
                    if success:
                        st.session_state.actions_taken += 1
                    
                    st.rerun()
        
        elif action == "View System Analysis":
            st.session_state.show_analysis = True
            show_system_analysis(game)
        
        elif action == "End Turn":
            # End turn
            if st.button("End Turn"):
                with st.spinner("Processing turn..."):
                    turn_summary = game.next_turn()
                    st.session_state.turn_summary = turn_summary
                    st.session_state.actions_taken = 0
                    st.session_state.message = ""
                    
                    # Check game status
                    game_status = game.game_status()
                    st.session_state.game_status = game_status
                    
                    if game_status != "ONGOING":
                        st.session_state.game_over = True
                
                st.rerun()
    
    # Show analysis if requested
    if st.session_state.show_analysis:
        show_system_analysis(game)

def show_system_analysis(game):
    st.markdown("---")
    st.header("System Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Complexity breakdown
        st.altair_chart(create_complexity_chart(game), use_container_width=True)
        
        # Growth rates
        complexity_growth = game.complexity_growth_rate * game.calculate_complexity_growth_modifier()
        st.metric("Complexity Growth Rate", f"{(complexity_growth - 1) * 100:.1f}% per turn")
    
    with col2:
        # Capacity breakdown
        st.altair_chart(create_capacity_chart(game), use_container_width=True)
    
    # Technology synergies
    st.subheader("Key Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        if game.technologies['Clean Energy']['level'] > 0:
            reduction = game.technologies['Clean Energy']['level'] * game.technologies['Clean Energy']['complexity_reduction'] * 100
            st.success(f"🌱 Clean Energy is helping slow complexity growth by {reduction:.1f}%")
        
        if game.technologies['AI & Automation']['level'] > 0:
            bonus = game.technologies['AI & Automation']['level'] * game.technologies['AI & Automation']['research_bonus'] * 100
            st.info(f"🤖 AI is increasing research efficiency by {bonus:.1f}%")
    
    with col2:
        if game.technologies['Biotechnology']['level'] > 0:
            resist = game.technologies['Biotechnology']['level'] * game.technologies['Biotechnology']['crisis_resistance'] * 100
            st.success(f"🧬 Biotechnology is improving crisis resilience by {resist:.1f}%")
        
        if game.technologies['Information Systems']['level'] > 0:
            cap_bonus = game.technologies['Information Systems']['level'] * game.technologies['Information Systems']['capacity_bonus'] * 100
            st.info(f"💾 Information Systems are enhancing institutional effectiveness by {cap_bonus:.1f}%")
    
    if st.button("Close Analysis"):
        st.session_state.show_analysis = False
        st.experimental_rerun()

def show_game_over():
    game = st.session_state.game
    status = st.session_state.game_status
    
    # Game over header
    if "VICTORY" in status:
        st.balloons()
        st.success(f"# 🏆 {status}")
    else:
        st.error(f"# ⚠️ {status}")
    
    # Final stats
    final_complexity = game.calculate_total_complexity()
    final_capacity = game.calculate_total_social_capacity()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Turn", f"{game.turn}/30")
    with col2:
        st.metric("Final Complexity", f"{final_complexity:.1f}")
    with col3:
        st.metric("Final Capacity", f"{final_capacity:.1f}", 
                 delta=f"{final_capacity - final_complexity:.1f}",
                 delta_color="inverse")
    
    # Historical chart
    st.subheader("Your Journey")
    st.altair_chart(create_history_chart(game), use_container_width=True)
    
    # Feedback based on play style
    st.subheader("Your Approach")
    
    tech_levels = sum(tech['level'] for tech in game.technologies.values())
    inst_levels = sum(inst['level'] for inst in game.institutions.values())
    
    if tech_levels > inst_levels * 1.5:
        st.write("You prioritized technological advancement over social capacity. This created rapid progress but high instability.")
    elif inst_levels > tech_levels * 1.5:
        st.write("You focused heavily on building social institutions. This created stability but may have slowed potential progress.")
    else:
        st.write("You maintained a balanced approach to progress, both advancing technology and building social capacity.")
    
    # Technology breakdown
    st.subheader("Technology Development")
    tech_data = []
    for tech, data in game.technologies.items():
        tech_data.append({
            'Technology': f"{data['icon']} {tech}",
            'Level': data['level']
        })
    
    tech_df = pd.DataFrame(tech_data)
    
    # Create bar chart for technologies
    tech_chart = alt.Chart(tech_df).mark_bar().encode(
        x=alt.X('Level:Q', title='Level Achieved'),
        y=alt.Y('Technology:N', title=None, sort='-x'),
        color=alt.Color('Technology:N', legend=None)
    ).properties(
        title='Technology Levels',
        width=600,
        height=200
    )
    
    st.altair_chart(tech_chart, use_container_width=True)
    
    # Institution breakdown
    st.subheader("Social Institutions")
    inst_data = []
    for inst, data in game.institutions.items():
        inst_data.append({
            'Institution': f"{data['icon']} {inst}",
            'Level': data['level']
        })
    
    inst_df = pd.DataFrame(inst_data)
    
    # Create bar chart for institutions
    inst_chart = alt.Chart(inst_df).mark_bar().encode(
        x=alt.X('Level:Q', title='Level Achieved'),
        y=alt.Y('Institution:N', title=None, sort='-x'),
        color=alt.Color('Institution:N', legend=None)
    ).properties(
        title='Institution Levels',
        width=600,
        height=200
    )
    
    st.altair_chart(inst_chart, use_container_width=True)
    
    # Educational summary
    st.subheader("Lessons From Your Simulation")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("#### Technology and Complexity")
        st.markdown("""
        - Technology creates both opportunities and complexities
        - Different technologies interact to create additional complexity
        - Some technologies can help manage complexity (like Clean Energy)
        - Balanced technological development is more sustainable
        """)
    
    with col2:
        st.success("#### Social Capacity")
        st.markdown("""
        - Social systems need to evolve alongside technology
        - Crisis occurs when complexity outpaces absorption capacity
        - Different institutions address different aspects of complexity
        - Sustainable progress requires balance and foresight
        """)
    
    # Restart button
    if st.button("Play Again"):
        st.session_state.restart = True
        st.experimental_rerun()

# Entry point
if __name__ == "__main__":
    main()
