import os
import pygame
import settings
from tabs.inv_tab.inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils

class ApparelTab(InvBase):
# too lazy to name fully or to be understandable
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.footer_font = getattr(tab_instance, 'footer_font', pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10))
        self._init_apparel_icons()
        super().__init__(screen, tab_instance, draw_space, category='Apparel', enable_turntable=True, enable_dot=True)
        self.item_grid = None
        if self.no_items:
            return
        if not self.is_nv:
            self.item_grid = ItemGrid(draw_space=self.calculate_grid_space(), font=self.inv_font, padding=1)
            if self.unique_items and 0 <= self.active_item_index < len(self.unique_items):
                ntrs = self.get_grid_entries(self.unique_items[self.active_item_index])
                self.item_grid.update(ntrs)
    def _init_apparel_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - settings.BOTTOM_BAR_HEIGHT // 4
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - settings.BOTTOM_BAR_HEIGHT // 2
        self.armor_icon = Utils.load_svg(self.big_icon_size, settings.ARMOR_ICON) if hasattr(settings, 'ARMOR_ICON') else None
        defense_icon_path = getattr(settings, 'DEFENSE_ICON', getattr(settings, 'SHIELD_ICON', None))
        if defense_icon_path and os.path.exists(defense_icon_path):
            self.defense_icon = Utils.load_svg(self.small_icon_size, defense_icon_path)
        else:
            self.defense_icon = pygame.Surface((self.small_icon_size, self.small_icon_size), pygame.SRCALPHA)

    def get_defense_display_data(self, active_apparel=None):
        if not hasattr(self, 'defense_icon'):
            self._init_apparel_icons()
        ttl_dr = 0
        ttl_dt = 0
        if active_apparel:
            tms_to_chck = active_apparel if isinstance(active_apparel, (list, tuple)) else [active_apparel]
            for item in tms_to_chck:
                if getattr(item, 'equipped', False) or getattr(item, 'is_equipped', False) or len(tms_to_chck) == 1:
                    ttl_dr += getattr(item, 'dr', getattr(item, 'damage_res', getattr(item, 'defense', 0)))
                    ttl_dt += getattr(item, 'dt', getattr(item, 'damage_threshold', 0))
        txt_vl = f'{ttl_dr} / {ttl_dt}' if ttl_dt else f'{ttl_dr}'
        return {'icon': self.defense_icon, 'text': txt_vl, 'value': ttl_dr}

    def init_footer_defense(self):
        active_apparel = getattr(self, 'unique_items', [])
        dfns_dt = self.get_defense_display_data(active_apparel)
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH // 4, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        if dfns_dt['icon']:
            cn_y = (settings.BOTTOM_BAR_HEIGHT - dfns_dt['icon'].get_height()) // 2
            ftr_srfc.blit(dfns_dt['icon'], (settings.BOTTOM_BAR_MARGIN, cn_y))
            font = getattr(self, 'footer_font', getattr(self, 'inv_font', None))
            if font:
                txt_srf = font.render(dfns_dt['text'], True, settings.PIP_BOY_LIGHT)
                txt_y = (settings.BOTTOM_BAR_HEIGHT - txt_srf.get_height()) // 2
                ftr_srfc.blit(txt_srf, (dfns_dt['icon'].get_width() + settings.BOTTOM_BAR_MARGIN * 2, txt_y))
        return ftr_srfc

    def init_footer_text(self):
        wght_srfc = self.init_footer_weight()
        cps_srfc = self.init_footer_caps()
        dfns_srfc = self.init_footer_defense()
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ftr_srfc.blit(wght_srfc, (0, 0))
        ftr_srfc.blit(cps_srfc, (0, 0))
        strt_x = settings.SCREEN_WIDTH // 2
        ftr_srfc.blit(dfns_srfc, (strt_x, 0))
        return ftr_srfc

    def get_grid_entries(self, item):
        ntrs = []
        dr_vl = getattr(item, 'dr', getattr(item, 'damage_res', getattr(item, 'defense', 0)))
        dt_vl = getattr(item, 'dt', getattr(item, 'damage_threshold', 0))
        dfns_lns = [{'icon': self.defense_icon, 'value': f'{dr_vl} / {dt_vl}' if dt_vl else dr_vl, 'is_base': True}]
        ntrs.append({'label': 'DMG Resist', 'lines': dfns_lns, 'highlight': True, 'split': True})
        stndrd = [('Weight', getattr(item, 'weight', 0)), ('Value', getattr(item, 'value', 0))]
        for lbl, val in stndrd:
            ntrs.append({'label': lbl, 'value': val})
        return ntrs

    def scroll(self, direction):
        if self.no_items:
            return
        prv_ndx = self.inv_list.selected_index
        super().scroll(direction)
        if not self.is_nv and self.item_grid and (prv_ndx != self.inv_list.selected_index) and self.unique_items:
            if 0 <= self.inv_list.selected_index < len(self.unique_items):
                ntrs = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
                self.item_grid.update(ntrs)

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not self.is_nv and self.item_grid and self.unique_items and (0 <= self.active_item_index < len(self.unique_items)):
                    ntrs = self.get_grid_entries(self.unique_items[self.active_item_index])
                    self.item_grid.update(ntrs)
    def render(self):
        super().render()
        if self.no_items or self.is_nv or self.item_grid is None:
            return
        self.item_grid.render(self.screen)