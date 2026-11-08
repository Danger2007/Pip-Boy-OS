import os
import math
import pygame
import settings
def draw_star(surface, color, center, outer_radius=6, inner_radius=2.2, filled=True, width=1):
    pnts = []
    ngl = -math.pi / 2
    stp = math.pi / 5
    for i in range(10):
        r = outer_radius if i % 2 == 0 else inner_radius
        x = center[0] + r * math.cos(ngl)
        y = center[1] + r * math.sin(ngl)
        pnts.append((x, y))
        ngl += stp
    if filled:
        pygame.draw.polygon(surface, color, pnts)
    else:
        pygame.draw.polygon(surface, color, pnts, width)

def colorize_surface(surface, color):
    if surface is None:
        return None
    tntd = surface.copy()
    r, g, b = (color[0], color[1], color[2])
    tntd.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tntd

class PerksTab:

    def __init__(self, screen, tab_base=None, draw_space=None):
        self.screen = screen
        self.tab_base = tab_base
        self.draw_space = draw_space if draw_space else pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.selected_index = 0
        self.scroll_offset = 0
        self.perks_data = []
        self._image_cache = {}
        self.load_perks_data()
    def load_perks_data(self):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if 'nv' in ui_stl or 'vegas' in ui_stl:
            self.perks_data = getattr(settings, 'DEFAULT_PERKS_NV', getattr(settings, 'PERKS_FALLOUT_NV', []))
        else:
            self.perks_data = getattr(settings, 'DEFAULT_PERKS_FO4', getattr(settings, 'PERKS_FALLOUT_4', []))
        if not self.perks_data:
            self.perks_data = getattr(settings, 'DEFAULT_PERKS', getattr(settings, 'PERKS', []))

    def _get_field(self, perk, field_name, default=None):
        if isinstance(perk, dict):
            return perk.get(field_name, default)
        return getattr(perk, field_name, default)
    def scroll_perks(self, direction):
        if not self.perks_data:
            return
        if isinstance(direction, bool):
            dlt = -1 if direction else 1
        elif isinstance(direction, str):
            dlt = -1 if direction.lower() in ('up', 'su', 'prev') else 1
        else:
            dlt = 1 if direction > 0 else -1
        nw_ndx = self.selected_index + dlt
        self.selected_index = max(0, min(len(self.perks_data) - 1, nw_ndx))

    def handle_input(self, event):
        if not self.perks_data:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = max(0, self.selected_index - 1)
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = min(len(self.perks_data) - 1, self.selected_index + 1)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.selected_index = max(0, self.selected_index - 5)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.selected_index = min(len(self.perks_data) - 1, self.selected_index + 5)
                return True
        return False
    def _load_and_scale_img(self, img_path, max_size, cache_key):
        srf = None
        try:
            srf = pygame.image.load(img_path).convert_alpha()
        except:
            try:
                from PIL import Image
                pl_mg = Image.open(img_path).convert('RGBA')
                data = pl_mg.tobytes()
                srf = pygame.image.fromstring(data, pl_mg.size, 'RGBA').convert_alpha()
            except:
                srf = None
        if srf:
            w, h = srf.get_size()
            mx_w, mx_h = max_size
            rt = min(mx_w / max(1, w), mx_h / max(1, h))
            nw_sz = (max(1, int(w * rt)), max(1, int(h * rt)))
            scld_srf = pygame.transform.smoothscale(srf, nw_sz)
            self._image_cache[cache_key] = scld_srf
            return scld_srf
        self._image_cache[cache_key] = None
        return None

    def _get_perk_image(self, perk, max_size=(80, 80)):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        is_nv = 'nv' in ui_stl or 'vegas' in ui_stl
        prk_nm = str(self._get_field(perk, 'name', ''))
        if not prk_nm:
            return None
        cache_key = f'{prk_nm}_{is_nv}_{max_size}'
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        curr_file_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = getattr(settings, 'BASE_DIR', os.path.abspath(os.path.join(curr_file_dir, '..', '..', '..')))
        explicit_path = self._get_field(perk, 'image', self._get_field(perk, 'icon', None))
        if explicit_path:
            fll_xplct = explicit_path if os.path.isabs(explicit_path) else os.path.join(root_dir, explicit_path)
            if os.path.exists(fll_xplct):
                return self._load_and_scale_img(fll_xplct, max_size, cache_key)
        search_dirs = [os.path.join(root_dir, 'images', 'new_vegas_icons', 'perks_nv'), os.path.join(root_dir, 'images', 'new_vegas_icons', 'perks'), os.path.join(root_dir, 'images', 'stats', 'perks'), os.path.join(root_dir, 'images', 'perks_nv'), os.path.join(root_dir, 'images', 'perks')]
        cln_nm = prk_nm.replace("'", '').strip()
        nm_vrnts = [cln_nm.replace(' ', '_'), cln_nm.replace(' ', ''), f"Fo4_{cln_nm.replace(' ', '_')}", f"Fo4_{cln_nm.replace(' ', '')}", cln_nm.lower().replace(' ', '_'), cln_nm.lower().replace(' ', '')]
        xtnsns = ['.webp', '.png', '.jpg', '.dds']
        for fldr in search_dirs:
            if not os.path.exists(fldr):
                continue
            for nm in nm_vrnts:
                for ext in xtnsns:
                    full_path = os.path.join(fldr, f'{nm}{ext}')
                    if os.path.exists(full_path):
                        return self._load_and_scale_img(full_path, max_size, cache_key)
        self._image_cache[cache_key] = None
        return None

    def update(self):
        if not self.perks_data:
            self.load_perks_data()
    def render(self):
        if not self.perks_data:
            self.load_perks_data()
        if not self.perks_data:
            return
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if 'nv' in ui_stl or 'vegas' in ui_stl:
            self._render_fallout_nv_ui()
        else:
            self._render_fallout4_ui()
    def _get_font(self, size=11):
        font_path = getattr(settings, 'MAIN_FONT_PATH', None)
        if font_path:
            try:
                return pygame.font.Font(font_path, size)
            except:
                pass
        return pygame.font.SysFont('monospace', size, bold=True)

    def _wrap_text(self, text, font, max_width):
        wrds = text.split(' ')
        lns = []
        crrnt_ln = []
        for wrd in wrds:
            tst_ln = ' '.join(crrnt_ln + [wrd])
            if font.size(tst_ln)[0] <= max_width:
                crrnt_ln.append(wrd)
            else:
                if crrnt_ln:
                    lns.append(' '.join(crrnt_ln))
                crrnt_ln = [wrd]
        if crrnt_ln:
            lns.append(' '.join(crrnt_ln))
        return lns
    def _render_fallout_nv_ui(self):
        color = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        scrn_w = settings.SCREEN_WIDTH
        scrn_h = settings.SCREEN_HEIGHT
        FONT_SIZE = 12
        fnt_mn = pygame.font.Font(getattr(settings, 'MAIN_FONT_PATH', None), FONT_SIZE)
        fnt_dsc = pygame.font.Font(getattr(settings, 'MAIN_FONT_PATH', None), FONT_SIZE - 3)
        LINE_HEIGHT = 18
        lft_x = int(scrn_w * 0.12)
        lft_w = int(scrn_w * 0.36)
        rght_x = int(scrn_w * 0.52)
        rght_w = int(scrn_w * 0.45)
        tp_y = int(scrn_h * 0.18)
        bttm_y = int(scrn_h * 0.82)
        vlbl_h = bttm_y - tp_y
        MAX_VISIBLE_ITEMS = max(1, vlbl_h // LINE_HEIGHT)
        ttl_tms = len(self.perks_data)
        scroll_offset = max(0, min(self.selected_index - MAX_VISIBLE_ITEMS // 2, ttl_tms - MAX_VISIBLE_ITEMS))
        scroll_offset = max(0, scroll_offset)
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
        pygame.draw.line(self.screen, color, (sldr_x, trck_tp), (sldr_x, trck_bttm), 1)
        if ttl_tms > MAX_VISIBLE_ITEMS:
            br_lngth = max(12, int(trck_lngth * (MAX_VISIBLE_ITEMS / ttl_tms)))
            mx_scrll = ttl_tms - MAX_VISIBLE_ITEMS
            scrll_rt = scroll_offset / mx_scrll if mx_scrll > 0 else 0
            br_tp = trck_tp + int(scrll_rt * (trck_lngth - br_lngth))
            br_bttm = br_tp + br_lngth
            pygame.draw.line(self.screen, color, (sldr_x, br_tp), (sldr_x, br_bttm), 2)
        vsbl_prks = self.perks_data[scroll_offset:scroll_offset + MAX_VISIBLE_ITEMS]
        for dx_in_vw, perk in enumerate(vsbl_prks):
            ctl_ndx = scroll_offset + dx_in_vw
            y_ps = tp_y + dx_in_vw * LINE_HEIGHT
            is_slctd = ctl_ndx == self.selected_index
            prk_nm = str(self._get_field(perk, 'name', ''))
            rnk = int(self._get_field(perk, 'rank', 1))
            dspl_txt = f'{prk_nm} ({rnk})' if rnk > 1 else prk_nm
            if is_slctd:
                slct_rct = pygame.Rect(lft_x - 4, y_ps, lft_w + 8, LINE_HEIGHT - 1)
                pygame.draw.rect(self.screen, color, slct_rct, 1)
            txt_srf = fnt_mn.render(dspl_txt, True, color)
            self.screen.blit(txt_srf, (lft_x, y_ps + (LINE_HEIGHT - txt_srf.get_height()) // 2))
        if 0 <= self.selected_index < ttl_tms:
            slctd_prk = self.perks_data[self.selected_index]
            mg_h = int(vlbl_h * 0.55)
            prk_mg = self._get_perk_image(slctd_prk, max_size=(rght_w, mg_h))
            if prk_mg:
                clrd_mg = colorize_surface(prk_mg, color)
                cntr_x = rght_x + (rght_w - clrd_mg.get_width()) // 2
                cntr_y = tp_y + (mg_h - clrd_mg.get_height()) // 2
                self.screen.blit(clrd_mg, (cntr_x, cntr_y))
            dvdr_y = tp_y + mg_h + 5
            pygame.draw.line(self.screen, color, (rght_x, dvdr_y), (rght_x + rght_w, dvdr_y), 1)
            pygame.draw.line(self.screen, color, (rght_x + rght_w, dvdr_y), (rght_x + rght_w, dvdr_y + 7), 1)
            dsc_y = dvdr_y + 8
            dsc_txt = str(self._get_field(slctd_prk, 'desc', ''))
            lns = self._wrap_text(dsc_txt, fnt_dsc, rght_w - 5)
            crr_y = dsc_y
            for line in lns:
                if crr_y + fnt_dsc.get_height() > bttm_y + 10:
                    break
                srf = fnt_dsc.render(line, True, color)
                self.screen.blit(srf, (rght_x, crr_y))
                crr_y += fnt_dsc.get_height() + 2

    def _render_fallout4_ui(self): # You thought it was NV? Guess again
        clr_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        fnt_mn = self._get_font(11)
        fnt_smll = self._get_font(9)
        x_lft = self.draw_space.x + 8
        y_strt = self.draw_space.y + 8
        lst_wdth = 125
        ln_hght = 15
        mx_vsbl_tms = 8
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + mx_vsbl_tms:
            self.scroll_offset = self.selected_index - mx_vsbl_tms + 1
        vsbl_prks = self.perks_data[self.scroll_offset:self.scroll_offset + mx_vsbl_tms]
        for i, perk in enumerate(vsbl_prks):
            ctl_dx = self.scroll_offset + i
            is_slctd = ctl_dx == self.selected_index
            prk_nm = str(self._get_field(perk, 'name', ''))
            tm_y = y_strt + i * ln_hght
            if is_slctd:
                bg_rct = pygame.Rect(x_lft - 2, tm_y, lst_wdth, ln_hght - 2)
                pygame.draw.rect(self.screen, clr_lght, bg_rct)
                txt_srf = fnt_mn.render(prk_nm, True, (0, 0, 0))
            else:
                txt_srf = fnt_mn.render(prk_nm, True, clr_lght)
            self.screen.blit(txt_srf, (x_lft, tm_y))
        if 0 <= self.selected_index < len(self.perks_data):
            slctd_prk = self.perks_data[self.selected_index]
            x_rght = x_lft + lst_wdth + 12
            rght_wdth = self.draw_space.right - x_rght - 8
            prk_mg = self._get_perk_image(slctd_prk, max_size=(rght_wdth, 105))
            crrnt_y = y_strt
            if prk_mg:
                clrd_mg = colorize_surface(prk_mg, clr_lght)
                mg_x = x_rght + (rght_wdth - clrd_mg.get_width()) // 2
                self.screen.blit(clrd_mg, (mg_x, crrnt_y))
                crrnt_y += clrd_mg.get_height() + 4
            rnk = int(self._get_field(slctd_prk, 'rank', 1))
            rnk_dscs = self._get_field(slctd_prk, 'rank_descs', None)
            rnks_dt = self._get_field(slctd_prk, 'ranks', None)
            if rnk_dscs and isinstance(rnk_dscs, (list, tuple)) and (len(rnk_dscs) > 0):
                mx_rnk = int(self._get_field(slctd_prk, 'max_rank', len(rnk_dscs)))
                idx = max(0, min(rnk - 1, len(rnk_dscs) - 1))
                dsc_txt = str(rnk_dscs[idx])
            elif rnks_dt and isinstance(rnks_dt, (list, tuple)) and (len(rnks_dt) > 0):
                mx_rnk = int(self._get_field(slctd_prk, 'max_rank', len(rnks_dt)))
                idx = max(0, min(rnk - 1, len(rnks_dt) - 1))
                r_tm = rnks_dt[idx]
                dsc_txt = r_tm.get('desc', '') if isinstance(r_tm, dict) else str(r_tm)
            else:
                mx_rnk = int(self._get_field(slctd_prk, 'max_rank', 5))
                dsc_txt = str(self._get_field(slctd_prk, 'desc', ''))
            str_spcng = 14
            ttl_strs_w = mx_rnk * str_spcng
            strt_str_x = x_rght + (rght_wdth - ttl_strs_w) // 2 + str_spcng // 2
            for r in range(mx_rnk):
                cx = strt_str_x + r * str_spcng
                cy = crrnt_y + 4
                is_flld = r < rnk
                draw_star(self.screen, clr_lght, (cx, cy), outer_radius=5, inner_radius=1.8, filled=is_flld, width=1)
            crrnt_y += 12
            lns = self._wrap_text(dsc_txt, fnt_smll, rght_wdth)
            dsc_ln_h = fnt_smll.get_height() + 1
            for line in lns:
                if crrnt_y + dsc_ln_h > self.draw_space.bottom - 2:
                    break
                srf = fnt_smll.render(line, True, clr_lght)
                self.screen.blit(srf, (x_rght, crrnt_y))
                crrnt_y += dsc_ln_h