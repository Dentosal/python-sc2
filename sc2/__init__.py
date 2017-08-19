from pathlib import Path
__all__ = [p.stem for p in Path().iterdir() if p.is_file() and p.suffix == ".py" and p.stem != "__init__"]

from . import maps
from .data import *
from .bot_ai import BotAI
from .main import run_game
