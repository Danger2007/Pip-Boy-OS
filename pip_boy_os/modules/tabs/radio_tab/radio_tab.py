import random
import time
import pygame
from datetime import datetime
from threading import Thread
import settings
import os
from util_functs import Utils
from .radio_station_loader import RadioStationLoader
from .playlist_manager import PlaylistManager
from .visualizer import Visualizer
# Should add FM radio connection
class NVRadioList:
    def __init__(self, draw_space, font):
        self.draw_space = draw_space
        self.font = font
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_count = 8
    def set_items(self, items):
        self.items = items
        self.selected_index = max(0, min(self.selected_index, len(items) - 1))

    def change_selection(self, direction):
        if not self.items:
            return
        if direction:
            self.selected_index = max(0, self.selected_index - 1)
        else:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_index - self.visible_count + 1
    def render(self, screen, active_station_index, station_playing):
        if not self.items:
            return
        vsbl_tms = self.items[self.scroll_offset:self.scroll_offset + self.visible_count]
        tm_hght = 24
        for i, tm_txt in enumerate(vsbl_tms):
            ctl_ndx = self.scroll_offset + i
            is_slctd = ctl_ndx == self.selected_index
            is_ctv = ctl_ndx == active_station_index and station_playing
            tm_rct = pygame.Rect(self.draw_space.left, self.draw_space.top + settings.LIST_TOP_MARGIN + i * tm_hght, self.draw_space.width, tm_hght - 4)
            if is_slctd:
                pygame.draw.rect(screen, settings.PIP_BOY_LIGHT, tm_rct, 1)
            sq_sz = 6
            sq_x = tm_rct.left + 8
            sq_y = tm_rct.centery - sq_sz // 2
            if is_ctv:
                sq_rct = pygame.Rect(sq_x, sq_y, sq_sz, sq_sz)
                pygame.draw.rect(screen, settings.PIP_BOY_LIGHT, sq_rct)
            txt_x = tm_rct.left + 22
            txt_y = tm_rct.centery - self.font.get_height() // 2
            txt_clr = settings.PIP_BOY_LIGHT
            txt_srf = self.font.render(tm_txt, True, txt_clr)
            screen.blit(txt_srf, (txt_x, txt_y))

class F4RadioList:

    def __init__(self, draw_space, font):
        self.draw_space = draw_space
        self.font = font
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_count = 8
    def set_items(self, items):
        self.items = items
        self.selected_index = max(0, min(self.selected_index, len(items) - 1))
    def change_selection(self, direction):
        if not self.items:
            return
        if direction:
            self.selected_index = max(0, self.selected_index - 1)
        else:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_index - self.visible_count + 1

    def render(self, screen, active_station_index, station_playing):
        if not self.items:
            return
        vsbl_tms = self.items[self.scroll_offset:self.scroll_offset + self.visible_count]
        tm_hght = 24
        for i, tm_txt in enumerate(vsbl_tms):
            ctl_ndx = self.scroll_offset + i
            is_slctd = ctl_ndx == self.selected_index
            is_ctv = ctl_ndx == active_station_index and station_playing
            tm_rct = pygame.Rect(self.draw_space.left, self.draw_space.top + settings.LIST_TOP_MARGIN + i * tm_hght, self.draw_space.width, tm_hght - 4)
            if is_slctd:
                pygame.draw.rect(screen, settings.PIP_BOY_LIGHT, tm_rct)
                txt_clr = settings.BACKGROUND
                sqr_clr = settings.BACKGROUND
            else:
                txt_clr = settings.PIP_BOY_LIGHT
                sqr_clr = settings.PIP_BOY_LIGHT
            if is_ctv:
                sq_sz = 6
                sq_x = tm_rct.left + 4
                sq_y = tm_rct.centery - sq_sz // 2
                sq_rct = pygame.Rect(sq_x, sq_y, sq_sz, sq_sz)
                pygame.draw.rect(screen, sqr_clr, sq_rct)
            txt_x = tm_rct.left + 16
            txt_y = tm_rct.centery - self.font.get_height() // 2
            txt_srf = self.font.render(tm_txt, True, txt_clr)
            screen.blit(txt_srf, (txt_x, txt_y))
class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.date = Utils.get_date()
        self.time = Utils.get_time()
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self._init_footer_text())
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        ui_stl = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        self.is_nv = ui_stl in ('fallout_nv', 'fallout_new_vegas')
        lst_lft = self.draw_space.left + settings.TAB_SIDE_MARGIN + (5 if self.is_nv else 0)
        lst_drw_spc = pygame.Rect(lst_lft, self.draw_space.top, self.draw_space.width // 2 - settings.TAB_SIDE_MARGIN, self.draw_space.height)
        if self.is_nv:
            self.station_list = NVRadioList(lst_drw_spc, self.main_font)
        else:
            self.station_list = F4RadioList(lst_drw_spc, self.main_font)
        self.station_playing = False
        self.active_station_index = None
        self.previous_station_index = None
        self.current_song = None
        self.radio_music_thread_running = True
        self.stations_loaded = False
        self.pending_station_names = []
        rd_tp = getattr(settings, 'RADIO_TYPE', 'FILES').upper()
        if rd_tp == 'FILES':
            if self.is_nv:
                sounds_dir = os.path.dirname(settings.RADIO_BASE_FOLDER)
                rd_fldr = os.path.join(sounds_dir, 'Radio NV')
            else:
                rd_fldr = settings.RADIO_BASE_FOLDER
        elif rd_tp == 'FM':
            rd_fldr = settings.RADIO_BASE_FOLDER
        else:
            rd_fldr = settings.RADIO_BASE_FOLDER
        self.loader = RadioStationLoader(rd_fldr, settings.DCR_INTERMISSIONS_BASE_FOLDER)
        self.playlist_manager = PlaylistManager()
        self.visualizer = Visualizer(self.draw_space, self.screen, self)
        self.footer_time_thread = Thread(target=self.update_footer_time, daemon=True)
        self.footer_time_thread.start()
        Thread(target=self.load_radio_stations, daemon=True).start()
        Thread(target=self.update_radio_music, daemon=True).start()

    def _blit_footer_time(self):
        """# fix temporaneo per evitare crash"""
        tm_srfc = self.tab_instance.footer_font.render(self.time, True, settings.PIP_BOY_LIGHT)
        self.tab_instance.update_footer(self, tm_srfc, (settings.SCREEN_WIDTH // 4 + 4, 2))

    def update_footer_time(self):
        while True:
            self.time = Utils.get_time()
            self.date = Utils.get_date()
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self._init_footer_text())
            self._blit_footer_time()
            now = datetime.now()
            wt_tm = 60 - now.second
            pygame.time.wait(wt_tm * 1000)
    def _init_footer_text(self):
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        dt_srfc = self.tab_instance.footer_font.render(self.date, True, settings.PIP_BOY_LIGHT)
        lctn_srfc = self.tab_instance.footer_font.render(settings.FAKE_LOCATION if getattr(settings, 'GAME_ACCURATE_MODE', False) else getattr(settings, 'REAL_LOCATION', ''), True, settings.PIP_BOY_LIGHT)
        ftr_srfc.blit(dt_srfc, (2, 2))
        ftr_srfc.blit(lctn_srfc, (settings.SCREEN_WIDTH - lctn_srfc.get_width() - 2, 2))
        return ftr_srfc

    def load_radio_stations(self):
        rd_tp = getattr(settings, 'RADIO_TYPE', 'FILES').upper()
        if rd_tp == 'FILES':
            self.loader.load_radio_stations()
        elif rd_tp == 'FM':
            pass
        self.pending_station_names = list(self.loader.radio_stations.keys())
        self.stations_loaded = True
    def play_station_switch_sound(self):
        if os.path.exists(settings.RADIO_STATIC_BURSTS_BASE_FOLDER):
            snds = os.listdir(settings.RADIO_STATIC_BURSTS_BASE_FOLDER)
            if snds:
                snd = random.choice(snds)
                Utils.play_sfx(os.path.join(settings.RADIO_STATIC_BURSTS_BASE_FOLDER, snd), settings.VOLUME)

    def scroll(self, direction):
        self.station_list.change_selection(direction)
    def handle_input(self, event):
        vnt_tp = getattr(event, 'type', None)
        key = getattr(event, 'key', None)
        if vnt_tp == pygame.KEYDOWN:
            if key in (pygame.K_UP, pygame.K_w):
                self.scroll(True)
                return True
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.scroll(False)
                return True
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self.select_station()
                return True
        return False
    def select_station(self):
        if self.station_list.selected_index == self.active_station_index:
            self.station_playing = not self.station_playing
        else:
            self.station_playing = True
        if not self.station_playing:
            Utils.play_sfx(settings.RADIO_TURN_OFF_SOUND)
        else:
            self.play_station_switch_sound()
        self.active_station_index = self.station_list.selected_index

    def update_radio_music(self):
        while self.radio_music_thread_running:
            if self.active_station_index is not None and self.station_playing and self.loader.radio_stations:
                sttn_nms = list(self.loader.radio_stations.keys())
                if self.active_station_index >= len(sttn_nms):
                    pygame.time.wait(1000)
                    continue
                sttn_nm = sttn_nms[self.active_station_index]
                sttn = self.loader.radio_stations[sttn_nm]
                if sttn_nm not in self.playlist_manager.station_playlists:
                    self.playlist_manager.station_playlists[sttn_nm] = {'playlist': self.playlist_manager.generate_station_playlist_for_station(sttn, sttn_nm), 'index': 0, 'song_start_time': None, 'initialized': False}
                pllst_dt = self.playlist_manager.station_playlists[sttn_nm]
                pllst = pllst_dt['playlist']
                idx = pllst_dt['index']
                if idx >= len(pllst):
                    pllst_dt['playlist'] = self.playlist_manager.generate_station_playlist_for_station(sttn, sttn_nm)
                    pllst_dt['index'] = 0
                    pllst_dt['song_start_time'] = None
                    pllst_dt['initialized'] = False
                    idx = 0
                    pllst = pllst_dt['playlist']
                if not pllst:
                    pygame.time.wait(1000)
                    continue
                current_song = pllst[idx]
                if settings.DCR_INTERMISSIONS_BASE_FOLDER in current_song:
                    drtn_ms = self.loader.intermissions.get(current_song, 0)
                else:
                    drtn_ms = sttn['music_files'].get(current_song, 0)
                drtn_sc = drtn_ms / 1000.0
                if pllst_dt['song_start_time'] is None:
                    if not pllst_dt['initialized']:
                        rndm_ffst = random.uniform(0, max(0, drtn_sc - 1))
                        pllst_dt['song_start_time'] = time.time() - rndm_ffst
                        pllst_dt['initialized'] = True
                    else:
                        pllst_dt['song_start_time'] = time.time()
                sng_ffst = time.time() - pllst_dt['song_start_time']
                if sng_ffst < drtn_sc:
                    if self.current_song != current_song:
                        try:
                            pygame.mixer.music.load(current_song)
                            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
                            pygame.mixer.music.play(start=sng_ffst)
                            self.current_song = current_song
                        except Exception as e:
                            print(f'Error playing {current_song}: {e}')
                            pllst_dt['index'] += 1
                            pllst_dt['song_start_time'] = None
                            self.current_song = None
                    elif not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(start=sng_ffst)
                else:
                    pllst_dt['index'] += 1
                    pllst_dt['song_start_time'] = None
                    self.current_song = None
                    pygame.mixer.music.stop()
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                self.current_song = None
            wt_tm = 300 if self.active_station_index is not None else 1000
            pygame.time.wait(wt_tm)

    def handle_threads(self, tab_selected):
        if tab_selected:
            self.visualizer.start()
        else:
            self.visualizer.stop()
    def render_visualizer_waves(self):
        self.visualizer.render()
    def render(self):
        if self.stations_loaded and self.pending_station_names:
            if hasattr(self.station_list, 'set_items'):
                self.station_list.set_items(self.pending_station_names)
            else:
                self.station_list.items = self.pending_station_names
            if hasattr(self.station_list, 'update_list'):
                self.station_list.update_list()
            elif hasattr(self.station_list, 'refresh'):
                self.station_list.refresh()
            self.pending_station_names = []
        self.tab_instance.render_footer(self)
        self.station_list.render(self.screen, self.active_station_index, self.station_playing)
        self.render_visualizer_waves()