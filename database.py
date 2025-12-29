import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import pytz

class Database:
    def __init__(self, db_path="goal_quest.db"):
        self.db_path = db_path
        self.conn = None
        self.cst = pytz.timezone('America/Chicago')
        self.init_db()
    
    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # User Profile
        c.execute('''CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            display_name TEXT DEFAULT 'Hunter',
            gender TEXT DEFAULT 'neutral',
            avatar_style TEXT DEFAULT 'warrior',
            timezone TEXT DEFAULT 'America/Chicago',
            onboarding_completed BOOLEAN DEFAULT 0,
            notifications_enabled BOOLEAN DEFAULT 1,
            daily_reminder_time TEXT DEFAULT '09:00',
            weekly_report_enabled BOOLEAN DEFAULT 1,
            philosophy_tradition TEXT DEFAULT 'esoteric',
            philosophy_traditions TEXT DEFAULT '[]',
            focus_areas TEXT DEFAULT '[]',
            challenge_approaches TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Habits
        c.execute('''CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            difficulty INTEGER NOT NULL DEFAULT 1,
            xp_reward INTEGER NOT NULL DEFAULT 50,
            difficulty_rationale TEXT,
            priority BOOLEAN DEFAULT 0,
            color TEXT NOT NULL DEFAULT 'bg-blue-500',
            frequency TEXT DEFAULT 'daily',
            frequency_days TEXT DEFAULT '[]',
            custom_interval INTEGER,
            reminder_time TEXT,
            reminder_enabled BOOLEAN DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Goals
        c.execute('''CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'personal',
            deadline DATE,
            progress INTEGER DEFAULT 0,
            difficulty INTEGER NOT NULL DEFAULT 1,
            xp_reward INTEGER NOT NULL DEFAULT 1000,
            completed BOOLEAN DEFAULT 0,
            priority BOOLEAN DEFAULT 0,
            steps TEXT DEFAULT '[]',
            reminder_enabled BOOLEAN DEFAULT 0,
            reminder_days_before INTEGER DEFAULT 1,
            parent_goal_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Habit Completions
        c.execute('''CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date DATE NOT NULL,
            completed BOOLEAN DEFAULT 1,
            UNIQUE(habit_id, date)
        )''')
        
        # User Stats (WITH GOLD!)
        c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY,
            level INTEGER DEFAULT 1,
            current_xp INTEGER DEFAULT 0,
            total_xp INTEGER DEFAULT 0,
            last_level_up TIMESTAMP,
            strength INTEGER DEFAULT 0,
            intelligence INTEGER DEFAULT 0,
            vitality INTEGER DEFAULT 0,
            agility INTEGER DEFAULT 0,
            sense INTEGER DEFAULT 0,
            willpower INTEGER DEFAULT 0,
            current_gold INTEGER DEFAULT 0,
            lifetime_gold INTEGER DEFAULT 0
        )''')
        
        # Notes
        c.execute('''CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            category TEXT DEFAULT 'personal',
            tags TEXT DEFAULT '[]',
            ai_summary TEXT,
            pinned BOOLEAN DEFAULT 0,
            color TEXT DEFAULT 'default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Achievements
        c.execute('''CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            tier TEXT DEFAULT 'bronze',
            xp_reward INTEGER DEFAULT 50,
            gold_reward INTEGER DEFAULT 0,
            stat_bonus TEXT,
            special_power TEXT,
            unlocked_at TIMESTAMP
        )''')
        
        # Daily Motivations
        c.execute('''CREATE TABLE IF NOT EXISTS motivations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            quote TEXT NOT NULL,
            philosophy TEXT NOT NULL,
            tradition TEXT NOT NULL,
            habit_context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Inventory (SHOP SYSTEM!)
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            equipped BOOLEAN DEFAULT 0,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Active Effects (CONSUMABLES!)
        c.execute('''CREATE TABLE IF NOT EXISTS active_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            effect_type TEXT NOT NULL,
            value REAL NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            item_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Equipment Loadout
        c.execute('''CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY,
            weapon_id TEXT,
            armor_id TEXT,
            ring_id TEXT,
            amulet_id TEXT,
            head_id TEXT
        )''')
        
        conn.commit()
        self.init_defaults()
    
    def init_defaults(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Initialize user profile if not exists
        c.execute("SELECT COUNT(*) FROM user_profile")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO user_profile (id) VALUES (1)")
        
        # Initialize user stats if not exists
        c.execute("SELECT COUNT(*) FROM user_stats")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO user_stats (id, current_gold) VALUES (1, 1000)")  # Start with 1000 gold
        
        # Initialize equipment if not exists
        c.execute("SELECT COUNT(*) FROM equipment")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO equipment (id) VALUES (1)")
        
        conn.commit()
    
    # ===== USER PROFILE =====
    def get_profile(self) -> Dict:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM user_profile WHERE id = 1")
        row = c.fetchone()
        if row:
            profile = dict(row)
            # Parse JSON fields
            for field in ['philosophy_traditions', 'focus_areas', 'challenge_approaches']:
                if profile.get(field):
                    try:
                        profile[field] = json.loads(profile[field]) if isinstance(profile[field], str) else profile[field]
                    except:
                        profile[field] = []
            return profile
        return {}
    
    def update_profile(self, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = json.dumps(value)
            fields.append(f"{key} = ?")
            values.append(value)
        
        query = f"UPDATE user_profile SET {', '.join(fields)} WHERE id = 1"
        c.execute(query, values)
        conn.commit()
    
    # ===== HABITS ===== (same as before, keeping existing code)
    def create_habit(self, name: str, category: str, description: str = "", **kwargs) -> int:
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'frequency_days' in kwargs and isinstance(kwargs['frequency_days'], list):
            kwargs['frequency_days'] = json.dumps(kwargs['frequency_days'])
        
        fields = ['name', 'category', 'description'] + list(kwargs.keys())
        values = [name, category, description] + list(kwargs.values())
        placeholders = ', '.join(['?'] * len(fields))
        
        query = f"INSERT INTO habits ({', '.join(fields)}) VALUES ({placeholders})"
        c.execute(query, values)
        conn.commit()
        return c.lastrowid
    
    def get_habits(self, active_only=True) -> List[Dict]:
        c = self.get_connection().cursor()
        query = "SELECT * FROM habits"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY priority DESC, created_at DESC"
        
        c.execute(query)
        habits = [dict(row) for row in c.fetchall()]
        
        for habit in habits:
            if habit.get('frequency_days'):
                try:
                    habit['frequency_days'] = json.loads(habit['frequency_days']) if isinstance(habit['frequency_days'], str) else []
                except:
                    habit['frequency_days'] = []
        
        return habits
    
    def update_habit(self, habit_id: int, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'frequency_days' in kwargs and isinstance(kwargs['frequency_days'], list):
            kwargs['frequency_days'] = json.dumps(kwargs['frequency_days'])
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(habit_id)
        query = f"UPDATE habits SET {', '.join(fields)} WHERE id = ?"
        c.execute(query, values)
        conn.commit()
    
    def delete_habit(self, habit_id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        c.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        conn.commit()
    
    # ===== COMPLETIONS =====
    def toggle_completion(self, habit_id: int, date_str: str, completed: bool = True):
        conn = self.get_connection()
        c = conn.cursor()
        
        if completed:
            c.execute("""
                INSERT OR REPLACE INTO completions (habit_id, date, completed)
                VALUES (?, ?, 1)
            """, (habit_id, date_str))
            
            # Get XP reward and add it
            c.execute("SELECT xp_reward FROM habits WHERE id = ?", (habit_id,))
            row = c.fetchone()
            if row:
                xp_reward = row[0]
                # Award XP
                self.add_xp(xp_reward)
                # Award gold (10% of XP as gold)
                self.add_gold(int(xp_reward * 0.1))
        else:
            c.execute("DELETE FROM completions WHERE habit_id = ? AND date = ?", (habit_id, date_str))
        
        conn.commit()
    
    def get_completions(self, habit_id: int, start_date: str = None, end_date: str = None) -> List[Dict]:
        c = self.get_connection().cursor()
        query = "SELECT * FROM completions WHERE habit_id = ?"
        params = [habit_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        c.execute(query, params)
        return [dict(row) for row in c.fetchall()]
    
    def is_completed(self, habit_id: int, date_str: str) -> bool:
        c = self.get_connection().cursor()
        c.execute("SELECT completed FROM completions WHERE habit_id = ? AND date = ?", (habit_id, date_str))
        row = c.fetchone()
        return bool(row and row[0]) if row else False
    
    # ===== GOALS ===== (keeping existing code)
    def create_goal(self, title: str, **kwargs) -> int:
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'steps' in kwargs and isinstance(kwargs['steps'], list):
            kwargs['steps'] = json.dumps(kwargs['steps'])
        
        fields = ['title'] + list(kwargs.keys())
        values = [title] + list(kwargs.values())
        placeholders = ', '.join(['?'] * len(fields))
        
        query = f"INSERT INTO goals ({', '.join(fields)}) VALUES ({placeholders})"
        c.execute(query, values)
        conn.commit()
        return c.lastrowid
    
    def get_goals(self, completed=None) -> List[Dict]:
        c = self.get_connection().cursor()
        query = "SELECT * FROM goals"
        if completed is not None:
            query += f" WHERE completed = {1 if completed else 0}"
        query += " ORDER BY priority DESC, deadline ASC"
        
        c.execute(query)
        goals = [dict(row) for row in c.fetchall()]
        
        for goal in goals:
            if goal.get('steps'):
                try:
                    goal['steps'] = json.loads(goal['steps']) if isinstance(goal['steps'], str) else []
                except:
                    goal['steps'] = []
        
        return goals
    
    def update_goal(self, goal_id: int, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'steps' in kwargs and isinstance(kwargs['steps'], list):
            kwargs['steps'] = json.dumps(kwargs['steps'])
        
        # If marking as complete, award XP
        if kwargs.get('completed'):
            c.execute("SELECT xp_reward, completed FROM goals WHERE id = ?", (goal_id,))
            row = c.fetchone()
            if row and not row[1]:  # If not already completed
                self.add_xp(row[0])
                self.add_gold(int(row[0] * 0.2))  # 20% of XP as gold for goals
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(goal_id)
        query = f"UPDATE goals SET {', '.join(fields)} WHERE id = ?"
        c.execute(query, values)
        conn.commit()
    
    def delete_goal(self, goal_id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
    
    # ===== USER STATS =====
    def get_stats(self) -> Dict:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM user_stats WHERE id = 1")
        row = c.fetchone()
        return dict(row) if row else {}
    
    def add_xp(self, amount: int):
        """Add XP and handle leveling up"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT level, current_xp, total_xp FROM user_stats WHERE id = 1")
        row = c.fetchone()
        
        if row:
            level, current_xp, total_xp = row
            new_current = current_xp + amount
            new_total = total_xp + amount
            
            # Level up logic: level N requires N * 500 XP
            new_level = level
            while new_current >= new_level * 500:
                new_current -= new_level * 500
                new_level += 1
            
            c.execute("""
                UPDATE user_stats 
                SET level = ?, current_xp = ?, total_xp = ?,
                    last_level_up = CASE WHEN ? > ? THEN CURRENT_TIMESTAMP ELSE last_level_up END
                WHERE id = 1
            """, (new_level, new_current, new_total, new_level, level))
            
            conn.commit()
            return new_level > level  # Return True if leveled up
        
        return False
    
    def add_gold(self, amount: int):
        """Add gold to player"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE user_stats 
            SET current_gold = current_gold + ?, lifetime_gold = lifetime_gold + ?
            WHERE id = 1
        """, (amount, amount))
        conn.commit()
    
    def spend_gold(self, amount: int) -> bool:
        """Spend gold if available"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT current_gold FROM user_stats WHERE id = 1")
        row = c.fetchone()
        
        if row and row[0] >= amount:
            c.execute("UPDATE user_stats SET current_gold = current_gold - ? WHERE id = 1", (amount,))
            conn.commit()
            return True
        return False
    
    def update_stat(self, stat_name: str, amount: int):
        """Update a specific stat"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"""
            UPDATE user_stats 
            SET {stat_name} = {stat_name} + ?
            WHERE id = 1
        """, (amount,))
        conn.commit()
    
    # ===== INVENTORY & SHOP =====
    def add_to_inventory(self, item_id: str, quantity: int = 1):
        """Add item to inventory"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Check if item already exists
        c.execute("SELECT id, quantity FROM inventory WHERE item_id = ?", (item_id,))
        row = c.fetchone()
        
        if row:
            # Update quantity
            c.execute("UPDATE inventory SET quantity = quantity + ? WHERE item_id = ?", (quantity, item_id))
        else:
            # Insert new
            c.execute("INSERT INTO inventory (item_id, quantity) VALUES (?, ?)", (item_id, quantity))
        
        conn.commit()
    
    def get_inventory(self) -> List[Dict]:
        """Get all inventory items"""
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM inventory ORDER BY purchased_at DESC")
        return [dict(row) for row in c.fetchall()]
    
    def get_equipped_items(self) -> Dict:
        """Get currently equipped items"""
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM equipment WHERE id = 1")
        row = c.fetchone()
        return dict(row) if row else {}
    
    def equip_item(self, item_id: str, slot: str):
        """Equip an item to a slot"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"UPDATE equipment SET {slot}_id = ? WHERE id = 1", (item_id,))
        conn.commit()
    
    # ===== NOTES ===== (keeping existing code)
    def create_note(self, title: str, content: str = "", **kwargs) -> int:
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            kwargs['tags'] = json.dumps(kwargs['tags'])
        
        fields = ['title', 'content'] + list(kwargs.keys())
        values = [title, content] + list(kwargs.values())
        placeholders = ', '.join(['?'] * len(fields))
        
        query = f"INSERT INTO notes ({', '.join(fields)}) VALUES ({placeholders})"
        c.execute(query, values)
        conn.commit()
        return c.lastrowid
    
    def get_notes(self) -> List[Dict]:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM notes ORDER BY pinned DESC, updated_at DESC")
        notes = [dict(row) for row in c.fetchall()]
        
        for note in notes:
            if note.get('tags'):
                try:
                    note['tags'] = json.loads(note['tags']) if isinstance(note['tags'], str) else []
                except:
                    note['tags'] = []
        
        return notes
    
    def update_note(self, note_id: int, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            kwargs['tags'] = json.dumps(kwargs['tags'])
        
        kwargs['updated_at'] = datetime.now().isoformat()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(note_id)
        query = f"UPDATE notes SET {', '.join(fields)} WHERE id = ?"
        c.execute(query, values)
        conn.commit()
    
    def delete_note(self, note_id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    
    # ===== ACHIEVEMENTS =====
    def get_achievements(self, unlocked_only=False) -> List[Dict]:
        c = self.get_connection().cursor()
        query = "SELECT * FROM achievements"
        if unlocked_only:
            query += " WHERE unlocked_at IS NOT NULL"
        query += " ORDER BY unlocked_at DESC NULLS LAST, tier, category"
        
        c.execute(query)
        achievements = [dict(row) for row in c.fetchall()]
        
        for ach in achievements:
            if ach.get('stat_bonus'):
                try:
                    ach['stat_bonus'] = json.loads(ach['stat_bonus']) if isinstance(ach['stat_bonus'], str) else None
                except:
                    ach['stat_bonus'] = None
        
        return achievements
    
    def unlock_achievement(self, key: str):
        """Unlock an achievement and award rewards"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT unlocked_at, xp_reward, gold_reward, stat_bonus FROM achievements WHERE key = ?", (key,))
        row = c.fetchone()
        
        if row and not row[0]:  # Not yet unlocked
            c.execute("UPDATE achievements SET unlocked_at = CURRENT_TIMESTAMP WHERE key = ?", (key,))
            
            # Award XP
            if row[1]:
                self.add_xp(row[1])
            
            # Award gold
            if row[2]:
                self.add_gold(row[2])
            
            # Award stat bonus
            if row[3]:
                try:
                    bonus = json.loads(row[3])
                    self.update_stat(bonus['stat'], bonus['amount'])
                except:
                    pass
            
            conn.commit()
            return True
        return False
    
    # ===== DAILY MOTIVATION =====
    def get_daily_motivation(self, date_str: str = None) -> Optional[Dict]:
        if date_str is None:
            date_str = datetime.now(self.cst).strftime('%Y-%m-%d')
        
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM motivations WHERE date = ?", (date_str,))
        row = c.fetchone()
        return dict(row) if row else None
    
    def save_motivation(self, date_str: str, quote: str, philosophy: str, tradition: str, habit_context: str = None):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO motivations (date, quote, philosophy, tradition, habit_context)
            VALUES (?, ?, ?, ?, ?)
        """, (date_str, quote, philosophy, tradition, habit_context))
        conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
