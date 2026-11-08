import os
from threading import Thread, Lock
import pygame
import settings
from tab import ThreadHandler
from .world_tab import WorldMap, RealMap
from datetime import datetime
from util_functs import Utils

class MapTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        ui_stl = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        if ui_stl in ('fallout_nv', 'fallout_new_vegas'):
            tp_mrgn = getattr(settings, 'TOP_BAR_HEIGHT', 35)
            bttm_mrgn = 30
            self.draw_space = pygame.Rect(draw_space.x, tp_mrgn, draw_space.width, settings.SCREEN_HEIGHT - tp_mrgn - bttm_mrgn)
        else:
            self.draw_space = draw_space
        self.current_sub_tab_index = 0
        self.footer_font = tab_instance.footer_font
        self.date = Utils.get_date()
        self.time = Utils.get_time()
        if getattr(settings, 'REAL_MAP', False):
            self.world_map_subtab = RealMap(self.screen, self.draw_space, settings.MAP_ZOOM)
        else:
            self.world_map_subtab = WorldMap(self.screen, self.draw_space)
        initial_zoom = 1.0
        if hasattr(self.world_map_subtab, 'zoom_level'):
            initial_zoom = self.world_map_subtab.zoom_level
        elif hasattr(self.world_map_subtab, 'map_zoom'):
            initial_zoom = self.world_map_subtab.map_zoom
        self.world_zoom = initial_zoom
        self.local_zoom = 2.2
        self.is_local_map = None
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self._init_footer_text())
        sb_tb_mp = {0: self.world_map_subtab}
        self.footer_time_thread = Thread(target=self.update_footer_time, daemon=True)
        self.sub_tab_thread_handler = ThreadHandler(sb_tb_mp, self.current_sub_tab_index)
        self.datetime_lock = Lock()
        self.footer_time_thread.start()

    def _get_current_zoom(self):
        if hasattr(self.world_map_subtab, 'zoom_level'):
            return self.world_map_subtab.zoom_level
        elif hasattr(self.world_map_subtab, 'map_zoom'):
            return self.world_map_subtab.map_zoom
        return self.local_zoom if self.is_local_map else self.world_zoom
    def _apply_zoom(self, target_zoom): # Rework zoom in the future
        if hasattr(self.world_map_subtab, 'set_zoom') and callable(getattr(self.world_map_subtab, 'set_zoom')):
            self.world_map_subtab.set_zoom(target_zoom)
        elif hasattr(self.world_map_subtab, 'zoom_level'):
            self.world_map_subtab.zoom_level = target_zoom
        elif hasattr(self.world_map_subtab, 'map_zoom'):
            self.world_map_subtab.map_zoom = target_zoom

    def set_map_mode(self, is_local):
        if self.is_local_map == is_local:
            return
        if self.is_local_map is not None:
            crrnt_zm = self._get_current_zoom()
            if self.is_local_map:
                self.local_zoom = crrnt_zm
            else:
                self.world_zoom = crrnt_zm
        self.is_local_map = is_local
        target_zoom = self.local_zoom if is_local else self.world_zoom
        self._apply_zoom(target_zoom)

    def _blit_footer_time(self):
        tm_srfc = self.footer_font.render(self.time, True, settings.PIP_BOY_LIGHT)
        self.tab_instance.update_footer(self, tm_srfc, (settings.SCREEN_WIDTH // 4 + 4, 2))
    def _init_footer_text(self):
        dt_srfc = self.footer_font.render(self.date, True, settings.PIP_BOY_LIGHT)
        lctn_srfc = self.footer_font.render(settings.FAKE_LOCATION if settings.GAME_ACCURATE_MODE else settings.REAL_LOCATION, True, settings.PIP_BOY_LIGHT)
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        ftr_srfc.blit(dt_srfc, (2, 2))
        ftr_srfc.blit(lctn_srfc, (settings.SCREEN_WIDTH - lctn_srfc.width - 2, 2))
        return ftr_srfc
    def change_sub_tab(self, sub_tab):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def scroll(self, direction):
        if self.world_map_subtab.is_initialized:
            self.world_map_subtab.zoom(direction)
            nw_zm = self._get_current_zoom()
            if self.is_local_map:
                self.local_zoom = nw_zm
            else:
                self.world_zoom = nw_zm
    def update_footer_time(self):
        while True:
            self.time = Utils.get_time()
            self.date = Utils.get_date()
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self._init_footer_text())
            self._blit_footer_time()
            now = datetime.now()
            wt_tm = 60 - now.second
            pygame.time.wait(wt_tm * 1000)

    def navigate(self, direction):
        if self.world_map_subtab.is_initialized:
            self.world_map_subtab.navigate(direction)
    def handle_threads(self, tab_selected):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)
    def render(self):
        self.tab_instance.render_footer(self)
        match self.current_sub_tab_index:
            case 0:
                if self.world_map_subtab.is_initialized:
                    self.world_map_subtab.render()