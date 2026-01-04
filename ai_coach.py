import os
from typing import Optional, Dict, List
import random
from anthropic import Anthropic

class AICoach:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key) if api_key else None

    def generate_daily_quote(self, tradition, habit_context, user_name):
        if not self.client:
            return {"quote": "Keep going!", "philosophy": "Connect API for wisdom", "tradition": tradition}
        
        # This is where the Anthropic API call happens
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            messages=[{"role": "user", "content": f"Generate a {tradition} quote for {user_name}..."}]
        )
        # Add logic here to parse the response...
    
    def assess_habit_difficulty(self, name: str, description: str, category: str, pdf_context: str = "") -> Dict:
        """Assess habit difficulty using AI or fallback logic with 50 XP increments"""
        
        if self.client:
            try:
                context_note = ""
                if pdf_context:
                    context_note = f"\n\nUser's Philosophy Library Context:\n{pdf_context[:2000]}"
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze this habit and rate its difficulty on a scale of 1-10.
                        
Habit: {name}
Description: {description}
Category: {category}{context_note}

Return ONLY a number 1-10 with a brief rationale.

Difficulty Scale:
1-3 = Easy (50-150 XP) - Simple daily tasks
4-6 = Medium (200-300 XP) - Moderate commitment  
7-10 = Hard (350-500 XP) - Significant effort required"""
                    }]
                )
                
                response_text = message.content[0].text.strip()
                
                difficulty_num = 5
                for word in response_text.split():
                    if word.isdigit():
                        difficulty_num = int(word)
                        break
                
                if difficulty_num <= 3:
                    difficulty = 1
                    xp_reward = random.choice([50, 100, 150])
                    gold_reward = int(xp_reward * 0.3)
                    tier = "Easy"
                elif difficulty_num <= 6:
                    difficulty = 2
                    xp_reward = random.choice([200, 250, 300])
                    gold_reward = int(xp_reward * 0.3)
                    tier = "Medium"
                else:
                    difficulty = 3
                    xp_reward = random.choice([350, 400, 450, 500])
                    gold_reward = int(xp_reward * 0.3)
                    tier = "Hard"
                
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp_reward,
                    "gold_reward": gold_reward,
                    "rationale": f"AI assessed as {tier} difficulty"
                }
            except Exception as e:
                print(f"AI assessment error: {e}")
                pass
        
        keywords_hard = ['workout', 'exercise', 'run', 'gym', 'marathon', 'lift', 'train', 'meditate', 'write', 'study', 'practice']
        keywords_medium = ['read', 'walk', 'journal', 'learn', 'organize', 'plan', 'review']
        
        name_lower = name.lower()
        desc_lower = description.lower()
        
        if any(word in name_lower or word in desc_lower for word in keywords_hard):
            difficulty = 3
            xp_reward = random.choice([350, 400, 450, 500])
            gold_reward = int(xp_reward * 0.3)
        elif any(word in name_lower or word in desc_lower for word in keywords_medium):
            difficulty = 2
            xp_reward = random.choice([200, 250, 300])
            gold_reward = int(xp_reward * 0.3)
        else:
            difficulty = 1
            xp_reward = random.choice([50, 100, 150])
            gold_reward = int(xp_reward * 0.3)
        
        return {
            "difficulty": difficulty,
            "xp_reward": xp_reward,
            "gold_reward": gold_reward,
            "rationale": "Keyword-based assessment"
        }
    
    def assess_goal_difficulty(self, title: str, description: str, category: str, pdf_context: str = "") -> Dict:
        """Assess goal difficulty"""
        
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"""Rate this goal's difficulty (1=easy, 2=medium, 3=hard). Return ONLY a number 1, 2, or 3.

Goal: {title}
Description: {description}
Category: {category}"""
                    }]
                )
                
                difficulty = int(message.content[0].text.strip())
                difficulty = max(1, min(3, difficulty))
                
                xp_map = {1: 1000, 2: 2000, 3: 3000}
                gold_map = {1: 250, 2: 500, 3: 750}
                
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp_map[difficulty],
                    "gold_reward": gold_map[difficulty]
                }
            except:
                pass
        
        return {
            "difficulty": 2,
            "xp_reward": 2000,
            "gold_reward": 500
        }
    
    def generate_action_steps(self, goal_title: str, goal_description: str, category: str, pdf_context: str = "") -> List[str]:
        """Generate AI action steps for a goal"""
        
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": f"""Create 5-10 specific, actionable steps to achieve this goal.

Goal: {goal_title}
Description: {goal_description}
Category: {category}

Return ONLY a numbered list of action steps."""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                steps = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        clean_step = line.lstrip('0123456789.-•) ').strip()
                        if clean_step:
                            steps.append(clean_step)
                
                return steps[:10]
                
            except Exception as e:
                print(f"AI action steps error: {e}")
        
        return [
            f"Research and plan your approach to {goal_title}",
            f"Break down {goal_title} into smaller milestones",
            f"Set a realistic timeline for {goal_title}",
            f"Take the first concrete action toward {goal_title}",
            f"Review and adjust your strategy as needed"
        ]
    
    def generate_habit_suggestions(self, goal_title: str, goal_description: str, action_steps: List[str], pdf_context: str = "") -> List[Dict]:
        """Generate habit suggestions based on goal"""
        
        if self.client:
            try:
                steps_text = "\n".join([f"- {step}" for step in action_steps])
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": f"""Based on this goal, suggest 3-5 daily/weekly habits.

Goal: {goal_title}
Description: {goal_description}

Action Steps:
{steps_text}

Format:
HABIT 1: [name]
Description: [description]
Frequency: [daily/weekdays/weekends]"""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                habits = []
                current_habit = {}
                
                for line in response.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('HABIT'):
                        if current_habit:
                            habits.append(current_habit)
                        name = line.split(':', 1)[1].strip() if ':' in line else line.replace('HABIT', '').strip()
                        current_habit = {'name': name, 'description': '', 'frequency': 'daily'}
                    elif line.startswith('Description:'):
                        current_habit['description'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Frequency:'):
                        freq = line.split(':', 1)[1].strip().lower()
                        if 'daily' in freq:
                            current_habit['frequency'] = 'daily'
                        elif 'weekday' in freq:
                            current_habit['frequency'] = 'weekdays'
                        elif 'weekend' in freq:
                            current_habit['frequency'] = 'weekends'
                
                if current_habit:
                    habits.append(current_habit)
                
                return habits[:5]
                
            except Exception as e:
                print(f"AI habit suggestions error: {e}")
        
        return [
            {
                'name': f"Daily progress on: {goal_title}",
                'description': "Spend 15-30 minutes each day working toward this goal",
                'frequency': 'daily'
            }
        ]
    
    def generate_progressive_goals(self, completed_goal: Dict, pdf_context: str = "") -> List[str]:
        """Suggest follow-up goals"""
        
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=800,
                    messages=[{
                        "role": "user",
                        "content": f"""The user just completed this goal. Suggest 3 progressive follow-up goals.

Completed Goal: {completed_goal.get('title', '')}
Description: {completed_goal.get('description', '')}

Return ONLY 3 new goal titles."""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                goals = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        clean_goal = line.lstrip('0123456789.-•) ').strip()
                        if clean_goal:
                            goals.append(clean_goal)
                
                return goals[:3]
                
            except:
                pass
        
        return [
            f"Advanced version of: {completed_goal.get('title', 'previous goal')}",
            f"Next level challenge in {completed_goal.get('category', 'this area')}",
            f"Mastery goal for {completed_goal.get('category', 'this category')}"
        ]
    
    def summarize_note(self, title: str, content: str, pdf_context: str = "") -> str:
        """Summarize a note with 10-20 bullet points"""
        
        if self.client and content:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": f"""Create a summary of this note with 10-20 bullet points.

Title: {title}

Content:
{content}

Format as a bulleted list with 10-20 key points."""
                    }]
                )
                
                return message.content[0].text.strip()
            except:
                pass
        
        if content:
            sentences = content.split('.')[:5]
            bullets = []
            for s in sentences:
                s = s.strip()
                if s:
                    bullets.append(f"• {s}")
            return "\n".join(bullets) if bullets else "No summary available"
        
        return "No summary available"
    
    def analyze_pdf_content(self, content: str, filename: str) -> Dict:
        """Analyze PDF content"""
        
        if self.client and content:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze this document and provide:

1. A summary (2-3 paragraphs)
2. 15-20 key concepts
3. Main themes (3-5)

Document: {filename}
Content: {content[:15000]}

Format:
SUMMARY:
[summary]

KEY CONCEPTS:
- [concept 1]
- [concept 2]

THEMES:
- [theme 1]"""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                summary = ""
                key_concepts = []
                themes = []
                
                current_section = None
                
                for line in response.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('SUMMARY:'):
                        current_section = 'summary'
                        continue
                    elif line.startswith('KEY CONCEPTS:'):
                        current_section = 'concepts'
                        continue
                    elif line.startswith('THEMES:'):
                        current_section = 'themes'
                        continue
                    
                    if current_section == 'summary' and line:
                        summary += line + " "
                    elif current_section == 'concepts' and line.startswith('•'):
                        key_concepts.append(line.lstrip('•').strip())
                    elif current_section == 'themes' and line.startswith('•'):
                        themes.append(line.lstrip('•').strip())
                
                return {
                    'summary': summary.strip(),
                    'key_concepts': key_concepts,
                    'themes': themes
                }
                
            except:
                pass
        
        return {
            'summary': f"Document uploaded: {filename}",
            'key_concepts': ["Document content available"],
            'themes': ["Philosophy", "Wisdom"]
        }
    
    def generate_daily_quote(self, tradition: str = "esoteric", habit_context: str = None, user_name: str = "Hunter") -> Dict:
        """Generate daily wisdom quote"""
        
        quotes_db = {
            "kemetic": [
                {
                    "quote": "As Thoth inscribed the scales of Ma'at, so too must you measure your deeds against the feather of truth.",
                    "philosophy": "The ancient Egyptians understood that cosmic balance was the foundation of existence. Your daily practices are offerings to maintain universal order.",
                    "context": "discipline and balance"
                }
            ],
            "samurai": [
                {
                    "quote": "The sword is sharpened through ten thousand repetitions.",
                    "philosophy": "Mastery emerges not from grand gestures but from disciplined repetition of fundamentals.",
                    "context": "mastery through repetition"
                }
            ],
            "biblical": [
                {
                    "quote": "Be steadfast, immovable, always abounding in the work of the Lord.",
                    "philosophy": "Constancy is a form of worship. Your daily disciplines are the material expression of faith.",
                    "context": "steadfastness and devotion"
                }
            ],
            "quranic": [
                {
                    "quote": "Indeed, Allah will not change the condition of a people until they change what is in themselves.",
                    "philosophy": "Transformation is an inside job. Your external circumstances mirror your internal state.",
                    "context": "self-transformation"
                }
            ],
            "esoteric": [
                {
                    "quote": "As above, so below; as within, so without.",
                    "philosophy": "Your personal practices participate in universal law. When you complete your habits with awareness, you align with cosmic cycles.",
                    "context": "correspondence and alignment"
                }
            ],
            "occult": [
                {
                    "quote": "Do what thou wilt shall be the whole of the Law.",
                    "philosophy": "True will is aligned purpose. Your habits train you to discern and execute cosmic command.",
                    "context": "will and reality"
                }
            ],
            "stoic": [
                {
                    "quote": "The impediment to action advances action. What stands in the way becomes the way.",
                    "philosophy": "Obstacles are not barriers—they are the path itself. Resistance is the forge where character is tempered.",
                    "context": "obstacles as opportunities"
                }
            ],
            "eastern": [
                {
                    "quote": "When the student is ready, the teacher appears.",
                    "philosophy": "Your daily disciplines prepare you for teachings you cannot yet imagine. Readiness is cultivated through practice.",
                    "context": "preparation and readiness"
                }
            ]
        }
        
        tradition_quotes = quotes_db.get(tradition, quotes_db["esoteric"])
        selected_quote = random.choice(tradition_quotes)
        
        if habit_context:
            matching_quotes = [q for q in tradition_quotes if habit_context.lower() in q["context"].lower()]
            if matching_quotes:
                selected_quote = random.choice(matching_quotes)
        
        philosophy = selected_quote["philosophy"]
        if user_name and user_name != "Hunter":
            philosophy = f"{user_name}, " + philosophy[0].lower() + philosophy[1:]
        
        return {
            "quote": selected_quote["quote"],
            "philosophy": philosophy,
            "tradition": tradition
        }
