"""
Character Visualization System
Creates dynamic SVG-based character avatars that evolve with level, stats, and equipment
"""

def get_character_svg(profile: dict, stats: dict, equipped: dict, active_effects: list = None) -> str:
    """
    Generate an animated SVG character based on profile, stats, and equipment
    
    Character evolves through 5 stages:
    - Novice (Lv 1-10): Basic form
    - Skilled (Lv 11-25): Enhanced features
    - Elite (Lv 26-50): Advanced design with auras
    - S-Rank (Lv 51-75): Legendary appearance
    - Monarch (Lv 76-100): Ultimate transcendent form
    """
    
    # Safely get values with defaults
    level = stats.get('level', 1) if stats else 1
    avatar_style = profile.get('avatar_style', 'warrior') if profile else 'warrior'
    
    # Safely get equipment IDs (handle None and missing keys)
    weapon_id = equipped.get('weapon_id', '') if equipped else ''
    armor_id = equipped.get('armor_id', '') if equipped else ''
    ring_id = equipped.get('ring_id', '') if equipped else ''
    amulet_id = equipped.get('amulet_id', '') if equipped else ''
    
    # Ensure they're strings
    weapon_id = weapon_id or ''
    armor_id = armor_id or ''
    ring_id = ring_id or ''
    amulet_id = amulet_id or ''
    
    # Determine evolution stage
    if level >= 76:
        stage = "monarch"
        stage_name = "Shadow Monarch"
        base_glow = "rgba(212, 175, 55, 0.9)"
        size_multiplier = 1.5
    elif level >= 51:
        stage = "srank"
        stage_name = "S-Rank Hunter"
        base_glow = "rgba(255, 215, 0, 0.8)"
        size_multiplier = 1.3
    elif level >= 26:
        stage = "elite"
        stage_name = "Elite Hunter"
        base_glow = "rgba(212, 175, 55, 0.6)"
        size_multiplier = 1.2
    elif level >= 11:
        stage = "skilled"
        stage_name = "Skilled Hunter"
        base_glow = "rgba(212, 175, 55, 0.4)"
        size_multiplier = 1.1
    else:
        stage = "novice"
        stage_name = "Novice Hunter"
        base_glow = "rgba(212, 175, 55, 0.2)"
        size_multiplier = 1.0
    
    # Stat-based visual modifiers (safely get with defaults)
    strength = stats.get('strength', 0) if stats else 0
    intelligence = stats.get('intelligence', 0) if stats else 0
    vitality = stats.get('vitality', 0) if stats else 0
    willpower = stats.get('willpower', 0) if stats else 0
    sense = stats.get('sense', 0) if stats else 0
    
    # Calculate visual properties
    character_height = 180 + (strength * 0.5)
    muscle_definition = min(100, strength * 2)
    aura_intensity = min(100, willpower * 1.5)
    glow_radius = 10 + (intelligence * 0.3)
    health_pulse = 0.5 + (vitality * 0.01)
    
    # Avatar style base colors
    style_colors = {
        'warrior': {
            'primary': '#8B0000',
            'secondary': '#FFD700',
            'accent': '#C0C0C0',
            'weapon': '⚔️'
        },
        'mage': {
            'primary': '#4B0082',
            'secondary': '#9370DB',
            'accent': '#00FFFF',
            'weapon': '🔮'
        },
        'rogue': {
            'primary': '#2F4F4F',
            'secondary': '#696969',
            'accent': '#00FF00',
            'weapon': '🗡️'
        },
        'sage': {
            'primary': '#DAA520',
            'secondary': '#F0E68C',
            'accent': '#FFFFFF',
            'weapon': '📿'
        }
    }
    
    colors = style_colors.get(avatar_style, style_colors['warrior'])
    
    # Equipment effects (safely check for equipment)
    weapon_glow = "none"
    armor_aura = "none"
    has_legendary_item = False
    
    if weapon_id:
        weapon_glow = f"drop-shadow(0 0 10px {colors['accent']})"
        if 'legendary' in weapon_id.lower() or 'demon' in weapon_id.lower():
            has_legendary_item = True
    
    if armor_id:
        armor_aura = f"drop-shadow(0 0 15px {colors['primary']})"
        if 'shadow' in armor_id.lower() or 'monarch' in armor_id.lower():
            has_legendary_item = True
    
    # Check for shadow armor specifically
    has_shadow_armor = 'shadow' in armor_id.lower()
    
    # Generate SVG
    svg = f"""
    <svg width="400" height="500" viewBox="0 0 400 500" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <!-- Gradients -->
            <radialGradient id="auraGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:{base_glow};stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:{base_glow};stop-opacity:0" />
            </radialGradient>
            
            <radialGradient id="powerGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:#FFD700;stop-opacity:0.9" />
                <stop offset="50%" style="stop-color:#d4af37;stop-opacity:0.5" />
                <stop offset="100%" style="stop-color:#d4af37;stop-opacity:0" />
            </radialGradient>
            
            <!-- Animations -->
            <animateTransform
                id="pulseAura"
                attributeName="transform"
                attributeType="XML"
                type="scale"
                from="1"
                to="1.1"
                dur="{health_pulse}s"
                repeatCount="indefinite"
                additive="sum"
            />
            
            <animate
                id="glowPulse"
                attributeName="opacity"
                values="0.6;1;0.6"
                dur="2s"
                repeatCount="indefinite"
            />
            
            <!-- Filters -->
            <filter id="glow">
                <feGaussianBlur stdDeviation="{glow_radius}" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            
            <filter id="innerGlow">
                <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="blur"/>
                <feOffset in="blur" dx="0" dy="0" result="offsetBlur"/>
                <feFlood flood-color="{colors['accent']}" flood-opacity="0.8"/>
                <feComposite in2="offsetBlur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background Power Aura (scales with willpower) -->
        <circle cx="200" cy="250" r="{100 + aura_intensity}" fill="url(#auraGradient)" opacity="{aura_intensity/100 if aura_intensity > 0 else 0.2}">
            <animateTransform
                attributeName="transform"
                attributeType="XML"
                type="scale"
                values="1;1.2;1"
                dur="3s"
                repeatCount="indefinite"
                additive="sum"
            />
        </circle>
        
        <!-- Stage-specific effects -->
        {'<!-- Monarch Crown -->' if stage == "monarch" else ''}
        {f'''<g transform="translate(200, 80)">
            <path d="M -30,-10 L -20,-30 L -10,-15 L 0,-35 L 10,-15 L 20,-30 L 30,-10 Z" 
                  fill="{colors['secondary']}" 
                  stroke="#FFD700" 
                  stroke-width="2"
                  filter="url(#glow)">
                <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
            </path>
        </g>''' if stage == "monarch" else ''}
        
        <!-- Character Body (size scales with strength) -->
        <g transform="translate(200, 250) scale({size_multiplier})">
            
            <!-- Shadow (if has shadow armor) -->
            {f'''<ellipse cx="0" cy="80" rx="60" ry="20" fill="#000000" opacity="0.5">
                <animate attributeName="rx" values="60;70;60" dur="2s" repeatCount="indefinite"/>
            </ellipse>''' if has_shadow_armor else ''}
            
            <!-- Body -->
            <ellipse cx="0" cy="0" rx="40" ry="60" fill="{colors['primary']}" 
                     stroke="{colors['secondary']}" stroke-width="3"
                     filter="{armor_aura if armor_aura != 'none' else 'url(#innerGlow)'}"/>
            
            <!-- Muscle definition (based on strength) -->
            {f'''<g opacity="{muscle_definition/100}">
                <line x1="-15" y1="-20" x2="-15" y2="20" stroke="{colors['accent']}" stroke-width="2"/>
                <line x1="15" y1="-20" x2="15" y2="20" stroke="{colors['accent']}" stroke-width="2"/>
                <line x1="-25" y1="0" x2="25" y2="0" stroke="{colors['accent']}" stroke-width="2"/>
            </g>''' if strength > 10 else ''}
            
            <!-- Head -->
            <circle cx="0" cy="-70" r="25" fill="{colors['primary']}" 
                    stroke="{colors['secondary']}" stroke-width="2"
                    filter="url(#innerGlow)"/>
            
            <!-- Eyes (glow with intelligence) -->
            <circle cx="-8" cy="-70" r="3" fill="{colors['accent']}">
                <animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/>
            </circle>
            <circle cx="8" cy="-70" r="3" fill="{colors['accent']}">
                <animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/>
            </circle>
            
            <!-- Third Eye (unlocked at high sense) -->
            {f'''<circle cx="0" cy="-75" r="4" fill="#9370DB" filter="url(#glow)">
                <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/>
            </circle>''' if sense > 50 else ''}
            
            <!-- Arms -->
            <rect x="-50" y="-20" width="15" height="50" rx="5" fill="{colors['primary']}" 
                  stroke="{colors['secondary']}" stroke-width="2"/>
            <rect x="35" y="-20" width="15" height="50" rx="5" fill="{colors['primary']}" 
                  stroke="{colors['secondary']}" stroke-width="2"/>
            
            <!-- Legs -->
            <rect x="-25" y="40" width="18" height="60" rx="5" fill="{colors['primary']}" 
                  stroke="{colors['secondary']}" stroke-width="2"/>
            <rect x="7" y="40" width="18" height="60" rx="5" fill="{colors['primary']}" 
                  stroke="{colors['secondary']}" stroke-width="2"/>
            
            <!-- Equipped Weapon -->
            {f'''<g transform="translate(60, 0) rotate(-45)">
                <rect x="0" y="-40" width="8" height="80" rx="2" 
                      fill="{colors['accent']}" 
                      stroke="#FFD700" 
                      stroke-width="2"
                      filter="{weapon_glow if weapon_glow != 'none' else 'none'}">
                    <animate attributeName="opacity" values="0.8;1;0.8" dur="1.5s" repeatCount="indefinite"/>
                </rect>
                <polygon points="4,-45 -5,-55 4,-50 13,-55" 
                         fill="#FFD700" 
                         stroke="#FFF" 
                         stroke-width="1"/>
            </g>''' if weapon_id else ''}
            
            <!-- Willpower Inner Fire (unlocked at high willpower) -->
            {f'''<g opacity="{min(1, willpower/50)}">
                <circle cx="0" cy="0" r="15" fill="none" stroke="#FF4500" stroke-width="2">
                    <animate attributeName="r" values="15;25;15" dur="2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
                </circle>
                <circle cx="0" cy="0" r="20" fill="none" stroke="#FFD700" stroke-width="1">
                    <animate attributeName="r" values="20;30;20" dur="2.5s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2.5s" repeatCount="indefinite"/>
                </circle>
            </g>''' if willpower > 30 else ''}
            
            <!-- Legendary Item Particle Effects -->
            {'''<g id="particles">
                <circle cx="40" cy="-60" r="2" fill="#FFD700" opacity="0.8">
                    <animate attributeName="cy" from="-60" to="-100" dur="2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" from="0.8" to="0" dur="2s" repeatCount="indefinite"/>
                </circle>
                <circle cx="-40" cy="-60" r="2" fill="#FFD700" opacity="0.8">
                    <animate attributeName="cy" from="-60" to="-100" dur="2.3s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" from="0.8" to="0" dur="2.3s" repeatCount="indefinite"/>
                </circle>
                <circle cx="0" cy="-80" r="2" fill="#d4af37" opacity="0.8">
                    <animate attributeName="cy" from="-80" to="-120" dur="2.5s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" from="0.8" to="0" dur="2.5s" repeatCount="indefinite"/>
                </circle>
            </g>''' if has_legendary_item else ''}
            
        </g>
        
        <!-- Level Badge -->
        <g transform="translate(200, 450)">
            <rect x="-60" y="-20" width="120" height="40" rx="20" 
                  fill="url(#powerGradient)" 
                  stroke="#FFD700" 
                  stroke-width="2"/>
            <text x="0" y="5" 
                  font-family="Arial, sans-serif" 
                  font-size="18" 
                  font-weight="bold" 
                  fill="#0a0a0a" 
                  text-anchor="middle">
                LEVEL {level}
            </text>
        </g>
        
        <!-- Stage Name -->
        <text x="200" y="30" 
              font-family="'Cinzel', serif" 
              font-size="16" 
              font-weight="bold" 
              fill="#d4af37" 
              text-anchor="middle"
              filter="url(#glow)">
            {stage_name.upper()}
        </text>
        
    </svg>
    """
    
    return svg


def get_stat_visual_bars(stats: dict) -> str:
    """Generate animated stat bars with icons and visual effects"""
    
    stat_config = {
        'strength': {'icon': '⚔️', 'color': '#FF4500', 'name': 'Strength'},
        'intelligence': {'icon': '🧠', 'color': '#9370DB', 'name': 'Intelligence'},
        'vitality': {'icon': '❤️', 'color': '#DC143C', 'name': 'Vitality'},
        'agility': {'icon': '⚡', 'color': '#FFD700', 'name': 'Agility'},
        'sense': {'icon': '👁️', 'color': '#00CED1', 'name': 'Sense'},
        'willpower': {'icon': '🔥', 'color': '#FF6347', 'name': 'Willpower'}
    }
    
    html = "<div style='background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 20px; border-radius: 15px; border: 2px solid #d4af37; margin: 20px 0;'>"
    
    for stat, config in stat_config.items():
        value = stats.get(stat, 0) if stats else 0
        max_value = 100
        percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0
        
        html += f"""
        <div style='margin: 15px 0;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                <span style='color: #ffffff; font-weight: bold;'>{config['icon']} {config['name']}</span>
                <span style='color: {config['color']}; font-weight: bold;'>{value}</span>
            </div>
            <div style='background: #0a0a0a; height: 25px; border-radius: 12px; overflow: hidden; border: 2px solid #d4af37;'>
                <div style='
                    width: {percentage}%; 
                    height: 100%; 
                    background: linear-gradient(90deg, {config['color']} 0%, {config['color']}88 100%);
                    box-shadow: 0 0 20px {config['color']};
                    animation: fillBar 1s ease-out;
                    position: relative;
                '>
                    <div style='
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
                        animation: shimmer 2s infinite;
                    '></div>
                </div>
            </div>
        </div>
        """
    
    html += """
    </div>
    <style>
        @keyframes fillBar {
            from { width: 0%; }
        }
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
    </style>
    """
    
    return html


def get_level_up_animation() -> str:
    """Epic level-up animation overlay"""
    
    return """
    <div id="levelUpOverlay" style='
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle, rgba(212,175,55,0.3) 0%, rgba(0,0,0,0.9) 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeIn 0.5s ease-in;
    '>
        <h1 style='
            color: #FFD700;
            font-size: 72px;
            font-weight: bold;
            text-shadow: 0 0 30px rgba(255,215,0,0.8);
            animation: scaleIn 0.5s ease-out, glow 1.5s infinite;
            margin: 0;
        '>
            LEVEL UP!
        </h1>
        <div style='
            margin-top: 40px;
            width: 200px;
            height: 200px;
            border: 5px solid #FFD700;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0 50px rgba(255,215,0,0.6);
            animation: rotate 2s linear infinite, pulse 1.5s infinite;
        '>
            <span style='font-size: 80px;'>⚔️</span>
        </div>
        <p style='
            color: #d4af37;
            font-size: 24px;
            margin-top: 30px;
            animation: fadeIn 1s ease-in 0.5s both;
        '>
            Power increases!
        </p>
    </div>
    
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes scaleIn {
            from { transform: scale(0.5); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        @keyframes glow {
            0%, 100% { text-shadow: 0 0 20px rgba(255,215,0,0.8); }
            50% { text-shadow: 0 0 40px rgba(255,215,0,1); }
        }
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
    </style>
    
    <script>
        setTimeout(() => {
            document.getElementById('levelUpOverlay').style.animation = 'fadeOut 0.5s ease-out';
            setTimeout(() => {
                document.getElementById('levelUpOverlay').remove();
            }, 500);
        }, 3000);
    </script>
    
    <style>
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    </style>
    """


def get_equipment_display(equipped: dict, inventory: list) -> str:
    """Visual display of equipped items with 3D effect"""
    
    # Safely handle equipped dict
    equipped = equipped or {}
    
    html = """
    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;'>
    """
    
    slots = {
        'weapon': {'icon': '⚔️', 'name': 'Weapon', 'pos': 'top-left'},
        'armor': {'icon': '🛡️', 'name': 'Armor', 'pos': 'top-right'},
        'ring': {'icon': '💍', 'name': 'Ring', 'pos': 'bottom-left'},
        'amulet': {'icon': '📿', 'name': 'Amulet', 'pos': 'bottom-right'}
    }
    
    for slot, config in slots.items():
        item_id = equipped.get(f"{slot}_id", None)
        item_id = item_id or ''  # Convert None to empty string
        
        if item_id:
            item_name = item_id.replace('_', ' ').title()
            equipped_html = f"""
            <div style='
                background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
                border: 3px solid #d4af37;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 8px 20px rgba(0,0,0,0.6), 0 0 30px rgba(212,175,55,0.3);
                transform: perspective(1000px) rotateX(5deg);
                transition: transform 0.3s ease;
            ' onmouseover='this.style.transform="perspective(1000px) rotateX(0deg) scale(1.05)"' 
               onmouseout='this.style.transform="perspective(1000px) rotateX(5deg)"'>
                <div style='font-size: 48px; margin-bottom: 10px;'>{config['icon']}</div>
                <div style='color: #d4af37; font-weight: bold; margin-bottom: 5px;'>{config['name']}</div>
                <div style='color: #ffffff; font-size: 14px;'>{item_name}</div>
            </div>
            """
        else:
            equipped_html = f"""
            <div style='
                background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
                border: 2px dashed #555;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                opacity: 0.5;
            '>
                <div style='font-size: 48px; margin-bottom: 10px; filter: grayscale(100%);'>{config['icon']}</div>
                <div style='color: #666; font-weight: bold;'>{config['name']}</div>
                <div style='color: #555; font-size: 12px;'>Empty</div>
            </div>
            """
        
        html += equipped_html
    
    html += "</div>"
    return html
