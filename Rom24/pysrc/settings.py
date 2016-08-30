import os
import logging

logger = logging.getLogger()

#Game settings
PORT = 1337
WIZLOCK = False
NEWLOCK = False
ENCRYPT_PASSWORD = True
LOGALL = False
MAX_ITERATIONS = 300

#Files
AREA_LIST = 'area.lst'
BUG_FILE = 'bug.txt'
TYPO_FILE = 'typo.txt'
SOCIAL_LIST = 'social.lst'
HELP_FILE = 'help_files'

#extn
DATA_EXTN = '.json'
PKL_EXTN = '.pickle'

#Folders
LEGACY_AREA_DIR = os.path.join('..', 'area')
LEGACY_PLAYER_DIR = os.path.join('..', 'player')
SOCIAL_DIR = os.path.join(LEGACY_AREA_DIR, 'socials')
HELP_DIR = os.path.join(LEGACY_AREA_DIR, 'help_files')

#New structure
DATA_DIR = os.path.join('..', 'data')
WORLD_DIR = os.path.join(DATA_DIR, 'world')

PLAYER_DIR = os.path.join(DATA_DIR, 'players')
SYSTEM_DIR = os.path.join(DATA_DIR, 'system')
DOC_DIR = os.path.join(DATA_DIR, 'docs')

AREA_DIR = os.path.join(WORLD_DIR, 'areas')
INSTANCE_DIR = os.path.join(WORLD_DIR, 'instances')

#Features
SHOW_DAMAGE_NUMBERS = True
DETAILED_INVALID_COMMANDS = True
SAVE_LIMITER = 0  # Only save files every N seconds, unless forced.
#Save file(s) format selector. Switch JSON to true to save entirely in JSON, Pickle will picklize the json string
#we serialize, this is a faster save, but somewhat less readable, and not hand edit friendly.
SAVE_FORMAT = {'Pickle': (True, PKL_EXTN),
               'JSON': (False, DATA_EXTN)}

ENABLE_DUPE_PROTECTION = False
ENABLE_HUNGER_THIRST = True

#Modifiers
# Percent modifiers to regen on ticks
GLOBAL_HIT_REGEN = 100
GLOBAL_MANA_REGEN = 100
GLOBAL_MOVE_REGEN = 100

# Percent modifiers to all damage dealt
PLAYER_DAMAGE = 100
NPC_DAMAGE = 100

# Percent modifiers to experience gained on kill
EXPERIENCE_GAINS = 100

# Reset multipliers
RESET_MOBS = 1
