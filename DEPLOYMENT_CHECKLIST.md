# 🚀 Goal Quest Deployment Checklist

## ✅ Pre-Deployment Verification

### 1. File Structure Check
Ensure your GitHub repository has this EXACT structure:
```
goal-quest-python/
├── .streamlit/
│   └── config.toml          ✓ Theme & server config
│
├── achievements.py           ✓ 200 achievements system
├── ai_coach.py              ✓ Philosophy quotes + AI
├── app.py                   ✓ Main application (1800+ lines)
├── character_visuals.py     ✓ Character SVG system
├── database.py              ✓ SQLite with 11 tables
├── shop_items.py            ✓ Complete shop system
├── utils.py                 ✓ Helper functions
├── requirements.txt         ✓ 4 dependencies
├── README.md                ✓ Documentation
└── .gitignore              ✓ Python ignores
```

### 2. Verify Each File

**Run this checklist:**

- [ ] `.streamlit/config.toml` exists with theme colors
- [ ] `requirements.txt` has exactly 4 packages (no plotly!)
- [ ] `app.py` has imports for character_visuals
- [ ] `character_visuals.py` exists and has get_character_svg function
- [ ] `shop_items.py` has ALL_SHOP_ITEMS list
- [ ] `achievements.py` has ALL_ACHIEVEMENTS (200 items)
- [ ] `database.py` has inventory and equipment tables
- [ ] `utils.py` has all 7 helper functions

### 3. Local Test (RECOMMENDED)

Before deploying to Streamlit Cloud, test locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Test in browser
# Visit: http://localhost:8501
```

**Test these features:**
- [ ] Onboarding flow completes
- [ ] Character avatar displays on dashboard
- [ ] Habits can be created and completed
- [ ] Goals can be created and tracked
- [ ] Shop displays items correctly
- [ ] Inventory shows equipment
- [ ] Achievements unlock
- [ ] Daily quote generates

---

## 🌐 Streamlit Cloud Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Complete Goal Quest restoration with character visuals"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Visit:** https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click:** "New app"
4. **Configure:**
   - Repository: `your-username/goal-quest-python`
   - Branch: `main`
   - Main file path: `app.py` ← **CRITICAL: Just "app.py" not ".streamlit/app.py"**
5. **Optional - Add AI:**
   - Click "Advanced settings"
   - Add secret: `ANTHROPIC_API_KEY = "sk-ant-..."`
6. **Click:** "Deploy!"

### Step 3: Wait for Build

**Expected timeline:**
- Installing dependencies: 30-60 seconds
- Building app: 30-60 seconds
- **Total:** 2-3 minutes

**Watch for:**
- ✅ Green checkmark = Success!
- ❌ Red X = Check logs for errors

---

## 🐛 Common Issues & Fixes

### Issue 1: "ModuleNotFoundError: No module named 'character_visuals'"

**Cause:** File not in repository root
**Fix:** 
```bash
# Verify file exists
ls character_visuals.py

# If missing, create it with content from FILE 8
```

### Issue 2: "ModuleNotFoundError: No module named 'plotly'"

**Cause:** Old requirements.txt still has plotly
**Fix:**
```bash
# Edit requirements.txt - remove plotly line
# Should only have 4 packages
```

### Issue 3: Pandas build failure

**Cause:** pandas==2.1.4 incompatible with Python 3.13
**Fix:**
```bash
# requirements.txt should have:
pandas>=2.2.0  # NOT pandas==2.1.4
```

### Issue 4: Character SVG not displaying

**Cause:** Missing import in app.py
**Fix:**
```python
# Add to top of app.py after other imports:
from character_visuals import get_character_svg, get_stat_visual_bars, get_level_up_animation, get_equipment_display
```

### Issue 5: Shop items not showing

**Cause:** Missing shop_items.py
**Fix:**
```bash
# Verify file exists
ls shop_items.py

# Should contain ALL_SHOP_ITEMS list with 30+ items
```

### Issue 6: "This app has encountered an error"

**Cause:** Various - check logs
**Fix:**
1. Click "Manage app" (bottom right)
2. Click "Logs"
3. Find the actual error message
4. Fix the specific issue

---

## 🎯 Post-Deployment Verification

Once deployed, test ALL features:

### Critical Path Test:

1. **Onboarding:**
   - [ ] Can complete onboarding
   - [ ] Character displays after onboarding
   - [ ] Philosophy tradition is saved

2. **Character System:**
   - [ ] Character avatar shows on dashboard
   - [ ] Stats display as animated bars
   - [ ] Character changes when leveling up
   - [ ] Equipment affects character appearance

3. **Habits:**
   - [ ] Create a habit
   - [ ] Complete a habit
   - [ ] XP and gold awarded
   - [ ] Streak counter works

4. **Goals:**
   - [ ] Create a goal
   - [ ] Update progress slider
   - [ ] Complete at 100%
   - [ ] XP and gold awarded

5. **Shop:**
   - [ ] Items display with rarities
   - [ ] Can purchase items
   - [ ] Gold deducted correctly
   - [ ] Items appear in inventory

6. **Inventory:**
   - [ ] Equipment slots display
   - [ ] Can equip items
   - [ ] Visual equipment display works
   - [ ] Consumables listed

7. **Achievements:**
   - [ ] Achievements unlock automatically
   - [ ] Stat bonuses applied
   - [ ] Progress tracked correctly

8. **Philosophy:**
   - [ ] Daily quote generates
   - [ ] Matches selected tradition
   - [ ] Quote changes daily
   - [ ] Philosophy text displays

---

## 🎨 Optional Enhancements

### Add Custom Domain (Streamlit Cloud Pro)
```
Settings → Custom domain → Add your domain
```

### Enable Analytics
```python
# Add to app.py if desired
import streamlit.components.v1 as components
components.html("""
<!-- Your analytics code -->
""")
```

### Add Favicon
```python
# In st.set_page_config
st.set_page_config(
    page_title="Goal Quest",
    page_icon="⚔️",  # or path to .ico file
    ...
)
```

---

## 📊 Performance Optimization

### If app is slow:

1. **Cache database calls:**
```python
@st.cache_data(ttl=60)
def get_cached_stats():
    return db.get_stats()
```

2. **Reduce SVG complexity:**
- Lower animation frame rates
- Simplify gradients
- Reduce particle effects

3. **Optimize queries:**
- Add indexes to database
- Limit query ranges
- Cache frequently accessed data

---

## 🔒 Security Best Practices

1. **Never commit API keys:**
   - Use Streamlit secrets
   - Add `.env` to `.gitignore`

2. **Validate user input:**
   - Already handled in database.py
   - SQL injection protected

3. **Rate limit shop purchases:**
   - Consider adding cooldowns
   - Prevent gold exploits

---

## 🎉 Success Criteria

Your app is fully deployed when:

- ✅ App loads without errors
- ✅ Character displays and animates
- ✅ All 9 pages accessible
- ✅ Database persists between sessions
- ✅ Achievements unlock correctly
- ✅ Shop purchases work
- ✅ Daily quotes generate
- ✅ Stats update in real-time
- ✅ Equipment affects character

**Congratulations! Your Goal Quest journey is complete!** ⚔️

---

## 📞 Support Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **Anthropic API:** https://docs.anthropic.com
- **GitHub Issues:** Create issue in your repo

---

## 🚀 Next Steps

1. **Share your app** with friends
2. **Track your habits** daily
3. **Level up** and unlock achievements
4. **Customize** the philosophy quotes
5. **Add more shop items** if desired
6. **Create your legend!**

*"The Hunter's journey never ends. Each day is a new quest."*

⚔️ **May your streaks be long and your XP abundant!** ⚔️
