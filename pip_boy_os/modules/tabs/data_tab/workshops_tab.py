import os
import pygame
import settings
from ui import ItemGrid

class WorkshopsTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)
        self.workshops = [{'name': 'Greentop Nursery', 'warning': True, 'stats': {'People': 3, 'Food': 12, 'Water': 15, 'Power': 3, 'Defense': 16, 'Beds': 12, 'Happiness': 40}}, {'name': "Hangman's Alley", 'warning': False, 'stats': {'People': 6, 'Food': 6, 'Water': 10, 'Power': 5, 'Defense': 28, 'Beds': 6, 'Happiness': 65}}, {'name': 'Jamaica Plain', 'warning': False, 'stats': {'People': 4, 'Food': 8, 'Water': 8, 'Power': 2, 'Defense': 12, 'Beds': 5, 'Happiness': 50}}, {'name': 'Lyon Outpost', 'warning': False, 'stats': {'People': 2, 'Food': 4, 'Water': 6, 'Power': 0, 'Defense': 8, 'Beds': 2, 'Happiness': 45}}, {'name': 'Murkwater Construction Site', 'warning': False, 'stats': {'People': 0, 'Food': 0, 'Water': 0, 'Power': 0, 'Defense': 0, 'Beds': 0, 'Happiness': 0}}, {'name': 'Nordhagen Beach', 'warning': True, 'stats': {'People': 5, 'Food': 10, 'Water': 10, 'Power': 3, 'Defense': 10, 'Beds': 4, 'Happiness': 38}}, {'name': 'Nuka World Overpass', 'warning': False, 'stats': {'People': 3, 'Food': 12, 'Water': 15, 'Power': 3, 'Defense': 16, 'Beds': 12, 'Happiness': 40}}, {'name': 'Oberland Station', 'warning': True, 'stats': {'People': 4, 'Food': 8, 'Water': 6, 'Power': 2, 'Defense': 14, 'Beds': 3, 'Happiness': 42}}, {'name': 'Parsons State Insane Asylum', 'warning': False, 'stats': {'People': 1, 'Food': 2, 'Water': 5, 'Power': 10, 'Defense': 50, 'Beds': 2, 'Happiness': 80}}, {'name': 'Sanctuary', 'warning': True, 'stats': {'People': 14, 'Food': 18, 'Water': 40, 'Power': 20, 'Defense': 65, 'Beds': 15, 'Happiness': 72}}]
        self.selected_index = 0
        self.scroll_offset = 0
        self.left_panel_width = int(self.draw_space.width * 0.55)
        grd_wdth = int(self.draw_space.width * 0.32)
        mgn = int((self.draw_space.width - self.left_panel_width - grd_wdth) / 2)
        grd_rght = self.draw_space.right - mgn
        grd_lft = grd_rght - grd_wdth
        grd_tp = self.draw_space.top + 8
        grd_hght = self.draw_space.height - 16
        self.grid_rect = pygame.Rect(grd_lft, grd_tp, grd_wdth, grd_hght)
        self.item_grid = ItemGrid(draw_space=self.grid_rect, font=self.font, padding=1)
        self.icons = {}
        self.warning_icon = None
        self._load_workshop_icons()
        self._update_grid()

    def _load_workshop_icons(self):
        """# test rapidi"""
        '# nota: controllare i path dei file'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_dirs = [os.path.join(script_dir, 'images', 'svgs', 'icons_workshops'), os.path.join(script_dir, '..', 'images', 'svgs', 'icons_workshops'), os.path.join(script_dir, '..', '..', 'images', 'svgs', 'icons_workshops'), os.path.join(os.getcwd(), 'images', 'svgs', 'icons_workshops')]
        icons_dir = None
        for d in possible_dirs:
            if os.path.exists(d) and os.path.isdir(d):
                icons_dir = d
                break
        cn_mppng = {'People': ['population.png', 'population.svg'], 'Food': ['food.png', 'food.svg'], 'Water': ['water.png', 'water.svg'], 'Power': ['power.png', 'power.svg'], 'Defense': ['defense.png', 'defense.svg'], 'Beds': ['bed.png', 'bed.svg'], 'Happiness': ['happiness.png', 'happiness.svg']}
        cn_sz = (11, 11)
        if icons_dir:
            warn_path = os.path.join(icons_dir, 'warning.png')
            if os.path.exists(warn_path):
                self.warning_icon = self._try_load_image(warn_path, (10, 10))
        if not self.warning_icon:
            srf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.polygon(srf, (255, 255, 255), [(5, 1), (1, 9), (9, 9)])
            self.warning_icon = srf
        for stat_name, file_candidates in cn_mppng.items():
            loaded_surf = None
            if icons_dir:
                for filename in file_candidates:
                    filepath = os.path.join(icons_dir, filename)
                    if os.path.exists(filepath):
                        loaded_surf = self._try_load_image(filepath, cn_sz)
                        if loaded_surf:
                            break
            if not loaded_surf:
                loaded_surf = self._create_procedural_icon(stat_name, cn_sz)
            if loaded_surf:
                self.icons[stat_name] = loaded_surf
    def _try_load_image(self, filepath, size):
        """# riprende dal loop principale"""
        try:
            img = pygame.image.load(filepath)
            return pygame.transform.smoothscale(img.convert_alpha(), size)
        except:
            return None
    def _create_procedural_icon(self, stat_name, size):
        """# mah..."""
        srf = pygame.Surface(size, pygame.SRCALPHA)
        wht = (255, 255, 255)
        if stat_name == 'People':
            pygame.draw.circle(srf, wht, (5, 3), 2)
            pygame.draw.rect(srf, wht, (2, 5, 6, 5), border_radius=1)
        elif stat_name == 'Food':
            pygame.draw.rect(srf, wht, (2, 2, 2, 7))
            pygame.draw.rect(srf, wht, (6, 2, 3, 7))
        elif stat_name == 'Water':
            pygame.draw.polygon(srf, wht, [(5, 1), (2, 6), (5, 10), (8, 6)])
        elif stat_name == 'Power':
            pygame.draw.polygon(srf, wht, [(6, 1), (2, 5), (5, 5), (3, 10), (9, 4), (5, 4)])
        elif stat_name == 'Defense':
            pygame.draw.polygon(srf, wht, [(5, 1), (9, 3), (8, 7), (5, 10), (2, 7), (1, 3)])
        elif stat_name == 'Beds':
            pygame.draw.rect(srf, wht, (1, 4, 9, 4))
            pygame.draw.rect(srf, wht, (2, 2, 3, 2))
            pygame.draw.line(srf, wht, (1, 8), (1, 10), 1)
            pygame.draw.line(srf, wht, (9, 8), (9, 10), 1)
        elif stat_name == 'Happiness':
            pygame.draw.circle(srf, wht, (5, 5), 4, width=1)
            pygame.draw.circle(srf, wht, (3, 4), 1)
            pygame.draw.circle(srf, wht, (7, 4), 1)
            pygame.draw.arc(srf, wht, (3, 4, 4, 4), 3.14, 0, 1)
        else:
            pygame.draw.rect(srf, wht, (2, 2, 7, 7))
        return srf

    def _get_tinted_icon(self, icon_surf, color):
        """# boh, sembra funzionare"""
        if not icon_surf:
            return None
        tntd = icon_surf.copy().convert_alpha()
        clr_srf = pygame.Surface(tntd.get_size(), pygame.SRCALPHA)
        clr_srf.fill(color)
        tntd.blit(clr_srf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tntd
    def _update_grid(self):
        """# FIXME: a volte lagga qui"""
        if 0 <= self.selected_index < len(self.workshops):
            slctd_ws = self.workshops[self.selected_index]
            ntrs = [{'label': k, 'value': v} for k, v in slctd_ws['stats'].items()]
            if self.item_grid:
                self.item_grid.update(ntrs)

    def scroll(self, direction):
        """# riprende dal loop principale"""
        '# boh, sembra funzionare'
        prv_ndx = self.selected_index
        if direction:
            if self.selected_index > 0:
                self.selected_index -= 1
        elif self.selected_index < len(self.workshops) - 1:
            self.selected_index += 1
        if prv_ndx != self.selected_index:
            self._update_grid()
    def select_item(self):
        """# TODO: ottimizzare questa parte"""
        '# mah...'
        return True
    def render(self):
        lft_mrgn = self.draw_space.left
        rw_h = self.font.get_linesize() + 6
        mx_vsbl = self.draw_space.height // rw_h
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + mx_vsbl:
            self.scroll_offset = self.selected_index - mx_vsbl + 1
        pp_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        pp_drk = getattr(settings, 'PIP_BOY_DARK', (0, 30, 0))
        lft_w = self.left_panel_width
        y = self.draw_space.top + 8
        vsbl_tms = self.workshops[self.scroll_offset:self.scroll_offset + mx_vsbl]
        for idx, tm in enumerate(vsbl_tms):
            ctl_dx = self.scroll_offset + idx
            tm_rct = pygame.Rect(lft_mrgn, y, lft_w, rw_h - 2)
            if ctl_dx == self.selected_index:
                pygame.draw.rect(self.screen, pp_lght, tm_rct)
                txt_clr = (0, 0, 0)
            else:
                txt_clr = pp_lght
            nm_srf = self.font.render(tm['name'], True, txt_clr)
            nm_rct = nm_srf.get_rect(midleft=(lft_mrgn + 10, tm_rct.centery))
            self.screen.blit(nm_srf, nm_rct)
            if tm.get('warning', False) and self.warning_icon:
                wrn_clr = (0, 0, 0) if ctl_dx == self.selected_index else pp_lght
                tntd_wrn = self._get_tinted_icon(self.warning_icon, wrn_clr)
                if tntd_wrn:
                    wrn_x = nm_rct.right + 6
                    mx_llwd_x = tm_rct.right - 14
                    if wrn_x > mx_llwd_x:
                        wrn_x = mx_llwd_x
                    wrn_rct = tntd_wrn.get_rect(midleft=(wrn_x, tm_rct.centery))
                    self.screen.blit(tntd_wrn, wrn_rct)
            y += rw_h
        if 0 <= self.selected_index < len(self.workshops):
            slctd_ws = self.workshops[self.selected_index]
            stats = slctd_ws['stats']
            ppl_cnt = stats.get('People', 0)
            rght_y = self.draw_space.top + 8
            stt_rw_h = rw_h
            for rw_dx, (stat_name, stt_vl) in enumerate(stats.items()):
                rw_rct = pygame.Rect(self.grid_rect.left, rght_y, self.grid_rect.width, stt_rw_h - 2)
                pygame.draw.rect(self.screen, pp_drk, rw_rct)
                hs_stt_wrnng = False
                if stat_name in ('Beds', 'Food', 'Water') and stt_vl < ppl_cnt:
                    hs_stt_wrnng = True
                elif stat_name == 'Happiness' and stt_vl < 50 and (ppl_cnt > 0):
                    hs_stt_wrnng = True
                cn_x = rw_rct.left + 4
                lbl_x = cn_x
                if stat_name in self.icons:
                    cn_mg = self.icons[stat_name]
                    tntd_cn = self._get_tinted_icon(cn_mg, pp_lght)
                    if tntd_cn:
                        cn_rct = tntd_cn.get_rect(midleft=(cn_x, rw_rct.centery))
                        self.screen.blit(tntd_cn, cn_rct)
                        lbl_x = cn_rct.right + 5
                lbl_srf = self.font.render(stat_name, True, pp_lght)
                lbl_rct = lbl_srf.get_rect(midleft=(lbl_x, rw_rct.centery))
                self.screen.blit(lbl_srf, lbl_rct)
                vl_srf = self.font.render(str(stt_vl), True, pp_lght)
                vl_rct = vl_srf.get_rect(midright=(rw_rct.right - 16 if hs_stt_wrnng else rw_rct.right - 4, rw_rct.centery))
                self.screen.blit(vl_srf, vl_rct)
                if hs_stt_wrnng and self.warning_icon:
                    tntd_wrn = self._get_tinted_icon(self.warning_icon, pp_lght)
                    if tntd_wrn:
                        wrn_rct = tntd_wrn.get_rect(midleft=(vl_rct.right + 4, rw_rct.centery))
                        self.screen.blit(tntd_wrn, wrn_rct)
                rght_y += stt_rw_h