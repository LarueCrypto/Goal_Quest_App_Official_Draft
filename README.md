# ⚔️ Goal Quest - Complete Python Edition

A gamified habit tracking and goal achievement system inspired by Solo Leveling. Transform your daily practices into epic quests, earn XP, level up, and unlock your true potential.

## ✨ Features

### 🎯 Core Systems
- **Habit Tracking** - Track daily habits with flexible scheduling (daily, weekdays, weekends, custom)
- **Goal Management** - Set and achieve goals with progress tracking and step-by-step breakdowns
- **XP & Leveling** - Earn 50-500 XP per habit (50 XP increments), level up, gain power
- **200 Achievements** - Bronze to Legendary achievements across 10 categories
- **Player Stats** - Develop 6 core stats: Strength, Intelligence, Vitality, Agility, Sense, Willpower

### 🛒 Shop & Economy
- **Gold System** - Earn gold from habits (10% of XP) and goals (20% of XP)
- **Complete Shop** - 30+ items across consumables, equipment, and cosmetics
- **Rarity System** - Common to Divine tier items with visual effects
- **Equipment Slots** - Weapon, Armor, Ring, Amulet with stat bonuses
- **Consumables** - XP boosters, gold multipliers, streak shields, stat elixirs

### 📚 Philosophy & Wisdom
- **8 Traditions** - Esoteric, Kemetic, Samurai, Biblical, Quranic, Stoic, Eastern, Occult
- **Daily Quotes** - Contextual wisdom based on your habits and chosen tradition
- **Deep Philosophy** - Extensive philosophical context with each quote
- **AI Integration** - Optional Claude AI for difficulty assessment and summaries

### 🎨 Rich Experience
- **Dark Theme** - Black and gold aesthetic with glows and animations
- **Streak Tracking** - Monitor daily streaks with comeback achievements
- **Notes System** - Journal your journey with AI-powered summaries
- **Analytics** - Track completions, XP earned, and completion rates

## 🚀 Tech Stack

- **Frontend:** Streamlit (Python web framework)
- **Database:** SQLite (11 tables)
- **AI:** Anthropic Claude API (optional)
- **Styling:** Custom CSS with animations
- **Charts:** Native Streamlit charts

## 📦 Installation

### Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/goal-quest-python.git
cd goal-quest-python
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the app:**
```bash
streamlit run app.py
```

4. **Open your browser:**
Navigate to `http://localhost:8501`

### Streamlit Cloud Deployment

1. **Push code to GitHub**

2. **Deploy on Streamlit Cloud:**
   - Visit https://share.streamlit.io
   - Click "New app"
   - Select your repository
   - Main file: `app.py`
   - Deploy!

3. **Optional - Add AI API Key:**
   - In Streamlit Cloud settings
   - Add secret: `ANTHROPIC_API_KEY = "your-key-here"`

## 🎮 Game Mechanics

### XP System
- **Easy Habits:** 50-150 XP
- **Medium Habits:** 200-300 XP  
- **Hard Habits:** 350-500 XP
- **Goals:** 1000-3000 XP based on difficulty
- **Level Formula:** Level N requires N × 500 XP

### Gold Economy
- Earn 10% of habit XP as gold
- Earn 20% of goal XP as gold
- Start with 1,000 gold
- Shop items range from 400 to 500,000 gold

### Streaks
- Track consecutive daily completions
- Achievements at: 3, 7, 14, 30, 60, 90, 180, 365 days
- Streak shields available in shop

### Achievements (200 Total)
- **Streaks** (25) - Daily consistency rewards
- **Levels** (25) - Leveling milestones
- **Habits** (40) - Habit creation and completion
- **Goals** (40) - Goal achievements
- **Special** (30) - Login, purchases, notes
- **Stats** (30) - Stat milestones
- **Legendary** (10) - Ultimate achievements

## 📁 Database Schema

### Core Tables
1. **user_profile** - Display name, gender, avatar, philosophy, preferences
2. **habits** - Name, category, difficulty, XP, frequency, reminders
3. **goals** - Title, progress, difficulty, XP, steps, deadlines
4. **completions** - Habit completion tracking by date
5. **user_stats** - Level, XP, gold, 6 player stats

### Shop Tables
6. **inventory** - Owned items and quantities
7. **active_effects** - Temporary buffs (XP/gold multipliers)
8. **equipment** - Equipped items per slot

### Content Tables
9. **notes** - Journal entries with AI summaries
10. **achievements** - Achievement progress
11. **motivations** - Daily wisdom quotes

## 🎨 Customization

### Philosophy Traditions
Choose your daily wisdom source:
- **Esoteric** - Hermetic mysteries and alchemy
- **Kemetic** - Ancient Egyptian wisdom (Ra, Thoth, Ma'at)
- **Samurai** - Bushido code and martial philosophy
- **Biblical** - Christian teachings and scripture
- **Quranic** - Islamic wisdom and Quranic verses
- **Stoic** - Greco-Roman philosophy (Marcus Aurelius, Seneca)
- **Eastern** - Tao, Zen, and Buddhist teachings
- **Occult** - Left-hand path and ceremonial magic

### Avatar Styles
- **Warrior** - Strength and discipline focused
- **Mage** - Intelligence and wisdom path
- **Rogue** - Agility and cunning approach
- **Sage** - Balance and enlightenment journey

## 🔮 Optional AI Features

With an Anthropic API key, unlock:
- **Smart Difficulty Assessment** - AI analyzes habit descriptions for accurate XP rewards
- **Contextual Quotes** - Personalized wisdom based on your current habits
- **Note Summaries** - AI-powered insights from your journal entries

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- Inspired by **Solo Leveling** (만화/웹툰)
- Philosophy quotes synthesized from traditional sources
- Built with passion for gamification and self-improvement

## 📧 Support

Questions? Issues? Open a GitHub issue or reach out!

---

**Remember:** Your journey is unique. The habits you build today shape the legend you become tomorrow.

*"The true power lies not in the system, but in the Hunter who wields it."*

⚔️ **Begin Your Quest** ⚔️
