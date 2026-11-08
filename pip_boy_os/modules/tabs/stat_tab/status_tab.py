import os
import pygame
import settings
from threading import Thread
from data_models import IconConfig
from typing import Dict, List
from util_functs import Utils
from .rad_tab import RadSubtab
from .eff_tab import EffSubtab

class StatusTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.player_data = getattr(self.tab_instance, 'player_data', {'status_side_index': 0})
        self.conditionboy_thread = None
        self.conditionboy_thread_running = False
        self.small_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 12)
        self.rad_subtab = RadSubtab(self.screen, self.draw_space)
        self.eff_subtab = EffSubtab(self.screen, self.draw_space)
        self._init_conditionboy()
        self.player_surface = self.small_font.render(settings.PLAYER_NAME, True, settings.PIP_BOY_LIGHT)
        self.setup_limb_damage(settings.DEFAULT_LIMB_DAMAGE)
        self.setup_stats_display(settings.DEFAULT_STATS_DAMAGE, settings.DEFAULT_STATS_ARMOR)
    def _init_conditionboy(self):
        # Renders the 2d animation of Fo4
        cndtnb_scl = self.draw_space.height / settings.CONDITIONBOY_SCALE
        self.extra_head_x = 0
        legs_index = self._get_legs_index()
        self.conditionboy_legs, self.conditionboy_transforms = Utils.load_svgs(os.path.join(settings.STAT_TAB_BODY_SVG_BASE_FOLDER, f'legs{legs_index}'), cndtnb_scl, load_transforms=True)
        hd_scl = cndtnb_scl / 2
        self.conditionboy_head = Utils.load_svg(hd_scl, self._get_head_path())
        self.conditionboy_legs_centerx = self.conditionboy_legs[0].width // 2
        self.conditionboy_legs_centery = self.conditionboy_legs[0].height // 2
        self.conditionboy_head_offsets = self._load_conditionboy_offsets(legs_index)
        self.conditionboy_surface = pygame.Surface((self.draw_space.width, self.draw_space.height), pygame.SRCALPHA)
        self.conditionboy_screen_position = self.conditionboy_surface.get_rect(center=(self.draw_space.x + self.draw_space.width // 2, self.draw_space.y + self.draw_space.height // 2))
        self.conditionboy_index = 0
        self.conditionboy_heads_index = 0

    def _get_legs_index(self):
        dflt_hp = settings.DEFAULT_LIMB_DAMAGE
        lft_rm_dmgd = dflt_hp[1] <= settings.CRIPPLED_THRESHOLD
        rght_rm_dmgd = dflt_hp[2] <= settings.CRIPPLED_THRESHOLD
        lft_lg_dmgd = dflt_hp[4] <= settings.CRIPPLED_THRESHOLD
        rght_lg_dmgd = dflt_hp[5] <= settings.CRIPPLED_THRESHOLD
        stt = 1
        if lft_rm_dmgd:
            stt += 1
        if rght_rm_dmgd:
            stt += 2
        if lft_lg_dmgd:
            self.extra_head_x = 3
            stt += 4
        if rght_lg_dmgd:
            self.extra_head_x = 3
            stt += 8
        hd_dmgd = dflt_hp[0] <= settings.CRIPPLED_THRESHOLD
        if hd_dmgd and lft_rm_dmgd and rght_rm_dmgd and lft_lg_dmgd and rght_lg_dmgd:
            stt = 16
        return stt

    def _get_head_path(self):
        hd_hp = settings.DEFAULT_LIMB_DAMAGE[0]
        paths = settings.STAT_TAB_HEADS
        crppld_lmbs = len([True for x in settings.DEFAULT_LIMB_DAMAGE if x < settings.CRIPPLED_THRESHOLD])
        if hd_hp >= settings.CRIPPLED_THRESHOLD:
            if settings.RADIATION_CURRENT > settings.DAMAGED_THRESHOLD:
                return paths['radiated']
            elif settings.ADDICTED:
                return paths['addicted']
            elif hd_hp >= settings.DAMAGED_THRESHOLD and crppld_lmbs <= 2:
                return paths['normal']
            return paths['damaged']
        else:
            if settings.RADIATION_CURRENT > settings.DAMAGED_THRESHOLD:
                return paths['radiated_crippled']
            elif settings.ADDICTED:
                return paths['addicted_crippled']
            return paths['crippled']

    def scroll(self, direction):
        p_dt = getattr(self.tab_instance, 'player_data', self.player_data)
        crrnt_dx = p_dt.get('status_side_index', 0)
        if direction:
            p_dt['status_side_index'] = (crrnt_dx - 1) % 3
        else:
            p_dt['status_side_index'] = (crrnt_dx + 1) % 3
    def _load_conditionboy_offsets(self, legs_index):
        ini_file = os.path.join(settings.STAT_TAB_BODY_SVG_BASE_FOLDER, f'legs{legs_index}', settings.STAT_TAB_OFFSET_INI)
        try:
            with open(ini_file, 'r') as f:
                pstns = []
                for pos in f.read().split(';'):
                    x, y = pos.split(',')
                    x = float(x) * self.draw_space.width / settings.CONDITIONBOY_SCALE
                    y = float(y) * self.draw_space.height / settings.CONDITIONBOY_SCALE
                    pstns.append((x, y))
                return pstns
        except:
            return [(0.0, 0.0) for _ in range(len(self.conditionboy_legs))]
    def _calculate_stats_width(self, big_rect_size, small_rect_size, num_damage_icons, num_armor_icons):
        ttl_mrgns = settings.DAMAGE_ARMOUR_MARGIN_BIG + num_damage_icons * settings.DAMAGE_ARMOUR_MARGIN_SMALL + num_armor_icons * settings.DAMAGE_ARMOUR_MARGIN_SMALL
        ttl_cn_spc = big_rect_size * 2 + num_damage_icons * small_rect_size + num_armor_icons * small_rect_size
        return ttl_cn_spc + ttl_mrgns
    def _render_stats_icons(self, icons, big_rect_size, small_rect_size):
        margin = 0

        def render_icon_section(icon_type):
            nonlocal margin
            bg_cn = Utils.scale_image(pygame.image.load(icons[icon_type]['big']).convert_alpha(), settings.DAMAGE_ARMOUR_ICON_BIG_SIZE)
            bg_cn = Utils.tint_image(bg_cn)
            pygame.draw.rect(self.stats_surface, settings.PIP_BOY_DARK, (margin, 0, big_rect_size, big_rect_size))
            self.stats_surface.blit(bg_cn, (margin + (big_rect_size // 2 - bg_cn.get_width() // 2), big_rect_size // 2 - bg_cn.get_height() // 2))
            margin += big_rect_size
            for small_icon_path, value in zip(icons[icon_type]['small'], icons[icon_type]['values']):
                margin += settings.DAMAGE_ARMOUR_MARGIN_SMALL
                smll_cn = Utils.scale_image(pygame.image.load(small_icon_path).convert_alpha(), settings.DAMAGE_ARMOUR_ICON_SMALL_SIZE)
                smll_cn = Utils.tint_image(smll_cn)
                pygame.draw.rect(self.stats_surface, settings.PIP_BOY_DARK, (margin, 0, small_rect_size, big_rect_size))
                self.stats_surface.blit(smll_cn, (margin + (small_rect_size // 2 - smll_cn.get_width() // 2), big_rect_size // 4 - smll_cn.get_height() // 2))
                txt_srfc = self.small_font.render(str(value), True, settings.PIP_BOY_LIGHT)
                self.stats_surface.blit(txt_srfc, (margin + (small_rect_size // 2 - txt_srfc.get_width() // 2), big_rect_size - txt_srfc.get_height() - settings.DAMAGE_ARMOUR_ICON_MARGIN // 4))
                margin += small_rect_size
        render_icon_section('damage')
        margin += settings.DAMAGE_ARMOUR_MARGIN_BIG
        render_icon_section('armor')

    def setup_limb_damage(self, limb_damages):
        if len(limb_damages) != len(settings.LIMB_POSITIONS):
            raise ValueError('Number of damage values must match number of limb positions')
        width = settings.LIMB_DAMAGE_WIDTH
        height = width // 4
        cntr_x = self.draw_space.width // 2
        self.limb_damage_surface = pygame.Surface((self.draw_space.width, self.draw_space.height), pygame.SRCALPHA).convert_alpha()
        for dmg, pos in zip(limb_damages, settings.LIMB_POSITIONS):
            rect = pygame.Rect(cntr_x - width // 2 + pos.x_offset, pos.y_position, width, height)
            dmg_rct = rect.copy()
            dmg_rct.width = int(dmg_rct.width * (dmg / 100))
            pygame.draw.rect(self.limb_damage_surface, settings.PIP_BOY_LIGHT, dmg_rct)
            pygame.draw.rect(self.limb_damage_surface, settings.PIP_BOY_LIGHT, rect, 1)

    def setup_stats_display(self, damage_icons, armor_icons):
        icons = {'damage': {'big': settings.STAT_TAB_GUN, 'small': [cn.path for cn in damage_icons], 'values': [cn.value for cn in damage_icons]}, 'armor': {'big': settings.STAT_TAB_ARMOUR, 'small': [cn.path for cn in armor_icons], 'values': [cn.value for cn in armor_icons]}}
        self._create_stats_surface(icons)

    def _create_stats_surface(self, icons):
        big_rect_size = self.draw_space.width // settings.DAMAGE_ARMOUR_ICON_ABSOLUTE_SIZE
        small_rect_size = big_rect_size // 2
        ttl_wdth = self._calculate_stats_width(big_rect_size, small_rect_size, len(icons['damage']['small']), len(icons['armor']['small']))
        self.stats_surface = pygame.Surface((ttl_wdth, big_rect_size), pygame.SRCALPHA).convert_alpha()
        self._render_stats_icons(icons, big_rect_size, small_rect_size)

    def update_conditionboy(self):
        while self.conditionboy_thread_running:
            self.conditionboy_surface.fill((0, 0, 0, 0))
            x_ffst_bd = self.draw_space.centerx - self.conditionboy_transforms[self.conditionboy_index][0] - self.conditionboy_legs_centerx
            y_ffst_bd = self.draw_space.centery / 2 - self.conditionboy_transforms[self.conditionboy_index][1] - self.conditionboy_legs_centery / 2 + 10
            self.conditionboy_surface.blit(self.conditionboy_legs[self.conditionboy_index], (x_ffst_bd, y_ffst_bd))
            x_ffst_hd = self.conditionboy_head_offsets[self.conditionboy_index][0] + self.draw_space.centerx - self.conditionboy_head.width / 2 - self.extra_head_x
            y_ffst_hd = self.conditionboy_head_offsets[self.conditionboy_index][1] + self.conditionboy_head.height
            self.conditionboy_surface.blit(self.conditionboy_head, (x_ffst_hd, y_ffst_hd))
            self.conditionboy_index = (self.conditionboy_index + 1) % len(self.conditionboy_legs)
            pygame.time.wait(settings.SPEED * 150)
    def handle_threads(self, tab_selected):
        p_dt = getattr(self.tab_instance, 'player_data', self.player_data)
        sd_ndx = p_dt.get('status_side_index', 0)
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        shld_rn = tab_selected and (ui_stl != 'fallout_nv' or sd_ndx == 0)
        if shld_rn and (not self.conditionboy_thread_running):
            self.conditionboy_thread_running = True
            self.conditionboy_thread = Thread(target=self.update_conditionboy, daemon=True)
            self.conditionboy_thread.start()
        elif not shld_rn and self.conditionboy_thread_running:
            self.conditionboy_thread_running = False
            if self.conditionboy_thread:
                self.conditionboy_thread.join()

    def render(self):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        p_dt = getattr(self.tab_instance, 'player_data', self.player_data)
        sd_ndx = p_dt.get('status_side_index', 0)
        self.handle_threads(True)
        if ui_stl == 'fallout_nv':
            if sd_ndx == 1:
                self.rad_subtab.render(p_dt, ui_stl)
                return
            if sd_ndx == 2:
                self.eff_subtab.render(p_dt, ui_stl)
                return
            return
        self.render_conditionboy()
        self.render_player_name()
        if hasattr(self, 'stats_surface'):
            self.render_stats()
        if hasattr(self, 'limb_damage_surface'):
            self.render_limb_damage()
    def render_conditionboy(self):
        self.screen.blit(self.conditionboy_surface, self.conditionboy_screen_position)
    def render_player_name(self):
        plr_ps = (self.draw_space.x + self.draw_space.width // 2 - self.player_surface.get_width() // 2, self.draw_space.y + self.draw_space.height - self.player_surface.get_height())
        self.screen.blit(self.player_surface, plr_ps)

    def render_stats(self):
        stts_ps = (self.draw_space.x + self.draw_space.width // 2 - self.stats_surface.get_width() // 2, self.draw_space.y + self.draw_space.height - self.stats_surface.get_height() * 1.7)
        self.screen.blit(self.stats_surface, stts_ps)
    def render_limb_damage(self):
        self.screen.blit(self.limb_damage_surface, self.draw_space)