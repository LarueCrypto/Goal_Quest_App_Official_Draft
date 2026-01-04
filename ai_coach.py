import os
from typing import Optional, Dict, List
import random
import json
from anthropic import Anthropic

class AICoach:
    def __init__(self, api_key):
        # Initializes the Anthropic client with the provided API key
        self.client = Anthropic(api_key=api_key) if api_key else None
        # Standardized model name for all calls
        self.model = "claude-3-5-sonnet-20240620"

    def generate_daily_quote(self, tradition: str = "esoteric", habit_context: str = None, user_name: str = "Hunter") -> Dict:
        """Generate daily wisdom quote using AI with a tradition-based fallback database."""
        
        if self.client:
            try:
                prompt = f"Generate a profound {tradition} wisdom quote for a user named {user_name}."
                if habit_context:
                    prompt += f" The focus today is on {habit_context}."
                
                prompt += " Return the response in this JSON format: {'quote': '...', 'philosophy': '...'}"

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                # Attempt to parse the AI response
                return json.loads(message.content[0].text)
            except Exception as e:
                print(f"AI Quote Error, falling back to database: {e}")

        # --- Tradition-Based Fallback Database ---
        quotes_db = {
            "kemetic": [
                {
                    "quote": "As Thoth inscribed the scales of Ma'at, so too must you measure your deeds against the feather of truth.",
                    "philosophy": "The ancient Egyptians understood that cosmic balance was the foundation of existence.",
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
                    "philosophy": "Your personal practices participate in universal law.",
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
                    "philosophy": "Obstacles are not barriers—they are the path itself.",
                    "context": "obstacles as opportunities"
                }
            ],
            "eastern": [
                {
                    "quote": "When the student is ready, the teacher appears.",
                    "philosophy": "Your daily disciplines prepare you for teachings you cannot yet imagine.",
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

    def assess_habit_difficulty(self, name: str, description: str, category: str, pdf_context: str = "") -> Dict:
        """Assess habit difficulty using AI or fallback logic with 50 XP increments."""
        if self.client:
            try:
                context_note = f"\n\nLibrary Context:\n{pdf_context[:2000]}" if pdf_context else ""
                
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"Analyze this habit and rate difficulty 1-10: {name}. Description: {description}. {context_note}"
                    }]
                )
                
                response_text = message.content[0].text.strip()
                difficulty_num = 5
                for word in response_text.split():
                    if word.isdigit():
                        difficulty_num = int(word)
                        break
                
                if difficulty_num <= 3:
                    difficulty, xp, tier = 1, random.choice([50, 100, 150]), "Easy"
                elif difficulty_num <= 6:
                    difficulty, xp, tier = 2, random.choice([200, 250, 300]), "Medium"
                else:
                    difficulty, xp, tier = 3, random.choice([350, 400, 450, 500]), "Hard"
                
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp,
                    "gold_reward": int(xp * 0.3),
                    "rationale": f"AI assessed as {tier} difficulty"
                }
            except Exception as e:
                print(f"AI assessment error: {e}")

        # Fallback keyword logic
        keywords_hard = ['workout', 'exercise', 'run', 'gym', 'marathon', 'lift', 'train', 'meditate', 'write', 'study', 'practice']
        name_lower, desc_lower = name.lower(), description.lower()
        
        if any(word in name_lower or word in desc_lower for word in keywords_hard):
            difficulty, xp = 3, random.choice([350, 400, 450, 500])
        else:
            difficulty, xp = 1, random.choice([50, 100, 150])
        
        return {"difficulty": difficulty, "xp_reward": xp, "gold_reward": int(xp * 0.3), "rationale": "Keyword assessment"}

    def assess_goal_difficulty(self, title: str, description: str, category: str, pdf_context: str = "") -> Dict:
        """Assess goal difficulty (1=easy, 2=medium, 3=hard)."""
        if self.client:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": f"Rate goal difficulty 1, 2, or 3: {title}. {description}"}]
                )
                difficulty = int(''.join(filter(str.isdigit, message.content[0].text.strip())) or 2)
                difficulty = max(1, min(3, difficulty))
                xp_map = {1: 1000, 2: 2000, 3: 3000}
                return {"difficulty": difficulty, "xp_reward": xp_map[difficulty], "gold_reward": int(xp_map[difficulty] * 0.25)}
            except: pass
        return {"difficulty": 2, "xp_reward": 2000, "gold_reward": 500}

    def generate_action_steps(self, goal_title: str, goal_description: str, category: str, pdf_context: str = "") -> List[str]:
        """Generate 5-10 specific, actionable steps for a goal."""
        if self.client:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": f"Create 5-10 numbered action steps for: {goal_title}"}]
                )
                response = message.content[0].text.strip()
                steps = [line.lstrip('0123456789.-•) ').strip() for line in response.split('\n') if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith(('-', '•')))]
                return steps[:10]
            except: pass
        return [f"Take the first concrete action toward {goal_title}"]

    def generate_habit_suggestions(self, goal_title: str, goal_description: str, action_steps: List[str], pdf_context: str = "") -> List[Dict]:
        """Suggest 3-5 daily/weekly habits based on goal."""
        if self.client:
            try:
                steps_text = "\n".join([f"- {step}" for step in action_steps])
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    messages=[{"role": "user", "content": f"Suggest habits for goal: {goal_title}. Steps: {steps_text}. Format: HABIT 1: [name] Description: [desc] Frequency: [freq]"}]
                )
                response = message.content[0].text.strip()
                habits, current_habit = [], {}
                for line in response.split('\n'):
                    line = line.strip()
                    if line.startswith('HABIT'):
                        if current_habit: habits.append(current_habit)
                        current_habit = {'name': line.split(':', 1)[1].strip() if ':' in line else line, 'description': '', 'frequency': 'daily'}
                    elif line.startswith('Description:'): current_habit['description'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Frequency:'): current_habit['frequency'] = 'daily' if 'daily' in line.lower() else 'weekdays'
                if current_habit: habits.append(current_habit)
                return habits[:5]
            except: pass
        return [{'name': f"Progress on: {goal_title}", 'description': "Daily work", 'frequency': 'daily'}]

    def generate_progressive_goals(self, completed_goal: Dict, pdf_context: str = "") -> List[str]:
        """Suggest 3 follow-up goals after completion."""
        if self.client:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    messages=[{"role": "user", "content": f"Suggest 3 follow-up goals for: {completed_goal.get('title')}"}]
                )
                response = message.content[0].text.strip()
                return [line.lstrip('0123456789.-•) ').strip() for line in response.split('\n') if line.strip()][:3]
            except: pass
        return [f"Advanced {completed_goal.get('title', 'Goal')}"]

    def summarize_note(self, title: str, content: str, pdf_context: str = "") -> str:
        """Summarize a note with 10-20 bullet points."""
        if self.client and content:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": f"Summarize as 10-20 bullets: {title}. Content: {content}"}]
                )
                return message.content[0].text.strip()
            except: pass
        return "No summary available"

    def analyze_pdf_content(self, content: str, filename: str) -> Dict:
        """Analyze PDF content for summary, concepts, and themes."""
        if self.client and content:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=3000,
                    messages=[{"role": "user", "content": f"Analyze: {filename}. Content: {content[:15000]}. Format: SUMMARY: [text] KEY CONCEPTS: • [item] THEMES: • [item]"}]
                )
                response = message.content[0].text.strip()
                summary, concepts, themes, current = "", [], [], None
                for line in response.split('\n'):
                    if 'SUMMARY:' in line: current = 's'
                    elif 'KEY CONCEPTS:' in line: current = 'c'
                    elif 'THEMES:' in line: current = 't'
                    elif current == 's': summary += line + " "
                    elif current == 'c' and line.startswith('•'): concepts.append(line.lstrip('•').strip())
                    elif current == 't' and line.startswith('•'): themes.append(line.lstrip('•').strip())
                return {'summary': summary.strip(), 'key_concepts': concepts, 'themes': themes}
            except: pass
        return {'summary': f"Uploaded: {filename}", 'key_concepts': ["Content processed"], 'themes': ["Wisdom"]}
