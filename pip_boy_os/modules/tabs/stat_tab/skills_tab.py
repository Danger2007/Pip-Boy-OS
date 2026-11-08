import os
import pygame
import settings
_SKILL_ICON_CACHE = {}

def find_image_file(skill_name):
    cln_nm = skill_name.strip()
    nm_mp = {'big guns': 'Guns', 'small guns': 'Guns', 'energy weapons': 'EnergyWeapons', 'melee weapons': 'MeleeWeapons'}
    key_lwr = cln_nm.lower()
    if key_lwr in nm_mp:
        trgt_nm = nm_mp[key_lwr]
    else:
        trgt_nm = ''.join((wrd.capitalize() for wrd in cln_nm.split()))
    possible_filenames = [f'{trgt_nm}.webp', f'{trgt_nm}.png', f'{trgt_nm}.dds', f"{cln_nm.lower().replace(' ', '_')}.webp"]
    base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [os.path.join(base_dir, 'images', 'new_vegas_icons', 'skills_nv'), os.path.join(base_dir, 'images', 'skills'), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'new_vegas_icons', 'skills_nv')]
    for s_dir in search_dirs:
        for fnm in possible_filenames:
            full_path = os.path.normpath(os.path.join(s_dir, fnm))
            if os.path.exists(full_path):
                return full_path
    print(f"[DEBUG PIP-BOY] Image NOT found for '{skill_name}' (searched for {trgt_nm}.webp)")
    return None
def load_skill_icon(skill_name):
    if skill_name in _SKILL_ICON_CACHE:
        return _SKILL_ICON_CACHE[skill_name]
    file_path = find_image_file(skill_name)
    if not file_path:
        _SKILL_ICON_CACHE[skill_name] = None
        return None
    try:
        img = pygame.image.load(file_path).convert_alpha()
        _SKILL_ICON_CACHE[skill_name] = img
        return img
    except:
        try:
            from PIL import Image
            pl_mg = Image.open(file_path).convert('RGBA')
            data = pl_mg.tobytes()
            img = pygame.image.fromstring(data, pl_mg.size, 'RGBA').convert_alpha()
            _SKILL_ICON_CACHE[skill_name] = img
            return img
        except Exception as e_pl:
            print(f'[DEBUG PIP-BOY] Error image decoding {file_path}: {e_pl}')
    _SKILL_ICON_CACHE[skill_name] = None
    return None

def colorize_surface(surface, color): # too many colorize/tint 
    if surface is None:
        return None
    tntd = surface.copy()
    r, g, b = (color[0], color[1], color[2])
    tntd.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tntd

def render_multiline_text(screen, text, font, color, rect):
    wrds = text.split(' ')
    lns = []
    crrnt_ln = []
    for wrd in wrds:
        tst_ln = ' '.join(crrnt_ln + [wrd])
        if font.size(tst_ln)[0] <= rect.width:
            crrnt_ln.append(wrd)
        else:
            if crrnt_ln:
                lns.append(' '.join(crrnt_ln))
            crrnt_ln = [wrd]
    if crrnt_ln:
        lns.append(' '.join(crrnt_ln))
    y = rect.top
    ln_spcng = font.get_height() + 3
    for line in lns:
        if y + font.get_height() > rect.bottom:
            break
        txt_srfc = font.render(line, True, color)
        screen.blit(txt_srfc, (rect.left, y))
        y += ln_spcng
def draw_skills_tab(screen, skills_data, selected_index, color, base_font, screen_w, screen_h):
    if not skills_data:
        return
    FONT_SIZE = 12
    skll_fnt = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE)
    LINE_HEIGHT = 18
    lft_x = int(screen_w * 0.12)
    lft_w = int(screen_w * 0.36)
    rght_x = int(screen_w * 0.52)
    rght_w = int(screen_w * 0.45)
    tp_y = int(screen_h * 0.18)
    bttm_y = int(screen_h * 0.82)
    vlbl_h = bttm_y - tp_y
    MAX_VISIBLE_ITEMS = max(1, vlbl_h // LINE_HEIGHT)
    scrll_ffst = max(0, min(selected_index - MAX_VISIBLE_ITEMS // 2, len(skills_data) - MAX_VISIBLE_ITEMS))
    scrll_ffst = max(0, scrll_ffst)
    sldr_x = lft_x - 18
    rrw_w = 5
    rrw_h = 8
    ntch = 3
    tp_rrw_y = tp_y
    up_rrw_pts = [(sldr_x, tp_rrw_y), (sldr_x + rrw_w, tp_rrw_y + rrw_h), (sldr_x, tp_rrw_y + rrw_h - ntch), (sldr_x - rrw_w, tp_rrw_y + rrw_h)]
    pygame.draw.polygon(screen, color, up_rrw_pts)
    bttm_rrw_y = bttm_y
    dwn_rrw_pts = [(sldr_x, bttm_rrw_y), (sldr_x + rrw_w, bttm_rrw_y - rrw_h), (sldr_x, bttm_rrw_y - rrw_h + ntch), (sldr_x - rrw_w, bttm_rrw_y - rrw_h)]
    pygame.draw.polygon(screen, color, dwn_rrw_pts)
    trck_tp = tp_rrw_y + rrw_h - ntch + 5
    trck_bttm = bttm_rrw_y - rrw_h + ntch - 5
    trck_lngth = trck_bttm - trck_tp
    ttl_tms = len(skills_data)
    if ttl_tms > MAX_VISIBLE_ITEMS:
        br_lngth = max(12, int(trck_lngth * (MAX_VISIBLE_ITEMS / ttl_tms)))
        mx_scrll = ttl_tms - MAX_VISIBLE_ITEMS
        scrll_rt = scrll_ffst / mx_scrll if mx_scrll > 0 else 0
        br_tp = trck_tp + int(scrll_rt * (trck_lngth - br_lngth))
        br_bttm = br_tp + br_lngth
        pygame.draw.line(screen, color, (sldr_x, br_tp), (sldr_x, br_bttm), 2)
    vsbl_sklls = skills_data[scrll_ffst:scrll_ffst + MAX_VISIBLE_ITEMS]
    for dx_in_vw, skll in enumerate(vsbl_sklls):
        ctl_ndx = scrll_ffst + dx_in_vw
        y_ps = tp_y + dx_in_vw * LINE_HEIGHT
        is_slctd = ctl_ndx == selected_index
        if is_slctd:
            slct_rct = pygame.Rect(lft_x - 4, y_ps, lft_w + 8, LINE_HEIGHT - 1)
            pygame.draw.rect(screen, color, slct_rct, 1)
        nm_srf = skll_fnt.render(skll['name'], True, color)
        screen.blit(nm_srf, (lft_x, y_ps + (LINE_HEIGHT - nm_srf.get_height()) // 2))
        vl_str = str(skll.get('value', 0))
        if skll.get('mod'):
            vl_str += f" ({skll['mod']})"
        vl_srf = skll_fnt.render(vl_str, True, color)
        vl_x = lft_x + lft_w - vl_srf.get_width()
        screen.blit(vl_srf, (vl_x, y_ps + (LINE_HEIGHT - vl_srf.get_height()) // 2))
    if 0 <= selected_index < len(skills_data):
        slctd_skll = skills_data[selected_index]
        mg_h = int(vlbl_h * 0.6)
        mg_rct = pygame.Rect(rght_x, tp_y, rght_w, mg_h)
        cn_srfc = load_skill_icon(slctd_skll['name'])
        if cn_srfc:
            rg_w, rg_h = cn_srfc.get_size()
            scl = min(mg_rct.width / rg_w, mg_rct.height / rg_h)
            nw_sz = (int(rg_w * scl), int(rg_h * scl))
            scld_mg = pygame.transform.smoothscale(cn_srfc, nw_sz)
            clrd_mg = colorize_surface(scld_mg, color)
            cntr_x = rght_x + (rght_w - nw_sz[0]) // 2
            cntr_y = tp_y + (mg_h - nw_sz[1]) // 2
            screen.blit(clrd_mg, (cntr_x, cntr_y))
        dvdr_y = tp_y + mg_h + 5
        pygame.draw.line(screen, color, (rght_x, dvdr_y), (rght_x + rght_w, dvdr_y), 1)
        pygame.draw.line(screen, color, (rght_x + rght_w, dvdr_y), (rght_x + rght_w, dvdr_y + 7), 1)
        dsc_y = dvdr_y + 5
        skll_fnt2 = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE - 3)
        dsc_rct = pygame.Rect(rght_x, dsc_y, rght_w - 5, bttm_y + 10)
        render_multiline_text(screen, slctd_skll.get('desc', ''), skll_fnt2, color, dsc_rct)