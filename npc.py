import pygame
from maps.map_manager import TILE_SIZE


class NPC(pygame.sprite.Sprite):
    def __init__(self, tile_pos, tile_folder="npc"):
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
        box_h = 120
        box_w = sw - 40
        box = pygame.Surface((box_w, box_h))
        box.fill((20, 20, 20))
        box.set_alpha(230)

        # portrait
        px = 10
        if self.portrait:
            box.blit(self.portrait, (px, 10))
            text_x = px + self.portrait.get_width() + 10
        else:
            text_x = px + 10

        # render text (wrap if necessary)
        lines = []
        words = self.display_text.split(' ')
        cur = ''
        for w in words:
            test = (cur + ' ' + w).strip()
            txt_surf = font.render(test, True, (255, 255, 255))
            if txt_surf.get_width() > box_w - text_x - 20:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)

        # blit text lines
        ty = 10
        for line in lines[:4]:
            txt = font.render(line, True, (255, 255, 255))
            box.blit(txt, (text_x, ty))
            ty += txt.get_height() + 4

        # position box at bottom
        surface.blit(box, (20, sh - box_h - 20))

    # ---- higher-level scripted dialogs ----
    def start_initial_tutorial(self, typing_delay=2):
        lines = [
            "Hôm nay lại có một chiến binh đến huấn luyện à!",
            "Điều khiển nhân vật của bạn bằng phím WASD hoặc phím mũi tên. Nhấp chuột vào màn hình để bắn đạn! Nhưng nhớ rằng bạn chỉ bắn được 15 viên liên tục thôi, sau đó phải nạp đạn — hãy cẩn thận trong những tình huống nguy hiểm!"
        ]
        self.start_dialog(lines, typing_delay=typing_delay)

    def start_followup_after_reload(self, typing_delay=2):
        lines = [
            "làm tốt lắm chiến binh!",
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
