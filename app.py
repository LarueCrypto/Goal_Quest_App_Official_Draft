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
    # ===== DASHBOARD PAGE ===== (ENHANCED WITH CHARACTER)
    # ===== DASHBOARD PAGE =====
    if current_page == "Dashboard":
        # Get user name for personalization
        user_name = profile.get('display_name', 'Hunter')
        
        st.title(f"🏠 {user_name}'s Command Center")
        st.markdown(f"<p style='font-size: 1.2em; color: #d4af37;'>Welcome back, {user_name}! Ready to continue your journey?</p>", unsafe_allow_html=True)
        
        # CHARACTER DISPLAY - Main feature!
        col_char, col_stats = st.columns([1, 1])
        
        with col_char:
            st.markdown("### 👤 Your Hunter")
            
            try:
                # Get equipped items
                equipped = db.get_equipped_items()
                
                # Generate character SVG
                character_svg = get_character_svg(profile, stats, equipped)
                
                # Render SVG in a container
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                            padding: 20px; 
                            border-radius: 15px; 
                            border: 2px solid #d4af37;
                            text-align: center;'>
                    {character_svg}
                </div>
                """, unsafe_allow_html=True)
                
                # Character info below avatar
                st.markdown(f"""
                <div style='text-align: center; margin-top: 20px; padding: 15px; 
                            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                            border-radius: 10px; border: 2px solid #d4af37;'>
                    <h3 style='color: #d4af37; margin: 0;'>{user_name}</h3>
                    <p style='color: #ffffff; margin: 5px 0;'>{profile.get('avatar_style', 'warrior').capitalize()} • Level {stats.get('level', 1)}</p>
                    <p style='color: #ffd700; margin: 5px 0;'>💰 {stats.get('current_gold', 0):,} Gold</p>
                </div>
                """, unsafe_allow_html=True)
            
            except Exception as e:
                # Fallback if character rendering fails
                st.error(f"Character display error. Showing simplified view.")
                st.markdown(f"""
                <div style='text-align: center; padding: 40px; 
                            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                            border-radius: 15px; border: 2px solid #d4af37;'>
                    <div style='font-size: 120px;'>⚔️</div>
                    <h2 style='color: #d4af37;'>{user_name}</h2>
                    <p style='color: #ffffff;'>{profile.get('avatar_style', 'warrior').capitalize()}</p>
                    <p style='color: #ffd700; font-size: 24px;'>Level {stats.get('level', 1)}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col_stats:
            st.markdown(f"### 📊 {user_name}'s Power")
            
            # Animated stat bars
            try:
                stat_bars_html = get_stat_visual_bars(stats)
                st.markdown(stat_bars_html, unsafe_allow_html=True)
            except:
                # Fallback stat display
                st.markdown("**Player Stats:**")
                for stat in ['strength', 'intelligence', 'vitality', 'agility', 'sense', 'willpower']:
                    st.metric(stat.capitalize(), stats.get(stat, 0))
            
            # Quick stats
            st.markdown("---")
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
            # Generate contextual quote
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
            
            db.save_motivation(
                today,
                quote_data['quote'],
                quote_data['philosophy'],
                quote_data['tradition'],
                habit_context
            )
            motivation = db.get_daily_motivation(today)
        
        if motivation:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                        border-left: 5px solid #d4af37; 
                        padding: 25px; 
                        margin: 20px 0; 
                        border-radius: 10px; 
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);'>
                <p style='font-size: 1.3em; color: #d4af37; margin-bottom: 15px; font-style: italic;'>"{motivation['quote']}"</p>
                <p style='font-size: 1em; line-height: 1.8; color: #ffffff;'>{motivation['philosophy']}</p>
                <p style='text-align: right; color: #d4af37; margin-top: 15px; font-weight: bold;'>
                    — {motivation['tradition'].capitalize()} Tradition
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Priority Quests Section
        st.markdown(f"### ⭐ {user_name}'s Priority Quests")
        priority_habits = [h for h in habits if h.get('priority')] if habits else []
        
        if priority_habits:
            for habit in priority_habits[:5]:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    completed = db.is_completed(habit['id'], today)
                    checkbox_key = f"dash_habit_{habit['id']}"
                    new_completed = st.checkbox(
                        f"{'✅' if completed else '⬜'} **{habit['name']}**",
                        value=completed,
                        key=checkbox_key
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
            st.info(f"💡 {user_name}, mark habits as priority in the Habits page to see them here!")
        
        st.markdown("---")
        
        # Active Goals Summary
        st.markdown(f"### 🎯 {user_name}'s Active Goals")
        goals = db.get_goals(completed=False)
        
        if goals:
            for goal in goals[:3]:
                progress = goal.get('progress', 0)
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                            padding: 15px; 
                            border-radius: 10px; 
                            border: 2px solid #d4af37;
                            margin: 10px 0;'>
                    <h4 style='color: #ffffff; margin: 0 0 10px 0;'>{goal['title']}</h4>
                    <p style='color: #aaaaaa; font-size: 0.9em;'>{goal.get('category', 'personal').capitalize()}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(progress / 100)
                st.caption(f"{progress}% complete • {goal.get('category', 'personal').capitalize()}")
                st.markdown("")
        else:
            st.info(f"🎯 {user_name}, create your first goal to start your journey!")
        
        # Quick Action Buttons
        st.markdown("---")
        st.markdown(f"### ⚡ Quick Actions for {user_name}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Create New Habit", use_container_width=True):
                st.session_state.page = 'Habits'
                st.rerun()
        
        with col2:
            if st.button("🎯 Create New Goal", use_container_width=True):
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
                        assessment = ai_coach.assess_habit_difficulty(name, description, category)
                        
                        habit_id = db.create_habit(
                            name=name,
                            category=category,
                            description=description,
                            difficulty=assessment['difficulty'],
                            xp_reward=assessment['xp_reward'],
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
                            st.caption(f"📅 {habit.get('frequency', 'daily').capitalize()}")
                        
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
                        assessment = ai_coach.assess_goal_difficulty(title, description, category)
                        
                        goal_id = db.create_goal(
                            title=title,
                            description=description,
                            category=category,
                            deadline=deadline.isoformat() if deadline else None,
                            difficulty=assessment['difficulty'],
                            xp_reward=assessment['xp_reward'],
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
                                st.success(f"🏆 Goal Completed! +{goal['xp_reward']} XP, +{int(goal['xp_reward'] * 0.2)} Gold!")
                                
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

    # ===== SHOP PAGE =====
    elif current_page == "Shop":
        st.title("🛒 Shadow Monarch's Shop")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 20px; border-radius: 15px; border: 2px solid #d4af37; margin-bottom: 20px;'>
            <h3 style='text-align: center; color: #d4af37;'>💰 Your Gold: {}</h3>
            <p style='text-align: center;'>Invest in your power. Choose wisely, Hunter.</p>
        </div>
        """.format(stats.get('current_gold', 0)), unsafe_allow_html=True)
        
        # Shop Categories
        shop_tabs = st.tabs(["⚗️ Consumables", "⚔️ Equipment", "🎨 Cosmetics"])
        
        with shop_tabs[0]:  # Consumables
            st.markdown("### ⚗️ Consumables - Power Through Items")
            consumables = get_items_by_category("consumable")
            
            for item in consumables:
                rarity = item['rarity']
                rarity_style = RARITY_COLORS[rarity]
                
                with st.container():
                    st.markdown(f"""
                    <div class='shop-item' style='border-color: {rarity_style["bg"]}; box-shadow: 0 4px 15px {rarity_style["glow"]};'>
                        <h4 style='color: {rarity_style["text"]}; margin: 0;'>{item['icon']} {item['name']}</h4>
                        <p style='color: {rarity_style["text"]}; font-size: 0.9em; margin: 5px 0;'>{rarity.upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{item['description']}**")
                        
                        # Display effect
                        effect = item.get('effect', {})
                        if effect.get('type') == 'xp_multiplier':
                            duration_hours = effect['duration'] / 3600
                            st.caption(f"✨ Effect: {effect['value']}x XP for {duration_hours:.0f} hours")
                        elif effect.get('type') == 'gold_multiplier':
                            duration_hours = effect['duration'] / 3600
                            st.caption(f"💰 Effect: {effect['value']}x Gold for {duration_hours:.0f} hours")
                        elif effect.get('type') == 'streak_protection':
                            st.caption(f"🛡️ Effect: Protects streak {effect['uses']} time(s)")
                        elif effect.get('type') == 'stat_boost_temp':
                            st.caption(f"💪 Effect: +{effect['value']} to all stats for 24h")
                        elif effect.get('type') == 'stat_boost_perm':
                            st.caption(f"✨ Effect: +{effect['value']} permanent to chosen stat")
                    
                    with col2:
                        price = item.get('price', {})
                        gold_cost = price.get('gold', 0)
                        crystal_cost = price.get('crystals', 0)
                        
                        st.markdown(f"**💰 {gold_cost:,}**")
                        if crystal_cost > 0:
                            st.caption(f"💎 {crystal_cost} crystals")
                        
                        # Purchase button
                        can_buy = can_afford(item, stats.get('current_gold', 0), 0)
                        level_ok = meets_level_requirement(item, stats.get('level', 1))
                        
                        if not level_ok:
                            st.caption(f"🔒 Level {item.get('level_required')} required")
                        elif st.button(f"Buy", key=f"buy_{item['id']}", disabled=not can_buy):
                            if db.spend_gold(gold_cost):
                                db.add_to_inventory(item['id'], 1)
                                db.unlock_achievement("shop_purchase")
                                st.success(f"✨ Purchased {item['name']}!")
                                st.rerun()
                    
                    st.markdown("---")
        
        with shop_tabs[1]:  # Equipment
            st.markdown("### ⚔️ Equipment - Enhance Your Power")
            equipment = get_items_by_category("equipment")
            
            for item in equipment:
                rarity = item['rarity']
                rarity_style = RARITY_COLORS[rarity]
                
                with st.container():
                    st.markdown(f"""
                    <div class='shop-item' style='border-color: {rarity_style["bg"]}; box-shadow: 0 4px 15px {rarity_style["glow"]};'>
                        <h4 style='color: {rarity_style["text"]}; margin: 0;'>{item['icon']} {item['name']}</h4>
                        <p style='color: {rarity_style["text"]}; font-size: 0.9em; margin: 5px 0;'>{rarity.upper()} • {item.get('slot', 'misc').upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{item['description']}**")
                        
                        # Display stats
                        if item.get('stats'):
                            stat_text = ", ".join([f"+{v} {k.capitalize()}" for k, v in item['stats'].items()])
                            st.caption(f"📊 Stats: {stat_text}")
                        
                        # Display effect
                        effect = item.get('effect', {})
                        if effect:
                            st.caption(f"✨ Special: {effect}")
                    
                    with col2:
                        price = item.get('price', {})
                        gold_cost = price.get('gold', 0)
                        crystal_cost = price.get('crystals', 0)
                        
                        st.markdown(f"**💰 {gold_cost:,}**")
                        if crystal_cost > 0:
                            st.caption(f"💎 {crystal_cost} crystals")
                        
                        can_buy = can_afford(item, stats.get('current_gold', 0), 0)
                        level_ok = meets_level_requirement(item, stats.get('level', 1))
                        
                        if not level_ok:
                            st.caption(f"🔒 Level {item.get('level_required')} required")
                        elif st.button(f"Buy", key=f"buy_{item['id']}", disabled=not can_buy):
                            if db.spend_gold(gold_cost):
                                db.add_to_inventory(item['id'], 1)
                                db.unlock_achievement("shop_purchase")
                                db.unlock_achievement("equipment_first")
                                st.success(f"✨ Purchased {item['name']}!")
                                st.rerun()
                    
                    st.markdown("---")
        
        with shop_tabs[2]:  # Cosmetics
            st.markdown("### 🎨 Cosmetics - Style Your Journey")
            cosmetics = get_items_by_category("cosmetic")
            
            if cosmetics:
                for item in cosmetics:
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
            else:
                st.info("🎨 Cosmetic items coming soon!")

    # ===== INVENTORY PAGE =====
    elif current_page == "Inventory":
        st.title("🎒 Inventory & Equipment")
        
        tab1, tab2 = st.tabs(["⚔️ Equipment", "🎒 Items"])
        
        with tab1:
            st.markdown("### ⚔️ Current Loadout")
            
            # Get equipped items and inventory
            equipped = db.get_equipped_items()
            inventory = db.get_inventory()
            
            # Visual equipment display with 3D effects
            equipment_html = get_equipment_display(equipped, inventory)
            st.markdown(equipment_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Equip Items Section
            st.markdown("### 🎒 Available Equipment")
            equipment_items = [item for item in inventory if get_item_by_id(item['item_id']) and get_item_by_id(item['item_id']).get('category') == 'equipment']
            
            if equipment_items:
                for inv_item in equipment_items:
                    item = get_item_by_id(inv_item['item_id'])
                    if item:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{item['icon']} {item['name']}**")
                            st.caption(f"{item.get('slot', 'misc').capitalize()} • {item['description']}")
                            
                            # Show stats if available
                            if item.get('stats'):
                                stat_text = ", ".join([f"+{v} {k.capitalize()}" for k, v in item['stats'].items()])
                                st.caption(f"📊 {stat_text}")
                        
                        with col2:
                            if st.button("⚔️ Equip", key=f"equip_{item['id']}"):
                                db.equip_item(item['id'], item.get('slot', 'misc'))
                                st.success(f"✨ Equipped {item['name']}!")
                                st.rerun()
            else:
                st.info("🛒 Visit the shop to purchase equipment!")
        
        with tab2:
            st.markdown("### 🎒 Consumables & Items")
            
            inventory = db.get_inventory()
            consumable_items = [item for item in inventory if get_item_by_id(item['item_id']) and get_item_by_id(item['item_id']).get('category') == 'consumable']
            
            if consumable_items:
                for inv_item in consumable_items:
                    item = get_item_by_id(inv_item['item_id'])
                    if item:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{item['icon']} {item['name']}** x{inv_item['quantity']}")
                            st.caption(item['description'])
                        
                        with col2:
                            effect = item.get('effect', {})
                            if effect.get('type') == 'xp_multiplier':
                                st.caption(f"⚡ {effect['value']}x XP")
                            elif effect.get('type') == 'gold_multiplier':
                                st.caption(f"💰 {effect['value']}x Gold")
                        
                        with col3:
                            st.button("Use", key=f"use_{item['id']}", disabled=True, help="Item usage coming soon!")
            else:
                st.info("🛒 Your inventory is empty. Visit the shop!")

    # ===== ANALYTICS PAGE =====
    elif current_page == "Analytics":
        st.title("📊 Performance Analytics")
        
        # Time period selector
        period = st.selectbox(
            "📅 Time Period",
            options=["daily", "weekly", "monthly", "yearly"],
            format_func=lambda x: {
                "daily": "Today",
                "weekly": "This Week",
                "monthly": "This Month",
                "yearly": "This Year"
            }[x]
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
            st.metric("✅ Total Completions", total_completions)
        
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
            st.metric("📈 Completion Rate", f"{completion_rate}%")
        
        st.markdown("---")
        
        # Habit Completion Chart
        if habits:
            st.markdown("### 📊 Habit Completions")
            
            habit_data = []
            for habit in habits:
                completions = db.get_completions(habit['id'], start_date, end_date)
                habit_data.append({
                    'Habit': habit['name'],
                    'Completions': len(completions),
                    'XP Earned': len(completions) * habit['xp_reward']
                })
            
            if habit_data:
                df = pd.DataFrame(habit_data)
                st.bar_chart(df.set_index('Habit')['Completions'])
                st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # Goals Progress
        st.markdown("### 🎯 Goals Overview")
        goals = db.get_goals(completed=False)
        
        if goals:
            for goal in goals:
                st.markdown(f"**{goal['title']}**")
                st.progress(goal.get('progress', 0) / 100)
                st.caption(f"{goal.get('progress', 0)}% complete")
        else:
            st.caption("No active goals")

    # ===== NOTES PAGE =====
    elif current_page == "Notes":
        st.title("📝 Journal & Notes")
        
        with st.expander("➕ Create New Note", expanded=False):
            with st.form("new_note_form"):
                title = st.text_input("Note Title*")
                content = st.text_area("Content", height=200, placeholder="Write your thoughts...")
                
                col1, col2 = st.columns(2)
                with col1:
                    category = st.selectbox(
                        "Category",
                        options=["personal", "work", "health", "goals", "ideas", "learning"],
                        format_func=lambda x: x.capitalize()
                    )
                
                with col2:
                    pinned = st.checkbox("📌 Pin Note")
                
                submitted = st.form_submit_button("💾 Save Note", use_container_width=True)
                
                if submitted and title:
                    note_id = db.create_note(
                        title=title,
                        content=content,
                        category=category,
                        pinned=pinned
                    )
                    
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
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.caption(f"📁 {note.get('category', 'personal').capitalize()}")
                    
                    with col2:
                        created = note.get('created_at', '')
                        if created:
                            st.caption(f"🕐 {created[:16]}")
                    
                    with col3:
                        if st.button("🤖 AI Summary", key=f"summarize_{note['id']}"):
                            summary = ai_coach.summarize_note(note['title'], note.get('content', ''))
                            db.update_note(note['id'], ai_summary=summary)
                            db.unlock_achievement("ai_summary")
                            st.rerun()
                    
                    if note.get('ai_summary'):
                        st.info(f"**💭 AI Summary:**\n\n{note['ai_summary']}")
        else:
            st.info("📝 Create your first note to capture your journey!")

    # ===== ACHIEVEMENTS PAGE =====
    elif current_page == "Achievements":
        st.title("🏆 Achievements & Rewards")
        
        # Player Stats Display
        st.markdown("### 💪 Player Stats")
        
        stat_cols = st.columns(3)
        stat_names = ['strength', 'intelligence', 'vitality', 'agility', 'sense', 'willpower']
        stat_icons = {'strength': '⚔️', 'intelligence': '🧠', 'vitality': '❤️', 'agility': '⚡', 'sense': '👁️', 'willpower': '🔥'}
        
        for idx, stat in enumerate(stat_names):
            with stat_cols[idx % 3]:
                stat_value = stats.get(stat, 0)
                st.markdown(f"""
                <div class='stat-display'>
                    <h3>{stat_icons[stat]}</h3>
                    <h2 style='color: #d4af37;'>{stat_value}</h2>
                    <p>{stat.capitalize()}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Achievements
        st.markdown("### 🏅 Achievements")
        
        achievements = db.get_achievements()
        unlocked_count = sum(1 for a in achievements if a.get('unlocked_at'))
        
        st.markdown(f"**Progress: {unlocked_count}/{len(achievements)} Unlocked**")
        st.progress(unlocked_count / len(achievements) if achievements else 0)
        
        # Group by category
        categories = {}
        for ach in achievements:
            cat = ach.get('category', 'general')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ach)
        
        # Tier icons
        tier_icons = {
            'bronze': '🥉',
            'silver': '🥈',
            'gold': '🥇',
            'platinum': '💎',
            'legendary': '👑'
        }
        
        for category, achs in categories.items():
            with st.expander(f"📁 {category.upper()} ({sum(1 for a in achs if a.get('unlocked_at'))}/{len(achs)})", expanded=category=="streaks"):
                
                cols = st.columns(2)
                for idx, ach in enumerate(achs):
                    with cols[idx % 2]:
                        unlocked = ach.get('unlocked_at') is not None
                        
                        icon = "✅" if unlocked else "🔒"
                        tier_icon = tier_icons.get(ach.get('tier', 'bronze'), '🥉')
                        
                        st.markdown(f"{icon} {tier_icon} **{ach['title']}**")
                        st.caption(ach['description'])
                        st.caption(f"⚡ +{ach['xp_reward']} XP, 💰 +{ach['gold_reward']} Gold")
                        
                        if ach.get('special_power'):
                            st.caption(f"✨ {ach['special_power']}")
                        
                        st.markdown("")

    # ===== SETTINGS PAGE =====
    elif current_page == "Settings":
        st.title("⚙️ Settings & Preferences")
        
        st.markdown("### 👤 Profile Settings")
        
        with st.form("settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                display_name = st.text_input("Display Name", value=profile.get('display_name', 'Hunter'))
                
                gender = st.selectbox(
                    "Gender",
                    options=["neutral", "male", "female"],
                    index=["neutral", "male", "female"].index(profile.get('gender', 'neutral')),
                    format_func=lambda x: x.capitalize()
                )
                
                avatar_style = st.selectbox(
                    "Avatar Style",
                    options=["warrior", "mage", "rogue", "sage"],
                    index=["warrior", "mage", "rogue", "sage"].index(profile.get('avatar_style', 'warrior')),
                    format_func=lambda x: x.capitalize()
                )
            
            with col2:
                philosophy_tradition = st.selectbox(
                    "Primary Philosophy Tradition",
                    options=["esoteric", "kemetic", "samurai", "biblical", "quranic", "stoic", "eastern", "occult"],
                    index=["esoteric", "kemetic", "samurai", "biblical", "quranic", "stoic", "eastern", "occult"].index(profile.get('philosophy_tradition', 'esoteric')),
                    format_func=lambda x: x.capitalize()
                )
                
                notifications = st.checkbox("🔔 Enable Notifications", value=profile.get('notifications_enabled', True))
                
                weekly_report = st.checkbox("📊 Weekly Report", value=profile.get('weekly_report_enabled', True))
            
            submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
            
            if submitted:
                db.update_profile(
                    display_name=display_name,
                    gender=gender,
                    avatar_style=avatar_style,
                    philosophy_tradition=philosophy_tradition,
                    notifications_enabled=notifications,
                    weekly_report_enabled=weekly_report
                )
                st.success("✨ Settings saved!")
                st.rerun()
        
        st.markdown("---")
        
        # Stats Display
        st.markdown("### 📊 Your Stats")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Level", stats.get('level', 1))
            st.metric("Total XP", format_xp(stats.get('total_xp', 0)))
        
        with col2:
            st.metric("Current Gold", f"{stats.get('current_gold', 0):,}")
            st.metric("Lifetime Gold", f"{stats.get('lifetime_gold', 0):,}")
        
        with col3:
            habits = db.get_habits()
            goals = db.get_goals()
            st.metric("Active Habits", len(habits))
            st.metric("Active Goals", len([g for g in goals if not g.get('completed')]))
        
        st.markdown("---")
        
        # About Section
        st.markdown("### 📖 About Goal Quest")
        st.info("""
        **Goal Quest - Python Edition**
        
        A gamified habit tracking and goal achievement system inspired by Solo Leveling.
        
        **Features:**
        - 🎯 Track habits with XP rewards (50 XP increments)
        - 🏆 200 achievements to unlock
        - 🛒 Complete shop system with equipment
        - 💪 6 player stats to develop
        - 📚 Deep philosophy quotes from 8 traditions
        - ⚡ Level up and gain power
        
        Built with ❤️ using Streamlit & SQLite
        
        **Version:** 2.0 - Complete Restoration
        """)
