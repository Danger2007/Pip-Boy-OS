import sys
import pygame
from queue import Queue
from threading import Lock
class InputManager:

    def __init__(self):
        self.key_queue = Queue()
        self.get_key_lock = Lock()
        self.pressed_key_event = None
        self.key_press_time = 0
        self.last_repeat_time = 0
        self.is_holding = False
        self.hold_delay = 350
        self.hold_interval = 45
    def handle_keyboard(self, event):
        if event.type == pygame.KEYDOWN:
            now = pygame.time.get_ticks()
            self.pressed_key_event = event
            self.key_press_time = now
            self.last_repeat_time = now
            self.is_holding = False
            self.key_queue.put(event)
        elif event.type == pygame.KEYUP:
            if self.pressed_key_event and event.key == self.pressed_key_event.key:
                self.pressed_key_event = None
                self.is_holding = False
            self.key_queue.put(event)

    def update_key_repeat(self):
        if not self.pressed_key_event:
            return
        ks_stt = pygame.key.get_pressed()
        if not ks_stt[self.pressed_key_event.key]:
            self.pressed_key_event = None
            self.is_holding = False
            return
        now = pygame.time.get_ticks()
        if not self.is_holding:
            if now - self.key_press_time >= self.hold_delay:
                self.is_holding = True
                self.last_repeat_time = now
                self.key_queue.put(self.pressed_key_event)
        elif now - self.last_repeat_time >= self.hold_interval:
            self.last_repeat_time = now
            self.key_queue.put(self.pressed_key_event)
    def handle_quit(self, event, tab_manager=None):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            if tab_manager and hasattr(tab_manager, 'tab_thread_handler'):
                for tab in tab_manager.tab_thread_handler.tab_map.values():
                    if hasattr(tab, 'handle_threads'):
                        try:
                            tab.handle_threads(False)
                        except:
                            pass
            try:
                pygame.quit()
            except:
                pass
            sys.exit()

    def handle_input(self, tab_manager): # Initializes inputs, you should kmow that
        self.update_key_repeat()
        with self.get_key_lock:
            while not self.key_queue.empty():
                event = self.key_queue.get()
                key = event.key if hasattr(event, 'key') else event
                if getattr(tab_manager, 'screensaver_active', False):
                    tab_manager.screensaver_active = False
                    tab_manager.reset_activity()
                    continue
                if hasattr(tab_manager, 'reset_activity'):
                    tab_manager.reset_activity()
                ctv_sbtb = tab_manager.get_active_subtab()
                trgt_sbtb = ctv_sbtb
                if ctv_sbtb and getattr(ctv_sbtb, 'mode', None) == 'SETTINGS' and hasattr(ctv_sbtb, 'settings_tab'):
                    trgt_sbtb = ctv_sbtb.settings_tab
                if trgt_sbtb and hasattr(trgt_sbtb, 'handle_input'):
                    if trgt_sbtb.handle_input(event):
                        continue
                if getattr(event, 'type', None) == pygame.KEYUP:
                    continue
                if trgt_sbtb and hasattr(trgt_sbtb, 'is_editing') and trgt_sbtb.is_editing():
                    match key:
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            tab_manager.select_item()
                        case pygame.K_x:
                            tab_manager.handle_x_press()
                        case pygame.K_UP:
                            if not (hasattr(trgt_sbtb, 'editing_mode') and trgt_sbtb.editing_mode is not None):
                                tab_manager.scroll_tab(True)
                        case pygame.K_DOWN:
                            if not (hasattr(trgt_sbtb, 'editing_mode') and trgt_sbtb.editing_mode is not None):
                                tab_manager.scroll_tab(False)
                        case _:
                            pass
                    continue
                match key:
                    case pygame.K_LEFT:
                        tab_manager.switch_tab(False)
                    case pygame.K_RIGHT:
                        tab_manager.switch_tab(True)
                    case pygame.K_DOWN:
                        tab_manager.scroll_tab(False)
                    case pygame.K_UP:
                        tab_manager.scroll_tab(True)
                    case pygame.K_RETURN | pygame.K_KP_ENTER:
                        tab_manager.select_item()
                    case pygame.K_a:
                        tab_manager.switch_sub_tab(False)
                    case pygame.K_d:
                        tab_manager.switch_sub_tab(True)
                    case pygame.K_x:
                        tab_manager.handle_x_press()
                    case pygame.K_j:
                        tab_manager.navigate(0)
                    case pygame.K_i:
                        tab_manager.navigate(1)
                    case pygame.K_k:
                        tab_manager.navigate(2)
                    case pygame.K_l:
                        tab_manager.navigate(3)
                    case _:
                        pass

    def run(self, tab_manager=None):
        try:
            for event in pygame.event.get():
                self.handle_keyboard(event)
                self.handle_quit(event, tab_manager)
        except pygame.error:
            return