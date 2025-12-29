import os
from typing import Optional, Dict, List
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
                
                # Extract difficulty number
                difficulty_num = 5  # default
                for word in response_text.split():
                    if word.isdigit():
                        difficulty_num = int(word)
                        break
                
                # Map to XP rewards (50 XP increments)
                if difficulty_num <= 3:
                    difficulty = 1
                    xp_reward = random.choice([50, 100, 150])  # Easy range
                    gold_reward = int(xp_reward * 0.3)
                    tier = "Easy"
                elif difficulty_num <= 6:
                    difficulty = 2
                    xp_reward = random.choice([200, 250, 300])  # Medium range
                    gold_reward = int(xp_reward * 0.3)
                    tier = "Medium"
                else:
                    difficulty = 3
                    xp_reward = random.choice([350, 400, 450, 500])  # Hard range
                    gold_reward = int(xp_reward * 0.3)
                    tier = "Hard"
                
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp_reward,
                    "gold_reward": gold_reward,
                    "rationale": f"AI assessed as {tier} difficulty ({difficulty_num}/10): {response_text[:100]}"
                }
            except Exception as e:
                print(f"AI assessment error: {e}")
                pass
        
        # Fallback logic with 50 XP increments
        keywords_hard = ['workout', 'exercise', 'run', 'gym', 'marathon', 'lift', 'train', 'meditate', 'write', 'study', 'practice']
        keywords_medium = ['read', 'walk', 'journal', 'learn', 'organize', 'plan', 'review']
        
        name_lower = name.lower()
        desc_lower = description.lower()
        
        if any(word in name_lower or word in desc_lower for word in keywords_hard):
            difficulty = 3
            xp_reward = random.choice([350, 400, 450, 500])
            gold_reward = int(xp_reward * 0.3)
            tier = "Hard"
        elif any(word in name_lower or word in desc_lower for word in keywords_medium):
            difficulty = 2
            xp_reward = random.choice([200, 250, 300])
            gold_reward = int(xp_reward * 0.3)
            tier = "Medium"
        else:
            difficulty = 1
            xp_reward = random.choice([50, 100, 150])
            gold_reward = int(xp_reward * 0.3)
            tier = "Easy"
        
        return {
            "difficulty": difficulty,
            "xp_reward": xp_reward,
            "gold_reward": gold_reward,
            "rationale": f"Assessed as {tier} based on keywords"
        }
    
    def assess_goal_difficulty(self, title: str, description: str, category: str, pdf_context: str = "") -> Dict:
        """Assess goal difficulty using AI or fallback logic"""
        
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
                        "content": f"""Analyze this goal and rate its difficulty (1=normal, 2=medium, 3=hard). Return ONLY a number 1, 2, or 3.

Goal: {title}
Description: {description}
Category: {category}{context_note}"""
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
        
        # Fallback
        xp_map = {1: 1000, 2: 2000, 3: 3000}
        gold_map = {1: 250, 2: 500, 3: 750}
        
        return {
            "difficulty": 2,
            "xp_reward": 2000,
            "gold_reward": 500
        }
    
    def generate_action_steps(self, goal_title: str, goal_description: str, category: str, pdf_context: str = "") -> List[str]:
        """Generate AI action steps for a goal using PDF context"""
        
        if self.client:
            try:
                context_note = ""
                if pdf_context:
                    context_note = f"\n\nRelevant wisdom from user's philosophy library:\n{pdf_context[:3000]}"
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": f"""Create 5-10 specific, actionable steps to achieve this goal. Make each step concrete and measurable.

Goal: {goal_title}
Description: {goal_description}
Category: {category}{context_note}

Return ONLY a numbered list of action steps, nothing else."""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                # Parse numbered list
                steps = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        # Remove numbering/bullets
                        clean_step = line.lstrip('0123456789.-•) ').strip()
                        if clean_step:
                            steps.append(clean_step)
                
                return steps[:10]  # Max 10 steps
                
            except Exception as e:
                print(f"AI action steps error: {e}")
        
        # Fallback steps
        return [
            f"Research and plan your approach to {goal_title}",
            f"Break down {goal_title} into smaller milestones",
            f"Set a realistic timeline for {goal_title}",
            f"Take the first concrete action toward {goal_title}",
            f"Review and adjust your strategy as needed"
        ]
    
    def generate_habit_suggestions(self, goal_title: str, goal_description: str, action_steps: List[str], pdf_context: str = "") -> List[Dict]:
        """Generate habit suggestions based on goal and action steps"""
        
        if self.client:
            try:
                steps_text = "\n".join([f"- {step}" for step in action_steps])
                
                context_note = ""
                if pdf_context:
                    context_note = f"\n\nUser's philosophy library context:\n{pdf_context[:2000]}"
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": f"""Based on this goal and its action steps, suggest 3-5 daily/weekly habits that would support achieving this goal.

Goal: {goal_title}
Description: {goal_description}

Action Steps:
{steps_text}{context_note}

For each habit, provide:
1. Habit name (concise)
2. Brief description
3. Suggested frequency (daily/weekdays/weekends)

Format as:
HABIT 1: [name]
Description: [description]
Frequency: [frequency]

HABIT 2: [name]
...etc"""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                # Parse habits
                habits = []
                current_habit = {}
                
                for line in response.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('HABIT'):
                        if current_habit:
                            habits.append(current_habit)
                        # Extract habit name
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
                
                return habits[:5]  # Max 5 habits
                
            except Exception as e:
                print(f"AI habit suggestions error: {e}")
        
        # Fallback habits
        return [
            {
                'name': f"Daily progress on: {goal_title}",
                'description': "Spend 15-30 minutes each day working toward this goal",
                'frequency': 'daily'
            }
        ]
    
    def generate_progressive_goals(self, completed_goal: Dict, pdf_context: str = "") -> List[str]:
        """Suggest follow-up goals based on completed goal"""
        
        if self.client:
            try:
                context_note = ""
                if pdf_context:
                    context_note = f"\n\nUser's philosophy library:\n{pdf_context[:2000]}"
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=800,
                    messages=[{
                        "role": "user",
                        "content": f"""The user just completed this goal. Suggest 3 progressive follow-up goals that build on this achievement.

Completed Goal: {completed_goal.get('title', '')}
Description: {completed_goal.get('description', '')}
Category: {completed_goal.get('category', '')}{context_note}

Return ONLY a numbered list of 3 new goal titles that are more challenging/advanced, nothing else."""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                # Parse goals
                goals = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        clean_goal = line.lstrip('0123456789.-•) ').strip()
                        if clean_goal:
                            goals.append(clean_goal)
                
                return goals[:3]
                
            except Exception as e:
                print(f"Progressive goals error: {e}")
        
        # Fallback
        return [
            f"Advanced version of: {completed_goal.get('title', 'previous goal')}",
            f"Next level challenge in {completed_goal.get('category', 'this area')}",
            f"Mastery goal for {completed_goal.get('category', 'this category')}"
        ]
    
    def summarize_note(self, title: str, content: str, pdf_context: str = "") -> str:
        """Summarize a note with 10-20 bullet points of key concepts"""
        
        if self.client and content:
            try:
                context_note = ""
                if pdf_context:
                    context_note = f"\n\nFor additional context, here's relevant wisdom from the user's library:\n{pdf_context[:1500]}"
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": f"""Create a comprehensive summary of this note with 10-20 bullet points extracting ALL key concepts, insights, and actionable items.

Title: {title}

Content:
{content}{context_note}

Format your response as a bulleted list with 10-20 key points. Each bullet should capture a distinct concept, insight, or action item. Be thorough and comprehensive."""
                    }]
                )
                
                return message.content[0].text.strip()
            except:
                pass
        
        # Fallback - extract first few sentences
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
        """Analyze PDF content and extract key concepts"""
        
        if self.client and content:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze this philosophy/wisdom document and provide:

1. A comprehensive summary (2-3 paragraphs)
2. 15-20 key concepts/teachings as bullet points
3. Main themes (3-5)

Document: {filename}

Content:
{content[:15000]}

Format:
SUMMARY:
[summary here]

KEY CONCEPTS:
- [concept 1]
- [concept 2]
...

THEMES:
- [theme 1]
- [theme 2]
..."""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                # Parse response
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
                
            except Exception as e:
                print(f"PDF analysis error: {e}")
        
        # Fallback
        return {
            'summary': f"Document uploaded: {filename}",
            'key_concepts': ["Document content available for AI context"],
            'themes': ["Philosophy", "Wisdom"]
        }
    
    def generate_daily_quote(self, tradition: str = "esoteric", habit_context: str = None, user_name: str = "Hunter") -> Dict:
        """Generate deeply philosophical daily wisdom quote based on tradition and user context"""
        
        # [KEEPING THE EXISTING QUOTE DATABASE FROM PREVIOUS VERSION - same as before]
        quotes_db = {
            "kemetic": [
                {
                    "quote": "As Thoth inscribed the scales of Ma'at, so too must you measure your deeds against the feather of truth. Balance in all things brings harmony to the ka.",
                    "philosophy": "The ancient Egyptians understood that cosmic balance (Ma'at) was the foundation of existence. Your daily practices are not mere tasks—they are offerings to maintain the order of your universe. As the heart is weighed against the feather, let your actions be light with integrity.",
                    "context": "discipline and balance"
                },
                {
                    "quote": "The ba rises at dawn, renewed by Ra's journey through the Duat. Each morning is resurrection, each habit a sacred rite of becoming.",
                    "philosophy": "In Kemetic wisdom, death and rebirth occur daily. The sun god Ra travels through the underworld each night and emerges victorious at dawn. Your morning routine is a ritual of resurrection—you are reborn each day with the power to transform.",
                    "context": "morning routines and renewal"
                },
                {
                    "quote": "Heka flows through intention and action united. The magician does not wish for transformation—they command it through disciplined will.",
                    "philosophy": "Heka is the primordial creative force, the magic that shapes reality. It is activated not by hope, but by deliberate action aligned with cosmic law. Your habits are spells, your consistency the incantation that bends reality to your will.",
                    "context": "willpower and manifestation"
                },
            ],
            "samurai": [
                {
                    "quote": "死ぬことと見つけたり (To find in death, to live). The samurai knows that each moment lived fully is a victory over the impermanence of all things.",
                    "philosophy": "Bushido teaches that acknowledging death's inevitability brings clarity to life. Every habit you complete is a moment seized from the void. Live each practice as if it were your last—not with fear, but with complete presence and honor.",
                    "context": "presence and mortality awareness"
                },
                {
                    "quote": "The sword is sharpened through ten thousand repetitions. Mastery is not the absence of struggle, but its embrace through ceaseless refinement.",
                    "philosophy": "A samurai's sword reflects their soul—both require constant polishing. Your habits are the whetstone against which your character is sharpened. Excellence emerges not from grand gestures but from the disciplined repetition of fundamentals.",
                    "context": "mastery through repetition"
                },
            ],
            "biblical": [
                {
                    "quote": "Therefore, my beloved brethren, be steadfast, immovable, always abounding in the work of the Lord. (1 Corinthians 15:58)",
                    "philosophy": "Paul's letter reveals that constancy is a form of worship. Your daily disciplines are not separate from spiritual practice—they are the material expression of faith. To be steadfast in small things is to honor the divine architecture of existence.",
                    "context": "steadfastness and devotion"
                },
            ],
            "quranic": [
                {
                    "quote": "Indeed, Allah will not change the condition of a people until they change what is in themselves. (Quran 13:11)",
                    "philosophy": "Divine law is clear: transformation is an inside job. Your external circumstances are mirrors of your internal state. Change your habits, and you change the patterns Allah has set in motion for your life.",
                    "context": "self-transformation and divine law"
                },
            ],
            "esoteric": [
                {
                    "quote": "As above, so below; as within, so without. The microcosm reflects the macrocosm, and your daily rituals echo the movements of celestial spheres.",
                    "philosophy": "The Hermetic axiom reveals that your personal practices are not isolated events but participations in universal law. When you complete your habits with awareness, you align your small orbit with the great cosmic cycles.",
                    "context": "correspondence and cosmic alignment"
                },
            ],
            "occult": [
                {
                    "quote": "The magician's will is law. Thelema commands: Do what thou wilt shall be the whole of the Law. Your disciplined intention shapes reality itself.",
                    "philosophy": "Crowley's teaching is often misunderstood. True will is not whim but aligned purpose. Your habits train you to discern and execute true will—desire purified into cosmic command. Each completion is a sigil activated.",
                    "context": "will and reality shaping"
                },
            ],
            "stoic": [
                {
                    "quote": "The impediment to action advances action. What stands in the way becomes the way. - Marcus Aurelius",
                    "philosophy": "Obstacles are not barriers to your path—they are the path itself. Your difficult habits teach more than easy ones. Resistance is the forge where character is tempered into steel.",
                    "context": "obstacles as opportunities"
                },
            ],
            "eastern": [
                {
                    "quote": "When the student is ready, the teacher appears. Your habits are preparing you for teachings you cannot yet imagine.",
                    "philosophy": "Zen wisdom reveals that readiness is cultivated through practice. Your daily disciplines are not about achieving specific outcomes—they're about becoming the person capable of receiving wisdom when it arrives.",
                    "context": "preparation and readiness"
                },
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
        
        def chunk_pdf_content(self, content: str, filename: str) -> List[Dict]:
        """Intelligently chunk PDF into searchable segments"""
        
        segments = []
        
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        
        current_segment = ""
        segment_number = 0
        word_count = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_words = len(para.split())
            
            # If current segment would be too large, save it
            if word_count + para_words > 500 and current_segment:
                segments.append({
                    'type': 'paragraph',
                    'number': segment_number,
                    'content': current_segment.strip(),
                    'word_count': word_count,
                    'key_terms': self._extract_key_terms(current_segment)
                })
                
                current_segment = ""
                word_count = 0
                segment_number += 1
            
            current_segment += para + "\n\n"
            word_count += para_words
        
        # Save last segment
        if current_segment:
            segments.append({
                'type': 'paragraph',
                'number': segment_number,
                'content': current_segment.strip(),
                'word_count': word_count,
                'key_terms': self._extract_key_terms(current_segment)
            })
        
        return segments
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text segment"""
        # Simple extraction
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                      'this', 'that', 'these', 'those', 'it', 'its', 'i', 'you', 'he', 'she'}
        
        # Get unique important words (longer than 4 chars)
        key_terms = list(set([
            word.strip('.,!?;:()[]{}"\'-') 
            for word in words 
            if len(word) > 4 and word not in stop_words
        ]))
        
        return key_terms[:20]  # Top 20 terms
    
    def ai_find_information(self, query: str, documents_content: str, user_name: str = "Hunter") -> Dict:
        """Use AI to find specific information across documents"""
        
        if self.client and documents_content:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    messages=[{
                        "role": "user",
                        "content": f"""You are helping {user_name} find specific information in their philosophy library.

User's Question/Search: {query}

Library Content:
{documents_content[:50000]}

Your task:
1. Find ALL relevant passages that answer the question
2. Quote the exact text (with "..." for context)
3. Explain how each passage relates to the question
4. Synthesize a clear answer

Format your response as:

ANSWER:
[Your synthesized answer here]

RELEVANT PASSAGES:
---
Passage 1:
"[exact quote]"
Relevance: [how this relates]
---
Passage 2:
"[exact quote]"
Relevance: [how this relates]
---
[continue for all relevant passages]

Be thorough - find ALL relevant information."""
                    }]
                )
                
                response = message.content[0].text.strip()
                
                # Parse response
                answer = ""
                passages = []
                
                current_section = None
                current_passage = {}
                
                for line in response.split('\n'):
                    line_stripped = line.strip()
                    
                    if line_stripped.startswith('ANSWER:'):
                        current_section = 'answer'
                        continue
                    elif line_stripped.startswith('RELEVANT PASSAGES:'):
                        current_section = 'passages'
                        continue
                    elif line_stripped == '---':
                        if current_passage:
                            passages.append(current_passage)
                            current_passage = {}
                        continue
                    
                    if current_section == 'answer' and line_stripped:
                        answer += line + "\n"
                    elif current_section == 'passages':
                        if line_stripped.startswith('Passage'):
                            continue
                        elif line_stripped.startswith('"'):
                            current_passage['quote'] = line_stripped.strip('"')
                        elif line_stripped.startswith('Relevance:'):
                            current_passage['relevance'] = line_stripped.replace('Relevance:', '').strip()
                
                if current_passage:
                    passages.append(current_passage)
                
                return {
                    'answer': answer.strip(),
                    'passages': passages,
                    'found': len(passages) > 0
                }
                
            except Exception as e:
                print(f"AI search error: {e}")
        
        return {
            'answer': f"Could not search documents. Please ensure you have documents uploaded and an API key configured.",
            'passages': [],
            'found': False
        }
    
    def summarize_pdf_section(self, section_content: str, section_title: str = "Section") -> str:
        """Summarize a specific section of PDF with 10-20 key points"""
        
        if self.client and section_content:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": f"""Summarize this section with 10-20 bullet points capturing ALL key concepts, insights, and important details.

Section: {section_title}

Content:
{section_content[:15000]}

Format as a comprehensive bulleted list. Each bullet should capture a distinct concept or insight. Be thorough."""
                    }]
                )
                
                return message.content[0].text.strip()
                
            except Exception as e:
                print(f"Summarization error: {e}")
        
        # Fallback
        sentences = section_content.split('.')[:10]
        bullets = [f"• {s.strip()}" for s in sentences if s.strip()]
        return "\n".join(bullets) if bullets else "No summary available"
        }
