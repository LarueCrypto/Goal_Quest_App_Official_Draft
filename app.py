import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from database import Database
from achievements import initialize_achievements
from ai_coach import AICoach
from utils import *

# Page config
st.set_page_config(
    page_title="Goal Quest",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    h1, h2, h3 {
        color: #d4af37;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }
    
    [data-testid="stMetricValue"] {
        color: #d4af37;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .stButton>button {
        background-color: #d4af37;
        color: #0a0a0a;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ffd700;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
    }
    
    .stProgress > div > div > div {
        background-color: #d4af37;
    }
    
    p, span, label {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()
    initialize_achievements(st.session_state.db)

if 'ai_coach' not in st.session_state:
    st.session_state.ai_coach = AICoach()

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

db = st.session_state.db
ai_coach = st.session_state.ai_coach

# Get user profile and stats
profile = db.get_profile()
stats = db.get_stats()

# Check if onboarding is needed
if not profile.get('onboarding_completed'):
    st.title("⚔️ Welcome to Goal Quest")
    st.markdown("### Begin Your Journey")
    
    with st.form("onboarding_form"):
        st.markdown("**Tell us about yourself:**")
        
        display_name = st.text_input("What should we call you?", value="Hunter")
        
        gender = st.selectbox(
            "Gender",
            options=["neutral", "male", "female"],
            format_func=lambda x: x.capitalize()
        )
        
        avatar_style = st.selectbox(
            "Choose your avatar style",
            options=["warrior", "mage", "rogue", "sage"],
            format_func=lambda x: x.capitalize()
        )
        
        philosophy_tradition = st.selectbox(
            "Primary wisdom tradition",
            options=["esoteric", "biblical", "quranic", "stoic", "eastern"],
            format_func=lambda x: x.capitalize()
        )
        
        focus_areas = st.multiselect(
            "What are your main focus areas?",
            options=["health", "career", "relationships", "creativity", "mindfulness", "learning"],
            default=["health", "mindfulness"]
        )
        
        submitted = st.form_submit_button("🚀 Begin Quest")
        
        if submitted:
            db.update_profile(
                display_name=display_name,
                gender=gender,
                avatar_style=avatar_style,
                philosophy_tradition=philosophy_tradition,
                focus_areas=focus_areas,
                onboarding_completed=True
            )
            st.success("✨ Welcome to your journey!")
            st.rerun()

else:
    # Sidebar Navigation
    with st.sidebar:
        st.title("⚔️ Goal Quest")
        
        # User Profile Card
        st.markdown(f"### {profile.get('display_name', 'Hunter')}")
        st.markdown(f"**Level {stats.get('level', 1)}** | {profile.get('avatar_style', 'warrior').capitalize()}")
        
        # XP Progress
        current_xp = stats.get('current_xp', 0)
        level = stats.get('level', 1)
        xp_needed = level * 500
        st.progress(current_xp / xp_needed if xp_needed > 0 else 0)
        st.caption(f"XP: {current_xp} / {xp_needed}")
        
        # Gold Counter
        st.markdown(f"💰 **Gold:** {stats.get('current_gold', 0):,}")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        
        pages = {
            "🏠 Dashboard": "Dashboard",
            "⚡ Habits": "Habits",
            "🎯 Goals": "Goals",
            "📊 Analytics": "Analytics",
            "📝 Notes": "Notes",
            "🏆 Rewards": "Rewards",
            "⚙️ Settings": "Settings"
        }
        
        for label, page_name in pages.items():
            if st.button(label, key=page_name, use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

    # Main Content Area
    current_page = st.session_state.page

    # ===== DASHBOARD PAGE =====
    if current_page == "Dashboard":
        st.title("🏠 Dashboard")
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Level", stats.get('level', 1), "+1" if stats.get('level', 1) > 1 else None)
        
        with col2:
            st.metric("Total XP", format_xp(stats.get('total_xp', 0)))
        
        with col3:
            habits = db.get_habits()
            max_streak = 0
            if habits:
                for habit in habits:
                    completions = db.get_completions(habit['id'])
                    streak = calculate_streak(completions)
                    max_streak = max(max_streak, streak)
            st.metric("Daily Streak", max_streak, "🔥")
        
        with col4:
            today = get_cst_date()
            completed_today = 0
            if habits:
                for habit in habits:
                    if db.is_completed(habit['id'], today):
                        completed_today += 1
            st.metric("Completed Today", f"{completed_today}/{len(habits) if habits else 0}")
        
        st.markdown("---")
        
        # Daily Wisdom Quote
        st.markdown("### 💫 Daily Wisdom")
        today = get_cst_date()
        motivation = db.get_daily_motivation(today)
        
        if not motivation:
            quote_data = ai_coach.generate_daily_quote(profile.get('philosophy_tradition', 'esoteric'))
            db.save_motivation(
                today,
                quote_data['quote'],
                quote_data['philosophy'],
                quote_data['tradition']
            )
            motivation = db.get_daily_motivation(today)
        
        if motivation:
            st.info(f"**{motivation['quote']}**")
            st.caption(motivation['philosophy'])
        
        st.markdown("---")
        
        # Priority Quests
        st.markdown("### ⭐ Priority Quests")
        priority_habits = [h for h in habits if h.get('priority')] if habits else []
        
        if priority_habits:
            for habit in priority_habits[:5]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    completed = db.is_completed(habit['id'], today)
                    if st.checkbox(
                        f"{'✅' if completed else '⬜'} {habit['name']}",
                        value=completed,
                        key=f"dash_habit_{habit['id']}"
                    ):
                        if not completed:
                            db.toggle_completion(habit['id'], today, True)
                            st.balloons()
                            st.rerun()
                    else:
                        if completed:
                            db.toggle_completion(habit['id'], today, False)
                            st.rerun()
                
                with col2:
                    difficulty_icons = {1: "🟢", 2: "🟡", 3: "🔴"}
                    st.caption(f"{difficulty_icons.get(habit['difficulty'], '🟢')} +{habit['xp_reward']} XP")
        else:
            st.caption("No priority habits set. Create some in the Habits page!")
        
        st.markdown("---")
        
        # Active Goals Summary
        st.markdown("### 🎯 Active Goals")
        goals = db.get_goals(completed=False)
        
        if goals:
            for goal in goals[:3]:
                st.markdown(f"**{goal['title']}**")
                progress = goal.get('progress', 0)
                st.progress(progress / 100)
                st.caption(f"{progress}% complete")
        else:
            st.caption("No active goals. Create some in the Goals page!")

    # ===== HABITS PAGE =====
    elif current_page == "Habits":
        st.title("⚡ Habits")
        
        tab1, tab2 = st.tabs(["Active Habits", "Completed"])
        
        with tab1:
            # Create New Habit
            with st.expander("➕ Create New Habit", expanded=False):
                with st.form("new_habit_form"):
                    name = st.text_input("Habit Name*")
                    description = st.text_area("Description")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        category = st.selectbox(
                            "Category*",
                            options=["fitness", "health", "learning", "mindfulness", "productivity", "creativity"]
                        )
                    
                    with col2:
                        frequency = st.selectbox(
                            "Frequency",
                            options=["daily", "weekdays", "weekends", "custom"]
                        )
                    
                    priority = st.checkbox("Mark as Priority")
                    
                    submitted = st.form_submit_button("🎯 Create Habit")
                    
                    if submitted and name:
                        assessment = ai_coach.assess_habit_difficulty(name, description, category)
                        
                        habit_id = db.create_habit(
                            name=name,
                            category=category,
                            description=description,
                            difficulty=assessment['difficulty'],
                            xp_reward=assessment['xp_reward'],
                            difficulty_rationale=assessment.get('rationale', ''),
                            frequency=frequency,
                            priority=priority
                        )
                        
                        habits = db.get_habits()
                        if len(habits) == 1:
                            db.unlock_achievement("first_habit")
                        elif len(habits) == 5:
                            db.unlock_achievement("habits_5")
                        elif len(habits) == 10:
                            db.unlock_achievement("habits_10")
                        
                        st.success(f"✨ Created habit: {name} (+{assessment['xp_reward']} XP per completion)")
                        st.rerun()
            
            # Display Habits
            habits = db.get_habits(active_only=True)
            today = get_cst_date()
            
            if habits:
                for habit in habits:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            completed = db.is_completed(habit['id'], today)
                            new_completed = st.checkbox(
                                f"{habit['name']}",
                                value=completed,
                                key=f"habit_{habit['id']}"
                            )
                            
                            if new_completed != completed:
                                db.toggle_completion(habit['id'], today, new_completed)
                                if new_completed:
                                    st.balloons()
                                    total_completions = len(db.get_completions(habit['id']))
                                    if total_completions == 1:
                                        db.unlock_achievement("first_complete")
                                    elif total_completions == 100:
                                        db.unlock_achievement("complete_100")
                                st.rerun()
                            
                            if habit.get('description'):
                                st.caption(habit['description'])
                        
                        with col2:
                            difficulty_map = {1: "🟢 Easy", 2: "🟡 Medium", 3: "🔴 Hard"}
                            st.caption(difficulty_map.get(habit['difficulty'], '🟢 Easy'))
                        
                        with col3:
                            if habit.get('priority'):
                                st.caption("⭐ Priority")
                            st.caption(f"+{habit['xp_reward']} XP")
                        
                        with col4:
                            completions = db.get_completions(habit['id'])
                            streak = calculate_streak(completions)
                            st.caption(f"🔥 {streak} day streak")
                        
                        st.markdown("---")
            else:
                st.info("No habits yet! Create your first habit above.")
        
        with tab2:
            all_habits = db.get_habits(active_only=False)
            completed_habits = [h for h in all_habits if not h.get('active', True)]
            
            if completed_habits:
                for habit in completed_habits:
                    st.caption(f"✅ {habit['name']}")
            else:
                st.caption("No completed habits")

    # ===== GOALS PAGE =====
    elif current_page == "Goals":
        st.title("🎯 Goals")
        
        tab1, tab2 = st.tabs(["Active Goals", "Completed"])
        
        with tab1:
            with st.expander("➕ Create New Goal", expanded=False):
                with st.form("new_goal_form"):
                    title = st.text_input("Goal Title*")
                    description = st.text_area("Description")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        category = st.selectbox(
                            "Category",
                            options=["personal", "career", "health", "learning", "financial", "relationships"]
                        )
                    
                    with col2:
                        deadline = st.date_input("Deadline (optional)", value=None)
                    
                    priority = st.checkbox("Mark as Priority")
                    
                    submitted = st.form_submit_button("🎯 Create Goal")
                    
                    if submitted and title:
                        assessment = ai_coach.assess_goal_difficulty(title, description, category)
                        
                        goal_id = db.create_goal(
                            title=title,
                            description=description,
                            category=category,
                            deadline=deadline.isoformat() if deadline else None,
                            difficulty=assessment['difficulty'],
                            xp_reward=assessment['xp_reward'],
                            priority=priority
                        )
                        
                        goals = db.get_goals()
                        if len(goals) == 1:
                            db.unlock_achievement("first_goal")
                        elif len(goals) == 5:
                            db.unlock_achievement("goals_5")
                        
                        st.success(f"✨ Created goal: {title}")
                        st.rerun()
            
            goals = db.get_goals(completed=False)
            
            if goals:
                for goal in goals:
                    with st.container():
                        st.markdown(f"### {goal['title']}")
                        
                        if goal.get('description'):
                            st.caption(goal['description'])
                        
                        progress = st.slider(
                            "Progress",
                            0, 100,
                            value=goal.get('progress', 0),
                            key=f"goal_progress_{goal['id']}"
                        )
                        
                        if progress != goal.get('progress', 0):
                            completed = progress >= 100
                            db.update_goal(goal['id'], progress=progress, completed=completed)
                            
                            if completed and not goal.get('completed'):
                                st.balloons()
                                st.success(f"🏆 Goal completed! +{goal['xp_reward']} XP")
                                
                                completed_goals = db.get_goals(completed=True)
                                if len(completed_goals) == 1:
                                    db.unlock_achievement("first_goal_complete")
                                elif len(completed_goals) == 5:
                                    db.unlock_achievement("goals_complete_5")
                            
                            st.rerun()
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if goal.get('priority'):
                                st.caption("⭐ Priority")
                        with col2:
                            st.caption(f"Category: {goal['category']}")
                        with col3:
                            if goal.get('deadline'):
                                st.caption(f"📅 {goal['deadline']}")
                        
                        st.markdown("---")
            else:
                st.info("No active goals! Create your first goal above.")
        
        with tab2:
            completed_goals = db.get_goals(completed=True)
            
            if completed_goals:
                for goal in completed_goals:
                    st.markdown(f"### ✅ {goal['title']}")
                    st.caption(f"Completed • +{goal['xp_reward']} XP earned")
                    st.markdown("---")
            else:
                st.caption("No completed goals yet")

    # ===== ANALYTICS PAGE =====
    elif current_page == "Analytics":
        st.title("📊 Analytics")
        
        period = st.selectbox(
            "Time Period",
            options=["daily", "weekly", "monthly", "yearly"],
            format_func=lambda x: x.capitalize()
        )
        
        start_date, end_date = get_date_range(period)
        
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Completions", total_completions)
        
        with col2:
            st.metric("XP Earned", format_xp(xp_earned))
        
        with col3:
            st.metric("Active Days", len(active_days))
        
        with col4:
            completion_rate = 0
            if habits:
                total_possible = len(habits) * len(active_days) if active_days else len(habits)
                completion_rate = get_completion_percentage(total_completions, total_possible)
            st.metric("Completion Rate", f"{completion_rate}%")
        
        st.markdown("---")
        
        # Habit Completions Chart
        if habits:
            st.markdown("### Habit Completions")
            
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
        st.markdown("### 🎯 Goals Progress")
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
        st.title("📝 Notes")
        
        with st.expander("➕ Create New Note", expanded=False):
            with st.form("new_note_form"):
                title = st.text_input("Note Title*")
                content = st.text_area("Content", height=200)
                
                col1, col2 = st.columns(2)
                with col1:
                    category = st.selectbox(
                        "Category",
                        options=["personal", "work", "health", "goals", "ideas", "learning"]
                    )
                
                with col2:
                    pinned = st.checkbox("Pin Note")
                
                submitted = st.form_submit_button("💾 Save Note")
                
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
                    
                    st.success("✨ Note saved!")
                    st.rerun()
        
        notes = db.get_notes()
        
        if notes:
            for note in notes:
                with st.expander(f"{'📌 ' if note.get('pinned') else ''}{note['title']}", expanded=note.get('pinned', False)):
                    st.markdown(note.get('content', ''))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"Category: {note.get('category', 'personal')}")
                    with col2:
                        created = note.get('created_at', '')
                        if created:
                            st.caption(f"Created: {created[:10]}")
                    with col3:
                        if st.button("🤖 AI Summary", key=f"summarize_{note['id']}"):
                            summary = ai_coach.summarize_note(note['title'], note.get('content', ''))
                            db.update_note(note['id'], ai_summary=summary)
                            st.rerun()
                    
                    if note.get('ai_summary'):
                        st.info(f"**AI Summary:**\n{note['ai_summary']}")
        else:
            st.info("No notes yet! Create your first note above.")

    # ===== REWARDS PAGE =====
    elif current_page == "Rewards":
        st.title("🏆 Rewards & Achievements")
        
        st.markdown("### 💪 Player Stats")
        
        stat_cols = st.columns(3)
        stat_names = ['strength', 'intelligence', 'vitality', 'agility', 'sense', 'willpower']
        
        for idx, stat in enumerate(stat_names):
            with stat_cols[idx % 3]:
                stat_value = stats.get(stat, 0)
                st.metric(stat.capitalize(), stat_value)
        
        st.markdown("---")
        
        st.markdown("### 🏅 Achievements")
        
        achievements = db.get_achievements()
        
        categories = {}
        for ach in achievements:
            cat = ach.get('category', 'general')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ach)
        
        for category, achs in categories.items():
            st.markdown(f"#### {category.capitalize()}")
            
            cols = st.columns(2)
            for idx, ach in enumerate(achs):
                with cols[idx % 2]:
                    unlocked = ach.get('unlocked_at') is not None
                    
                    icon = "✅" if unlocked else "🔒"
                    tier_colors = {
                        'bronze': '🥉',
                        'silver': '🥈',
                        'gold': '🥇',
                        'platinum': '💎',
                        'legendary': '👑'
                    }
                    tier_icon = tier_colors.get(ach.get('tier', 'bronze'), '🥉')
                    
                    st.markdown(f"{icon} {tier_icon} **{ach['title']}**")
                    st.caption(ach['description'])
                    st.caption(f"+{ach['xp_reward']} XP, +{ach['gold_reward']} Gold")
                    
                    if ach.get('special_power'):
                        st.caption(f"✨ {ach['special_power']}")
            
            st.markdown("---")

    # ===== SETTINGS PAGE =====
    elif current_page == "Settings":
        st.title("⚙️ Settings")
        
        st.markdown("### 👤 Profile")
        
        with st.form("settings_form"):
            display_name = st.text_input("Display Name", value=profile.get('display_name', 'Hunter'))
            
            gender = st.selectbox(
                "Gender",
                options=["neutral", "male", "female"],
                index=["neutral", "male", "female"].index(profile.get('gender', 'neutral'))
            )
            
            avatar_style = st.selectbox(
                "Avatar Style",
                options=["warrior", "mage", "rogue", "sage"],
                index=["warrior", "mage", "rogue", "sage"].index(profile.get('avatar_style', 'warrior'))
            )
            
            philosophy_tradition = st.selectbox(
                "Philosophy Tradition",
                options=["esoteric", "biblical", "quranic", "stoic", "eastern"],
                index=["esoteric", "biblical", "quranic", "stoic", "eastern"].index(profile.get('philosophy_tradition', 'esoteric'))
            )
            
            submitted = st.form_submit_button("💾 Save Settings")
            
            if submitted:
                db.update_profile(
                    display_name=display_name,
                    gender=gender,
                    avatar_style=avatar_style,
                    philosophy_tradition=philosophy_tradition
                )
                st.success("✨ Settings saved!")
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 About")
        st.info("""
        **Goal Quest - Python Edition**
        
        A gamified habit tracking and goal achievement system.
        
        - Track daily habits
        - Set and achieve goals
        - Earn XP and level up
        - Unlock achievements
        - Take notes with AI assistance
        
        Built with Streamlit & SQLite
        """)
