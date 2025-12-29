from datetime import datetime, timedelta, date
import pytz

def get_cst_date():
    """Get current date in CST timezone"""
    cst = pytz.timezone('America/Chicago')
    return datetime.now(cst).date()

def get_cst_datetime():
    """Get current datetime in CST timezone"""
    cst = pytz.timezone('America/Chicago')
    return datetime.now(cst)

def format_xp(xp: int) -> str:
    """Format XP with commas for readability"""
    return f"{xp:,}"

def calculate_streak(completions: list) -> int:
    """Calculate current streak from completion dates"""
    if not completions:
        return 0
    
    today = get_cst_date()
    streak = 0
    current_date = today
    
    sorted_dates = sorted([c['date'] for c in completions], reverse=True)
    sorted_dates = [d if isinstance(d, date) else datetime.fromisoformat(d).date() for d in sorted_dates]
    
    for completion_date in sorted_dates:
        if completion_date == current_date or completion_date == current_date - timedelta(days=1):
            streak += 1
            current_date = completion_date - timedelta(days=1)
        else:
            break
    
    return streak

def get_date_range(period: str) -> tuple:
    """Get start and end dates for a given period"""
    today = get_cst_date()
    
    if period == "daily":
        return today, today
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == "monthly":
        start = today.replace(day=1)
        return start, today
    elif period == "yearly":
        start = today.replace(month=1, day=1)
        return start, today
    else:
        return today, today

def get_completion_percentage(completed: int, total: int) -> int:
    """Calculate completion percentage"""
    if total == 0:
        return 0
    return int((completed / total) * 100)

def format_time_ago(dt: datetime) -> str:
    """Format datetime as X time ago"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    
    now = get_cst_datetime()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def validate_habit_frequency(frequency: str, frequency_days: list = None) -> bool:
    """Validate habit frequency settings"""
    valid_frequencies = ["daily", "weekdays", "weekends", "custom"]
    
    if frequency not in valid_frequencies:
        return False
    
    if frequency == "custom" and not frequency_days:
        return False
    
    return True

def get_level_from_xp(xp: int) -> int:
    """Calculate level from total XP"""
    level = 1
    current_xp = xp
    
    while current_xp >= level * 500 and level < 100:
        current_xp -= level * 500
        level += 1
    
    return level

def get_xp_for_next_level(current_level: int) -> int:
    """Get XP required for next level"""
    return current_level * 500

def parse_reminder_time(time_str: str) -> datetime.time:
    """Parse time string to time object"""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except:
        return datetime.strptime("09:00", "%H:%M").time()
