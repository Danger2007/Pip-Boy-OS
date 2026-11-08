import os
import time
import settings
import pygame
import random
import math
import ui
from threading import Thread, Lock
from util_functs import Utils
from tabs.radio_tab.radio_tab import RadioTab
from tabs.stat_tab.stat_tab import StatTab
from tabs.inv_tab.inv_tab import InvTab
from tabs.data_tab.data_tab import DataTab
from tabs.map_tab.map_tab import MapTab
from tabs.clock_tab.clock_tab import ClockTab
from tab import Tab, ThreadHandler
class TabManager: # This is self explanatory 
    def __init__(self, screen):
        self.screen = screen
        self.ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        self.player_data = {'hp': getattr(settings, 'PLAYER_HP', 280), 'max_hp': getattr(settings, 'PLAYER_MAX_HP', 280), 'limbs': {'head': 100, 'torso': 100, 'arm_l': 100, 'arm_r': 100, 'leg_l': 100, 'leg_r': 40}, 'ap': getattr(settings, 'PLAYER_AP', 85), 'max_ap': getattr(settings, 'PLAYER_MAX_AP', 85), 'xp': getattr(settings, 'PLAYER_XP', 1880), 'next_xp': getattr(settings, 'PLAYER_NEXT_XP', 2000), 'name': getattr(settings, 'PLAYER_NAME', 'DanieleM'), 'level': getattr(settings, 'PLAYER_LEVEL', 28), 'quick_items': ['(5) Stimpak S', "(3) Doctor's Bag E"], 'status_side_index': 0}
        if self.ui_style == 'fallout_nv':
            self.tabs = ['STATS', 'ITEMS', 'DATA']
        else:
            self.tabs = settings.TABS
        self.main_tab_font = pygame.font.Font(settings.MAIN_FONT_PATH, 14)
        self.tab_font_height = self.main_tab_font.get_height()
        self.current_tab_index = 0
        self.previous_tab_index = None
        drw_spc_crds = (settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height * 2 + settings.TAB_BOTTOM_MARGIN, settings.BOTTOM_BAR_HEIGHT + settings.BOTTOM_BAR_MARGIN)
        self.draw_space = pygame.Rect(0, drw_spc_crds[0], settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - drw_spc_crds[1] - drw_spc_crds[0])
        mp_drw_spc_crds = (settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height + settings.TAB_BOTTOM_MARGIN, settings.BOTTOM_BAR_HEIGHT + settings.BOTTOM_BAR_MARGIN)
        self.map_draw_space = pygame.Rect(settings.MAP_EDGES_OFFSET, mp_drw_spc_crds[0], settings.SCREEN_WIDTH - settings.MAP_EDGES_OFFSET * 2, settings.SCREEN_HEIGHT - mp_drw_spc_crds[1] - mp_drw_spc_crds[0])
        self.tab_base = Tab(self.screen)
        self.stat_tab = StatTab(self.screen, self.tab_base, self.draw_space)
        self.inv_tab = InvTab(self.screen, self.tab_base, self.draw_space)
        self.data_tab = DataTab(self.screen, self.tab_base, self.draw_space)
        self.map_tab = MapTab(self.screen, self.tab_base, self.map_draw_space)
        self.radio_tab = RadioTab(self.screen, self.tab_base, self.draw_space)
        self.clock_tab = ClockTab(self.screen, self.tab_base, self.draw_space)
        self.last_activity_time = time.time()
        self.screensaver_active = False
        self.current_sub_tab_index = [0] * len(self.tabs)
        self.previous_sub_tab_index = [0] * len(self.tabs)
        self.tab_x_offset = []
        self.glitch_thread = None
        self.render_blur = False
        self.switch_lock = Lock()
        self.subtab_bar_surfaces = {}
        self.subtab_offsets = {}
        self.header_background = None
        self.tab_highlight_surfaces = []
        self.init_header_surfaces()
        self.init_subtab_data()
        self.tab_base.player_data = self.player_data
        tb_mp = {0: self.stat_tab, 1: self.inv_tab, 2: self.data_tab, 3: self.map_tab, 4: self.radio_tab}
        self.tab_thread_handler = ThreadHandler(tb_mp, self.current_tab_index)

    def reset_activity(self):
        self.last_activity_time = time.time()
    def render_tab(self):
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_style == 'fallout_nv':
            match self.current_tab_index:
                case 0:
                    self.stat_tab.render()
                case 1:
                    self.inv_tab.render()
                case 2:
                    sb_dx = self.current_sub_tab_index[2]
                    if sb_dx in [0, 1]:
                        self.map_tab.set_map_mode(is_local=sb_dx == 0)
                        self.map_tab.render()
                    elif sb_dx == 4:
                        self.radio_tab.render()
                    else:
                        self.data_tab.render()
        else:
            match self.current_tab_index:
                case 0:
                    self.stat_tab.render()
                case 1:
                    self.inv_tab.render()
                case 2:
                    self.data_tab.render()
                case 3:
                    self.map_tab.render()
                case 4:
                    self.radio_tab.render()
    def switch_tab_sound(self):
        if settings.SOUND_ON:
            if self.previous_tab_index is not None and self.current_tab_index > self.previous_tab_index:
                Utils.play_sfx(os.path.join(settings.ROTARY_VERTICAL_1), settings.VOLUME / 5)
            else:
                Utils.play_sfx(os.path.join(settings.ROTARY_VERTICAL_2), settings.VOLUME / 5)
            if random.randrange(100) < settings.SWITCH_SOUND_CHANCE:
                snd = random.choice(os.listdir(settings.BUZZ_SOUND_BASE_FOLDER))
                Utils.play_sfx(os.path.join(settings.BUZZ_SOUND_BASE_FOLDER, snd), settings.VOLUME / 3)
    def switch_sub_tab_sound(self):
        if settings.SOUND_ON:
            mn_dx = self.current_tab_index
            crr_sb = self.current_sub_tab_index[mn_dx]
            prv_sb = self.previous_sub_tab_index[mn_dx]
            if crr_sb > prv_sb:
                Utils.play_sfx(os.path.join(settings.ROTARY_HORIZONTAL_1), settings.VOLUME / 5)
            elif crr_sb < prv_sb:
                Utils.play_sfx(os.path.join(settings.ROTARY_HORIZONTAL_2), settings.VOLUME / 5)
            self.previous_sub_tab_index[mn_dx] = crr_sb
    def init_header_surfaces(self):
        tb_txt_srfc = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height))
        ttl_tb_wdth = sum((self.main_tab_font.size(tab)[0] for tab in self.tabs))
        tb_spcng = (settings.SCREEN_WIDTH - ttl_tb_wdth - 2 * settings.TAB_MARGIN) // (len(self.tabs) + 1)
        self.tab_x_offset.append(settings.TAB_MARGIN + tb_spcng)
        for i, tab in enumerate(self.tabs):
            txt_srfc = self.main_tab_font.render(tab, True, settings.PIP_BOY_LIGHT)
            tb_txt_srfc.blit(txt_srfc, (self.tab_x_offset[i], settings.TAB_VERTICAL_OFFSET))
            self.tab_x_offset.append(self.main_tab_font.size(tab)[0] + tb_spcng + self.tab_x_offset[i])
        self.header_background = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height + settings.TAB_SCREEN_EDGE_LENGTH + 1))
        self.header_background.fill(settings.BACKGROUND)
        self.header_background.blit(tb_txt_srfc, (0, 0))
        pygame.draw.line(self.header_background, settings.PIP_BOY_LIGHT, (0, self.tab_font_height), (settings.SCREEN_WIDTH, self.tab_font_height), 1)
        pygame.draw.line(self.header_background, settings.PIP_BOY_LIGHT, (0, settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (0, self.tab_font_height), 1)
        pygame.draw.line(self.header_background, settings.PIP_BOY_LIGHT, (settings.SCREEN_WIDTH - 1, self.tab_font_height + settings.TAB_SCREEN_EDGE_LENGTH), (settings.SCREEN_WIDTH - 1, self.tab_font_height), 1)
        for i, tab in enumerate(self.tabs):
            surf = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height + 1), pygame.SRCALPHA)
            tb_wdth = self.main_tab_font.size(tab)[0]
            x_strt = self.tab_x_offset[i] - settings.TAB_HORIZONTAL_LINE_OFFSET
            x_nd = self.tab_x_offset[i] + tb_wdth + settings.TAB_HORIZONTAL_LENGTH
            pygame.draw.line(surf, settings.BACKGROUND, (x_strt, self.tab_font_height), (x_nd, self.tab_font_height), 1)
            pygame.draw.line(surf, settings.PIP_BOY_LIGHT, (x_strt, self.tab_font_height), (x_strt, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), 1)
            pygame.draw.line(surf, settings.PIP_BOY_LIGHT, (x_nd, self.tab_font_height), (x_nd, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), 1)
            pygame.draw.line(surf, settings.PIP_BOY_LIGHT, (x_strt, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), (x_strt + settings.TAB_SCREEN_EDGE_LENGTH, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), 1)
            pygame.draw.line(surf, settings.PIP_BOY_LIGHT, (x_nd, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), (x_nd - settings.TAB_SCREEN_EDGE_LENGTH, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), 1)
            self.tab_highlight_surfaces.append(surf)

    def init_subtab_data(self):
        self.subtab_offsets = {}
        self.subtab_bar_surfaces = {}
        for tb_nm, sbtbs in settings.SUBTABS.items():
            if tb_nm not in self.tabs:
                continue
            ctv_srfcs = []
            nctv_srfcs = []
            ttl_wdths = []
            self.subtab_offsets[tb_nm] = []
            for sbtb in sbtbs:
                ctv = self.main_tab_font.render(sbtb, True, settings.PIP_BOY_LIGHT)
                nctv = self.main_tab_font.render(sbtb, True, settings.PIP_BOY_MID)
                ctv_srfcs.append(ctv)
                nctv_srfcs.append(nctv)
                ttl_wdths.append(ctv.get_width())
            cmltv_wdth = 0
            for i, width in enumerate(ttl_wdths):
                mn_tb_cntr = self.tab_x_offset[self.tabs.index(tb_nm)] + self.main_tab_font.size(tb_nm)[0] / 2
                sbtb_cntr = cmltv_wdth + width / 2
                rqrd_ffst = mn_tb_cntr - sbtb_cntr
                self.subtab_offsets[tb_nm].append(rqrd_ffst)
                cmltv_wdth += width + settings.SUBTAB_SPACING
            self.subtab_bar_surfaces[tb_nm] = []
            for ctv_dx in range(len(sbtbs)):
                surf = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height + settings.TAB_SCREEN_EDGE_LENGTH), pygame.SRCALPHA)
                crrnt_x = self.subtab_offsets[tb_nm][ctv_dx]
                for i in range(len(sbtbs)):
                    txt_srf = ctv_srfcs[i] if i == ctv_dx else nctv_srfcs[i]
                    surf.blit(txt_srf, (crrnt_x, settings.SUBTAB_VERTICAL_OFFSET))
                    crrnt_x += txt_srf.get_width() + settings.SUBTAB_SPACING
                self.subtab_bar_surfaces[tb_nm].append(surf)

    def tab_switch_glitch(self):
        for _ in range(20):
            tm_tck = pygame.time.get_ticks()
            jmp_ffst = int(20 * math.sin(tm_tck))
            self.screen.blit(self.screen, (0, -jmp_ffst))
            pygame.time.wait(settings.SPEED * 100)

    def tab_blur(self):
        scrn_cp = self.screen.copy()
        for i in range(1, 18, 6):
            blr = pygame.transform.box_blur(scrn_cp, i)
            blr.set_alpha(180)
            self.screen.blit(blr, (0, 0), special_flags=pygame.BLEND_ADD)
            self.render_blur = False
    def switch_tab(self, direction):
        ctv_sbtb = self.get_active_subtab()
        if ctv_sbtb and hasattr(ctv_sbtb, 'is_editing') and ctv_sbtb.is_editing():
            return
        with self.switch_lock:
            prv_tb_ndx = self.current_tab_index
            self.previous_tab_index = self.current_tab_index
            self.current_tab_index = max(0, min((self.current_tab_index + (1 if direction else -1)) % len(self.tabs), len(self.tabs) - 1))
        if self.ui_style == 'fallout_nv':
            if prv_tb_ndx == 0:
                self.stat_tab.handle_threads(False)
            elif prv_tb_ndx == 1:
                self.inv_tab.handle_threads(False)
            elif prv_tb_ndx == 2:
                prv_sb = self.current_sub_tab_index[2]
                if prv_sb == 4:
                    self.radio_tab.handle_threads(False)
                elif prv_sb in [0, 1]:
                    self.map_tab.handle_threads(False)
                else:
                    self.data_tab.handle_threads(False)
        elif prv_tb_ndx == 0:
            self.stat_tab.handle_threads(False)
        elif prv_tb_ndx == 1:
            self.inv_tab.handle_threads(False)
        elif prv_tb_ndx == 2:
            self.data_tab.handle_threads(False)
        elif prv_tb_ndx == 3:
            self.map_tab.handle_threads(False)
        elif prv_tb_ndx == 4:
            self.radio_tab.handle_threads(False)
        if self.ui_style == 'fallout_nv':
            if self.current_tab_index == 0:
                self.stat_tab.handle_threads(True)
            elif self.current_tab_index == 1:
                self.inv_tab.handle_threads(True)
            elif self.current_tab_index == 2:
                crr_sb = self.current_sub_tab_index[2]
                if crr_sb == 4:
                    self.radio_tab.handle_threads(True)
                elif crr_sb in [0, 1]:
                    self.map_tab.set_map_mode(is_local=crr_sb == 0)
                    self.map_tab.handle_threads(True)
                else:
                    self.data_tab.handle_threads(True)
        elif self.current_tab_index == 0:
            self.stat_tab.handle_threads(True)
        elif self.current_tab_index == 1:
            self.inv_tab.handle_threads(True)
        elif self.current_tab_index == 2:
            self.data_tab.handle_threads(True)
        elif self.current_tab_index == 3:
            self.map_tab.handle_threads(True)
        elif self.current_tab_index == 4:
            self.radio_tab.handle_threads(True)
        if random.randrange(100) < settings.GLITCH_MOVE_CHANCE and (self.glitch_thread == None or not self.glitch_thread.is_alive()):
            self.glitch_thread = Thread(target=self.tab_switch_glitch, args=())
            self.glitch_thread.start()
        else:
            self.render_blur = True
        self.tab_thread_handler.update_tab_index(self.current_tab_index)
        self.switch_tab_sound()

    def switch_sub_tab(self, direction):
        ctv_sbtb = self.get_active_subtab()
        if ctv_sbtb and hasattr(ctv_sbtb, 'is_editing') and ctv_sbtb.is_editing():
            return
        crrnt_mn_ndx = self.current_tab_index
        crrnt_sb_ndx = self.current_sub_tab_index[crrnt_mn_ndx]
        sbtbs = self.get_current_subtabs()
        if not sbtbs:
            return
        nw_ndx = crrnt_sb_ndx + (1 if direction else -1)
        nw_ndx = max(0, min(nw_ndx, len(sbtbs) - 1))
        if nw_ndx != crrnt_sb_ndx:
            self.current_sub_tab_index[crrnt_mn_ndx] = nw_ndx
            self.switch_sub_tab_sound()
            if self.ui_style == 'fallout_nv':
                if crrnt_mn_ndx == 0:
                    self.stat_tab.change_sub_tab(nw_ndx)
                elif crrnt_mn_ndx == 1:
                    self.inv_tab.change_sub_tab(nw_ndx)
                elif crrnt_mn_ndx == 2:
                    if crrnt_sb_ndx == 4:
                        self.radio_tab.handle_threads(False)
                    elif crrnt_sb_ndx in [0, 1]:
                        self.map_tab.handle_threads(False)
                    else:
                        self.data_tab.handle_threads(False)
                    if nw_ndx == 4:
                        self.radio_tab.handle_threads(True)
                    elif nw_ndx in [0, 1]:
                        self.map_tab.set_map_mode(is_local=nw_ndx == 0)
                        self.map_tab.handle_threads(True)
                    else:
                        dt_ntrnl_dx = 0 if nw_ndx == 2 else 3
                        self.data_tab.change_sub_tab(dt_ntrnl_dx)
                        self.data_tab.handle_threads(True)
            else:
                match self.current_tab_index:
                    case 0:
                        self.stat_tab.change_sub_tab(nw_ndx)
                    case 1:
                        self.inv_tab.change_sub_tab(nw_ndx)
                    case 2:
                        self.data_tab.change_sub_tab(nw_ndx)
                    case _:
                        pass
    def get_current_subtabs(self):
        if self.ui_style == 'fallout_nv':
            nv_sbtbs = {'STATS': ['STATUS', 'S.P.E.C.I.A.L.', 'SKILLS', 'PERKS', 'GENERAL'], 'ITEMS': ['WEAPONS', 'APPAREL', 'AID', 'MISC', 'AMMO'], 'DATA': ['LOCAL MAP', 'WORLD MAP', 'QUESTS', 'MISC', 'RADIO']}
            return nv_sbtbs.get(self.tabs[self.current_tab_index], [])
        return settings.SUBTABS.get(self.tabs[self.current_tab_index], [])
    def scroll_tab(self, direction):
        if self.ui_style == 'fallout_nv':
            match self.current_tab_index:
                case 0:
                    self.stat_tab.scroll(direction)
                case 1:
                    self.inv_tab.scroll(direction)
                case 2:
                    sb_dx = self.current_sub_tab_index[2]
                    if sb_dx == 4:
                        self.radio_tab.scroll(direction)
                    elif sb_dx in (0, 1):
                        self.map_tab.scroll(direction)
                    else:
                        self.data_tab.scroll(direction)
        else:
            match self.current_tab_index:
                case 0:
                    self.stat_tab.scroll(direction)
                case 1:
                    self.inv_tab.scroll(direction)
                case 2:
                    self.data_tab.scroll(direction)
                case 3:
                    self.map_tab.scroll(direction)
                case 4:
                    self.radio_tab.scroll(direction)
    def select_item(self):
        if self.ui_style == 'fallout_nv':
            match self.current_tab_index:
                case 0:
                    ctv_sbtb = self.get_active_subtab()
                    if ctv_sbtb and hasattr(ctv_sbtb, 'select_item'):
                        ctv_sbtb.select_item()
                    else:
                        self.stat_tab.select_item()
                case 1:
                    self.inv_tab.select_item()
                case 2:
                    sb_dx = self.current_sub_tab_index[2]
                    if sb_dx == 4:
                        self.radio_tab.select_station()
                    elif sb_dx in (0, 1):
                        pass
                    else:
                        ctv_sbtb = self.get_active_subtab()
                        if ctv_sbtb and hasattr(ctv_sbtb, 'select_item') and (ctv_sbtb != self.data_tab):
                            ctv_sbtb.select_item()
                        else:
                            self.data_tab.select_item()
        else:
            match self.current_tab_index:
                case 0:
                    ctv_sbtb = self.get_active_subtab()
                    if ctv_sbtb and hasattr(ctv_sbtb, 'select_item'):
                        ctv_sbtb.select_item()
                case 1:
                    self.inv_tab.select_item()
                case 2:
                    self.data_tab.select_item()
                case 3:
                    pass
                case 4:
                    self.radio_tab.select_station()
    def navigate(self, direction):
        if self.ui_style == 'fallout_nv':
            match self.current_tab_index:
                case 2:
                    sb_dx = self.current_sub_tab_index[2]
                    if sb_dx in (0, 1):
                        self.map_tab.navigate(direction)
        elif self.current_tab_index == 3:
            self.map_tab.navigate(direction)
    def render_header(self):
        self.screen.blit(self.header_background, (0, 0))
        self.screen.blit(self.tab_highlight_surfaces[self.current_tab_index], (0, 0))
    def render_footer(self, current_tab_instance=None):
        if getattr(settings, 'UI_STYLE', 'Fallout_4') == 'Fallout_NV':
            ui.draw_nv_ui(self.screen, self)
        else:
            self.draw_original_f4_footer(current_tab_instance)
    def get_current_tab_instance(self):
        match self.current_tab_index:
            case 0:
                return self.stat_tab
            case 1:
                return self.inv_tab
            case 2:
                return self.data_tab
            case 3:
                return self.map_tab
            case 4:
                return self.radio_tab
            case _:
                return self.stat_tab

    def draw_original_f4_footer(self):
        if hasattr(self, 'tab_base') and hasattr(self.tab_base, 'render_footer'):
            crrnt_tb = self.get_current_tab_instance()
            self.tab_base.render_footer(crrnt_tb)

    def render_sub_tabs(self):
        crrnt_tb = self.tabs[self.current_tab_index]
        if crrnt_tb not in self.subtab_bar_surfaces:
            return
        sbtb_ndx = self.current_sub_tab_index[self.current_tab_index]
        if sbtb_ndx >= len(self.subtab_bar_surfaces[crrnt_tb]):
            return
        surf = self.subtab_bar_surfaces[crrnt_tb][sbtb_ndx]
        self.screen.blit(surf, (0, self.tab_font_height + settings.TAB_SCREEN_EDGE_LENGTH))

    def crt_glitch_effect(self):
        gltch_srfc = self.screen.copy()
        scrn_rct = self.screen.get_rect()
        for _ in range(random.randint(1, 15)):
            slc_hght = random.randint(5, 20)
            y = random.randint(0, scrn_rct.height - slc_hght)
            x_ffst = random.randint(-20, 20)
            slc_rct = pygame.Rect(0, y, scrn_rct.width, slc_hght)
            self.screen.blit(gltch_srfc, (x_ffst, y), slc_rct)
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, scrn_rct.width)
            y = random.randint(0, scrn_rct.height)
            pygame.draw.line(self.screen, settings.PIP_BOY_LIGHT, (x, y), (x + random.randint(-2, 2), y + random.randint(-2, 2)), 1)

    def render(self):
        tmt = getattr(settings, 'SCREENSAVER_TIMEOUT', 60)
        if tmt > 0 and (not self.screensaver_active):
            if time.time() - self.last_activity_time > tmt:
                self.screensaver_active = True
        if self.screensaver_active:
            self.screen.fill(settings.BACKGROUND)
            self.clock_tab.render()
            return
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_style == 'fallout_nv':
            self.screen.fill(settings.BACKGROUND)
            ui.draw_nv_ui(screen=self.screen, player_data=self.player_data, current_tab=self.tabs[self.current_tab_index], current_subtab=self.current_sub_tab_index[self.current_tab_index])
            self.render_tab()
        else:
            self.render_header()
            self.render_sub_tabs()
            self.render_tab()
        if self.render_blur:
            self.tab_blur()
            self.render_blur = False
        if settings.RANDOM_GLITCHES and random.random() < settings.RANDOM_GLITCH_CHANCE / 100:
            self.crt_glitch_effect()
    def get_active_subtab(self):
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_style == 'fallout_nv':
            match self.current_tab_index:
                case 0:
                    if hasattr(self.stat_tab, 'get_active_subtab'):
                        ctv = self.stat_tab.get_active_subtab()
                        if ctv:
                            return ctv
                    return self.stat_tab
                case 1:
                    return self.inv_tab
                case 2:
                    sb_dx = self.current_sub_tab_index[2]
                    if sb_dx in (0, 1):
                        return self.map_tab
                    elif sb_dx == 4:
                        return self.radio_tab
                    else:
                        if hasattr(self.data_tab, 'get_active_subtab'):
                            ctv = self.data_tab.get_active_subtab()
                            if ctv:
                                return ctv
                        return self.data_tab
        else:
            match self.current_tab_index:
                case 0:
                    if hasattr(self.stat_tab, 'get_active_subtab'):
                        ctv = self.stat_tab.get_active_subtab()
                        if ctv:
                            return ctv
                    return self.stat_tab
                case 1:
                    return self.inv_tab
                case 2:
                    if hasattr(self.data_tab, 'get_active_subtab'):
                        ctv = self.data_tab.get_active_subtab()
                        if ctv:
                            return ctv
                    return self.data_tab
                case 3:
                    return self.map_tab
                case 4:
                    return self.radio_tab
        return None
    def toggle_focus(self): # X use in data
        ctv_sbtb = self.get_active_subtab()
        if ctv_sbtb and hasattr(ctv_sbtb, 'toggle_focus'):
            ctv_sbtb.toggle_focus()

    def handle_x_press(self):
        ctv_sbtb = self.get_active_subtab()
        if not ctv_sbtb:
            return
        if hasattr(ctv_sbtb, 'handle_x_press'):
            ctv_sbtb.handle_x_press()
        elif getattr(ctv_sbtb, 'mode', None) == 'SETTINGS' and hasattr(ctv_sbtb, 'settings_tab'):
            ctv_sbtb.settings_tab.handle_x_press()
        elif hasattr(ctv_sbtb, 'toggle_focus'):
            ctv_sbtb.toggle_focus()