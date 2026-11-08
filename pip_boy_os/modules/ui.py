from threading import Thread, Event, Lock
import pygame
import settings
from util_functs import Utils
from cpp import wireframe
import os
import math
import random
VAULTBOY_CACHE = {} # Please do NOT modify the values if the image is not changed
PART_CONFIG = {'torso_ok': ((48, 54), (+1, -1)), 'torso_crippled': ((48, 54), (+1, -1)), 'head_ok': ((42, 42), (+3, -49)), 'head_crippled': ((42, 42), (+3, -49)), 'face_1': ((23, 28), (-2, -43)), 'face_2': ((23, 28), (-2, -43)), 'face_3': ((23, 28), (-2, -43)), 'face_4': ((23, 28), (-2, -43)), 'face_5': ((23, 28), (-2, -43)), 'arm_r_ok': ((60, 30), (-47, -16)), 'arm_r_crippled': ((60, 30), (-47, -16)), 'arm_l_ok': ((60, 30), (+50, -17)), 'arm_l_crippled': ((60, 30), (+50, -17)), 'leg_r_ok': ((38, 52), (-23, +46)), 'leg_r_crippled': ((38, 52), (-23, +46)), 'leg_l_ok': ((38, 52), (+14, +46)), 'leg_l_crippled': ((38, 52), (+14, +46))}
def load_vaultboy_assets():
    if VAULTBOY_CACHE:
        return VAULTBOY_CACHE
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_dir, '..', 'images', 'new_vegas_icons', 'condition_nv')
    file_mapping = {'head_ok': 'Head_CND_Intact.png', 'head_crippled': 'Head_CND_Crippled.png', 'torso_ok': 'Torso_CND_Intact.png', 'torso_crippled': 'Torso_CND_Crippled.png', 'arm_l_ok': 'LeftArm_CND_Intact.png', 'arm_l_crippled': 'LeftArm_CND_Crippled.png', 'arm_r_ok': 'RightArm_CND_Intact.png', 'arm_r_crippled': 'RightArm_CND_Crippled.png', 'leg_l_ok': 'LeftLeg_CND_Intact.png', 'leg_l_crippled': 'LeftLeg_CND_Crippled.png', 'leg_r_ok': 'RightLeg_CND_Intact.png', 'leg_r_crippled': 'RightLeg_CND_Crippled.png'}
    for i in range(1, 6):
        file_mapping[f'face_{i}'] = f'Face_CND_{i}.png'
    for key, filename in file_mapping.items():
        if key in PART_CONFIG:
            trgt_sz, ffst = PART_CONFIG[key]
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                scld_mg = pygame.transform.smoothscale(img, trgt_sz)
                VAULTBOY_CACHE[key] = (scld_mg, ffst)
            else:
                print(f'[UI Warning] File not found: {path}')
    return VAULTBOY_CACHE
def draw_vaultboy_and_cnd(screen, player_data, center_x, center_y, color):
    ssts = load_vaultboy_assets()
    try:
        fnt_smll = pygame.font.Font(settings.MAIN_FONT_PATH, 9)
    except:
        fnt_smll = pygame.font.SysFont(None, 12)
    lmbs = player_data.get('limbs', {'head': 100, 'torso': 100, 'arm_l': 100, 'arm_r': 100, 'leg_l': 100, 'leg_r': 100})
    hp = player_data.get('hp', 280)
    mx_hp = player_data.get('max_hp', 280)
    hp_pct = hp / mx_hp if mx_hp > 0 else 1.0
    if ssts:
        if hp_pct >= 0.8:
            fc_dx = 1
        elif hp_pct >= 0.6:
            fc_dx = 2
        elif hp_pct >= 0.4:
            fc_dx = 3
        elif hp_pct >= 0.2:
            fc_dx = 4
        else:
            fc_dx = 5
        lrs = ['torso', 'leg_l', 'leg_r', 'arm_l', 'arm_r', 'head']
        for prt in lrs:
            is_ok = lmbs.get(prt, 100) > 0
            stt = 'ok' if is_ok else 'crippled'
            key = f'{prt}_{stt}'
            if key in ssts:
                img, (ff_x, ff_y) = ssts[key]
                tntd_mg = img.copy()
                tntd_mg.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                rect = tntd_mg.get_rect(center=(center_x + ff_x, center_y + ff_y))
                screen.blit(tntd_mg, rect)
        fc_key = f'face_{fc_dx}'
        if fc_key in ssts:
            fc_mg, (ff_x, ff_y) = ssts[fc_key]
            tntd_fc = fc_mg.copy()
            tntd_fc.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            fc_rct = tntd_fc.get_rect(center=(center_x + ff_x, center_y + ff_y))
            screen.blit(tntd_fc, fc_rct)
    br_pstns = {'head': (center_x - 13, center_y - 80, 32, 5), 'torso': (center_x - 15, center_y - 18, 32, 5), 'arm_r': (center_x - 75, center_y - 50, 28, 5), 'arm_l': (center_x + 48, center_y - 50, 28, 5), 'leg_r': (center_x - 75, center_y + 32, 28, 5), 'leg_l': (center_x + 46, center_y + 32, 28, 5)}
    crppld_txt_ffsts = {'head': (center_x - 18, center_y - 88), 'torso': (center_x - 18, center_y - 20), 'arm_r': (center_x - 130, center_y - 22), 'arm_l': (center_x + 100, center_y - 22), 'leg_r': (center_x - 110, center_y + 46), 'leg_l': (center_x + 80, center_y + 46)}
    pad = 1
    tr_w = 6
    xt_ln = 16
    for lmb_key, (bx, by, bw, bh) in br_pstns.items():
        val = lmbs.get(lmb_key, 100)
        pct = max(0.0, min(1.0, val / 100.0))
        if val <= 0:
            tx, ty = crppld_txt_ffsts[lmb_key]
            crp_txt = fnt_smll.render('CRIPPLED', True, color)
            screen.blit(crp_txt, (tx, ty))
        fll_w = int((bw - 2) * pct)
        if fll_w > 0:
            pygame.draw.rect(screen, color, (bx + 1, by + 1, fll_w, bh - 2))
        vrt_hght = bh - 2
        tp_y = by - pad
        bttm_y = by + vrt_hght
        tr_bttm_y = by + bh - 3
        lft_x = bx - pad
        rght_x = bx + bw + pad
        if lmb_key in ['head', 'torso']:
            u_pnts = [(lft_x, bttm_y), (lft_x, tp_y), (rght_x, tp_y), (rght_x, bttm_y)]
            pygame.draw.lines(screen, color, False, u_pnts, 1)
        elif lmb_key in ['arm_r', 'leg_r']:
            pygame.draw.line(screen, color, (lft_x, tp_y), (lft_x, bttm_y), 1)
            pygame.draw.line(screen, color, (lft_x, tp_y), (rght_x + xt_ln - 2, tp_y), 1)
            tr_pnts = [(rght_x, tp_y), (rght_x, tr_bttm_y), (rght_x + tr_w, tp_y)]
            pygame.draw.polygon(screen, color, tr_pnts, 0)
        elif lmb_key in ['arm_l', 'leg_l']:
            pygame.draw.line(screen, color, (rght_x, tp_y), (rght_x, bttm_y), 1)
            pygame.draw.line(screen, color, (rght_x, tp_y), (lft_x - xt_ln + 2, tp_y), 1)
            tr_pnts = [(lft_x, tp_y), (lft_x, tr_bttm_y), (lft_x - tr_w, tp_y)]
            pygame.draw.polygon(screen, color, tr_pnts, 0)
class GenericList:
    def __init__(self, draw_space, font, items=None, enable_dot=False, selection_rect_color=None, text_color=None, selected_text_color=None, stats=None, stats_color=None, selected_stats_color=None, dot_color=None, dot_darker_color=None, dot_size=None, text_margin=None, selection_dot_margin=None):
        self.draw_space = draw_space
        self.font = font
        self.enable_dot = enable_dot
        self.font_height = self.font.get_height()
        self.selection_rect_width = draw_space.width
        self.selection_rect_color = selection_rect_color or settings.PIP_BOY_LIGHT
        self.text_color = text_color or settings.PIP_BOY_LIGHT
        self.selected_text_color = selected_text_color or settings.PIP_BOY_DARK
        self.stats = stats
        self.stats_color = stats_color or settings.PIP_BOY_LIGHT
        self.selected_stats_color = selected_stats_color or settings.PIP_BOY_DARK
        self.dot_color = dot_color or settings.PIP_BOY_LIGHT
        self.dot_darker_color = dot_darker_color or settings.PIP_BOY_DARK
        self.dot_size = dot_size if dot_size is not None else settings.RADIO_STATION_SELECTION_DOT_SIZE
        self.text_margin = text_margin if text_margin is not None else settings.RADIO_STATION_TEXT_MARGIN
        self.selection_dot_margin = selection_dot_margin if selection_dot_margin is not None else settings.RADIO_STATION_SELECTION_MARGIN
        self.items = items if items is not None else ['']
        if self.stats is not None:
            if len(self.stats) != len(self.items):
                raise ValueError('Length of stats must match the number of items')
            self.max_stat_width = max([self.font.size(str(stt_2))[0] for stt_2 in self.stats])
        self.dot = None
        self.dot_darker = None
        self.list_surface = None
        self.selected_text = None
        self.selected_stat = None
        self.view_surface = pygame.Surface((self.draw_space.width, self.draw_space.height), pygame.SRCALPHA)
        self._init_selection_rect()
        self.selected_index = 0
        self.previously_selected_index = 0
        if len(self.items) > 0 and self.selected_index >= len(self.items):
            self.selected_index = max(0, len(self.items) - 1)
        self._prepare_list_surface()
        if self.enable_dot:
            self._create_dots()

    def _prepare_list_surface(self):
        if not self.items:
            self.list_surface = pygame.Surface((self.draw_space.width, 0), pygame.SRCALPHA)
            return
        height = self.font_height * len(self.items)
        self.list_surface = pygame.Surface((self.draw_space.width, height), pygame.SRCALPHA)
        stts_clmn_cntr_x = 0
        if self.stats is not None:
            stts_clmn_cntr_x = self.selection_rect_width - self.max_stat_width
        for i, item in enumerate(self.items):
            txt_srfc = self.font.render(item, True, self.text_color)
            self.list_surface.blit(txt_srfc, (self.text_margin, i * self.font_height))
            if self.stats is not None:
                stt_2 = str(self.stats[i])
                stt_srfc = self.font.render(stt_2, True, self.stats_color)
                stt_x = stts_clmn_cntr_x - stt_srfc.get_width() // 2
                self.list_surface.blit(stt_srfc, (stt_x, i * self.font_height))
        self.update_list()
    def _create_dots(self):
        self.dot = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot.fill(self.dot_color)
        self.dot_darker = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot_darker.fill(self.dot_darker_color)
    def _init_selection_rect(self):
        self.selection_rect = pygame.Rect(0, 0, self.selection_rect_width, self.font_height)

    def set_items(self, items, stats=None):
        self.items = items
        if stats is not None:
            if len(stats) != len(items):
                raise ValueError('Length of stats must match the number of items')
            self.stats = stats
        else:
            self.stats = None
        if self.selected_index >= len(self.items):
            self.selected_index = max(0, len(self.items) - 1)
        self._prepare_list_surface()

    def update_list(self):
        if not self.items:
            self.selected_text = None
            return
        self.selection_rect.y = self.selected_index * self.font_height
        slctd_tm = self.items[self.selected_index]
        self.selected_text = self.font.render(slctd_tm, True, self.selected_text_color)
        if self.stats is not None:
            stt_2 = str(self.stats[self.selected_index])
            self.selected_stat = self.font.render(stt_2, True, self.selected_stats_color)

    def change_selection(self, direction):
        nw_ndx = self.selected_index + (-1 if direction else 1)
        prv_ndx = self.selected_index
        if 0 <= nw_ndx < len(self.items):
            self.selected_index = nw_ndx
            self.update_list()
        return prv_ndx
    def render(self, screen, active_index=None, is_playing=False):
        ui_stl = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        y = self.draw_space.top
        fnt_h = self.font.get_height()
        item_h = fnt_h + 4
        spacing = 4
        is_nv = ui_stl in ('fallout_nv', 'fallout_new_vegas')
        for i, item in enumerate(self.items):
            y = self._render_item(screen, i, item, y, item_h, spacing, is_nv, active_index, is_playing)
    def _render_item(self, screen, i, item, y, item_h, spacing, is_nv, active_index, is_playing):
        rect_x = self.draw_space.left
        rct_w = self.draw_space.width
        txt_x = rect_x + (6 if is_nv else 10)
        item_rect = pygame.Rect(rect_x, y, rct_w, item_h)
        if i == self.selected_index:
            text_color = self._draw_selected_item_bg(screen, item_rect, is_nv)
        else:
            text_color = settings.PIP_BOY_LIGHT
        txt_srfc = self.font.render(str(item), True, text_color)
        screen.blit(txt_srfc, (txt_x, y + 1))
        if getattr(self, 'enable_dot', False) and active_index == i and is_playing:
            self._draw_playing_dot(screen, rect_x, y, item_h, is_nv, i)
        return y + item_h + spacing
    def _draw_selected_item_bg(self, screen, item_rect, is_nv):
        if is_nv:
            pygame.draw.rect(screen, settings.PIP_BOY_LIGHT, item_rect, width=1)
            return settings.PIP_BOY_LIGHT
        else:
            pygame.draw.rect(screen, settings.PIP_BOY_LIGHT, item_rect)
            return settings.BACKGROUND
        
    def _draw_playing_dot(self, screen, rect_x, y, item_h, is_nv, index):
        sqr_sz = 6
        sq_x = rect_x + 4
        sq_y = y + (item_h - sqr_sz) // 2
        is_slctd_nv = is_nv and index == self.selected_index
        sqr_clr = settings.BACKGROUND if is_slctd_nv else settings.PIP_BOY_LIGHT
        pygame.draw.rect(screen, sqr_clr, (sq_x, sq_y, sqr_sz, sqr_sz))
class ItemGrid:

    def __init__(self, draw_space, font, padding=5, text_margin=0.5, padding_x=5):
        self.draw_space = draw_space
        self.font = font
        self.line_height = self.font.get_height()
        self.padding = padding
        self.padding_x = padding_x
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None
        self.top_margin = text_margin
        self.bottom_margin = text_margin * 2
        self.text_cache = {}

    def _get_rendered_text(self, text, color):
        key = (text, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.font.render(text, True, color)
        return self.text_cache[key]
    def update(self, entries):
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None
        current_y = self.draw_space.top
        label_x = self.draw_space.left + self.padding_x
        for entry in entries:
            if current_y >= self.draw_space.bottom:
                break
            current_y = self._process_single_entry(entry, current_y, label_x)
            if entry != entries[-1]:
                current_y += self.padding

    def _process_single_entry(self, entry, current_y, label_x):
        bg_clr = settings.PIP_BOY_DARKER if entry.get('highlight') else settings.PIP_BOY_DARK
        entry_lines = []
        label_y = current_y + self.top_margin
        icon_x = label_x
        icon_front_x = label_x
        value_x = self.draw_space.right - self.padding_x
        icon_front_x, icon_x = self._handle_front_icon(entry, entry_lines, icon_x, icon_front_x, label_y)
        lbl_srfc = self._get_rendered_text(entry['label'], settings.PIP_BOY_LIGHT)
        entry_lines.append(('label', lbl_srfc, (icon_front_x, label_y)))
        vl_y = label_y
        txt_wdth = 0
        if 'lines' in entry:
            vl_y, ln_cmpnnts = self._process_entry_lines(entry['lines'], vl_y, value_x)
            entry_lines.extend(ln_cmpnnts)
        if 'value' in entry:
            txt_srfc = self._get_rendered_text(str(entry['value']), settings.PIP_BOY_LIGHT)
            txt_wdth = txt_srfc.get_width()
            entry_lines.append(('value', txt_srfc, (value_x - txt_wdth, vl_y)))
        if not entry.get('icon_front') and 'icon' in entry:
            cn_srfc = entry['icon']
            icon_x = value_x - cn_srfc.get_width() - txt_wdth - self.padding * 2
            entry_lines.append(('icon', cn_srfc, (icon_x, vl_y + 1)))
        ddtnl_lns = max(0, len(entry.get('lines', [])) - 1)
        ntr_hght = int(self.top_margin) + self.line_height + ddtnl_lns * self.line_height + int(self.bottom_margin)
        bg_rct = pygame.Rect(self.draw_space.left, current_y, self.draw_space.width, ntr_hght)
        self.precomputed_bg.append((bg_rct, bg_clr))
        for elem in entry_lines:
            self.precomputed_text.append((elem[1], elem[2]))
        if self.precomputed_divider is None and entry.get('split') and (icon_x is not None):
            self.precomputed_divider = pygame.Rect(icon_x, current_y, self.padding, ntr_hght)
        return current_y + ntr_hght

    def _handle_front_icon(self, entry, entry_lines, icon_x, icon_front_x, label_y):
        if entry.get('icon_front') and 'icon' in entry:
            cn_srfc = entry['icon']
            entry_lines.append(('icon', cn_srfc, (icon_x, label_y + 1)))
            icon_front_x += cn_srfc.get_width() + self.padding
        return (icon_front_x, icon_x)

    def _process_entry_lines(self, lines, start_y, value_x):
        entry_lines = []
        vl_y = start_y
        for i, line in enumerate(lines):
            if i > 0:
                vl_y += self.line_height
            cmpnnts, ln_wdth = self.build_lcomp(line)
            crrnt_x = value_x - ln_wdth
            for cmpnnt in cmpnnts:
                y_ps = vl_y + (1 if cmpnnt == line.get('icon') else 0)
                entry_lines.append(('component', cmpnnt, (crrnt_x, y_ps)))
                crrnt_x += cmpnnt.get_width() + self.padding
        return (vl_y, entry_lines)
    def build_lcomp(self, line):
        cmpnnts = []
        ln_wdth = 0
        if 'icon' in line:
            cmpnnts.append(line['icon'])
            ln_wdth += line['icon'].get_width() + self.padding
        txt_srfc = self.font.render(str(line['value']), True, settings.PIP_BOY_LIGHT)
        cmpnnts.append(txt_srfc)
        ln_wdth += txt_srfc.get_width()
        return (cmpnnts, ln_wdth)

    def render(self, surface):
        for rect, bg_clr in self.precomputed_bg:
            pygame.draw.rect(surface, bg_clr, rect)
        for txt_srfc, pos in self.precomputed_text:
            surface.blit(txt_srfc, pos)
        if self.precomputed_divider is not None:
            pygame.draw.rect(surface, settings.BACKGROUND, self.precomputed_divider)

class AnimatedImage: # 2D photos in images

    def __init__(self, screen, images, position, frame_duration, frame_order=None, loop=True, sound_path=None):
        self.screen = screen
        self.images = images
        self.position = position
        self.frame_duration = frame_duration / 1000
        self.frame_order = frame_order or list(range(len(images)))
        self.loop = loop
        self.sound_path = sound_path
        self.current_frame_index = 0
        self.done = False
        self.running = False
        self.stop_event = Event()
        self.lock = Lock()
        self.thread = None

    def _update_loop(self):
        while not self.stop_event.is_set() and (not self.done):
            self._step_animation()
            self.stop_event.wait(timeout=self.frame_duration)
    def _step_animation(self):
        with self.lock:
            if self.done:
                return
            self._advance_frame()

    def _advance_frame(self):
        self.current_frame_index += 1
        if self.current_frame_index < len(self.frame_order):
            return
        if self.loop:
            self.current_frame_index = 0
            self.play_sound()
        else:
            self.done = True

    def play_sound(self): # should add a song about spinning (SBR reference?) just for fun
        if self.sound_path:
            Utils.play_sfx(self.sound_path, settings.VOLUME / 8, channel=5)

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.done = False
            self.stop_event.clear()
            self.thread = Thread(target=self._update_loop, daemon=True)
            self.play_sound()
            self.thread.start()

    def stop(self): # Never
        ch = pygame.mixer.Channel(5)
        ch.stop()
        self.stop_event.set()
        self.thread = None
    def render(self):
        with self.lock:
            self.screen.blit(self.images[self.frame_order[self.current_frame_index]], self.position)

    def reset(self):
        self.stop()
        self.current_frame_index = 0
        self.done = False
        self.start()

class WireframeItem:

    def __init__(self, screen, position, draw_space, model_path, frame_duration=100, loop=True):
        self.screen = screen
        self.position = position
        self.rect = draw_space
        self.loop = loop
        self.renderer = wireframe.WireframeRenderer(draw_space.width, draw_space.height, 125.0)
        self.renderer.load_model(model_path)
        self.renderer.set_camera(5.0, -2.0, -30.0)
        self.renderer.set_rotation(0.0, 0.0, 0.0)
        self.frame_duration = frame_duration / 500.0
        self.done = False
        self.stop_event = Event()
        self.lock = Lock()
        self.thread = None
        self.lines = []
    def _update_loop(self):
        while not self.stop_event.is_set() and (not self.done):
            self._render_wireframe_frame()
            self.stop_event.wait(timeout=self.frame_duration)
    def _render_wireframe_frame(self):
        with self.lock:
            self.lines = self.renderer.render()
            if not self.lines and (not self.loop):
                self.done = True

    def start(self): # Might be repetitive, should rework these thread functions
        if self.thread is None or not self.thread.is_alive():
            self.done = False
            self.stop_event.clear()
            self.renderer.start()
            self.thread = Thread(target=self._update_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.renderer.stop()
        self.thread = None
    def reset(self):
        self.stop()
        self.done = False
        self.lines = []
        self.start()
    def render(self):
        with self.lock:
            for line in self.lines:
                self._draw_wireframe_line(line)

    def _draw_wireframe_line(self, line):
        pygame.draw.aaline(self.screen, settings.PIP_BOY_LIGHT, (line.x1 + self.position[0], line.y1 + self.position[1]), (line.x2 + self.position[0], line.y2 + self.position[1]))
def draw_nv_ui(screen, player_data, current_tab='STATS', current_subtab=0): # Most of NV UI moved to tabs 
    COLOR_NV = settings.PIP_BOY_LIGHT
    font = pygame.font.Font(settings.MAIN_FONT_PATH, 11)
    fnt_lrg = pygame.font.Font(settings.MAIN_FONT_PATH, 13)
    scrn_w = screen.get_width()
    scrn_h = screen.get_height()
    if isinstance(player_data, dict):
        hp = player_data.get('hp', 280)
        mx_hp = player_data.get('max_hp', 280)
        ap = player_data.get('ap', 85)
        mx_ap = player_data.get('max_ap', 85)
        xp = player_data.get('xp', 1880)
        nxt_xp = player_data.get('next_xp', 2000)
        nm = player_data.get('name', 'DanieleM')
        lvl = player_data.get('level', 28)
        stts_sd_ndx = player_data.get('status_side_index', 0)
    else:
        hp = getattr(settings, 'PLAYER_HP', 280)
        mx_hp = getattr(settings, 'PLAYER_MAX_HP', 280)
        ap = getattr(settings, 'PLAYER_AP', 85)
        mx_ap = getattr(settings, 'PLAYER_MAX_AP', 85)
        xp = getattr(settings, 'PLAYER_XP', 1880)
        nxt_xp = getattr(settings, 'PLAYER_NEXT_XP', 2000)
        nm = getattr(settings, 'PLAYER_NAME', 'DanieleM')
        lvl = getattr(settings, 'PLAYER_LEVEL', 28)
        stts_sd_ndx = 0
    hdr_ln_y = 14
    tck_h = 8
    mrgn_lft = 10
    tb_nm = str(current_tab).upper()
    tb_txt = fnt_lrg.render(tb_nm, True, COLOR_NV)
    wng_ln = 12
    txt_gp = 4
    lft_tck_x = mrgn_lft
    lft_ln_nd = lft_tck_x + wng_ln
    tb_rct = tb_txt.get_rect(left=lft_ln_nd + txt_gp + 10, centery=hdr_ln_y)
    rght_ln_strt = tb_rct.right + txt_gp
    rght_tck_x = rght_ln_strt + wng_ln
    pygame.draw.line(screen, COLOR_NV, (lft_tck_x, hdr_ln_y), (lft_tck_x, hdr_ln_y + tck_h), 1)
    pygame.draw.line(screen, COLOR_NV, (lft_tck_x, hdr_ln_y), (lft_ln_nd + 5, hdr_ln_y), 1)
    screen.blit(tb_txt, tb_rct)
    pygame.draw.line(screen, COLOR_NV, (rght_ln_strt + 5, hdr_ln_y), (rght_tck_x + 10, hdr_ln_y), 1)
    stts_tms = [f'LVL {lvl}', f'HP {hp}/{mx_hp}', f'AP {ap}/{mx_ap}', f'XP {xp}/{nxt_xp}']
    padding_x = 2
    spcng_btwn_bxs = 4
    crr_rght = scrn_w - 10
    for item in reversed(stts_tms):
        txt_srf = font.render(item, True, COLOR_NV)
        txt_w = txt_srf.get_width()
        bx_rght = crr_rght
        bx_lft = bx_rght - (txt_w + padding_x * 2)
        pygame.draw.line(screen, COLOR_NV, (bx_lft, hdr_ln_y), (bx_rght, hdr_ln_y), 1)
        pygame.draw.line(screen, COLOR_NV, (bx_rght, hdr_ln_y), (bx_rght, hdr_ln_y + tck_h), 1)
        screen.blit(txt_srf, (bx_lft + padding_x, hdr_ln_y + 3))
        crr_rght = bx_lft - spcng_btwn_bxs
    if tb_nm in ['STAT', 'STATS'] and current_subtab == 0:
        sd_ptns = ['CND', 'RAD', 'EFF']
        sd_y = 55
        for idx, opt in enumerate(sd_ptns):
            txt = font.render(opt, True, COLOR_NV)
            if idx == stts_sd_ndx:
                box = pygame.Rect(8, sd_y - 2, txt.get_width() + 6, txt.get_height() + 3)
                pygame.draw.rect(screen, COLOR_NV, box, 1)
            screen.blit(txt, (11, sd_y))
            sd_y += 20
        if stts_sd_ndx == 0:
            vb_cntr_x = scrn_w // 2 - 10
            vb_cntr_y = scrn_h // 2 - 5
            draw_vaultboy_and_cnd(screen, player_data, vb_cntr_x, vb_cntr_y, COLOR_NV)
            qck_tms = player_data.get('quick_items', ['(5) Stimpak S)', "(3) Doctor's Bag E)"]) if isinstance(player_data, dict) else ['(5) Stimpak S)', "(3) Doctor's Bag E)"]
            tm_y = 45
            for tm_str in qck_tms:
                tm_txt = font.render(tm_str, True, COLOR_NV)
                item_rect = tm_txt.get_rect(right=scrn_w - 20, top=tm_y)
                screen.blit(tm_txt, item_rect)
                tm_y += 37
    sbtbs_mp = {'STATS': ['Status', 'S.P.E.C.I.A.L.', 'Skills', 'Perks', 'General'], 'ITEMS': ['Weapons', 'Apparel', 'Aid', 'Misc', 'Ammo'], 'DATA': ['Local Map', 'World Map', 'Quests', 'Misc', 'Radio']}
    sbtbs = sbtbs_mp.get(tb_nm, sbtbs_mp.get('STATS'))
    if tb_nm in ['STAT', 'STATS'] and current_subtab == 0 and (stts_sd_ndx == 0):
        chr_txt = font.render(f'{nm} - Level {lvl}', True, COLOR_NV)
        rct_chr = chr_txt.get_rect()
        rct_chr.centerx = scrn_w // 2 - 10
        rct_chr.bottom = scrn_h - 42
        screen.blit(chr_txt, rct_chr)
    sb_y = scrn_h - 18
    bx_pd_x = 3
    bx_pd_y = 2
    dsh_mrgn = 5
    gp_btwn_tms = 18
    tm_wdths = [font.size(st)[0] for st in sbtbs]
    ttl_cntnt_w = sum(tm_wdths) + (len(sbtbs) - 1) * gp_btwn_tms
    strt_x = max(20, (scrn_w - ttl_cntnt_w) // 2)
    tm_x_pstns = []
    crr_x = strt_x
    for w in tm_wdths:
        tm_x_pstns.append(crr_x)
        crr_x += w + gp_btwn_tms
    txt_h = font.size('A')[1]
    ln_y = sb_y + txt_h // 2
    crnr_tck_h = tck_h
    mrgn_lft = 10
    mrgn_rght = scrn_w - 10
    for i, st_nm in enumerate(sbtbs):
        x = tm_x_pstns[i]
        w = tm_wdths[i]
        txt_srf = font.render(st_nm, True, COLOR_NV)
        is_slctd = i == current_subtab
        if is_slctd:
            bx_rct = pygame.Rect(x - bx_pd_x, sb_y - bx_pd_y, w + bx_pd_x * 2, txt_h + bx_pd_y * 2)
            pygame.draw.rect(screen, COLOR_NV, bx_rct, 1)
        screen.blit(txt_srf, (x, sb_y))
        if i == 0:
            pygame.draw.line(screen, COLOR_NV, (mrgn_lft, ln_y - crnr_tck_h), (mrgn_lft, ln_y), 1)
            ln_nd_x = x - bx_pd_x if is_slctd else x - dsh_mrgn
            if ln_nd_x > mrgn_lft:
                pygame.draw.line(screen, COLOR_NV, (mrgn_lft, ln_y), (ln_nd_x, ln_y), 1)
        if i < len(sbtbs) - 1:
            nxt_is_slctd = i + 1 == current_subtab
            nxt_x = tm_x_pstns[i + 1]
            sg_strt_x = x + w + bx_pd_x if is_slctd else x + w + dsh_mrgn
            sg_nd_x = nxt_x - bx_pd_x if nxt_is_slctd else nxt_x - dsh_mrgn
            if sg_nd_x > sg_strt_x:
                pygame.draw.line(screen, COLOR_NV, (sg_strt_x, ln_y), (sg_nd_x, ln_y), 1)
        else:
            sg_strt_x = x + w + bx_pd_x if is_slctd else x + w + dsh_mrgn
            if mrgn_rght > sg_strt_x:
                pygame.draw.line(screen, COLOR_NV, (sg_strt_x, ln_y), (mrgn_rght, ln_y), 1)
            pygame.draw.line(screen, COLOR_NV, (mrgn_rght, ln_y - crnr_tck_h), (mrgn_rght, ln_y), 1)