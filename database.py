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
            gold_reward INTEGER NOT NULL DEFAULT 10,
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
            gold_reward INTEGER NOT NULL DEFAULT 200,
            completed BOOLEAN DEFAULT 0,
            priority BOOLEAN DEFAULT 0,
            steps TEXT DEFAULT '[]',
            ai_generated_steps TEXT DEFAULT '[]',
            habit_suggestions TEXT DEFAULT '[]',
            reminder_enabled BOOLEAN DEFAULT 0,
            reminder_days_before INTEGER DEFAULT 1,
            parent_goal_id INTEGER,
            progressive_suggestions TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )''')
        
        # Habit Completions
        c.execute('''CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date DATE NOT NULL,
            completed BOOLEAN DEFAULT 1,
            UNIQUE(habit_id, date)
        )''')
        
        # User Stats (100 LEVELS!)
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
            gold_reward INTEGER DEFAULT 10,
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
        
        # Inventory
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            equipped BOOLEAN DEFAULT 0,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Active Effects
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
        
        # Philosophy Library (NEW!)
        c.execute('''CREATE TABLE IF NOT EXISTS philosophy_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content TEXT,
            file_type TEXT,
            file_size INTEGER,
            ai_summary TEXT,
            key_concepts TEXT DEFAULT '[]',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        self.init_defaults()
    
    def init_defaults(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM user_profile")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO user_profile (id) VALUES (1)")
        
        c.execute("SELECT COUNT(*) FROM user_stats")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO user_stats (id, current_gold) VALUES (1, 5000)")  # Start with 5000 gold!
        
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
    
    # ===== HABITS =====
    def create_habit(self, name: str, category: str, description: str = "", **kwargs) -> int:
        conn = self.get_connection()
        c = conn.cursor()
        
        # Enhanced gold rewards (30% of XP as gold)
        if 'xp_reward' in kwargs and 'gold_reward' not in kwargs:
            kwargs['gold_reward'] = int(kwargs['xp_reward'] * 0.3)
        
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
            
            # Get rewards
            c.execute("SELECT xp_reward, gold_reward FROM habits WHERE id = ?", (habit_id,))
            row = c.fetchone()
            if row:
                xp_reward = row[0]
                gold_reward = row[1]
                self.add_xp(xp_reward)
                self.add_gold(gold_reward)
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
    
    # ===== GOALS =====
    def create_goal(self, title: str, **kwargs) -> int:
        conn = self.get_connection()
        c = conn.cursor()
        
        # Enhanced gold rewards (25% of XP as gold)
        if 'xp_reward' in kwargs and 'gold_reward' not in kwargs:
            kwargs['gold_reward'] = int(kwargs['xp_reward'] * 0.25)
        
        if 'steps' in kwargs and isinstance(kwargs['steps'], list):
            kwargs['steps'] = json.dumps(kwargs['steps'])
        if 'ai_generated_steps' in kwargs and isinstance(kwargs['ai_generated_steps'], list):
            kwargs['ai_generated_steps'] = json.dumps(kwargs['ai_generated_steps'])
        if 'habit_suggestions' in kwargs and isinstance(kwargs['habit_suggestions'], list):
            kwargs['habit_suggestions'] = json.dumps(kwargs['habit_suggestions'])
        if 'progressive_suggestions' in kwargs and isinstance(kwargs['progressive_suggestions'], list):
            kwargs['progressive_suggestions'] = json.dumps(kwargs['progressive_suggestions'])
        
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
            for field in ['steps', 'ai_generated_steps', 'habit_suggestions', 'progressive_suggestions']:
                if goal.get(field):
                    try:
                        goal[field] = json.loads(goal[field]) if isinstance(goal[field], str) else []
                    except:
                        goal[field] = []
        
        return goals
    
    def update_goal(self, goal_id: int, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        
        for field in ['steps', 'ai_generated_steps', 'habit_suggestions', 'progressive_suggestions']:
            if field in kwargs and isinstance(kwargs[field], list):
                kwargs[field] = json.dumps(kwargs[field])
        
        # If marking as complete
        if kwargs.get('completed') and not kwargs.get('completed_at'):
            kwargs['completed_at'] = datetime.now().isoformat()
            
            c.execute("SELECT xp_reward, gold_reward, completed FROM goals WHERE id = ?", (goal_id,))
            row = c.fetchone()
            if row and not row[2]:
                self.add_xp(row[0])
                self.add_gold(row[1])
        
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
    
    def get_goal_by_id(self, goal_id: int) -> Optional[Dict]:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = c.fetchone()
        if row:
            goal = dict(row)
            for field in ['steps', 'ai_generated_steps', 'habit_suggestions', 'progressive_suggestions']:
                if goal.get(field):
                    try:
                        goal[field] = json.loads(goal[field]) if isinstance(goal[field], str) else []
                    except:
                        goal[field] = []
            return goal
        return None
    
    # ===== USER STATS (100 LEVELS!) =====
    def get_stats(self) -> Dict:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM user_stats WHERE id = 1")
        row = c.fetchone()
        return dict(row) if row else {}
    
    def add_xp(self, amount: int):
        """Add XP and handle leveling up (UP TO LEVEL 100!)"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT level, current_xp, total_xp FROM user_stats WHERE id = 1")
        row = c.fetchone()
        
        if row:
            level, current_xp, total_xp = row
            new_current = current_xp + amount
            new_total = total_xp + amount
            
            # Level up logic: level N requires N * 500 XP (up to level 100!)
            new_level = level
            while new_current >= new_level * 500 and new_level < 100:
                new_current -= new_level * 500
                new_level += 1
            
            c.execute("""
                UPDATE user_stats 
                SET level = ?, current_xp = ?, total_xp = ?,
                    last_level_up = CASE WHEN ? > ? THEN CURRENT_TIMESTAMP ELSE last_level_up END
                WHERE id = 1
            """, (new_level, new_current, new_total, new_level, level))
            
            conn.commit()
            return new_level > level
        
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
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT id, quantity FROM inventory WHERE item_id = ?", (item_id,))
        row = c.fetchone()
        
        if row:
            c.execute("UPDATE inventory SET quantity = quantity + ? WHERE item_id = ?", (quantity, item_id))
        else:
            c.execute("INSERT INTO inventory (item_id, quantity) VALUES (?, ?)", (item_id, quantity))
        
        conn.commit()
    
    def get_inventory(self) -> List[Dict]:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM inventory ORDER BY purchased_at DESC")
        return [dict(row) for row in c.fetchall()]
    
    def get_equipped_items(self) -> Dict:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM equipment WHERE id = 1")
        row = c.fetchone()
        return dict(row) if row else {}
    
    def equip_item(self, item_id: str, slot: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"UPDATE equipment SET {slot}_id = ? WHERE id = 1", (item_id,))
        conn.commit()
    
    # ===== NOTES =====
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
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT unlocked_at, xp_reward, gold_reward, stat_bonus FROM achievements WHERE key = ?", (key,))
        row = c.fetchone()
        
        if row and not row[0]:
            c.execute("UPDATE achievements SET unlocked_at = CURRENT_TIMESTAMP WHERE key = ?", (key,))
            
            if row[1]:
                self.add_xp(row[1])
            
            if row[2]:
                self.add_gold(row[2])
            
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
    
    # ===== PHILOSOPHY LIBRARY =====
    def upload_document(self, filename: str, content: str, file_type: str, file_size: int) -> int:
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO philosophy_documents (filename, content, file_type, file_size)
            VALUES (?, ?, ?, ?)
        """, (filename, content, file_type, file_size))
        conn.commit()
        return c.lastrowid
    
    def get_documents(self) -> List[Dict]:
        c = self.get_connection().cursor()
        c.execute("SELECT * FROM philosophy_documents ORDER BY uploaded_at DESC")
        docs = [dict(row) for row in c.fetchall()]
        
        for doc in docs:
            if doc.get('key_concepts'):
                try:
                    doc['key_concepts'] = json.loads(doc['key_concepts']) if isinstance(doc['key_concepts'], str) else []
                except:
                    doc['key_concepts'] = []
        
        return docs
    
    def update_document(self, doc_id: int, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        
        if 'key_concepts' in kwargs and isinstance(kwargs['key_concepts'], list):
            kwargs['key_concepts'] = json.dumps(kwargs['key_concepts'])
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(doc_id)
        query = f"UPDATE philosophy_documents SET {', '.join(fields)} WHERE id = ?"
        c.execute(query, values)
        conn.commit()
    
    def get_all_document_content(self) -> str:
        """Get all document content for AI context"""
        c = self.get_connection().cursor()
        c.execute("SELECT content FROM philosophy_documents WHERE content IS NOT NULL")
        rows = c.fetchall()
        return "\n\n---\n\n".join([row[0] for row in rows if row[0]])

    # ===== PDF SEGMENTS & SEARCH =====
    def create_segments_table(self):
        """Create table for PDF segments/chunks"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS document_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            segment_type TEXT DEFAULT 'paragraph',
            segment_number INTEGER,
            title TEXT,
            content TEXT NOT NULL,
            page_number INTEGER,
            word_count INTEGER,
            key_terms TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES philosophy_documents(id) ON DELETE CASCADE
        )''')
        
        conn.commit()
    
    def save_document_segments(self, document_id: int, segments: List[Dict]):
        """Save document segments for intelligent search"""
        conn = self.get_connection()
        c = conn.cursor()
        
        for segment in segments:
            c.execute("""
                INSERT INTO document_segments 
                (document_id, segment_type, segment_number, title, content, page_number, word_count, key_terms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                segment.get('type', 'paragraph'),
                segment.get('number', 0),
                segment.get('title', ''),
                segment['content'],
                segment.get('page', 0),
                segment.get('word_count', 0),
                json.dumps(segment.get('key_terms', []))
            ))
        
        conn.commit()
    
    def get_document_segments(self, document_id: int, segment_type: str = None) -> List[Dict]:
        """Get all segments for a document"""
        c = self.get_connection().cursor()
        
        query = "SELECT * FROM document_segments WHERE document_id = ?"
        params = [document_id]
        
        if segment_type:
            query += " AND segment_type = ?"
            params.append(segment_type)
        
        query += " ORDER BY segment_number ASC"
        
        c.execute(query, params)
        segments = [dict(row) for row in c.fetchall()]
        
        for segment in segments:
            if segment.get('key_terms'):
                try:
                    segment['key_terms'] = json.loads(segment['key_terms'])
                except:
                    segment['key_terms'] = []
        
        return segments
    
    def search_documents(self, query: str, document_id: int = None) -> List[Dict]:
        """Search through document content"""
        c = self.get_connection().cursor()
        
        search_query = """
            SELECT ds.*, pd.filename 
            FROM document_segments ds
            JOIN philosophy_documents pd ON ds.document_id = pd.id
            WHERE ds.content LIKE ?
        """
        params = [f"%{query}%"]
        
        if document_id:
            search_query += " AND ds.document_id = ?"
            params.append(document_id)
        
        search_query += " ORDER BY ds.document_id, ds.segment_number LIMIT 50"
        
        c.execute(search_query, params)
        return [dict(row) for row in c.fetchall()]
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
