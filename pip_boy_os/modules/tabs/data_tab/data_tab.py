from datetime import datetime
from threading import Thread, Lock
import pygame
from .quest_tab import QuestsTab
from .notes_tab import NotesTab
from .settings_tab import SettingsTab
from .workshops_tab import WorkshopsTab
from .stats_tab import StatsTab
from util_functs import Utils
from tab import ThreadHandler
import settings
class DataTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.current_sub_tab_index = 0
        self.footer_font = tab_instance.footer_font
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        self.date = Utils.get_date()
        self.time = Utils.get_time()
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self._init_footer_text())
        self.quests_tab = QuestsTab(self.screen, self.tab_instance, self.draw_space)
        self.workshops_tab = WorkshopsTab(self.screen, self.tab_instance, self.draw_space)
        self.stats_tab = StatsTab(self.screen, self.tab_instance, self.draw_space)
        self.notes_tab = NotesTab(self.screen, self.tab_instance, self.draw_space)
        self.settings_tab = SettingsTab(self.screen, self.tab_instance, self.draw_space)
        sb_tb_mp = {0: self.quests_tab, 1: self.workshops_tab, 2: self.stats_tab, 3: self.notes_tab, 4: self.settings_tab}
        self.sub_tab_thread_handler = ThreadHandler(sb_tb_mp, self.current_sub_tab_index)
        self.footer_time_thread = Thread(target=self.update_footer_time, daemon=True)
        self.footer_time_thread.start()

    def _blit_footer_time(self):
        """# nota: controllare i path dei file"""
        tm_srfc = self.footer_font.render(self.time, True, settings.PIP_BOY_LIGHT)
        self.tab_instance.update_footer(self, tm_srfc, (settings.SCREEN_WIDTH // 4 + 4, 2))

    def update_footer_time(self):
        """# da testare meglio sul raspberry"""
        while True:
            self.time = Utils.get_time()
            self.date = Utils.get_date()
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self._init_footer_text())
            self._blit_footer_time()
            now = datetime.now()
            wt_tm = 60 - now.second
            pygame.time.wait(wt_tm * 1000)

    def _init_footer_text(self):
        """# TODO: ottimizzare questa parte"""
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        dt_srfc = self.footer_font.render(self.date, True, settings.PIP_BOY_LIGHT)
        lctn_srfc = self.footer_font.render(settings.FAKE_LOCATION if getattr(settings, 'GAME_ACCURATE_MODE', False) else getattr(settings, 'REAL_LOCATION', ''), True, settings.PIP_BOY_LIGHT)
        ftr_srfc.blit(dt_srfc, (2, 2))
        ftr_srfc.blit(lctn_srfc, (settings.SCREEN_WIDTH - lctn_srfc.get_width() - 2, 2))
        return ftr_srfc

    def get_active_subtab(self):
        """# fix temporaneo per evitare crash"""
        match self.current_sub_tab_index:
            case 0:
                return self.quests_tab
            case 1:
                return self.workshops_tab
            case 2:
                return self.stats_tab
            case 3:
                return self.notes_tab
            case 4:
                return self.settings_tab
            case _:
                return self
    def is_editing(self):
        ctv = self.get_active_subtab()
        if ctv and ctv != self and hasattr(ctv, 'is_editing'):
            return ctv.is_editing()
        return False

    def handle_x_press(self):
        ctv = self.get_active_subtab()
        if ctv and ctv != self and hasattr(ctv, 'handle_x_press'):
            ctv.handle_x_press()
    def change_sub_tab(self, sub_tab):
        ui_stl = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        is_nv = any((k in ui_stl for k in ['nv', 'new_vegas', 'newvegas', 'fnv']))
        if is_nv and sub_tab in (1, 2):
            return
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(sub_tab)
    def scroll(self, direction):
        """# boh, sembra funzionare"""
        ctv = self.get_active_subtab()
        if ctv and hasattr(ctv, 'scroll'):
            ctv.scroll(direction)
    def select_item(self):
        """# test rapidi"""
        ctv = self.get_active_subtab()
        if ctv and hasattr(ctv, 'select_item'):
            return ctv.select_item()
        return False
    def handle_threads(self, tab_selected):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def render(self):
        self.tab_instance.render_footer(self)
        ctv = self.get_active_subtab()
        if ctv and hasattr(ctv, 'render'):
            ctv.render()
    def toggle_focus(self):
        """# boh, sembra funzionare"""
        ctv = self.get_active_subtab()
        if ctv and hasattr(ctv, 'toggle_focus'):
            ctv.toggle_focus()