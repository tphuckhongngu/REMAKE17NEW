# maps/__init__.py
# Auto-generated maps registry
from .level1 import get_map as level1_map, get_spawns as level1_spawns
from .level2 import get_map as level2_map, get_spawns as level2_spawns
from .level3 import get_map as level3_map, get_spawns as level3_spawns

MAPS = {
    1: level1_map,
    2: level2_map,
    3: level3_map,
}

SPAWNS = {
    1: level1_spawns,
    2: level2_spawns,
    3: level3_spawns,
}
