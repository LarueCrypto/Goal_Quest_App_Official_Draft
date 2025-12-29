# Achievement definitions
ALL_ACHIEVEMENTS = [
    # STREAKS
    {"key": "streak_3", "title": "Getting Started", "description": "Maintain a 3-day streak", "icon": "🔥", "category": "streaks", "tier": "bronze", "xp_reward": 100, "gold_reward": 10},
    {"key": "streak_7", "title": "Week Warrior", "description": "Maintain a 7-day streak", "icon": "🔥", "category": "streaks", "tier": "bronze", "xp_reward": 250, "gold_reward": 25},
    {"key": "streak_14", "title": "Fortnight Fighter", "description": "Maintain a 14-day streak", "icon": "🔥", "category": "streaks", "tier": "silver", "xp_reward": 500, "gold_reward": 50},
    {"key": "streak_30", "title": "Monthly Master", "description": "Maintain a 30-day streak", "icon": "🔥", "category": "streaks", "tier": "gold", "xp_reward": 1000, "gold_reward": 100},
    {"key": "perfect_week", "title": "Perfect Week", "description": "Complete all habits for 7 consecutive days", "icon": "✓", "category": "streaks", "tier": "gold", "xp_reward": 1200, "gold_reward": 120},
    
    # LEVELS
    {"key": "level_5", "title": "Rising Star", "description": "Reach Level 5", "icon": "⭐", "category": "levels", "tier": "bronze", "xp_reward": 500, "gold_reward": 50},
    {"key": "level_10", "title": "Seasoned Adventurer", "description": "Reach Level 10", "icon": "⭐", "category": "levels", "tier": "silver", "xp_reward": 1000, "gold_reward": 100},
    {"key": "level_20", "title": "Expert", "description": "Reach Level 20", "icon": "👑", "category": "levels", "tier": "gold", "xp_reward": 2000, "gold_reward": 200},
    {"key": "level_30", "title": "Master", "description": "Reach Level 30", "icon": "👑", "category": "levels", "tier": "gold", "xp_reward": 3000, "gold_reward": 300},
    {"key": "level_50", "title": "Legendary Hero", "description": "Reach Level 50", "icon": "🛡️", "category": "levels", "tier": "platinum", "xp_reward": 5000, "gold_reward": 500},
    
    # HABITS
    {"key": "first_habit", "title": "Habit Former", "description": "Create your first habit", "icon": "⚡", "category": "habits", "tier": "bronze", "xp_reward": 100, "gold_reward": 10},
    {"key": "habits_5", "title": "Building Foundation", "description": "Create 5 habits", "icon": "📚", "category": "habits", "tier": "bronze", "xp_reward": 250, "gold_reward": 25},
    {"key": "habits_10", "title": "Habit Collector", "description": "Create 10 habits", "icon": "📚", "category": "habits", "tier": "silver", "xp_reward": 500, "gold_reward": 50},
    {"key": "first_complete", "title": "First Step", "description": "Complete your first habit", "icon": "✓", "category": "habits", "tier": "bronze", "xp_reward": 50, "gold_reward": 5},
    {"key": "complete_100", "title": "Century Mark", "description": "Complete habits 100 times", "icon": "✓", "category": "habits", "tier": "silver", "xp_reward": 800, "gold_reward": 80},
    {"key": "complete_500", "title": "Half Millennium", "description": "Complete habits 500 times", "icon": "✓", "category": "habits", "tier": "gold", "xp_reward": 2000, "gold_reward": 200},
    
    # GOALS
    {"key": "first_goal", "title": "Goal Setter", "description": "Create your first goal", "icon": "🎯", "category": "goals", "tier": "bronze", "xp_reward": 100, "gold_reward": 10},
    {"key": "goals_5", "title": "Visionary", "description": "Create 5 goals", "icon": "🎯", "category": "goals", "tier": "bronze", "xp_reward": 250, "gold_reward": 25},
    {"key": "first_goal_complete", "title": "Goal Achiever", "description": "Complete your first goal", "icon": "🏆", "category": "goals", "tier": "bronze", "xp_reward": 500, "gold_reward": 50},
    {"key": "goals_complete_5", "title": "Goal Crusher", "description": "Complete 5 goals", "icon": "🏆", "category": "goals", "tier": "silver", "xp_reward": 1000, "gold_reward": 100},
    
    # SPECIAL
    {"key": "first_note", "title": "Journal Keeper", "description": "Create your first note", "icon": "📝", "category": "special", "tier": "bronze", "xp_reward": 50, "gold_reward": 5},
]

def initialize_achievements(db):
    """Initialize all achievements in the database"""
    conn = db.get_connection()
    c = conn.cursor()
    
    for ach in ALL_ACHIEVEMENTS:
        try:
            c.execute("""
                INSERT OR IGNORE INTO achievements 
                (key, title, description, icon, category, tier, xp_reward, gold_reward, stat_bonus, special_power)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ach["key"],
                ach["title"],
                ach["description"],
                ach["icon"],
                ach["category"],
                ach["tier"],
                ach["xp_reward"],
                ach["gold_reward"],
                ach.get("stat_bonus"),
                ach.get("special_power")
            ))
        except Exception as e:
            print(f"Error initializing achievement {ach['key']}: {e}")
    
    conn.commit()
