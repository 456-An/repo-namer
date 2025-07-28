import re
import json

# Global variable to store rules
RULES = {}

def load_rules():
    """Load naming conversion rules from rules.json"""
    global RULES
    try:
        with open("rules.json", encoding="utf-8") as f:
            RULES = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default rules if file doesn't exist or is invalid
        RULES = {
            "c#": "csharp",
            "c++": "cpp",
            " ": "-",
            "+": "",
            "#": "",
            "&": "and"
        }

def reload_rules():
    """Reload rules from rules.json file"""
    load_rules()

# Load rules on module import
load_rules()

def clean_name(name: str, style='kebab') -> str:
    name = name.lower()

    for keyword, replacement in RULES.items():
        name = name.replace(keyword, replacement)

    # Remove invalid characters (keep letters, numbers, -, _, .)
    name = re.sub(r"[^\w\-.]", "", name)
    
    # Convert to specified style
    if style == 'kebab':
        # Convert spaces and underscores to hyphens
        name = re.sub(r'[_\s]+', '-', name)
        name = name.strip('-')
    elif style == 'snake':
        # Convert spaces and hyphens to underscores
        name = re.sub(r'[-\s]+', '_', name)
        name = name.strip('_')
    elif style == 'lower-camel':
        # Convert to kebab-case first
        name = re.sub(r'[_\s]+', '-', name)
        name = name.strip('-')
        # Convert to lowerCamelCase
        parts = name.split('-')
        if parts:
            name = parts[0] + ''.join(word.capitalize() for word in parts[1:])
    elif style == 'upper-camel':
        # Convert to kebab-case first
        name = re.sub(r'[_\s]+', '-', name)
        name = name.strip('-')
        # Convert to UpperCamelCase
        parts = name.split('-')
        if parts:
            name = ''.join(word.capitalize() for word in parts)
    
    return name
