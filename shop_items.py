# Complete shop system from original app

RARITY_COLORS = {
    "common": {"bg": "#64748b", "text": "#f1f5f9", "glow": "0 0 5px rgba(100,116,139,0.3)"},
    "uncommon": {"bg": "#22c55e", "text": "#f0fdf4", "glow": "0 0 10px rgba(34,197,94,0.4)"},
    "rare": {"bg": "#3b82f6", "text": "#eff6ff", "glow": "0 0 15px rgba(59,130,246,0.5)"},
    "epic": {"bg": "#a855f7", "text": "#faf5ff", "glow": "0 0 20px rgba(168,85,247,0.6)"},
    "legendary": {"bg": "#f97316", "text": "#fff7ed", "glow": "0 0 25px rgba(249,115,22,0.7)"},
    "mythic": {"bg": "#ef4444", "text": "#fef2f2", "glow": "0 0 30px rgba(239,68,68,0.8)"},
    "divine": {"bg": "#facc15", "text": "#422006", "glow": "0 0 35px rgba(250,204,21,0.9)"}
}

ALL_SHOP_ITEMS = [
    # CONSUMABLES - XP BOOSTERS
    {
        "id": "xp_boost_1h",
        "name": "Lesser Mana Potion",
        "description": "Doubles XP gains for 1 hour. The energy of a low-rank dungeon flows through you.",
        "icon": "⚗️",
        "rarity": "common",
        "price": {"gold": 500},
        "effect": {"type": "xp_multiplier", "value": 2, "duration": 3600},
        "stackable": True,
        "max_stack": 99,
        "category": "consumable"
    },
    {
        "id": "xp_boost_6h",
        "name": "Greater Mana Potion",
        "description": "Doubles XP gains for 6 hours. Concentrated essence from B-Rank dungeons.",
        "icon": "🧪",
        "rarity": "uncommon",
        "price": {"gold": 2500},
        "effect": {"type": "xp_multiplier", "value": 2, "duration": 21600},
        "stackable": True,
        "max_stack": 50,
        "category": "consumable"
    },
    {
        "id": "xp_boost_24h",
        "name": "Elixir of Awakening",
        "description": "Triples XP gains for 24 hours. A rare elixir that awakens your true potential.",
        "icon": "🍷",
        "rarity": "rare",
        "price": {"gold": 8000, "crystals": 10},
        "effect": {"type": "xp_multiplier", "value": 3, "duration": 86400},
        "stackable": True,
        "max_stack": 10,
        "category": "consumable"
    },
    {
        "id": "xp_mega_boost",
        "name": "Essence of the Monarch",
        "description": "5x XP for 12 hours. The concentrated power of a Monarch flows through your veins.",
        "icon": "👑",
        "rarity": "legendary",
        "price": {"gold": 50000, "crystals": 100},
        "effect": {"type": "xp_multiplier", "value": 5, "duration": 43200},
        "stackable": True,
        "max_stack": 3,
        "category": "consumable"
    },
    
    # CONSUMABLES - GOLD BOOSTERS
    {
        "id": "gold_boost_1h",
        "name": "Goblin's Lucky Coin",
        "description": "Doubles gold earned for 1 hour. Even goblins know the value of wealth.",
        "icon": "🪙",
        "rarity": "common",
        "price": {"gold": 400},
        "effect": {"type": "gold_multiplier", "value": 2, "duration": 3600},
        "stackable": True,
        "max_stack": 99,
        "category": "consumable"
    },
    {
        "id": "gold_boost_24h",
        "name": "Dragon's Hoard Blessing",
        "description": "Triples gold earned for 24 hours. A dragon's greed becomes your fortune.",
        "icon": "🔥",
        "rarity": "epic",
        "price": {"gold": 10000, "crystals": 15},
        "effect": {"type": "gold_multiplier", "value": 3, "duration": 86400},
        "stackable": True,
        "max_stack": 5,
        "category": "consumable"
    },
    
    # CONSUMABLES - STREAK PROTECTORS
    {
        "id": "streak_shield",
        "name": "Shield of Perseverance",
        "description": "Protects your streak from breaking once. Even hunters need a safety net.",
        "icon": "🛡️",
        "rarity": "uncommon",
        "price": {"gold": 1000},
        "effect": {"type": "streak_protection", "uses": 1},
        "stackable": True,
        "max_stack": 20,
        "category": "consumable"
    },
    {
        "id": "streak_shield_mega",
        "name": "Barrier of the Unwavering",
        "description": "Protects your streak from breaking 5 times. For those who refuse to fall.",
        "icon": "🛡️",
        "rarity": "rare",
        "price": {"gold": 4000, "crystals": 5},
        "effect": {"type": "streak_protection", "uses": 5},
        "stackable": True,
        "max_stack": 5,
        "category": "consumable"
    },
    
    # CONSUMABLES - INSTANT COMPLETES
    {
        "id": "instant_complete_habit",
        "name": "Shadow Clone Scroll",
        "description": "Instantly complete one habit. Your shadow does the work for you.",
        "icon": "📜",
        "rarity": "rare",
        "price": {"gold": 3000, "crystals": 5},
        "effect": {"type": "instant_complete_habit", "quantity": 1},
        "stackable": True,
        "max_stack": 10,
        "category": "consumable"
    },
    {
        "id": "instant_complete_step",
        "name": "Time Manipulation Crystal",
        "description": "Instantly complete one goal step. Bend time to your will.",
        "icon": "⏱️",
        "rarity": "epic",
        "price": {"gold": 8000, "crystals": 20},
        "effect": {"type": "instant_complete_step", "quantity": 1},
        "stackable": True,
        "max_stack": 5,
        "category": "consumable"
    },
    
    # CONSUMABLES - STAT BOOSTERS
    {
        "id": "stat_boost_temp",
        "name": "Essence of Strength",
        "description": "+10 to all stats for 24 hours. Feel the power surge through you.",
        "icon": "💪",
        "rarity": "rare",
        "price": {"gold": 6000, "crystals": 10},
        "effect": {"type": "stat_boost_temp", "stats": "all", "value": 10, "duration": 86400},
        "stackable": True,
        "max_stack": 10,
        "category": "consumable"
    },
    {
        "id": "stat_boost_perm",
        "name": "Eternal Growth Elixir",
        "description": "Permanently increases one stat by 5. Choose your path wisely.",
        "icon": "✨",
        "rarity": "legendary",
        "price": {"gold": 50000, "crystals": 150},
        "effect": {"type": "stat_boost_perm", "value": 5, "choosable": True},
        "stackable": True,
        "max_stack": 5,
        "category": "consumable"
    },
    
    # EQUIPMENT - WEAPONS
    {
        "id": "iron_dagger",
        "name": "Iron Dagger of the Novice",
        "description": "+5% XP for fitness goals. Your first real weapon.",
        "icon": "🗡️",
        "rarity": "common",
        "price": {"gold": 2000},
        "effect": {"type": "category_xp_boost", "category": "fitness", "value": 1.05},
        "slot": "weapon",
        "stats": {"strength": 5},
        "category": "equipment"
    },
    {
        "id": "knights_sword",
        "name": "Knight's Longsword",
        "description": "+15% XP for fitness goals. A weapon worthy of a true warrior.",
        "icon": "⚔️",
        "rarity": "uncommon",
        "price": {"gold": 8000, "crystals": 10},
        "effect": {"type": "category_xp_boost", "category": "fitness", "value": 1.15},
        "slot": "weapon",
        "stats": {"strength": 15, "vitality": 5},
        "category": "equipment"
    },
    {
        "id": "demons_dagger",
        "name": "Demon King's Dagger",
        "description": "+25% XP for all challenging goals. Forged in the depths of hell.",
        "icon": "🗡️",
        "rarity": "legendary",
        "price": {"gold": 100000, "crystals": 200},
        "effect": {"type": "difficulty_xp_boost", "difficulty": "hard", "value": 1.25},
        "slot": "weapon",
        "stats": {"strength": 30, "agility": 20, "willpower": 15},
        "category": "equipment",
        "level_required": 50
    },
    
    # EQUIPMENT - ARMOR
    {
        "id": "leather_armor",
        "name": "Hunter's Leather Armor",
        "description": "Reduces habit difficulty by 5%. Lighter steps on your journey.",
        "icon": "🛡️",
        "rarity": "common",
        "price": {"gold": 2500},
        "effect": {"type": "difficulty_reduction", "value": 0.05},
        "slot": "armor",
        "stats": {"vitality": 10},
        "category": "equipment"
    },
    {
        "id": "knight_armor",
        "name": "Knight's Plate Armor",
        "description": "Streak shield activates automatically once per week.",
        "icon": "🛡️",
        "rarity": "rare",
        "price": {"gold": 15000, "crystals": 25},
        "effect": {"type": "auto_streak_shield", "frequency": "weekly"},
        "slot": "armor",
        "stats": {"vitality": 25, "willpower": 10},
        "category": "equipment",
        "level_required": 25
    },
    {
        "id": "shadow_armor",
        "name": "Armor of the Shadow Monarch",
        "description": "Immune to streak breaks. The shadows protect you always.",
        "icon": "🌑",
        "rarity": "mythic",
        "price": {"gold": 500000, "crystals": 1000},
        "effect": {"type": "streak_immunity"},
        "slot": "armor",
        "stats": {"vitality": 50, "willpower": 50, "sense": 30},
        "category": "equipment",
        "level_required": 80
    },
    
    # EQUIPMENT - ACCESSORIES
    {
        "id": "ring_focus",
        "name": "Ring of Focus",
        "description": "+10% XP for learning goals. Clarity of mind brings power.",
        "icon": "💍",
        "rarity": "uncommon",
        "price": {"gold": 5000, "crystals": 5},
        "effect": {"type": "category_xp_boost", "category": "learning", "value": 1.10},
        "slot": "ring",
        "stats": {"intelligence": 10},
        "category": "equipment"
    },
    {
        "id": "amulet_wealth",
        "name": "Amulet of Prosperity",
        "description": "+20% gold from all sources. Wealth flows to you naturally.",
        "icon": "📿",
        "rarity": "rare",
        "price": {"gold": 12000, "crystals": 20},
        "effect": {"type": "gold_multiplier_passive", "value": 1.20},
        "slot": "amulet",
        "stats": {"sense": 15},
        "category": "equipment"
    },
    
    # COSMETICS
    {
        "id": "aura_blue",
        "name": "Azure Aura",
        "description": "Surround yourself with a calm blue glow.",
        "icon": "💙",
        "rarity": "uncommon",
        "price": {"gold": 3000},
        "effect": {"type": "cosmetic", "aura": "blue"},
        "category": "cosmetic"
    },
    {
        "id": "aura_gold",
        "name": "Golden Radiance",
        "description": "Shine with the brilliance of gold.",
        "icon": "💛",
        "rarity": "rare",
        "price": {"gold": 10000, "crystals": 15},
        "effect": {"type": "cosmetic", "aura": "gold"},
        "category": "cosmetic"
    },
    {
        "id": "aura_shadow",
        "name": "Shadow Monarch Aura",
        "description": "Command the darkness itself.",
        "icon": "🖤",
        "rarity": "legendary",
        "price": {"gold": 50000, "crystals": 100},
        "effect": {"type": "cosmetic", "aura": "shadow"},
        "category": "cosmetic",
        "level_required": 50
    }
]

def get_items_by_category(category):
    """Get all shop items for a specific category"""
    return [item for item in ALL_SHOP_ITEMS if item["category"] == category]

def get_item_by_id(item_id):
    """Get a specific shop item by ID"""
    for item in ALL_SHOP_ITEMS:
        if item["id"] == item_id:
            return item
    return None

def can_afford(item, gold, crystals=0):
    """Check if player can afford an item"""
    price = item.get("price", {})
    gold_cost = price.get("gold", 0)
    crystal_cost = price.get("crystals", 0)
    
    return gold >= gold_cost and crystals >= crystal_cost

def meets_level_requirement(item, player_level):
    """Check if player meets level requirement"""
    required = item.get("level_required", 0)
    return player_level >= required
