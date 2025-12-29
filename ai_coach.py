import os
from typing import Optional, Dict
import random

class AICoach:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except:
                self.client = None
    
    def assess_habit_difficulty(self, name: str, description: str, category: str) -> Dict:
        """Assess habit difficulty using AI or fallback logic"""
        
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"Analyze this habit and rate its difficulty (1=easy, 2=medium, 3=hard). Return ONLY a number 1, 2, or 3.\n\nHabit: {name}\nDescription: {description}\nCategory: {category}"
                    }]
                )
                
                difficulty = int(message.content[0].text.strip())
                difficulty = max(1, min(3, difficulty))
                
                xp_map = {1: 100, 2: 200, 3: 300}
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp_map[difficulty],
                    "rationale": f"AI assessed as {'Easy' if difficulty == 1 else 'Medium' if difficulty == 2 else 'Hard'}"
                }
            except:
                pass
        
        # Fallback logic
        keywords_hard = ['workout', 'exercise', 'run', 'gym', 'study', 'meditate', 'write']
        keywords_medium = ['read', 'walk', 'practice', 'learn', 'organize']
        
        name_lower = name.lower()
        desc_lower = description.lower()
        
        difficulty = 1
        if any(word in name_lower or word in desc_lower for word in keywords_hard):
            difficulty = 3
        elif any(word in name_lower or word in desc_lower for word in keywords_medium):
            difficulty = 2
        
        xp_map = {1: 100, 2: 200, 3: 300}
        return {
            "difficulty": difficulty,
            "xp_reward": xp_map[difficulty],
            "rationale": f"Assessed as {'Easy' if difficulty == 1 else 'Medium' if difficulty == 2 else 'Hard'} based on keywords"
        }
    
    def assess_goal_difficulty(self, title: str, description: str, category: str) -> Dict:
        """Assess goal difficulty using AI or fallback logic"""
        
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"Analyze this goal and rate its difficulty (1=normal, 2=medium, 3=hard). Return ONLY a number 1, 2, or 3.\n\nGoal: {title}\nDescription: {description}\nCategory: {category}"
                    }]
                )
                
                difficulty = int(message.content[0].text.strip())
                difficulty = max(1, min(3, difficulty))
                
                xp_map = {1: 1000, 2: 2000, 3: 3000}
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp_map[difficulty]
                }
            except:
                pass
        
        # Fallback
        xp_map = {1: 1000, 2: 2000, 3: 3000}
        return {
            "difficulty": 2,
            "xp_reward": 2000
        }
    
    def generate_daily_quote(self, tradition: str = "esoteric") -> Dict:
        """Generate daily wisdom quote"""
        
        traditions = {
            "esoteric": [
                "As above, so below; as within, so without.",
                "The path to mastery begins with a single step taken in awareness.",
                "Your inner world shapes the outer reality you experience."
            ],
            "biblical": [
                "Faith without works is dead.",
                "As a man thinketh, so is he.",
                "The journey of a thousand miles begins with one step."
            ],
            "quranic": [
                "Verily, with hardship comes ease.",
                "And those who strive for Us, We will guide them in Our ways.",
                "Indeed, Allah will not change the condition of a people until they change what is in themselves."
            ],
            "stoic": [
                "The impediment to action advances action. What stands in the way becomes the way.",
                "You have power over your mind, not outside events.",
                "Waste no more time arguing what a good man should be. Be one."
            ],
            "eastern": [
                "The journey of a thousand miles begins with a single step.",
                "When the student is ready, the teacher appears.",
                "Fall seven times, stand up eight."
            ]
        }
        
        quotes = traditions.get(tradition, traditions["esoteric"])
        quote = random.choice(quotes)
        
        return {
            "quote": quote,
            "philosophy": f"Wisdom from the {tradition} tradition to guide your path today.",
            "tradition": tradition
        }
    
    def summarize_note(self, title: str, content: str) -> str:
        """Summarize a note using AI or fallback"""
        
        if self.client and content:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    messages=[{
                        "role": "user",
                        "content": f"Summarize this note in 2-3 bullet points:\n\nTitle: {title}\n\n{content}"
                    }]
                )
                
                return message.content[0].text.strip()
            except:
                pass
        
        # Fallback
        if content:
            sentences = content.split('.')[:3]
            return "• " + "\n• ".join(s.strip() for s in sentences if s.strip())
        
        return "No summary available"
