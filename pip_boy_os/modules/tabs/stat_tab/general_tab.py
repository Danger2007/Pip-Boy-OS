import os
import pygame
import settings
from ..data_tab.settings_tab import SettingsTab
_GENERAL_ICON_CACHE = {}
REPUTATION_IMAGE_MAP = {'Boomers': 'BoomersReputation', 'Brotherhood of Steel': 'BrotherhoodOfSteelReputation', "Caesar's Legion": 'CaesarLegionReputation', 'Followers of the Apocalypse': 'FollowersApocalypseReputation', 'Freeside': 'FreesideReputation', 'Goodsprings': 'GoodspringsReputation', 'Great Khans': 'GreatKhansNewVegas', 'NCR': 'NCRReputation', 'Novac': 'NovacReputation', 'Powder Gangers': 'PowderNewVegas', 'Primm': 'PrimmReputation', 'The Strip': 'NewVegasReputation', 'White Gloves': 'WhiteGloveSociety'}
KARMA_IMAGE_MAP = {'Very Evil': 'Very_Evil', 'Evil': 'Evil', 'Neutral': 'Neutral', 'Good': 'Good', 'Very Good': 'Very_Good'}
def find_general_image_file(name, folder):# Karma Looks redundant but it makes it simple to remember
    if folder == 'reputation_general_nv':
        trgt_nm = REPUTATION_IMAGE_MAP.get(name, name)
    elif folder == 'karma_general_nv':
        trgt_nm = KARMA_IMAGE_MAP.get(name, name)
    else:
        trgt_nm = name
    cln_nm = trgt_nm.strip()
    wrds = cln_nm.split()
    pscl = ''.join((w.capitalize() for w in wrds))
    ndr_ttl = '_'.join((w.capitalize() for w in wrds))
    lwr_ndr = cln_nm.lower().replace(' ', '_')
    cnddts = [cln_nm, pscl, ndr_ttl, lwr_ndr, cln_nm.lower()]
    nq_cnddts = []
    for c in cnddts:
        if c and c not in nq_cnddts:
            nq_cnddts.append(c)
    xts = ['.png', '.webp', '.dds']
    possible_filenames = [f'{stm}{ext}' for stm in nq_cnddts for ext in xts]
    base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [os.path.join(base_dir, 'images', 'new_vegas_icons', folder), os.path.join(base_dir, 'images', folder), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'new_vegas_icons', folder)]
    for s_dir in search_dirs:
        for fnm in possible_filenames:
            full_path = os.path.normpath(os.path.join(s_dir, fnm))
            if os.path.exists(full_path):
                return full_path
    return None

def load_general_icon(name, folder):
    cch_key = f'{folder}_{name}'
    if cch_key in _GENERAL_ICON_CACHE:
        return _GENERAL_ICON_CACHE[cch_key]
    file_path = find_general_image_file(name, folder)
    if not file_path:
        _GENERAL_ICON_CACHE[cch_key] = None
        return None
    try:
        img = pygame.image.load(file_path).convert_alpha()
        _GENERAL_ICON_CACHE[cch_key] = img
        return img
    except:
        pass
    _GENERAL_ICON_CACHE[cch_key] = None
    return None
def colorize_surface(surface, color):
    if surface is None:
        return None
    tntd = surface.copy()
    r, g, b = (color[0], color[1], color[2])
    tntd.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tntd
class GeneralTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.ui_style = getattr(settings, 'UI_STYLE', 'Fallout_4')
        self.is_nv = self.ui_style == 'Fallout_NV'
        self.modes = ['GENERAL', 'REPUTATION', 'SETTINGS']
        self.mode_index = 0
        self.selected_general_index = 0
        self.selected_rep_index = 0
        self.settings_tab = SettingsTab(self.screen, self.tab_instance, self.draw_space)
        self.general_stats = getattr(settings, 'DEFAULT_GENERAL_STATS', [{'name': 'Quests Completed', 'value': 3}, {'name': 'Locations Discovered', 'value': 2}, {'name': 'People Killed', 'value': 0}, {'name': 'Creatures Killed', 'value': 3}, {'name': 'Locks Picked', 'value': 0}, {'name': 'Computers Hacked', 'value': 0}, {'name': 'Stimpaks Taken', 'value': 0}, {'name': 'Rad-X Taken', 'value': 0}, {'name': 'RadAway Taken', 'value': 0}, {'name': 'Chems Taken', 'value': 0}])
        self.karma_alignment = 'Neutral'
        self.karma_title = 'Renegade'
        self.reputations = getattr(settings, 'DEFAULT_REPUTATIONS', [{'name': 'Boomers', 'status': 'Neutral'}, {'name': 'Brotherhood of Steel', 'status': 'Neutral'}, {'name': "Caesar's Legion", 'status': 'Neutral'}, {'name': 'Followers of the Apocalypse', 'status': 'Neutral'}, {'name': 'Freeside', 'status': 'Neutral'}, {'name': 'Great Khans', 'status': 'Neutral'}, {'name': 'NCR', 'status': 'Idolized'}, {'name': 'Novac', 'status': 'Neutral'}, {'name': 'Powder Gangers', 'status': 'Shunned'}, {'name': 'The Strip', 'status': 'Neutral'}])
    @property
    def mode(self):
        return self.modes[self.mode_index]

    def is_editing(self):
        if self.mode == 'SETTINGS':
            return self.settings_tab.is_editing()
        return False
    def handle_threads(self, tab_selected):
        pass

    def toggle_mode(self):
        if not self.is_editing():
            self.mode_index = (self.mode_index + 1) % len(self.modes)
    def handle_x_press(self):
        if self.mode == 'SETTINGS':
            self.settings_tab.handle_x_press()

    def select_item(self):
        if self.mode == 'SETTINGS':
            if self.settings_tab.is_editing():
                return self.settings_tab.select_item()
            else:
                self.toggle_mode()
                return True
        else:
            self.toggle_mode()
            return True
    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return False
        if self.mode == 'SETTINGS' and self.settings_tab.is_editing():
            return self.settings_tab.handle_input(event)
        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r]:
            self.toggle_mode()
            return True
        if self.mode == 'SETTINGS':
            return self.settings_tab.handle_input(event)
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.scroll_general(direction=True)
            return True
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.scroll_general(direction=False)
            return True
        return False

    def scroll_general(self, direction): 
        if self.mode == 'GENERAL':
            if direction:
                if self.selected_general_index > 0:
                    self.selected_general_index -= 1
            elif self.selected_general_index < len(self.general_stats) - 1:
                self.selected_general_index += 1
        elif self.mode == 'REPUTATION':
            if direction:
                if self.selected_rep_index > 0:
                    self.selected_rep_index -= 1
            elif self.selected_rep_index < len(self.reputations) - 1:
                self.selected_rep_index += 1
        elif self.mode == 'SETTINGS': # Extremely complex logic
            self.settings_tab.scroll(direction)

    def _render_new_vegas_ui(self):
        scrn_w = self.screen.get_width()
        scrn_h = self.screen.get_height()
        color = settings.PIP_BOY_LIGHT
        FONT_SIZE = 12
        mn_fnt = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE)
        sb_fnt = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE - 2)
        LINE_HEIGHT = 18
        lft_x = max(20, int(scrn_w * 0.12) - 5)
        lft_w = int(scrn_w * 0.45)
        rght_x = lft_x + lft_w + 10
        rght_w = scrn_w - rght_x - 10
        tp_y = int(scrn_h * 0.18)
        bttm_y = int(scrn_h * 0.82) + 15
        vlbl_h = bttm_y - tp_y
        rght_ffst_y = 12
        nxt_md_dx = (self.mode_index + 1) % len(self.modes)
        nxt_md_nm = self.modes[nxt_md_dx].title()
        tggl_txt = f'{nxt_md_nm} ENTER)'
        tggl_srf = mn_fnt.render(tggl_txt, True, color)
        tggl_x = rght_x + rght_w - tggl_srf.get_width() - 10
        self.screen.blit(tggl_srf, (tggl_x, tp_y - 20 + rght_ffst_y))
        if self.mode == 'SETTINGS':
            self.settings_tab.render()
            return
        ctv_lst = self.general_stats if self.mode == 'GENERAL' else self.reputations
        ctv_ndx = self.selected_general_index if self.mode == 'GENERAL' else self.selected_rep_index
        MAX_VISIBLE_ITEMS = max(1, vlbl_h // LINE_HEIGHT)
        scrll_ffst = max(0, min(ctv_ndx - MAX_VISIBLE_ITEMS // 2, len(ctv_lst) - MAX_VISIBLE_ITEMS))
        scrll_ffst = max(0, scrll_ffst)
        sldr_x = lft_x - 18
        rrw_w = 5
        rrw_h = 8
        ntch = 3
        tp_rrw_y = tp_y
        up_rrw_pts = [(sldr_x, tp_rrw_y), (sldr_x + rrw_w, tp_rrw_y + rrw_h), (sldr_x, tp_rrw_y + rrw_h - ntch), (sldr_x - rrw_w, tp_rrw_y + rrw_h)]
        pygame.draw.polygon(self.screen, color, up_rrw_pts)
        bttm_rrw_y = bttm_y
        dwn_rrw_pts = [(sldr_x, bttm_rrw_y), (sldr_x + rrw_w, bttm_rrw_y - rrw_h), (sldr_x, bttm_rrw_y - rrw_h + ntch), (sldr_x - rrw_w, bttm_rrw_y - rrw_h)]
        pygame.draw.polygon(self.screen, color, dwn_rrw_pts)
        trck_tp = tp_rrw_y + rrw_h - ntch + 5
        trck_bttm = bttm_rrw_y - rrw_h + ntch - 5
        trck_lngth = trck_bttm - trck_tp
        ttl_tms = len(ctv_lst)
        if ttl_tms > MAX_VISIBLE_ITEMS:
            br_lngth = max(12, int(trck_lngth * (MAX_VISIBLE_ITEMS / ttl_tms)))
            mx_scrll = ttl_tms - MAX_VISIBLE_ITEMS
            scrll_rt = scrll_ffst / mx_scrll if mx_scrll > 0 else 0
            br_tp = trck_tp + int(scrll_rt * (trck_lngth - br_lngth))
            br_bttm = br_tp + br_lngth
            pygame.draw.line(self.screen, color, (sldr_x, br_tp), (sldr_x, br_bttm), 2)
        vsbl_tms = ctv_lst[scrll_ffst:scrll_ffst + MAX_VISIBLE_ITEMS]
        for dx_in_vw, tm in enumerate(vsbl_tms):
            ctl_ndx = scrll_ffst + dx_in_vw
            y_ps = tp_y + dx_in_vw * LINE_HEIGHT
            is_slctd = ctl_ndx == ctv_ndx
            if is_slctd:
                slct_rct = pygame.Rect(lft_x - 4, y_ps, lft_w, LINE_HEIGHT - 1)
                pygame.draw.rect(self.screen, color, slct_rct, 1)
            nm_srf = mn_fnt.render(tm['name'], True, color)
            self.screen.blit(nm_srf, (lft_x, y_ps + (LINE_HEIGHT - nm_srf.get_height()) // 2))
            if self.mode == 'GENERAL':
                vl_srf = mn_fnt.render(str(tm['value']), True, color)
                vl_x = lft_x + lft_w - 15
                self.screen.blit(vl_srf, (vl_x, y_ps + (LINE_HEIGHT - vl_srf.get_height()) // 2))
        if self.mode == 'GENERAL':
            krm_ffst_y = rght_ffst_y - 15
            cntr_x = rght_x + rght_w // 2
            lgn_srf = sb_fnt.render(self.karma_alignment, True, color)
            self.screen.blit(lgn_srf, (cntr_x - lgn_srf.get_width() // 2, tp_y + 20 + krm_ffst_y))
            cn_srf = load_general_icon(self.karma_alignment, 'karma_general_nv')
            if cn_srf:
                rg_w, rg_h = cn_srf.get_size()
                scl = min(rght_w / rg_w, vlbl_h * 0.5 / rg_h)
                nw_sz = (int(rg_w * scl), int(rg_h * scl))
                scld_mg = pygame.transform.smoothscale(cn_srf, nw_sz)
                clrd_mg = colorize_surface(scld_mg, color)
                mg_x = cntr_x - nw_sz[0] // 2
                mg_y = tp_y + 45 + krm_ffst_y
                self.screen.blit(clrd_mg, (mg_x, mg_y))
                ttl_y = mg_y + nw_sz[1] + 15
            else:
                ttl_y = tp_y + 120 + krm_ffst_y
            ttl_srf = mn_fnt.render(self.karma_title, True, color)
            self.screen.blit(ttl_srf, (cntr_x - ttl_srf.get_width() // 2, ttl_y))
        elif self.mode == 'REPUTATION':
            if 0 <= self.selected_rep_index < len(self.reputations):
                slctd_rp = self.reputations[self.selected_rep_index]
                cntr_x = rght_x + rght_w // 2
                cn_srf = load_general_icon(slctd_rp['name'], 'reputation_general_nv')
                if cn_srf:
                    rg_w, rg_h = cn_srf.get_size()
                    scl = min(rght_w / rg_w, vlbl_h * 0.55 / rg_h)
                    nw_sz = (int(rg_w * scl), int(rg_h * scl))
                    scld_mg = pygame.transform.smoothscale(cn_srf, nw_sz)
                    clrd_mg = colorize_surface(scld_mg, color)
                    mg_x = cntr_x - nw_sz[0] // 2
                    mg_y = tp_y + 20 + rght_ffst_y
                    self.screen.blit(clrd_mg, (mg_x, mg_y))
                    stts_y = mg_y + nw_sz[1] + 15
                else:
                    stts_y = tp_y + 100 + rght_ffst_y
                stts_srf = mn_fnt.render(slctd_rp.get('status', 'Neutral'), True, color)
                self.screen.blit(stts_srf, (cntr_x - stts_srf.get_width() // 2, stts_y))
                fctn_srf = mn_fnt.render(slctd_rp['name'], True, color)
                self.screen.blit(fctn_srf, (cntr_x - fctn_srf.get_width() // 2, stts_y + 20))
    def render(self):
        if self.is_nv:
            self._render_new_vegas_ui()