# ⚔️ Goal Quest - Python Edition

A gamified habit tracking and goal achievement system built with Streamlit.

## Features

- **📊 Dashboard** - Overview of your progress, daily wisdom, and priority quests
- **⚡ Habits** - Track daily habits with streaks and XP rewards
- **🎯 Goals** - Set and track long-term goals with progress tracking
- **📈 Analytics** - Visualize your progress over time
- **📝 Notes** - Take notes with AI-powered summaries
- **🏆 Achievements** - Unlock achievements as you progress
- **💰 Rewards** - Earn gold and level up your character

## Tech Stack

- **Frontend:** Streamlit
- **Database:** SQLite
- **AI:** Anthropic Claude (optional)
- **Charts:** Plotly
- **Data:** Pandas

## Setup

### Local Development

1. Clone the repository
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Run the app:
```bash
   streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

## Optional: AI Features

To enable AI-powered features (habit difficulty assessment, daily quotes, note summaries):

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Add it to Streamlit secrets:
   - Go to your app settings on Streamlit Cloud
   - Add secret: `ANTHROPIC_API_KEY = "your-key-here"`

## Database Schema

- **user_profile** - User settings and preferences
- **habits** - Habit definitions
- **completions** - Habit completion records
- **goals** - Goal definitions
- **user_stats** - XP, level, and player stats
- **notes** - User notes
- **achievements** - Achievement tracking
- **motivations** - Daily wisdom quotes

## Game Mechanics

- **XP System:** Level N requires N × 500 XP
- **Habit XP:** Easy (100), Medium (200), Hard (300)
- **Goal XP:** Normal (1000), Medium (2000), Hard (3000)
- **Streaks:** Consecutive daily completions
- **Achievements:** Unlock rewards for milestones

## License

MIT License
