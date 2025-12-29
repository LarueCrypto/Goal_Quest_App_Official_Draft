# Import character visuals
from character_visuals import get_character_svg, get_stat_visual_bars, get_level_up_animation, get_equipment_display
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from database import Database
from achievements import initialize_achievements, ALL_ACHIEVEMENTS
from ai_coach import AICoach
from shop_items import ALL_SHOP_ITEMS, RARITY_COLORS, get_items_by_category, get_item_by_id, can_afford, meets_level_requirement
from utils import *
import json

# Page config
st.set_page_config(
    page_title="Goal Quest",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with animations and glows
st.markdown("""
<style>
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
        border-right: 2px solid #d4af37;
    }
    
    h1, h2, h3 {
        color: #d4af37;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        font-family: 'Cinzel', serif;
        letter-spacing: 2px;
    }
    
    [data-testid="stMetricValue"] {
        color: #d4af37;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 0 0 15px rgba(212, 175, 55, 0.6);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #d4af37 0%, #f1c40f 100%);
        color: #0a0a0a;
        border: 2px solid #ffd700;
        border-radius: 12px;
        font-weight: bold;
        padding: 12px 24px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #ffd700 0%, #d4af37 100%);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.7);
        transform: translateY(-2px);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #d4af37 0%, #ffd700 100%);
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.8);
    }
    
    .stCheckbox {
        color: #ffffff;
    }
    
    .achievement-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #d4af37;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
    }
    
    .shop-item {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 3px solid;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .shop-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.8);
    }
    
    .shop-item::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .stat-display {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        border: 2px solid #d4af37;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    
    .quote-box {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        border-left: 5px solid #d4af37;
        padding: 20px;
        margin: 20px 0;
        border-radius: 10px;
        font-style: italic;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    .level-badge {
        display: inline-block;
        background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
        color: #0a0a0a;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(212, 175, 55, 0.5);
    }
    
    .xp-glow {
        animation: xpPulse 2s infinite;
    }
    
    @keyframes xpPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; text-shadow: 0 0 20px #d4af37; }
    }
    
    p, span, label {
        color: #ffffff;
    }
    
    .stSelectbox, .stTextInput, .stTextArea {
        color: #ffffff;
    }
    
    [data-baseweb="select"] {
        background-color: #2d2d2d;
    }
    
    input, textarea {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 2px solid #d4af37 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()
    initialize_achievements(st.session_state.db)

if 'ai_coach' not in st.session_state:
    api_key = st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, 'secrets') else None
    st.session_state.ai_coach = AICoach(api_key)

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

db = st.session_state.db
ai_coach = st.session_state.ai_coach

# Get user profile and stats
profile = db.get_profile()
stats = db.get_stats()

# ===== ONBOARDING FLOW =====
if not profile.get('onboarding_completed'):
    st.markdown("<h1 style='text-align: center;'>⚔️ WELCOME TO GOAL QUEST</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #d4af37;'>Your Journey to Power Begins Here</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.form("onboarding_form"):
        st.markdown("### 👤 Hunter Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            display_name = st.text_input("What shall we call you?", value="Hunter", help="Your name in this world")
            
            gender = st.selectbox(
                "Gender",
                options=["neutral", "male", "female"],
                format_func=lambda x: {"neutral": "⚖️ Neutral", "male": "⚔️ Male", "female": "🛡️ Female"}[x]
            )
            
            avatar_style = st.selectbox(
                "Choose Your Path",
                options=["warrior", "mage", "rogue", "sage"],
                format_func=lambda x: {
                    "warrior": "⚔️ Warrior - Strength and discipline",
                    "mage": "🔮 Mage - Intelligence and wisdom", 
                    "rogue": "🗡️ Rogue - Agility and cunning",
                    "sage": "📿 Sage - Balance and enlightenment"
                }[x],
                help="Your combat style and stat bonuses"
            )
        
        with col2:
            philosophy_tradition = st.selectbox(
                "Primary Wisdom Tradition",
                options=["esoteric", "kemetic", "samurai", "biblical", "quranic", "stoic", "eastern", "occult"],
                format_func=lambda x: {
                    "esoteric": "🔯 Esoteric - Hermetic mysteries",
                    "kemetic": "𓂀 Kemetic - Ancient Egyptian wisdom",
                    "samurai": "🗾 Samurai - Bushido code",
                    "biblical": "✝️ Biblical - Christian teachings",
                    "quranic": "☪️ Quranic - Islamic wisdom",
                    "stoic": "🏛️ Stoic - Greco-Roman philosophy",
                    "eastern": "☯️ Eastern - Tao and Zen",
                    "occult": "🕯️ Occult - Left-hand path mysteries"
                }[x],
                help="The source of your daily wisdom"
            )
            
            st.markdown("**Additional Traditions** (optional)")
            philosophy_traditions = st.multiselect(
                "Secondary wisdom sources",
                options=["esoteric", "kemetic", "samurai", "biblical", "quranic", "stoic", "eastern", "occult"],
                default=[],
                label_visibility="collapsed"
            )
        
        st.markdown("### 🎯 Focus Areas")
        focus_areas = st.multiselect(
            "What are your primary goals?",
            options=["fitness", "health", "career", "relationships", "creativity", "mindfulness", "learning", "wealth"],
            default=["fitness", "mindfulness"],
            help="Areas you want to develop"
        )
        
        st.markdown("### 🔥 Challenge Approach")
        challenge_approaches = st.multiselect(
            "How do you approach challenges?",
            options=["discipline", "curiosity", "competition", "spirituality", "logic", "intuition"],
            default=["discipline"],
            help="This customizes your experience"
        )
        
        submitted = st.form_submit_button("🚀 BEGIN YOUR QUEST", use_container_width=True)
        
        if submitted:
            db.update_profile(
                display_name=display_name,
                gender=gender,
                avatar_style=avatar_style,
                philosophy_tradition=philosophy_tradition,
                philosophy_traditions=philosophy_traditions,
                focus_areas=focus_areas,
                challenge_approaches=challenge_approaches,
                onboarding_completed=True
            )
            
            # Unlock first achievement
            db.unlock_achievement("first_login")
            db.unlock_achievement("profile_complete")
            
            st.success("✨ Your legend begins now!")
            st.balloons()
            st.rerun()

else:
    # ===== SIDEBAR NAVIGATION =====
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>⚔️ GOAL QUEST</h1>", unsafe_allow_html=True)
        
        # User Profile Card
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); border-radius: 15px; border: 2px solid #d4af37; margin-bottom: 20px;'>
            <h2 style='margin: 0;'>{profile.get('display_name', 'Hunter')}</h2>
            <p style='margin: 5px 0; color: #d4af37;'>{profile.get('avatar_style', 'warrior').capitalize()}</p>
            <div class='level-badge'>LEVEL {stats.get('level', 1)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # XP Progress
        current_xp = stats.get('current_xp', 0)
        level = stats.get('level', 1)
        xp_needed = level * 500
        progress = current_xp / xp_needed if xp_needed > 0 else 0
        
        st.progress(progress)
        st.markdown(f"<p style='text-align: center;' class='xp-glow'>⚡ XP: {current_xp:,} / {xp_needed:,}</p>", unsafe_allow_html=True)
        
        # Gold Counter with glow
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: 10px; border: 2px solid #ffd700; margin: 10px 0;'>
            <h3 style='margin: 0; color: #ffd700;'>💰 {stats.get('current_gold', 0):,} Gold</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Buttons
        st.markdown("### 🗺️ Navigation")
        
        pages = {
            "🏠 Dashboard": "Dashboard",
            "⚡ Habits": "Habits",
            "🎯 Goals": "Goals",
            "🤖 AI Coach": "AI Coach",
            "📚 Library": "Library",
            "🛒 Shop": "Shop",
            "🎒 Inventory": "Inventory",
            "📊 Analytics": "Analytics",
            "📝 Notes": "Notes",
            "🏆 Achievements": "Achievements",
            "⚙️ Settings": "Settings"
        }
        
        for label, page_name in pages.items():
            if st.button(label, key=page_name, use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

    # ===== MAIN CONTENT AREA =====
    current_page = st.session_state.page

    # ===== DASHBOARD PAGE =====
    if current_page == "Dashboard":
        user_name = profile.get('display_name', 'Hunter')
        
        st.title(f"🏠 {user_name}'s Command Center")
        st.markdown(f"<p style='font-size: 1.2em; color: #d4af37;'>Welcome back, {user_name}! Ready to continue your journey?</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # CHARACTER DISPLAY - Simplified working version
        col_char, col_stats = st.columns([1, 1])
        
        # Get equipped items safely (FIX APPLIED)
        equipped = db.get_equipped_items() or {}
        
        with col_char:
            st.markdown("### 👤 Your Hunter")
            
            # Character card with level-based appearance
            level = stats.get('level', 1)
            avatar_style = profile.get('avatar_style', 'warrior')
            
            # Determine stage
            if level >= 76:
                stage_name = "Shadow Monarch"
                stage_icon = "👑"
                border_color = "#FFD700"
                glow = "0 0 30px rgba(255, 215, 0, 0.8)"
            elif level >= 51:
                stage_name = "S-Rank Hunter"
                stage_icon = "⚔️"
                border_color = "#FFA500"
                glow = "0 0 25px rgba(255, 165, 0, 0.6)"
            elif level >= 26:
                stage_name = "Elite Hunter"
                stage_icon = "🛡️"
                border_color = "#d4af37"
                glow = "0 0 20px rgba(212, 175, 55, 0.5)"
            elif level >= 11:
                stage_name = "Skilled Hunter"
                stage_icon = "🗡️"
                border_color = "#C0C0C0"
                glow = "0 0 15px rgba(192, 192, 192, 0.4)"
            else:
                stage_name = "Novice Hunter"
                stage_icon = "⚡"
                border_color = "#808080"
                glow = "0 0 10px rgba(128, 128, 128, 0.3)"
            
            # Avatar style icons
            style_icons = {
                'warrior': '⚔️',
                'mage': '🔮',
                'rogue': '🗡️',
                'sage': '📿'
            }
            
            main_icon = style_icons.get(avatar_style, '⚔️')
            
            # Render character card
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                padding: 40px;
                border-radius: 20px;
                border: 4px solid {border_color};
                box-shadow: {glow};
                text-align: center;
                margin: 20px 0;
            '>
                <div style='font-size: 120px; margin-bottom: 20px;'>{main_icon}</div>
                <div style='font-size: 48px; margin-bottom: 10px;'>{stage_icon}</div>
                <h2 style='color: #d4af37; margin: 10px 0;'>{user_name}</h2>
                <p style='color: #ffffff; font-size: 1.2em; margin: 5px 0;'>{stage_name}</p>
                <p style='color: #aaaaaa; margin: 5px 0;'>{avatar_style.capitalize()}</p>
                
                <div style='
                    background: linear-gradient(90deg, #d4af37 0%, #ffd700 100%);
                    padding: 15px;
                    border-radius: 15px;
                    margin-top: 20px;
                '>
                    <p style='color: #0a0a0a; font-size: 1.5em; font-weight: bold; margin: 0;'>
                        LEVEL {level}
                    </p>
                </div>
                
                <div style='margin-top: 20px;'>
                    <p style='color: #ffd700; font-size: 1.3em; margin: 5px 0;'>
                        💰 {stats.get('current_gold', 0):,} Gold
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Equipment Display
            st.markdown("#### ⚔️ Equipment")
            
            eq_cols = st.columns(2)
            slots = [
                ('weapon_id', '⚔️', 'Weapon'),
                ('armor_id', '🛡️', 'Armor'),
                ('ring_id', '💍', 'Ring'),
                ('amulet_id', '📿', 'Amulet')
            ]
            
            for idx, (slot, icon, name) in enumerate(slots):
                with eq_cols[idx % 2]:
                    item_id = equipped.get(slot, '')
                    if item_id:
                        item_name = item_id.replace('_', ' ').title()
                        st.markdown(f"""
                        <div style='
                            background: #2d2d2d;
                            padding: 10px;
                            border-radius: 8px;
                            border: 2px solid #d4af37;
                            margin: 5px 0;
                        '>
                            <div style='font-size: 24px;'>{icon}</div>
                            <div style='color: #d4af37; font-size: 0.9em;'>{name}</div>
                            <div style='color: #ffffff; font-size: 0.8em;'>{item_name}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.caption(f"{icon} {name}: Empty")
        
        with col_stats:
            st.markdown(f"### 📊 {user_name}'s Power")
            
            # Display stats as metrics
            stats_config = {
                'strength': '⚔️',
                'intelligence': '🧠',
                'vitality': '❤️',
                'agility': '⚡',
                'sense': '👁️',
                'willpower': '🔥'
            }
            
            stat_cols = st.columns(2)
            for idx, (stat, icon) in enumerate(stats_config.items()):
                with stat_cols[idx % 2]:
                    value = stats.get(stat, 0)
                    st.metric(f"{icon} {stat.capitalize()}", value)
            
            st.markdown("---")
            
            # Quick stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("⚡ Total XP", format_xp(stats.get('total_xp', 0)))
                st.metric("💰 Gold", f"{stats.get('current_gold', 0):,}")
            with col2:
                habits = db.get_habits()
                max_streak = 0
                if habits:
                    for habit in habits:
                        completions = db.get_completions(habit['id'])
                        streak = calculate_streak(completions)
                        max_streak = max(max_streak, streak)
                st.metric("🔥 Best Streak", max_streak)
                
                today = get_cst_date()
                completed_today = sum(1 for h in habits if db.is_completed(h['id'], today))
                st.metric("✅ Today", f"{completed_today}/{len(habits) if habits else 0}")
        
        st.markdown("---")
        
        # Daily Wisdom Quote
        st.markdown(f"### 💫 Daily Wisdom for {user_name}")
        today = get_cst_date()
        motivation = db.get_daily_motivation(today)
        
        if not motivation:
            habit_context = None
            if habits:
                categories = [h['category'] for h in habits]
                if categories:
                    habit_context = max(set(categories), key=categories.count)
            
            quote_data = ai_coach.generate_daily_quote(
                tradition=profile.get('philosophy_tradition', 'esoteric'),
                habit_context=habit_context,
                user_name=user_name
            )
            
            db.save_motivation(today, quote_data['quote'], quote_data['philosophy'], quote_data['tradition'], habit_context)
            motivation = db.get_daily_motivation(today)
        
        if motivation:
            st.info(f"**\"{motivation['quote']}\"**\n\n{motivation['philosophy']}\n\n— *{motivation['tradition'].capitalize()} Tradition*")
        
        st.markdown("---")
        
        # Priority Quests
        st.markdown(f"### ⭐ {user_name}'s Priority Quests")
        priority_habits = [h for h in habits if h.get('priority')] if habits else []
        
        if priority_habits:
            for habit in priority_habits[:5]:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    completed = db.is_completed(habit['id'], today)
                    new_completed = st.checkbox(
                        f"{'✅' if completed else '⬜'} **{habit['name']}**",
                        value=completed,
                        key=f"dash_habit_{habit['id']}"
                    )
                    
                    if new_completed != completed:
                        db.toggle_completion(habit['id'], today, new_completed)
                        if new_completed:
                            st.balloons()
                            st.success(f"🎉 {user_name} completed: {habit['name']}! +{habit['xp_reward']} XP, +{habit.get('gold_reward', 0)} Gold!")
                        st.rerun()
                
                with col2:
                    difficulty_icons = {1: "🟢 Easy", 2: "🟡 Med", 3: "🔴 Hard"}
                    st.caption(difficulty_icons.get(habit['difficulty'], '🟢'))
                
                with col3:
                    st.caption(f"⚡ +{habit['xp_reward']} XP")
                    st.caption(f"💰 +{habit.get('gold_reward', 0)} Gold")
        else:
            st.info(f"💡 {user_name}, mark habits as priority in the Habits page!")
        
        st.markdown("---")
        
        # Active Goals
        st.markdown(f"### 🎯 {user_name}'s Active Goals")
        goals = db.get_goals(completed=False)
        
        if goals:
            for goal in goals[:3]:
                progress = goal.get('progress', 0)
                st.markdown(f"**{goal['title']}**")
                st.progress(progress / 100)
                st.caption(f"{progress}% • {goal.get('category', 'personal').capitalize()}")
        else:
            st.info(f"🎯 {user_name}, create your first goal!")
        
        # Quick Actions
        st.markdown("---")
        st.markdown(f"### ⚡ Quick Actions for {user_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Create Habit", use_container_width=True):
                st.session_state.page = 'Habits'
                st.rerun()
        with col2:
            if st.button("🎯 Create Goal", use_container_width=True):
                st.session_state.page = 'Goals'
                st.rerun()
        with col3:
            if st.button("🛒 Visit Shop", use_container_width=True):
                st.session_state.page = 'Shop'
                st.rerun()
                
    # ===== HABITS PAGE =====
    elif current_page == "Habits":
        st.title("⚡ Habit Management")
        
        tab1, tab2 = st.tabs(["📋 Active Habits", "✅ Completed"])
        
        with tab1:
            # Create New Habit
            with st.expander("➕ Create New Habit", expanded=False):
                with st.form("new_habit_form"):
                    st.markdown("#### Habit Details")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Habit Name*", placeholder="e.g., Morning Meditation")
                        category = st.selectbox(
                            "Category*",
                            options=["fitness", "health", "learning", "mindfulness", "productivity", "creativity"],
                            format_func=lambda x: {
                                "fitness": "💪 Fitness",
                                "health": "❤️ Health",
                                "learning": "📚 Learning",
                                "mindfulness": "🧘 Mindfulness",
                                "productivity": "⚡ Productivity",
                                "creativity": "🎨 Creativity"
                            }[x]
                        )
                        
                        frequency = st.selectbox(
                            "Frequency",
                            options=["daily", "weekdays", "weekends", "custom"],
                            format_func=lambda x: {
                                "daily": "📅 Daily",
                                "weekdays": "🗓️ Weekdays Only",
                                "weekends": "🎉 Weekends Only",
                                "custom": "⚙️ Custom Schedule"
                            }[x]
                        )
                        
                        if frequency == "custom":
                            frequency_days = st.multiselect(
                                "Select Days",
                                options=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                                format_func=lambda x: x.capitalize()
                            )
                        else:
                            frequency_days = []
                    
                    with col2:
                        description = st.text_area("Description (optional)", height=100, placeholder="Why is this habit important?")
                        priority = st.checkbox("⭐ Mark as Priority", help="Priority habits appear on dashboard")
                        reminder_enabled = st.checkbox("🔔 Enable Reminder")
                        
                        if reminder_enabled:
                            reminder_time = st.time_input("Reminder Time", value=datetime.strptime("09:00", "%H:%M").time())
                        else:
                            reminder_time = None
                    
                    submitted = st.form_submit_button("🎯 Create Habit", use_container_width=True)
                    
                    if submitted and name:
                        # AI difficulty assessment
                        pdf_context = db.get_all_document_content()
                        assessment = ai_coach.assess_habit_difficulty(name, description, category, pdf_context)
                        
                        habit_id = db.create_habit(
                            name=name,
                            category=category,
                            description=description,
                            difficulty=assessment['difficulty'],
                            xp_reward=assessment['xp_reward'],
                            gold_reward=assessment.get('gold_reward', int(assessment['xp_reward'] * 0.3)),
                            difficulty_rationale=assessment.get('rationale', ''),
                            frequency=frequency,
                            frequency_days=frequency_days,
                            priority=priority,
                            reminder_enabled=reminder_enabled,
                            reminder_time=reminder_time.strftime("%H:%M") if reminder_time else None
                        )
                        
                        # Check achievements
                        habits = db.get_habits()
                        if len(habits) == 1:
                            db.unlock_achievement("first_habit")
                        elif len(habits) == 5:
                            db.unlock_achievement("habits_5")
                        elif len(habits) == 10:
                            db.unlock_achievement("habits_10")
                        
                        st.success(f"✨ Created: {name} (+{assessment['xp_reward']} XP per completion)")
                        st.rerun()
            
            # Display Active Habits
            habits = db.get_habits(active_only=True)
            today = get_cst_date()
            
            if habits:
                st.markdown(f"### {len(habits)} Active Habits")
                
                for habit in habits:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            completed = db.is_completed(habit['id'], today)
                            new_completed = st.checkbox(
                                f"**{habit['name']}**",
                                value=completed,
                                key=f"habit_{habit['id']}"
                            )
                            
                            if new_completed != completed:
                                db.toggle_completion(habit['id'], today, new_completed)
                                
                                if new_completed:
                                    st.balloons()
                                    # Check completion achievements
                                    total_completions = len(db.get_completions(habit['id']))
                                    if total_completions == 1:
                                        db.unlock_achievement("first_complete")
                                    elif total_completions == 100:
                                        db.unlock_achievement("complete_100")
                                
                                st.rerun()
                            
                            if habit.get('description'):
                                st.caption(habit['description'])
                        
                        with col2:
                            difficulty_map = {1: "🟢 Easy", 2: "🟡 Med", 3: "🔴 Hard"}
                            st.caption(difficulty_map.get(habit['difficulty'], '🟢'))
                            if habit.get('priority'):
                                st.caption("⭐ Priority")
                        
                        with col3:
                            st.caption(f"⚡ +{habit['xp_reward']} XP")
                            st.caption(f"💰 +{habit.get('gold_reward', 0)} Gold")
                        
                        with col4:
                            completions = db.get_completions(habit['id'])
                            streak = calculate_streak(completions)
                            st.caption(f"🔥 {streak} days")
                            st.caption(f"✅ {len(completions)} total")
                        
                        st.markdown("---")
            else:
                st.info("💡 Create your first habit to begin your journey!")
        
        with tab2:
            all_habits = db.get_habits(active_only=False)
            completed_habits = [h for h in all_habits if not h.get('active', True)]
            
            if completed_habits:
                st.markdown(f"### {len(completed_habits)} Archived Habits")
                for habit in completed_habits:
                    st.caption(f"✅ {habit['name']} - {habit['category']}")
            else:
                st.caption("No archived habits")

    # ===== GOALS PAGE =====
    elif current_page == "Goals":
        st.title("🎯 Goal Management")
        
        tab1, tab2 = st.tabs(["🎯 Active Goals", "🏆 Completed"])
        
        with tab1:
            with st.expander("➕ Create New Goal", expanded=False):
                with st.form("new_goal_form"):
                    st.markdown("#### Goal Details")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        title = st.text_input("Goal Title*", placeholder="e.g., Run a Marathon")
                        category = st.selectbox(
                            "Category",
                            options=["personal", "career", "health", "learning", "financial", "relationships"],
                            format_func=lambda x: {
                                "personal": "👤 Personal",
                                "career": "💼 Career",
                                "health": "❤️ Health",
                                "learning": "📚 Learning",
                                "financial": "💰 Financial",
                                "relationships": "💑 Relationships"
                            }[x]
                        )
                        
                        deadline = st.date_input("Deadline (optional)", value=None, min_value=date.today())
                    
                    with col2:
                        description = st.text_area("Description", height=100, placeholder="Describe your goal and why it matters")
                        priority = st.checkbox("⭐ Mark as Priority")
                    
                    # Goal Steps
                    st.markdown("#### Action Steps (optional)")
                    num_steps = st.number_input("Number of steps", min_value=0, max_value=20, value=0)
                    steps = []
                    
                    if num_steps > 0:
                        for i in range(num_steps):
                            step = st.text_input(f"Step {i+1}", key=f"step_{i}", placeholder=f"Action step {i+1}")
                            if step:
                                steps.append(step)
                    
                    submitted = st.form_submit_button("🎯 Create Goal", use_container_width=True)
                    
                    if submitted and title:
                        # AI difficulty assessment
                        pdf_context = db.get_all_document_content()
                        assessment = ai_coach.assess_goal_difficulty(title, description, category, pdf_context)
                        
                        goal_id = db.create_goal(
                            title=title,
                            description=description,
                            category=category,
                            deadline=deadline.isoformat() if deadline else None,
                            difficulty=assessment['difficulty'],
                            xp_reward=assessment['xp_reward'],
                            gold_reward=assessment.get('gold_reward', int(assessment['xp_reward'] * 0.25)),
                            priority=priority,
                            steps=steps
                        )
                        
                        # Check achievements
                        goals = db.get_goals()
                        if len(goals) == 1:
                            db.unlock_achievement("first_goal")
                        elif len(goals) == 5:
                            db.unlock_achievement("goals_5")
                        
                        if len(steps) >= 5:
                            db.unlock_achievement("goal_steps_5")
                        if len(steps) >= 10:
                            db.unlock_achievement("goal_steps_10")
                        
                        st.success(f"✨ Goal Created: {title}")
                        st.rerun()
            
            # Display Active Goals
            goals = db.get_goals(completed=False)
            
            if goals:
                st.markdown(f"### {len(goals)} Active Goals")
                
                for goal in goals:
                    with st.expander(f"{'⭐ ' if goal.get('priority') else ''}{goal['title']}", expanded=True):
                        if goal.get('description'):
                            st.markdown(goal['description'])
                        
                        # Progress Slider
                        progress = st.slider(
                            "Progress",
                            0, 100,
                            value=goal.get('progress', 0),
                            key=f"goal_progress_{goal['id']}",
                            help="Slide to update progress"
                        )
                        
                        if progress != goal.get('progress', 0):
                            completed = progress >= 100
                            db.update_goal(goal['id'], progress=progress, completed=completed)
                            
                            if completed and not goal.get('completed'):
                                st.balloons()
                                st.success(f"🏆 Goal Completed! +{goal['xp_reward']} XP, +{goal.get('gold_reward', 0)} Gold!")
                                
                                # Check achievements
                                completed_goals = db.get_goals(completed=True)
                                if len(completed_goals) == 1:
                                    db.unlock_achievement("goal_complete_1")
                                elif len(completed_goals) == 5:
                                    db.unlock_achievement("goal_complete_5")
                            
                            st.rerun()
                        
                        # Goal Info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"📁 {goal['category'].capitalize()}")
                        with col2:
                            if goal.get('deadline'):
                                st.caption(f"📅 Due: {goal['deadline']}")
                        with col3:
                            st.caption(f"⚡ Reward: {goal['xp_reward']} XP")
                        
                        # Display Steps
                        if goal.get('steps'):
                            steps = json.loads(goal['steps']) if isinstance(goal['steps'], str) else goal['steps']
                            if steps:
                                st.markdown("**Action Steps:**")
                                for i, step in enumerate(steps, 1):
                                    st.caption(f"{i}. {step}")
            else:
                st.info("🎯 Set your first goal and watch your power grow!")
        
        with tab2:
            completed_goals = db.get_goals(completed=True)
            
            if completed_goals:
                st.markdown(f"### 🏆 {len(completed_goals)} Completed Goals")
                for goal in completed_goals:
                    st.markdown(f"**✅ {goal['title']}**")
                    st.caption(f"{goal['category'].capitalize()} • +{goal['xp_reward']} XP earned")
                    st.markdown("---")
            else:
                st.caption("No completed goals yet. Complete your first to unlock achievements!")

    # ===== AI COACH PAGE =====
    elif current_page == "AI Coach":
        user_name = profile.get('display_name', 'Hunter')
        
        st.title(f"🤖 AI Coach for {user_name}")
        st.markdown(f"Your personal guide on the path to mastery.")
        
        # Check if AI is available
        has_api_key = ai_coach.client is not None
        
        if not has_api_key:
            st.warning("⚠️ AI Coach requires an Anthropic API key. Add it in Streamlit Cloud secrets.")
            st.info("💡 Without AI, you'll get basic coaching responses.")
        
        st.markdown("---")
        
        # Tabs for different AI Coach features
        coach_tabs = st.tabs(["💬 Ask Coach", "🎯 Goal Planning", "⚡ Habit Builder", "📈 Progress Analysis"])
        
        with coach_tabs[0]:  # Ask Coach
            st.markdown(f"### 💬 Ask Your AI Coach")
            
            # Get all PDF context
            pdf_context = db.get_all_document_content()
            
            with st.form("ask_coach_form"):
                question = st.text_area(
                    "What would you like guidance on?",
                    height=150,
                    placeholder="Example: How can I stay motivated when I feel stuck?"
                )
                
                include_library = st.checkbox("📚 Include context from my Philosophy Library", value=True)
                include_progress = st.checkbox("📊 Include my current habits and goals", value=True)
                
                submitted = st.form_submit_button("🤖 Get AI Guidance", use_container_width=True)
                
                if submitted and question:
                    if ai_coach.client:
                        with st.spinner(f"🤖 AI Coach is thinking..."):
                            try:
                                # Build context
                                context = ""
                                
                                if include_progress:
                                    habits = db.get_habits()
                                    goals = db.get_goals(completed=False)
                                    context += f"\n\n{user_name}'s Current Habits:\n"
                                    for h in habits[:5]:
                                        context += f"- {h['name']} ({h['category']})\n"
                                    context += f"\n{user_name}'s Active Goals:\n"
                                    for g in goals[:5]:
                                        context += f"- {g['title']} ({g.get('progress', 0)}% complete)\n"
                                
                                if include_library and pdf_context:
                                    context += f"\n\nRelevant wisdom from {user_name}'s philosophy library:\n{pdf_context[:5000]}"
                                
                                # Get AI response
                                message = ai_coach.client.messages.create(
                                    model="claude-sonnet-4-20250514",
                                    max_tokens=3000,
                                    messages=[{
                                        "role": "user",
                                        "content": f"""You are a wise AI coach helping {user_name} on their personal growth journey. 

User's Philosophy Tradition: {profile.get('philosophy_tradition', 'esoteric').capitalize()}
User's Focus Areas: {', '.join(profile.get('focus_areas', ['personal growth']))}

{context}

Question from {user_name}:
{question}

Provide thoughtful, actionable guidance. Be encouraging but honest."""
                                    }]
                                )
                                
                                response = message.content[0].text
                                
                                st.success(f"🤖 **AI Coach's Guidance:**")
                                st.markdown(response)
                                
                            except Exception as e:
                                st.error(f"Error getting AI response: {e}")
                    else:
                        st.info(f"Add your Anthropic API key to unlock full AI coaching!")
        
        with coach_tabs[1]:  # Goal Planning
            st.markdown(f"### 🎯 AI-Powered Goal Planning")
            
            # Select a goal
            goals = db.get_goals(completed=False)
            
            if goals:
                goal_titles = {g['title']: g['id'] for g in goals}
                
                selected_goal_title = st.selectbox(
                    "Select a goal to plan:",
                    options=list(goal_titles.keys())
                )
                
                if st.button(f"🤖 Generate Action Plan", use_container_width=True):
                    goal_id = goal_titles[selected_goal_title]
                    goal = db.get_goal_by_id(goal_id)
                    
                    with st.spinner(f"🤖 AI is creating your action plan..."):
                        # Get PDF context
                        pdf_context = db.get_all_document_content()
                        
                        # Generate action steps
                        action_steps = ai_coach.generate_action_steps(
                            goal['title'],
                            goal.get('description', ''),
                            goal.get('category', 'personal'),
                            pdf_context
                        )
                        
                        # Generate habit suggestions
                        habit_suggestions = ai_coach.generate_habit_suggestions(
                            goal['title'],
                            goal.get('description', ''),
                            action_steps,
                            pdf_context
                        )
                        
                        # Update goal in database
                        db.update_goal(
                            goal_id,
                            ai_generated_steps=action_steps,
                            habit_suggestions=habit_suggestions
                        )
                        
                        st.success(f"✨ Action plan created!")
                        
                        # Display action steps
                        st.markdown("#### 📋 Action Steps")
                        for idx, step in enumerate(action_steps, 1):
                            st.markdown(f"**{idx}.** {step}")
                        
                        st.markdown("---")
                        
                        # Display habit suggestions
                        st.markdown("#### ⚡ Suggested Habits")
                        for habit in habit_suggestions:
                            with st.expander(f"💡 {habit['name']}"):
                                st.markdown(f"**Description:** {habit['description']}")
                                st.markdown(f"**Frequency:** {habit['frequency'].capitalize()}")
                                
                                if st.button(f"➕ Create This Habit", key=f"create_habit_{habit['name']}"):
                                    assessment = ai_coach.assess_habit_difficulty(
                                        habit['name'],
                                        habit['description'],
                                        goal.get('category', 'personal'),
                                        pdf_context
                                    )
                                    
                                    db.create_habit(
                                        name=habit['name'],
                                        category=goal.get('category', 'personal'),
                                        description=habit['description'],
                                        difficulty=assessment['difficulty'],
                                        xp_reward=assessment['xp_reward'],
                                        gold_reward=assessment.get('gold_reward', int(assessment['xp_reward'] * 0.3)),
                                        frequency=habit['frequency']
                                    )
                                    
                                    st.success(f"✅ Created habit: {habit['name']}")
                                    st.rerun()
            else:
                st.info(f"Create a goal first to use AI planning!")
        
        with coach_tabs[2]:  # Habit Builder
            st.markdown(f"### ⚡ AI Habit Builder")
            
            with st.form("habit_builder_form"):
                habit_goal = st.text_area(
                    "What do you want to achieve?",
                    height=100,
                    placeholder="Example: I want to improve my focus and concentration"
                )
                
                category = st.selectbox(
                    "Category",
                    options=["fitness", "health", "learning", "mindfulness", "productivity", "creativity"]
                )
                
                submitted = st.form_submit_button("🤖 Design My Habit", use_container_width=True)
                
                if submitted and habit_goal:
                    if ai_coach.client:
                        with st.spinner("🤖 Designing your perfect habit..."):
                            try:
                                pdf_context = db.get_all_document_content()
                                
                                message = ai_coach.client.messages.create(
                                    model="claude-sonnet-4-20250514",
                                    max_tokens=1000,
                                    messages=[{
                                        "role": "user",
                                        "content": f"""Design a specific, actionable daily habit for this goal:

Goal: {habit_goal}
Category: {category}

Provide:
HABIT NAME: [name]
DESCRIPTION: [description]
FREQUENCY: [daily/weekdays/weekends]
WHY IT WORKS: [reasoning]"""
                                    }]
                                )
                                
                                response = message.content[0].text.strip()
                                
                                # Parse response
                                habit_name = ""
                                habit_desc = ""
                                frequency = "daily"
                                reasoning = ""
                                
                                for line in response.split('\n'):
                                    if line.startswith('HABIT NAME:'):
                                        habit_name = line.split(':', 1)[1].strip()
                                    elif line.startswith('DESCRIPTION:'):
                                        habit_desc = line.split(':', 1)[1].strip()
                                    elif line.startswith('FREQUENCY:'):
                                        freq = line.split(':', 1)[1].strip().lower()
                                        if 'weekday' in freq:
                                            frequency = 'weekdays'
                                        elif 'weekend' in freq:
                                            frequency = 'weekends'
                                        else:
                                            frequency = 'daily'
                                    elif line.startswith('WHY IT WORKS:'):
                                        reasoning = line.split(':', 1)[1].strip()
                                
                                st.success(f"✨ Habit designed!")
                                
                                st.markdown(f"### {habit_name}")
                                st.markdown(f"**Description:** {habit_desc}")
                                st.markdown(f"**Frequency:** {frequency.capitalize()}")
                                st.info(f"**💡 Why it works:** {reasoning}")
                                
                                if st.button("➕ Create This Habit", key="create_designed_habit"):
                                    assessment = ai_coach.assess_habit_difficulty(
                                        habit_name,
                                        habit_desc,
                                        category,
                                        pdf_context
                                    )
                                    
                                    db.create_habit(
                                        name=habit_name,
                                        category=category,
                                        description=habit_desc,
                                        difficulty=assessment['difficulty'],
                                        xp_reward=assessment['xp_reward'],
                                        gold_reward=assessment.get('gold_reward', int(assessment['xp_reward'] * 0.3)),
                                        frequency=frequency
                                    )
                                    
                                    st.success(f"✅ Habit created: {habit_name}")
                                    st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error: {e}")
                    else:
                        st.info("Add API key for AI habit design!")
        
        with coach_tabs[3]:  # Progress Analysis
            st.markdown(f"### 📈 AI Progress Analysis")
            
            if st.button(f"🤖 Analyze My Progress", use_container_width=True):
                if ai_coach.client:
                    with st.spinner(f"🤖 Analyzing your journey..."):
                        try:
                            # Gather data
                            habits = db.get_habits()
                            goals = db.get_goals()
                            completed_goals = db.get_goals(completed=True)
                            stats = db.get_stats()
                            
                            # Calculate stats
                            total_completions = 0
                            for habit in habits:
                                completions = db.get_completions(habit['id'])
                                total_completions += len(completions)
                            
                            # Build analysis context
                            context = f"""
{user_name}'s Stats:
- Level: {stats.get('level', 1)}
- Total XP: {stats.get('total_xp', 0):,}
- Active Habits: {len(habits)}
- Total Completions: {total_completions}
- Active Goals: {len([g for g in goals if not g.get('completed')])}
- Completed Goals: {len(completed_goals)}

Recent Habits:
"""
                            for habit in habits[:10]:
                                completions = db.get_completions(habit['id'])
                                streak = calculate_streak(completions)
                                context += f"- {habit['name']}: {len(completions)} completions, {streak} day streak\n"
                            
                            pdf_context = db.get_all_document_content()
                            
                            # Get AI analysis
                            message = ai_coach.client.messages.create(
                                model="claude-sonnet-4-20250514",
                                max_tokens=3000,
                                messages=[{
                                    "role": "user",
                                    "content": f"""Analyze {user_name}'s progress and provide:

1. Strengths (2-3 points)
2. Growth Areas (2-3 points)  
3. Recommendations (3-5 points)

{context}

Philosophy: {profile.get('philosophy_tradition', 'esoteric')}

Be encouraging and specific."""
                                }]
                            )
                            
                            analysis = message.content[0].text
                            
                            st.markdown("### 🤖 AI Analysis")
                            st.markdown(analysis)
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.info("Add API key for progress analysis!")

    # ===== LIBRARY PAGE =====
    elif current_page == "Library":
        user_name = profile.get('display_name', 'Hunter')
        
        st.title(f"📚 {user_name}'s Philosophy Library")
        st.markdown("Your personal wisdom collection with AI-powered analysis.")
        
        st.markdown("---")
        
        # Get documents
        documents = db.get_documents()
        
        # Display library stats
        if documents:
            total_size = sum(doc['file_size'] for doc in documents)
            total_size_mb = total_size / (1024 * 1024)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Documents", len(documents))
            with col2:
                st.metric("💾 Total Size", f"{total_size_mb:.1f} MB")
            with col3:
                analyzed = sum(1 for doc in documents if doc.get('ai_summary'))
                st.metric("🤖 AI Analyzed", analyzed)
            
            st.markdown("---")
        
        # Upload Section
        with st.expander("📤 Upload New Document", expanded=not documents):
            st.markdown("### Upload Philosophy Document")
            st.caption("Supported: PDF files up to 999MB")
            
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload philosophical texts, wisdom literature, journals"
            )
            
            if uploaded_file is not None:
                file_size = uploaded_file.size
                file_size_mb = file_size / (1024 * 1024)
                
                st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
                
                if file_size_mb > 999:
                    st.error(f"⚠️ File too large! Max 999MB. Your file: {file_size_mb:.2f}MB")
                else:
                    if st.button(f"📥 Process and Add to Library", use_container_width=True):
                        with st.spinner(f"📖 Processing {uploaded_file.name}..."):
                            try:
                                import PyPDF2
                                import io
                                
                                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                                
                                text_content = ""
                                for page in pdf_reader.pages:
                                    text_content += page.extract_text() + "\n\n"
                                
                                if text_content.strip():
                                    # Save document
                                    doc_id = db.upload_document(
                                        filename=uploaded_file.name,
                                        content=text_content,
                                        file_type='pdf',
                                        file_size=file_size
                                    )
                                    
                                    st.success(f"✅ Text extracted from {len(pdf_reader.pages)} pages")
                                    
                                    # AI Analysis
                                    if ai_coach.client:
                                        with st.spinner("🤖 AI analyzing..."):
                                            analysis = ai_coach.analyze_pdf_content(text_content, uploaded_file.name)
                                            
                                            db.update_document(
                                                doc_id,
                                                ai_summary=analysis['summary'],
                                                key_concepts=analysis['key_concepts']
                                            )
                                            
                                            st.success("✨ AI analysis complete!")
                                            
                                            st.markdown("**📝 Summary:**")
                                            st.info(analysis['summary'])
                                            
                                            st.markdown("**💡 Key Concepts:**")
                                            for concept in analysis['key_concepts'][:10]:
                                                st.markdown(f"• {concept}")
                                    
                                    # Achievements
                                    db.unlock_achievement("philosophy_upload")
                                    docs = db.get_documents()
                                    if len(docs) >= 5:
                                        db.unlock_achievement("philosophy_5")
                                    
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("❌ Could not extract text. Make sure PDF contains readable text.")
                                
                            except Exception as e:
                                st.error(f"Error: {e}")
        
        st.markdown("---")
        
        # Document Library Display
        if documents:
            st.markdown(f"### 📚 Your Documents ({len(documents)})")
            
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}", expanded=False):
                    doc_size_mb = doc['file_size'] / (1024 * 1024)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.caption(f"📅 Uploaded: {doc.get('uploaded_at', '')[:16]}")
                        st.caption(f"💾 Size: {doc_size_mb:.2f} MB")
                        
                        # AI Summary
                        if doc.get('ai_summary'):
                            st.markdown("#### 🤖 AI Summary")
                            st.info(doc['ai_summary'])
                        
                        # Key Concepts
                        if doc.get('key_concepts'):
                            concepts = doc['key_concepts']
                            if isinstance(concepts, str):
                                try:
                                    concepts = json.loads(concepts)
                                except:
                                    concepts = []
                            
                            if concepts:
                                st.markdown("#### 💡 Key Concepts")
                                for concept in concepts[:15]:
                                    st.markdown(f"• {concept}")
                        
                        # Content preview
                        if doc.get('content'):
                            st.markdown("#### 📖 Preview")
                            preview = doc['content'][:500]
                            st.text_area(
                                "Preview",
                                value=preview + "..." if len(doc['content']) > 500 else preview,
                                height=150,
                                disabled=True,
                                key=f"preview_{doc['id']}",
                                label_visibility="collapsed"
                            )
                    
                    with col2:
                        st.markdown("**Actions**")
                        
                        # View full
                        if st.button("👁️ View Full", key=f"view_{doc['id']}", use_container_width=True):
                            st.session_state[f'viewing_{doc["id"]}'] = True
                        
                        # Re-analyze
                        if ai_coach.client:
                            if st.button("🔄 Re-analyze", key=f"reanalyze_{doc['id']}", use_container_width=True):
                                with st.spinner("🤖 Re-analyzing..."):
                                    analysis = ai_coach.analyze_pdf_content(
                                        doc.get('content', ''),
                                        doc['filename']
                                    )
                                    
                                    db.update_document(
                                        doc['id'],
                                        ai_summary=analysis['summary'],
                                        key_concepts=analysis['key_concepts']
                                    )
                                    
                                    st.success("✅ Re-analyzed!")
                                    st.rerun()
                        
                        # Delete
                        if st.button("🗑️ Delete", key=f"delete_{doc['id']}", use_container_width=True, type="secondary"):
                            st.session_state[f'confirm_delete_{doc["id"]}'] = True
                        
                        if st.session_state.get(f'confirm_delete_{doc["id"]}'):
                            st.warning("⚠️ Confirm?")
                            
                            if st.button("✅ Yes", key=f"yes_{doc['id']}"):
                                conn = db.get_connection()
                                c = conn.cursor()
                                c.execute("DELETE FROM philosophy_documents WHERE id = ?", (doc['id'],))
                                conn.commit()
                                
                                st.success(f"🗑️ Deleted: {doc['filename']}")
                                del st.session_state[f'confirm_delete_{doc["id"]}']
                                st.rerun()
                            
                            if st.button("❌ No", key=f"no_{doc['id']}"):
                                del st.session_state[f'confirm_delete_{doc["id"]}']
                                st.rerun()
                    
                    # Show full content if viewing
                    if st.session_state.get(f'viewing_{doc["id"]}'):
                        st.markdown("---")
                        st.markdown("### 📖 Full Content")
                        
                        if doc.get('content'):
                            st.text_area(
                                "Full Content",
                                value=doc['content'],
                                height=400,
                                disabled=True,
                                key=f"full_{doc['id']}",
                                label_visibility="collapsed"
                            )
                            
                            st.download_button(
                                "💾 Download as TXT",
                                data=doc['content'],
                                file_name=f"{doc['filename']}.txt",
                                mime="text/plain",
                                key=f"download_{doc['id']}"
                            )
                        
                        if st.button("❌ Close", key=f"close_{doc['id']}"):
                            del st.session_state[f'viewing_{doc["id"]}']
                            st.rerun()
        else:
            st.info(f"📚 {user_name}'s library is empty. Upload your first document above!")

    # ===== SHOP PAGE =====
    elif current_page == "Shop":
        st.title("🛒 Shadow Monarch's Shop")
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 20px; border-radius: 15px; border: 2px solid #d4af37; margin-bottom: 20px;'>
            <h3 style='text-align: center; color: #d4af37;'>💰 Your Gold: {stats.get('current_gold', 0):,}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Shop Categories
        shop_tabs = st.tabs(["⚗️ Consumables", "⚔️ Equipment", "🎨 Cosmetics"])
        
        with shop_tabs[0]:  # Consumables
            st.markdown("### ⚗️ Consumables")
            consumables = get_items_by_category("consumable")
            
            for item in consumables:
                rarity = item['rarity']
                rarity_style = RARITY_COLORS[rarity]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{item['icon']} {item['name']}** ({rarity.upper()})")
                    st.caption(item['description'])
                
                with col2:
                    price = item.get('price', {})
                    st.caption(f"💰 {price.get('gold', 0):,}")
                    
                    can_buy = can_afford(item, stats.get('current_gold', 0), 0)
                    if st.button(f"Buy", key=f"buy_{item['id']}", disabled=not can_buy):
                        if db.spend_gold(price.get('gold', 0)):
                            db.add_to_inventory(item['id'], 1)
                            st.success(f"✨ Purchased {item['name']}!")
                            st.rerun()
        
        with shop_tabs[1]:  # Equipment
            st.markdown("### ⚔️ Equipment")
            equipment = get_items_by_category("equipment")
            
            for item in equipment:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{item['icon']} {item['name']}**")
                    st.caption(item['description'])
                    
                    if item.get('stats'):
                        stat_text = ", ".join([f"+{v} {k.capitalize()}" for k, v in item['stats'].items()])
                        st.caption(f"📊 {stat_text}")
                
                with col2:
                    price = item.get('price', {})
                    st.caption(f"💰 {price.get('gold', 0):,}")
                    
                    can_buy = can_afford(item, stats.get('current_gold', 0), 0)
                    if st.button(f"Buy", key=f"buy_{item['id']}", disabled=not can_buy):
                        if db.spend_gold(price.get('gold', 0)):
                            db.add_to_inventory(item['id'], 1)
                            st.success(f"✨ Purchased {item['name']}!")
                            st.rerun()
        
        with shop_tabs[2]:  # Cosmetics
            st.info("🎨 Cosmetic items coming soon!")

    # ===== INVENTORY PAGE =====
    elif current_page == "Inventory":
        st.title("🎒 Inventory & Equipment")
        
        tab1, tab2 = st.tabs(["⚔️ Equipment", "🎒 Items"])
        
        # Get equipped items safely (FIX APPLIED)
        equipped = db.get_equipped_items() or {}
        inventory = db.get_inventory()
        
        with tab1:
            st.markdown("### ⚔️ Current Loadout")
            
            # Equipment slots
            for slot, icon, name in [('weapon_id', '⚔️', 'Weapon'), ('armor_id', '🛡️', 'Armor'), ('ring_id', '💍', 'Ring'), ('amulet_id', '📿', 'Amulet')]:
                item_id = equipped.get(slot, '')
                if item_id:
                    st.markdown(f"**{icon} {name}:** {item_id.replace('_', ' ').title()}")
                else:
                    st.caption(f"{icon} {name}: Empty")
            
            st.markdown("---")
            st.markdown("### 🎒 Available Equipment")
            
            equipment_items = [item for item in inventory if get_item_by_id(item['item_id']) and get_item_by_id(item['item_id']).get('category') == 'equipment']
            
            if equipment_items:
                for inv_item in equipment_items:
                    item = get_item_by_id(inv_item['item_id'])
                    if item:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{item['icon']} {item['name']}**")
                            st.caption(item['description'])
                        
                        with col2:
                            if st.button("⚔️ Equip", key=f"equip_{item['id']}"):
                                db.equip_item(item['id'], item.get('slot', 'misc'))
                                st.success(f"✨ Equipped {item['name']}!")
                                st.rerun()
            else:
                st.info("🛒 Visit the shop to purchase equipment!")
        
        with tab2:
            st.markdown("### 🎒 Consumables")
            
            consumable_items = [item for item in inventory if get_item_by_id(item['item_id']) and get_item_by_id(item['item_id']).get('category') == 'consumable']
            
            if consumable_items:
                for inv_item in consumable_items:
                    item = get_item_by_id(inv_item['item_id'])
                    if item:
                        st.markdown(f"**{item['icon']} {item['name']}** x{inv_item['quantity']}")
                        st.caption(item['description'])
            else:
                st.info("🛒 Your inventory is empty. Visit the shop!")

    # ===== ANALYTICS PAGE =====
    elif current_page == "Analytics":
        st.title("📊 Performance Analytics")
        
        # Time period selector
        period = st.selectbox(
            "📅 Time Period",
            options=["daily", "weekly", "monthly", "yearly"],
            format_func=lambda x: {"daily": "Today", "weekly": "This Week", "monthly": "This Month", "yearly": "This Year"}[x]
        )
        
        start_date, end_date = get_date_range(period)
        
        # Calculate stats
        habits = db.get_habits()
        total_completions = 0
        xp_earned = 0
        active_days = set()
        
        for habit in habits:
            completions = db.get_completions(habit['id'], start_date, end_date)
            total_completions += len(completions)
            xp_earned += len(completions) * habit['xp_reward']
            for comp in completions:
                active_days.add(comp['date'])
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✅ Completions", total_completions)
        with col2:
            st.metric("⚡ XP Earned", format_xp(xp_earned))
        with col3:
            st.metric("📅 Active Days", len(active_days))
        with col4:
            if habits and active_days:
                total_possible = len(habits) * len(active_days)
                completion_rate = get_completion_percentage(total_completions, total_possible)
            else:
                completion_rate = 0
            st.metric("📈 Rate", f"{completion_rate}%")
        
        st.markdown("---")
        
        # Habit Chart
        if habits:
            st.markdown("### 📊 Habit Completions")
            
            habit_data = []
            for habit in habits:
                completions = db.get_completions(habit['id'], start_date, end_date)
                habit_data.append({
                    'Habit': habit['name'],
                    'Completions': len(completions)
                })
            
            if habit_data:
                df = pd.DataFrame(habit_data)
                st.bar_chart(df.set_index('Habit')['Completions'])

    # ===== NOTES PAGE =====
    elif current_page == "Notes":
        st.title("📝 Journal & Notes")
        
        with st.expander("➕ Create New Note", expanded=False):
            with st.form("new_note_form"):
                title = st.text_input("Note Title*")
                content = st.text_area("Content", height=200)
                category = st.selectbox("Category", options=["personal", "work", "health", "goals", "ideas", "learning"])
                pinned = st.checkbox("📌 Pin Note")
                
                submitted = st.form_submit_button("💾 Save Note", use_container_width=True)
                
                if submitted and title:
                    pdf_context = db.get_all_document_content()
                    note_id = db.create_note(title=title, content=content, category=category, pinned=pinned)
                    
                    notes = db.get_notes()
                    if len(notes) == 1:
                        db.unlock_achievement("first_note")
                    elif len(notes) == 10:
                        db.unlock_achievement("notes_10")
                    
                    st.success("✨ Note saved!")
                    st.rerun()
        
        # Display Notes
        notes = db.get_notes()
        
        if notes:
            st.markdown(f"### 📚 {len(notes)} Notes")
            
            for note in notes:
                with st.expander(f"{'📌 ' if note.get('pinned') else ''}{note['title']}", expanded=note.get('pinned', False)):
                    st.markdown(note.get('content', ''))
                    st.caption(f"📁 {note.get('category', 'personal').capitalize()} • {note.get('created_at', '')[:16]}")
                    
                    if st.button("🤖 AI Summary", key=f"summarize_{note['id']}"):
                        pdf_context = db.get_all_document_content()
                        summary = ai_coach.summarize_note(note['title'], note.get('content', ''), pdf_context)
                        db.update_note(note['id'], ai_summary=summary)
                        st.rerun()
                    
                    if note.get('ai_summary'):
                        st.info(f"**💭 AI Summary:**\n\n{note['ai_summary']}")
        else:
            st.info("📝 Create your first note!")

    # ===== ACHIEVEMENTS PAGE =====
    elif current_page == "Achievements":
        st.title("🏆 Achievements")
        
        achievements = db.get_achievements()
        unlocked_count = sum(1 for a in achievements if a.get('unlocked_at'))
        
        st.markdown(f"**Progress: {unlocked_count}/{len(achievements)} Unlocked**")
        st.progress(unlocked_count / len(achievements) if achievements else 0)
        
        # Tier icons
        tier_icons = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇', 'platinum': '💎', 'legendary': '👑'}
        
        for ach in achievements:
            unlocked = ach.get('unlocked_at') is not None
            icon = "✅" if unlocked else "🔒"
            tier_icon = tier_icons.get(ach.get('tier', 'bronze'), '🥉')
            
            st.markdown(f"{icon} {tier_icon} **{ach['title']}**")
            st.caption(ach['description'])
            st.caption(f"⚡ +{ach['xp_reward']} XP, 💰 +{ach['gold_reward']} Gold")
            st.markdown("")

    # ===== SETTINGS PAGE =====
    elif current_page == "Settings":
        st.title("⚙️ Settings")
        
        with st.form("settings_form"):
            display_name = st.text_input("Display Name", value=profile.get('display_name', 'Hunter'))
            
            submitted = st.form_submit_button("💾 Save", use_container_width=True)
            
            if submitted:
                db.update_profile(display_name=display_name)
                st.success("✨ Settings saved!")
                st.rerun()
