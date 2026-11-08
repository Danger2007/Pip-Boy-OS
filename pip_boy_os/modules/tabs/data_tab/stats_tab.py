import pygame
import settings
from ui import ItemGrid

class StatTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)
        self.categories = [{'name': 'General', 'stats': [('Locations Discovered', 322), ('Locations Cleared', 191), ('Days Passed', 383), ('Hours Slept', 798), ('Hours Waiting', 1313), ('Caps Found', 309358), ('Most Caps Carried', 224581), ('Junk Collected', 15572), ('Chests Looted', 1361), ('Magazines Found', 69)]}, {'name': 'Quest', 'stats': [('Quests Completed', 45), ('Misc Objectives Completed', 128), ('Main Quests Completed', 12), ('Side Quests Completed', 33)]}, {'name': 'Combat', 'stats': [('People Killed', 542), ('Creatures Killed', 890), ('Robots Destroyed', 120), ('Synths Destroyed', 215), ('Critical Hits', 310), ('Sneak Attacks', 142)]}, {'name': 'Crafting', 'stats': [('Weapons Improved', 84), ('Armor Improved', 112), ('Chems Crafted', 65), ('Food Cooked', 140), ('Objects Built', 512)]}, {'name': 'Crime', 'stats': [('Locks Picked', 156), ('Pockets Picked', 24), ('Items Stolen', 310), ('Trespasses', 15)]}]
        self.selected_category = 0
        lft_w = int((self.draw_space.width + 15) / 2)
        pddng_x = 5
        grd_lft = self.draw_space.left + lft_w + pddng_x
        grd_tp = self.draw_space.top + 8
        grd_wdth = self.draw_space.right - pddng_x - grd_lft
        grd_hght = self.draw_space.height - 16
        grd_rct = pygame.Rect(grd_lft, grd_tp, grd_wdth, grd_hght)
        self.item_grid = ItemGrid(draw_space=grd_rct, font=self.font, padding=1)
        self._update_grid()
    def _update_grid(self):
        """# test rapidi"""
        '# boh, sembra funzionare'
        if 0 <= self.selected_category < len(self.categories):
            slctd_ct = self.categories[self.selected_category]
            ntrs = [{'label': k, 'value': v} for k, v in slctd_ct['stats']]
            if self.item_grid:
                self.item_grid.update(ntrs)
    def scroll(self, direction):
        prv_ndx = self.selected_category
        if direction:
            if self.selected_category > 0:
                self.selected_category -= 1
        elif self.selected_category < len(self.categories) - 1:
            self.selected_category += 1
        if prv_ndx != self.selected_category:
            self._update_grid()

    def select_item(self):
        return True
    def render(self):
        lft_mrgn = self.draw_space.left
        rw_h = self.font.get_linesize() + 6
        lft_w = int((self.draw_space.width + 15) / 2)
        y = self.draw_space.top + 8
        pp_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        for idx, cat in enumerate(self.categories):
            tm_rct = pygame.Rect(lft_mrgn, y, lft_w, rw_h - 2)
            if idx == self.selected_category:
                pygame.draw.rect(self.screen, pp_lght, tm_rct)
                txt_clr = (0, 0, 0)
            else:
                txt_clr = pp_lght
            ct_srf = self.font.render(cat['name'], True, txt_clr)
            ct_rct = ct_srf.get_rect(midleft=(lft_mrgn + 11, tm_rct.centery))
            self.screen.blit(ct_srf, ct_rct)
            y += rw_h
        if self.item_grid:
            self.item_grid.render(self.screen)
StatsTab = StatTab