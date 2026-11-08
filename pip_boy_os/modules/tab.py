import datetime
import os
import pygame
import settings
try:
    import user_config
except:
    user_config = None
from threading import Thread
from typing import Callable, Dict, Optional

class ThreadHandler:
    def __init__(self, tab_map, initial_tab_index=None):
        self.tab_map = tab_map
        self.current_tab_index = initial_tab_index
        self.previous_tab_index = None
        self.handle_current_tab()

    def update_tab_index(self, new_index):
        self.previous_tab_index = self.current_tab_index
        self.current_tab_index = new_index
        if self.current_tab_index != self.previous_tab_index:
            self.handle_current_tab()
            self.handle_previous_tab()
    def _start_thread(self, tab_index, flag):
        tab = self.tab_map.get(tab_index)
        if tab:
            fnc = getattr(tab, f'handle_threads', None)
            if fnc and callable(fnc):
                Thread(target=fnc, args=(flag,)).start()
    def handle_current_tab(self):
        if self.current_tab_index is not None:
            self._start_thread(self.current_tab_index, True)

    def handle_previous_tab(self):
        if self.previous_tab_index is not None:
            self._start_thread(self.previous_tab_index, False)
class Tab:

    def __init__(self, screen):
        self.footer_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 12)
        self.screen = screen
        now = datetime.datetime.now()# smart date system (from games or irl)
        self.current_date = now.strftime('%d.%m.')
        dt_md = getattr(user_config, 'DATE_MODE', None) if user_config else None
        if dt_md is None:
            dt_md = getattr(settings, 'DATE_MODE', 'Game')
        ui_stl = getattr(user_config, 'UI_STYLE', None) if user_config else None
        if ui_stl is None:
            ui_stl = getattr(settings, 'UI_STYLE', '')
        ui_stl = str(ui_stl).lower()
        if dt_md == 'Real':
            self.current_year = now.strftime('%Y')
        elif dt_md == 'Game':
            if ui_stl == 'fallout_nv':
                self.current_year = '2281'
            else:
                self.current_year = '2287'
        else: # fallback just in case
            self.current_year = now.strftime('%Y')
        self.tab_footers = {}
    def init_footer(self, object, margins=None, text_surface=None):
        key = object
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT))
        ftr_srfc.fill(settings.PIP_BOY_DARK)
        if margins is not None:
            line = 0
            for mgn in margins:
                line += mgn - settings.BOTTOM_BAR_VERTICAL_MARGINS // 2
                pygame.draw.line(ftr_srfc, settings.BACKGROUND, (line, 0), (line, settings.BOTTOM_BAR_HEIGHT), settings.BOTTOM_BAR_VERTICAL_MARGINS)
        if text_surface is not None:
            if isinstance(text_surface, (list, tuple)):
                for tm in text_surface:
                    if isinstance(tm, (list, tuple)) and len(tm) == 2:
                        ftr_srfc.blit(tm[0], tm[1])
                    elif isinstance(tm, pygame.Surface):
                        ftr_srfc.blit(tm, (0, 0))
            else:
                ftr_srfc.blit(text_surface, (0, 0))
        self.tab_footers[key] = ftr_srfc

    def update_footer(self, object, text_surface, destination=(0, 0)):
        self.tab_footers[object].fill(settings.PIP_BOY_DARK, (destination[0], destination[1], text_surface.get_width(), text_surface.get_height()))
        self.tab_footers[object].blit(text_surface, destination)

    def render_footer(self, object):
        if str(getattr(settings, 'UI_STYLE', '')).lower() == 'fallout_nv':
            return
        self.screen.blit(self.tab_footers[object], (0, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT))