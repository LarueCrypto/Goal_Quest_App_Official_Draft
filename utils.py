from datetime import datetime, timedelta, date
from typing import Tuple, List
import pytz

def get_cst_now():
    """Get current time in CST"""
    cst = pytz.timezone('America/Chicago')
    return datetime.now(cst)

def get_cst_date():
    """Get current date in CST as string"""
    return get_cst_now().strftime('%Y-%m-%d')

def calculate_streak(completions: List[dict]) -> int:
    """Calculate current streak from completion records"""
    if not completions:
        return 0
    
    # Sort by date descending
    sorted_completions = sorted(completions, key=lambda x: x['date'], reverse=True)
    
    today = get_cst_date()
    current_date = datetime.strptime(today, '%Y-%m-%d').date()
    
    streak = 0
    for completion in sorted_completions:
        comp_date = datetime.strptime(completion['date'], '%Y-%m-%d').date()
        
        expected_date = current_date - timedelta(days=streak)
        
        if comp_date == expected_date:
            streak += 1
        elif comp_date < expected_date:
            break
    
    return streak

def format_xp(xp: int) -> str:
    """Format XP with K/M suffixes"""
    if xp >= 1000000:
        return f"{xp/1000000:.1f}M"
    elif xp >= 1000:
        return f"{xp/1000:.1f}K"
    return str(xp)

def get_rank_color(level: int) -> str:
    """Get color for level/rank"""
    if level >= 100:
        return "#ffd700"  # Gold
    elif level >= 50:
        return "#c0c0c0"  # Silver
    elif level >= 20:
        return "#cd7f32"  # Bronze
    return "#808080"  # Gray

def get_completion_percentage(completed: int, total: int) -> int:
    """Calculate completion percentage"""
    if total == 0:
        return 0
    return int((completed / total) * 100)

def get_date_range(period: str) -> Tuple[str, str]:
    """Get date range for analytics periods"""
    today = get_cst_now().date()
    
    if period == "daily":
        return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    elif period == "monthly":
        start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end = next_month - timedelta(days=next_month.day)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    elif period == "yearly":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    
    return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
```
