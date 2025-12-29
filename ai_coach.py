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
        """Assess habit difficulty using AI or fallback logic with 50 XP increments"""
        
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze this habit and rate its difficulty on a scale of 1-10.
                        
Habit: {name}
Description: {description}
Category: {category}

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
                    tier = "Easy"
                elif difficulty_num <= 6:
                    difficulty = 2
                    xp_reward = random.choice([200, 250, 300])  # Medium range
                    tier = "Medium"
                else:
                    difficulty = 3
                    xp_reward = random.choice([350, 400, 450, 500])  # Hard range
                    tier = "Hard"
                
                return {
                    "difficulty": difficulty,
                    "xp_reward": xp_reward,
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
            tier = "Hard"
        elif any(word in name_lower or word in desc_lower for word in keywords_medium):
            difficulty = 2
            xp_reward = random.choice([200, 250, 300])
            tier = "Medium"
        else:
            difficulty = 1
            xp_reward = random.choice([50, 100, 150])
            tier = "Easy"
        
        return {
            "difficulty": difficulty,
            "xp_reward": xp_reward,
            "rationale": f"Assessed as {tier} based on keywords"
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
                        "content": f"""Analyze this goal and rate its difficulty (1=normal, 2=medium, 3=hard). Return ONLY a number 1, 2, or 3.

Goal: {title}
Description: {description}
Category: {category}"""
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
    
    def generate_daily_quote(self, tradition: str = "esoteric", habit_context: str = None, user_name: str = "Hunter") -> Dict:
        """Generate deeply philosophical daily wisdom quote based on tradition and user context"""
        
        # Comprehensive quote database by tradition
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
                {
                    "quote": "As Ptah spoke the world into being, so do your daily words and deeds create the temple of your existence.",
                    "philosophy": "Ptah, the divine architect, created reality through speech. Every action you take, every habit you maintain, is an act of divine creation. You are building a temple—let each stone be placed with sacred intention.",
                    "context": "creation and consistency"
                },
                {
                    "quote": "The Scarab pushes the sun across the sky not by strength alone, but by unwavering purpose. Khepri teaches us that persistence births transformation.",
                    "philosophy": "Khepri, the scarab-headed god of transformation, represents the soul's journey toward self-becoming. Like the beetle rolling dung to create new life, your seemingly mundane efforts contain the seeds of profound metamorphosis.",
                    "context": "transformation through persistence"
                }
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
                {
                    "quote": "There is nothing outside of yourself that can ever enable you to get better, stronger, richer, quicker, or smarter. Everything is within.",
                    "philosophy": "This teaching from Miyamoto Musashi's Dokkōdō reveals the warrior's self-reliance. External tools and conditions are secondary to the cultivation of inner strength. Your discipline is not dependent on perfect circumstances—it creates them.",
                    "context": "self-reliance and inner strength"
                },
                {
                    "quote": "The way of the warrior is found in death. Meditation on inevitable death should be performed daily.",
                    "philosophy": "Memento mori is central to Bushido. By contemplating your mortality each day, trivial concerns dissolve and what truly matters emerges with crystalline clarity. Your habits are the legacy you build with the time you have left.",
                    "context": "mortality and meaning"
                },
                {
                    "quote": "Fall seven times, stand eight times. (七転び八起き) The samurai measures strength not by victories but by the will to rise.",
                    "philosophy": "Resilience defines the warrior more than prowess. Your streak may break, your resolve may falter, but the true test is whether you return. Each return is a victory over the lesser self.",
                    "context": "resilience and recovery"
                }
            ],
            "biblical": [
                {
                    "quote": "Therefore, my beloved brethren, be steadfast, immovable, always abounding in the work of the Lord. (1 Corinthians 15:58)",
                    "philosophy": "Paul's letter reveals that constancy is a form of worship. Your daily disciplines are not separate from spiritual practice—they are the material expression of faith. To be steadfast in small things is to honor the divine architecture of existence.",
                    "context": "steadfastness and devotion"
                },
                {
                    "quote": "As a man thinketh in his heart, so is he. (Proverbs 23:7)",
                    "philosophy": "The inner world determines the outer. Your habits are thoughts made flesh, intentions crystallized into reality. Guard your mind carefully, for it is the forge where your destiny is hammered into form.",
                    "context": "thought and manifestation"
                },
                {
                    "quote": "The kingdom of heaven is like a mustard seed, which a man took and planted in his field. Though it is the smallest of all seeds, yet when it grows, it is the largest of garden plants. (Matthew 13:31-32)",
                    "philosophy": "Jesus teaches that great transformations begin with imperceptible actions. Your small daily habits are mustard seeds—insignificant in the moment, but containing within them the potential for magnificent growth.",
                    "context": "small beginnings and growth"
                },
                {
                    "quote": "Not by might, nor by power, but by my Spirit, says the Lord. (Zechariah 4:6)",
                    "philosophy": "True transformation comes not through force but through alignment with divine will. Your practices succeed not through willpower alone but through surrendering to a purpose greater than ego.",
                    "context": "surrender and divine alignment"
                },
                {
                    "quote": "He who is faithful in what is least is faithful also in much. (Luke 16:10)",
                    "philosophy": "Christ reveals that character is proven in small things. The way you handle your morning routine indicates how you'll handle life's great challenges. Excellence is not selective—it permeates all actions or none.",
                    "context": "faithfulness in small things"
                }
            ],
            "quranic": [
                {
                    "quote": "Indeed, Allah will not change the condition of a people until they change what is in themselves. (Quran 13:11)",
                    "philosophy": "Divine law is clear: transformation is an inside job. Your external circumstances are mirrors of your internal state. Change your habits, and you change the patterns Allah has set in motion for your life.",
                    "context": "self-transformation and divine law"
                },
                {
                    "quote": "Verily, with hardship comes ease. (Quran 94:5-6)",
                    "philosophy": "This is repeated twice in Surah Ash-Sharh to emphasize its certainty. Your difficult habits are not obstacles but doorways. The struggle itself contains its resolution—persevere, and relief becomes inevitable.",
                    "context": "perseverance through difficulty"
                },
                {
                    "quote": "And those who strive for Us, We will surely guide them to Our ways. (Quran 29:69)",
                    "philosophy": "Allah promises guidance to those who struggle in His path. Your daily jihad (struggle) against laziness and distraction is sacred work. Each completed habit is a prayer answered through action.",
                    "context": "sacred struggle"
                },
                {
                    "quote": "So be patient with gracious patience. (Quran 70:5)",
                    "philosophy": "Sabr (patience) is not passive waiting but active perseverance with grace. Your habits cultivate this virtue—the ability to persist without complaint, to endure without bitterness, to trust in Allah's timing.",
                    "context": "patience and grace"
                },
                {
                    "quote": "Indeed, prayer prohibits immorality and wrongdoing, and the remembrance of Allah is greater. (Quran 29:45)",
                    "philosophy": "Regular practice transforms character. Your habits are a form of dhikr (remembrance)—each completion reminds you of your higher purpose and pulls you away from base impulses toward your elevated self.",
                    "context": "regular practice and remembrance"
                }
            ],
            "esoteric": [
                {
                    "quote": "As above, so below; as within, so without. The microcosm reflects the macrocosm, and your daily rituals echo the movements of celestial spheres.",
                    "philosophy": "The Hermetic axiom reveals that your personal practices are not isolated events but participations in universal law. When you complete your habits with awareness, you align your small orbit with the great cosmic cycles.",
                    "context": "correspondence and cosmic alignment"
                },
                {
                    "quote": "The alchemist knows: it is not lead that becomes gold, but the alchemist who is transformed through the work.",
                    "philosophy": "The Great Work is not about changing external matter but transmuting the self. Your habits are alchemical operations—each one refines the prima materia of your base nature into the philosophical gold of your higher self.",
                    "context": "alchemical transformation"
                },
                {
                    "quote": "In the eye of the Merkabah, all patterns spiral. Your habits are the sacred geometry through which consciousness ascends.",
                    "philosophy": "Mystical Judaism teaches that the divine chariot (Merkabah) moves through geometric patterns of ascent. Your consistent practices create a spiral staircase of consciousness—each rotation elevates you toward prophetic vision.",
                    "context": "sacred patterns and ascension"
                },
                {
                    "quote": "The fool sees obstacles; the initiate sees initiations. Every resistance in your path is a secret teaching veiled in difficulty.",
                    "philosophy": "Esoteric tradition holds that challenges are intentional tests designed by the universe to catalyze growth. Your hardest habits are your greatest teachers—lean into the difficulty and extract the hidden wisdom.",
                    "context": "obstacles as initiations"
                },
                {
                    "quote": "The lotus grows in mud. Darkness is not the absence of light but the womb from which illumination is born.",
                    "philosophy": "Eastern esotericism reveals that purity emerges from impurity, enlightenment from ignorance. Your struggles and failures are not setbacks—they are the fertile soil from which your transcendence blooms.",
                    "context": "growth through adversity"
                }
            ],
            "occult": [
                {
                    "quote": "The magician's will is law. Thelema commands: Do what thou wilt shall be the whole of the Law. Your disciplined intention shapes reality itself.",
                    "philosophy": "Crowley's teaching is often misunderstood. True will is not whim but aligned purpose. Your habits train you to discern and execute true will—desire purified into cosmic command. Each completion is a sigil activated.",
                    "context": "will and reality shaping"
                },
                {
                    "quote": "The serpent eats its tail—Ouroboros reveals that endings are beginnings, completions are commencements. Your daily cycle contains eternity.",
                    "philosophy": "The eternal return is not mere repetition but spiral evolution. Each day's habits seem the same, yet you are different each time you perform them. You are the serpent consuming and rebirthing yourself continuously.",
                    "context": "cycles and eternal return"
                },
                {
                    "quote": "Invoke often. The powers respond to those who call consistently, not occasionally. Your habits are invocations of your higher self.",
                    "philosophy": "Ceremonial magic requires regular practice to establish rapport with spiritual forces. Your mundane habits are actually ritual invocations—summoning the version of yourself that already embodies mastery.",
                    "context": "invocation and ritual"
                },
                {
                    "quote": "The grimoire is written in your deeds. Each action inscribes a word in the book of your becoming.",
                    "philosophy": "Medieval grimoires contained instructions for conjuring spirits and powers. Your life is the living grimoire—each habit a spell, each day a ritual, each year a chapter in your book of power.",
                    "context": "life as magical text"
                },
                {
                    "quote": "As you light the black candle, remember: shadow work precedes illumination. Confront what you avoid, and power awakens.",
                    "philosophy": "Left-hand path traditions emphasize embracing the shadow. Your hardest habits force you to face what you resist. This confrontation with the shadow-self is where true magical power is forged.",
                    "context": "shadow work and power"
                }
            ],
            "stoic": [
                {
                    "quote": "The impediment to action advances action. What stands in the way becomes the way. - Marcus Aurelius",
                    "philosophy": "Obstacles are not barriers to your path—they are the path itself. Your difficult habits teach more than easy ones. Resistance is the forge where character is tempered into steel.",
                    "context": "obstacles as opportunities"
                },
                {
                    "quote": "You have power over your mind—not outside events. Realize this, and you will find strength. - Marcus Aurelius",
                    "philosophy": "External circumstances are indifferent. Your habits cultivate the only thing truly in your control: your reasoned choice. Each practice session is sovereignty exercised, autonomy claimed.",
                    "context": "internal control"
                },
                {
                    "quote": "He who fears death will never do anything worthy of a man who is alive. - Seneca",
                    "philosophy": "Memento mori liberates. When you remember that time is limited, trivial concerns dissolve. Your habits become urgent—not from anxiety but from the clarity that comes with knowing each day is precious.",
                    "context": "mortality and urgency"
                },
                {
                    "quote": "Waste no more time arguing what a good man should be. Be one. - Marcus Aurelius",
                    "philosophy": "Virtue is action, not theory. Your habits are philosophy made flesh. Stop deliberating about who you should become—become that person through what you do today.",
                    "context": "action over contemplation"
                },
                {
                    "quote": "The whole future lies in uncertainty: live immediately. - Seneca",
                    "philosophy": "Tomorrow is not promised. Your habit completed today is worth more than ten planned for tomorrow. Seize the present moment—it is the only time that truly exists.",
                    "context": "present action"
                }
            ],
            "eastern": [
                {
                    "quote": "When the student is ready, the teacher appears. Your habits are preparing you for teachings you cannot yet imagine.",
                    "philosophy": "Zen wisdom reveals that readiness is cultivated through practice. Your daily disciplines are not about achieving specific outcomes—they're about becoming the person capable of receiving wisdom when it arrives.",
                    "context": "preparation and readiness"
                },
                {
                    "quote": "The Tao that can be told is not the eternal Tao. Yet in your silent practice, you speak the unspeakable.",
                    "philosophy": "Lao Tzu teaches that ultimate truth transcends words. Your habits are a wordless conversation with the Tao—aligning your small will with the great flow of all things.",
                    "context": "wordless alignment"
                },
                {
                    "quote": "Sitting quietly, doing nothing, spring comes and the grass grows by itself. - Zen proverb",
                    "philosophy": "Paradoxically, effortless achievement requires disciplined preparation. Your habits create the conditions for spontaneous growth. Master the fundamentals, then let nature take its course.",
                    "context": "effortless action through preparation"
                },
                {
                    "quote": "Before enlightenment, chop wood, carry water. After enlightenment, chop wood, carry water.",
                    "philosophy": "Spiritual attainment does not exempt you from daily practice—it transforms your relationship to it. Your mundane habits become sacred when performed with full presence.",
                    "context": "sacred mundane"
                },
                {
                    "quote": "The bamboo that bends is stronger than the oak that resists. Flexibility in your practice ensures its longevity.",
                    "philosophy": "Rigid systems break. Your habit practice should be disciplined yet adaptable. Missing one day is not failure—refusing to return is. Bend with circumstances, then resume your true north.",
                    "context": "adaptive resilience"
                }
            ]
        }
        
        # Select appropriate quotes for the tradition
        tradition_quotes = quotes_db.get(tradition, quotes_db["esoteric"])
        
        # If habit context provided, try to match contextually
        selected_quote = random.choice(tradition_quotes)
        
        if habit_context:
            # Try to find a quote that matches context
            matching_quotes = [q for q in tradition_quotes if habit_context.lower() in q["context"].lower()]
            if matching_quotes:
                selected_quote = random.choice(matching_quotes)
        
        # Personalize if user name provided
        philosophy = selected_quote["philosophy"]
        if user_name and user_name != "Hunter":
            philosophy = f"{user_name}, " + philosophy[0].lower() + philosophy[1:]
        
        return {
            "quote": selected_quote["quote"],
            "philosophy": philosophy,
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
                        "content": f"Summarize this note in 2-3 insightful bullet points:\n\nTitle: {title}\n\n{content}"
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
