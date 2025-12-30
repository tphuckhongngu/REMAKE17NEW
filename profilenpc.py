# Profiles data for NPCs and characters
# Each entry may contain 'name', 'desc', and 'portrait' which is a tuple path to the image
PROFILES = [
    {
        'name': 'Đại úy. Trần Chí Hướng',
        'desc': 'Là một trong những người sống sót cuối cùng trong đại thảm họa rác thải. Anh và những đồng đội đã chiến đấu anh dũng chống lại lũ quái vật. Hiện tại anh đang đảm nhiệm vị trí huấn luyện các tân binh.',
        # portrait as path segments relative to project root (used by UI.load_img)
        'portrait': ('npc', 'anhnpc.png')
    },
    # four placeholders to be filled later
    {'name': '???', 'desc': '', 'portrait': None},
    {'name': '???', 'desc': '', 'portrait': None},
    {'name': '???', 'desc': '', 'portrait': None},
    {'name': '???', 'desc': '', 'portrait': None}
]
