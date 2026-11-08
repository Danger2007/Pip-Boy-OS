import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
class MiscTab(InvBase): # Bit hard to mix 3 tabs in 1 but I did it!
    def __init__(self, screen, tab_instance, draw_space):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        is_nv = any((k in ui_stl for k in ['nv', 'new_vegas', 'newvegas', 'fnv']))
        ctgr = ('Misc', 'Junk', 'Mods') if is_nv else 'Misc'
        super().__init__(screen, tab_instance, draw_space, category=ctgr, enable_turntable=True)
        self.item_grid = None
        if self.no_items:
            return
        self.item_grid = ItemGrid(draw_space=self.calculate_grid_space(), font=self.inv_font, padding=1)
        if self.unique_items and 0 <= self.inv_list.selected_index < len(self.unique_items):
            ntrs = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(ntrs)
    def init_footer_text(self):
        wght_srfc = self.init_footer_weight()
        cps_srfc = self.init_footer_caps()
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ftr_srfc.blit(wght_srfc, (0, 0))
        ftr_srfc.blit(cps_srfc, (0, 0))
        return ftr_srfc

    def calculate_grid_space(self):
        return super().calculate_grid_space()
    def get_grid_entries(self, item):
        ntrs = []
        stndrd = [('Weight', getattr(item, 'weight', 0)), ('Value', getattr(item, 'value', 0))]
        for lbl, val in stndrd:
            ntrs.append({'label': lbl, 'value': val})
        return ntrs

    def scroll(self, direction):
        if self.no_items or self.item_grid is None:
            return
        prv_ndx = self.inv_list.selected_index
        super().scroll(direction)
        if prv_ndx != self.inv_list.selected_index and self.unique_items and (0 <= self.inv_list.selected_index < len(self.unique_items)):
            ntrs = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(ntrs)

    def select_item(self):
        if self.no_items:
            return
        super().select_item()
        if not self.is_nv:
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())
    def render(self):
        super().render()
        if self.no_items or self.item_grid is None or self.is_nv:
            return
        self.item_grid.render(self.screen)