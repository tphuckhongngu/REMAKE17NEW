import pygame
from maps.map_manager import TILE_SIZE


class NPC(pygame.sprite.Sprite):
    def __init__(self, tile_pos, tile_folder="npc", name=None):
        super().__init__()
        self.tile_x, self.tile_y = tile_pos
        # load small map icon for npc (to show on map)
        try:
            img = pygame.image.load(f"{tile_folder}/npcmap.png").convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.image = img
        except Exception:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            # use a neutral grey if image missing to avoid bright magenta squares
            self.image.fill((120, 180, 120))

        self.rect = self.image.get_rect()
        self.rect.center = (self.tile_x * TILE_SIZE + TILE_SIZE // 2,
                            self.tile_y * TILE_SIZE + TILE_SIZE // 2)

        # portrait for dialog (shown when speaking)
        try:
            portrait = pygame.image.load(f"{tile_folder}/anhnpc.png").convert_alpha()
            # keep portrait at reasonable size
            w = min(200, portrait.get_width())
            h = min(200, portrait.get_height())
            self.portrait = pygame.transform.scale(portrait, (w, h))
        except Exception:
            self.portrait = None

        # speaking state and dialog queue
        self.dialog_queue = []
        self.is_speaking = False
        self.full_text = ""
        self.display_text = ""
        self.char_index = 0
        self.typing_timer = 0
        self.typing_delay = 3  # frames per character
        self.waiting_for_input = False
        # optional display name for dialog (shown above text)
        self.name = name or "NPC"
        # no small speech bubble (we'll draw dialog only)

    def speak(self, text, typing_delay=3):
        # start speaking a single text (push to queue)
        self.dialog_queue = [text]
        self.typing_delay = typing_delay
        self._start_next()

    def start_dialog(self, lines, typing_delay=3):
        """Start a sequence of dialog lines."""
        if isinstance(lines, str):
            lines = [lines]
        self.dialog_queue = list(lines)
        self.typing_delay = typing_delay
        self._start_next()

    def _start_next(self):
        if self.dialog_queue:
            self.full_text = self.dialog_queue.pop(0)
            self.display_text = ""
            self.char_index = 0
            self.typing_timer = 0
            self.is_speaking = True
            self.waiting_for_input = False
        else:
            self.is_speaking = False
            self.waiting_for_input = False

    def update(self):
        if not self.is_speaking:
            return
        self.typing_timer += 1
        if self.typing_timer >= self.typing_delay:
            self.typing_timer = 0
            if self.char_index < len(self.full_text):
                self.display_text += self.full_text[self.char_index]
                self.char_index += 1
            else:
                # finished typing current line; wait for player input to continue
                self.waiting_for_input = True
                

    def advance(self):
        """Advance dialog: if currently typing, finish; otherwise go to next line or end."""
        # if not speaking and nothing queued, nothing to do
        if not self.is_speaking and not self.dialog_queue:
            return

        # if still typing, finish the current line and set waiting flag
        if self.char_index < len(self.full_text):
            self.display_text = self.full_text
            self.char_index = len(self.full_text)
            self.waiting_for_input = True
            return

        # if finished current line and waiting for input: either go next or end
        if self.waiting_for_input:
            if self.dialog_queue:
                self._start_next()
            else:
                # no more lines: end speaking
                self.is_speaking = False
                self.waiting_for_input = False
        else:
            # fallback: start next if available
            self._start_next()

    def draw_dialog(self, surface, font, screen_size):
        """Draw dialog box with portrait and current typed text."""
        if not self.is_speaking:
            return
        sw, sh = screen_size

        # make dialog box slightly narrower than full width to avoid covering edges
        box_w = int(sw * 0.8)
        # compute available width for text after portrait
        px = 12
        portrait_w = self.portrait.get_width() if self.portrait else 0
        text_x = px + (portrait_w + 10 if portrait_w else 0)
        text_available = box_w - text_x - 20

        # wrap text into lines according to available width
        words = self.display_text.split(' ')
        lines = []
        cur = ''
        for w in words:
            test = (cur + ' ' + w).strip()
            try:
                txt_surf = font.render(test, True, (255, 255, 255))
                if txt_surf.get_width() > text_available:
                    if cur:
                        lines.append(cur)
                    cur = w
                else:
                    cur = test
            except Exception:
                # fallback: naive wrap
                if len(test) * 8 > text_available:
                    if cur:
                        lines.append(cur)
                    cur = w
                else:
                    cur = test
        if cur:
            lines.append(cur)

        # include name as one line above text if present
        name_lines = []
        if self.name:
            name_lines = [self.name]

        # compute box height dynamically: padding + name + text lines + portrait height
        line_h = font.get_height() + 4
        text_lines_count = max(len(lines), 1)
        content_h = (len(name_lines) * line_h) + (text_lines_count * line_h)
        portrait_h = self.portrait.get_height() if self.portrait else 0
        inner_h = max(content_h, portrait_h)
        box_h = inner_h + 24

        # ensure box not too tall for screen
        max_box_h = int(sh * 0.45)
        if box_h > max_box_h:
            box_h = max_box_h

        # position box centered horizontally, slightly above bottom
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((20, 20, 20, 230))

        # blit portrait on left if exists
        if self.portrait:
            try:
                portrait_y = 12
                box.blit(self.portrait, (px, portrait_y))
            except Exception:
                pass

        # blit name then text lines
        ty = 12
        try:
            if self.name:
                name_surf = font.render(self.name, True, (220, 200, 60))
                box.blit(name_surf, (text_x, ty))
                ty += name_surf.get_height() + 6
        except Exception:
            pass

        for i, line in enumerate(lines):
            if ty + font.get_height() > box_h - 20:
                break
            txt = font.render(line, True, (255, 255, 255))
            box.blit(txt, (text_x, ty))
            ty += txt.get_height() + 4

        # final position and blit to screen
        bx = (sw - box_w) // 2
        by = sh - box_h - 20
        try:
            surface.blit(box, (bx, by))
        except Exception:
            surface.blit(box, (20, by))

        # draw "press Enter" prompt when waiting for input placed inside box bottom-right
        if self.waiting_for_input:
            try:
                prompt = font.render("Nhấn Enter để tiếp tục", True, (180, 180, 180))
                px_prompt = bx + box_w - prompt.get_width() - 12
                py_prompt = by + box_h - prompt.get_height() - 8
                surface.blit(prompt, (px_prompt, py_prompt))
            except Exception:
                pass

    # ---- higher-level scripted dialogs ----
    def start_initial_tutorial(self, typing_delay=2):
        lines = [
            "Hôm nay lại có chiến binh đến huấn luyện? Hãy cố gắng luyện tập sau đó ra chiến trường Nếu chúng ta thất bại, Trái Đất sẽ không còn cơ hội thứ hai.",
            "Những sinh vật kia từng là động vật bình thường… ô nhiễm đã biến chúng thành quái vật. Mỗi con quái vật bị tiêu diệt là môi trường được thanh lọc thêm một chút.",
            "Điều khiển nhân vật của bạn bằng phím WASD hoặc phím mũi tên. Nhấp chuột vào màn hình để bắn đạn! Nhưng nhớ rằng bạn chỉ bắn được 15 viên liên tục thôi, sau đó phải nạp đạn — hãy cẩn thận trong những tình huống nguy hiểm!",
            "Bây giờ, hãy bắn thử đạn đi!"
        ]
        self.start_dialog(lines, typing_delay=typing_delay)

    def start_followup_after_reload(self, typing_delay=2):
        lines = [
           
            "Luôn nhớ rằng bạn chỉ có 100hp mà thôi, khi hết hp thì bạn sẽ gặp nguy hiểm!.",
            "Quân cứu trợ có đặt bình thuốc trên chiến trường, hãy nhặt nó bạn sẽ có thêm cơ hội sống!."
        ]
        self.start_dialog(lines, typing_delay=typing_delay)

    def start_training_intro(self, typing_delay=2):
        lines = [
            "Bây giờ thể hiện những gì bạn có đi!",
            "Hãy tiêu diệt hết tất cả bọn quái vật này để chứng minh bạn đủ sức để giải cứu thế giới tan hoang này!"
        ]
        self.start_dialog(lines, typing_delay=typing_delay)

    def start_training_end(self, typing_delay=2):
        lines = ["bạn đã hoàn thành huấn luyện cơ bản rồi đấy, hãy cẩn thận nhé người anh em, chúng ta sẽ còn gặp lại!"]
        self.start_dialog(lines, typing_delay=typing_delay)

    def is_busy(self):
        return getattr(self, 'is_speaking', False) or getattr(self, 'waiting_for_input', False) or bool(self.dialog_queue)
