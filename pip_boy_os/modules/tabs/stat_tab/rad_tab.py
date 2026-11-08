import pygame
import random
import math
import settings

class RadSubtab:

    def __init__(self, screen, draw_space):
        self.screen = screen
        self.draw_space = draw_space
        self.font = pygame.font.Font(settings.MAIN_FONT_PATH, 11)
        self.font_large = pygame.font.Font(settings.MAIN_FONT_PATH, 13)
        self.font_title = pygame.font.Font(settings.MAIN_FONT_PATH, 14)

    def render(self, player_data, ui_style):
        if str(ui_style).lower() in ('fallout_nv', 'fallout_new_vegas'):
            self._render_nv(player_data)
        else:
            self._render_fo4(player_data)
    def _get_danger_color(self, base_color):
        r, g, b = base_color[:3]
        is_wht_or_gr = max(r, g, b) - min(r, g, b) < 30 and max(r, g, b) > 170
        if is_wht_or_gr or (g > r + 30 and g > b + 30):
            return (255, 30, 30)
        cmp_r, cmp_g, cmp_b = (255 - r, 255 - g, 255 - b)
        if cmp_r + cmp_g + cmp_b < 120:
            return (255, 30, 30)
        return (cmp_r, cmp_g, cmp_b)

    def _draw_smooth_arc(self, surf, color, center, radius, start_deg, end_deg, width=2):
        cx, cy = center
        stps = max(10, int(abs(end_deg - start_deg) * 4))
        pnts_tr = []
        pnts_nnr = []
        r_out = radius
        r_in = radius - width
        for i in range(stps + 1):
            deg = start_deg + (end_deg - start_deg) * (i / stps)
            rad = math.radians(deg)
            cs_a = math.cos(rad)
            sn_a = math.sin(rad)
            x_out = cx + r_out * cs_a
            y_out = cy - r_out * sn_a
            x_in = cx + r_in * cs_a
            y_in = cy - r_in * sn_a
            pnts_tr.append((x_out, y_out))
            pnts_nnr.append((x_in, y_in))
        pl_pts = pnts_tr + pnts_nnr[::-1]
        pygame.draw.polygon(surf, color, pl_pts) # optimized
    def _get_rad_values(self, player_data):
        bs_rds = player_data.get('rads', getattr(settings, 'RADIATION_VALUE', 312))
        flcttn_md = str(getattr(settings, 'RADIATION_FLUCTUATION', 'Fixed')).lower()
        JITTER_AMPLITUDE = 8.0
        JITTER_INTERVAL_MS = 50
        MAX_RAD_CHANGE_PER_SEC = 25.0
        TARGET_CHANGE_INTERVAL_MS = 2500
        crrnt_tcks = pygame.time.get_ticks()
        if flcttn_md == 'none':
            if '_rad_state' in player_data:
                del player_data['_rad_state']
            return (float(bs_rds), float(bs_rds))
        elif flcttn_md in ['fixed', 'static']:
            crrnt_mn = float(bs_rds)
            if '_rad_state' in player_data:
                del player_data['_rad_state']
        else:
            if '_rad_state' not in player_data:
                player_data['_rad_state'] = {'current_mean': float(bs_rds), 'target_mean': random.uniform(0.0, 1000.0), 'last_ticks': crrnt_tcks, 'last_target_change': crrnt_tcks}
            st = player_data['_rad_state']
            dt = (crrnt_tcks - st['last_ticks']) / 1000.0
            st['last_ticks'] = crrnt_tcks
            if crrnt_tcks - st['last_target_change'] > TARGET_CHANGE_INTERVAL_MS:
                st['target_mean'] = random.uniform(0.0, 1000.0)
                st['last_target_change'] = crrnt_tcks
            dff = st['target_mean'] - st['current_mean']
            if abs(dff) > 0.01:
                mx_stp = MAX_RAD_CHANGE_PER_SEC * dt
                stp = max(-mx_stp, min(mx_stp, dff))
                st['current_mean'] += stp
            crrnt_mn = st['current_mean']
        jttr_sd = crrnt_tcks // JITTER_INTERVAL_MS
        jttr_rng = random.Random(jttr_sd)
        mcr_jttr = jttr_rng.uniform(-JITTER_AMPLITUDE, JITTER_AMPLITUDE)
        dspl_rds = max(0.0, min(1000.0, crrnt_mn + mcr_jttr))
        return (dspl_rds, crrnt_mn)
    def _render_nv(self, player_data):
        COLOR_NV = settings.PIP_BOY_LIGHT
        scrn_w = self.screen.get_width()
        rd_rsst = player_data.get('rad_resist', getattr(settings, 'RAD_RESIST', 6))
        dspl_rds, crrnt_mn = self._get_rad_values(player_data)
        dspl_rds_nt = int(round(dspl_rds))
        qck_rd_tms = player_data.get('quick_rad_items', ['(1) RadAway A)', '(3) Rad-X X)'])
        tm_y = 45
        for tm_str in qck_rd_tms: 
            tm_txt = self.font.render(tm_str, True, COLOR_NV)
            tm_rct = tm_txt.get_rect(right=scrn_w - 15, top=tm_y)
            self.screen.blit(tm_txt, tm_rct)
            tm_y += 25
        cntr_x = 115
        rght_x = scrn_w - 10
        ff_tp_y = 120
        ff_bttm_y = 170
        if crrnt_mn >= 800:
            rd_ff_str = '-3 END, -2 AGL, -2 STR'
        elif crrnt_mn >= 600:
            rd_ff_str = '-2 END, -2 AGL'
        elif crrnt_mn >= 400:
            rd_ff_str = '-2 END, -1 AGL'
        elif crrnt_mn >= 200:
            rd_ff_str = '-1 END'
        else:
            rd_ff_str = 'NONE'# stile from game (beautiful tbh)
        pygame.draw.line(self.screen, COLOR_NV, (cntr_x, ff_tp_y), (rght_x, ff_tp_y), 1)
        pygame.draw.line(self.screen, COLOR_NV, (rght_x, ff_tp_y), (rght_x, ff_bttm_y - 17), 1)
        ff_lbl = self.font_large.render('EFF', True, COLOR_NV)
        ff_vl = self.font_large.render(rd_ff_str, True, COLOR_NV)
        self.screen.blit(ff_lbl, (cntr_x, ff_tp_y + 2))
        self.screen.blit(ff_vl, ff_vl.get_rect(right=rght_x - 15, top=ff_tp_y + 2))
        pygame.draw.line(self.screen, COLOR_NV, (0, ff_bttm_y), (cntr_x - 5, ff_bttm_y), 1)
        bt_y = ff_bttm_y + 2
        pygame.draw.line(self.screen, COLOR_NV, (cntr_x - 5, ff_bttm_y), (cntr_x - 5, ff_bttm_y + 20), 1)
        rr_lbl = self.font.render('RAD RESIST', True, COLOR_NV)
        rr_vl = self.font.render(f'{rd_rsst}%', True, COLOR_NV)
        self.screen.blit(rr_lbl, (10, bt_y))
        self.screen.blit(rr_vl, rr_vl.get_rect(right=cntr_x - 10, top=bt_y))
        rds_lbl = self.font.render('RADS', True, COLOR_NV)
        rds_x = cntr_x
        self.screen.blit(rds_lbl, (rds_x, bt_y))
        mtr_x1 = rds_x + rds_lbl.get_width() + 10
        mtr_x2 = rght_x - 3
        mtr_y = ff_bttm_y
        mtr_w = max(10, mtr_x2 - mtr_x1)
        pygame.draw.line(self.screen, COLOR_NV, (cntr_x, mtr_y), (rght_x, mtr_y), 1)
        pygame.draw.line(self.screen, COLOR_NV, (rght_x, ff_bttm_y), (rght_x, ff_bttm_y + 20), 1)
        lbl_500 = self.font.render('500', True, COLOR_NV)
        lbl_1000 = self.font.render('1000', True, COLOR_NV)
        self.screen.blit(lbl_500, lbl_500.get_rect(center=(mtr_x1 + mtr_w // 2, mtr_y - 7)))
        self.screen.blit(lbl_1000, lbl_1000.get_rect(right=mtr_x2, bottom=mtr_y - 2))
        tr_0 = [(mtr_x1 - 5, mtr_y), (mtr_x1, mtr_y), (mtr_x1, mtr_y + 6)]
        pygame.draw.polygon(self.screen, COLOR_NV, tr_0)
        tr_1000 = [(rght_x, mtr_y), (mtr_x2 - 2, mtr_y), (mtr_x2 - 2, mtr_y + 6)]
        pygame.draw.polygon(self.screen, COLOR_NV, tr_1000)
        for val in [200, 400, 600, 800]:
            tx = mtr_x1 + int(val / 1000.0 * mtr_w)
            pygame.draw.line(self.screen, COLOR_NV, (tx, mtr_y), (tx, mtr_y + 7), 1)
        for val in [50, 150, 250, 350, 450, 550, 650, 750, 850, 950]:
            tx = mtr_x1 + int(val / 1000.0 * mtr_w)
            pygame.draw.line(self.screen, COLOR_NV, (tx, mtr_y), (tx, mtr_y + 4), 1)
        RIGHT_ALIGN_OFFSET = 2
        ffctv_x2 = mtr_x2 - RIGHT_ALIGN_OFFSET
        ffctv_w = ffctv_x2 - mtr_x1
        ndctr_x = mtr_x1 + int(dspl_rds_nt / 1000.0 * ffctv_w)
        ndctr_x = max(mtr_x1, min(ffctv_x2, ndctr_x))
        nd_txt = self.font.render(f'{dspl_rds_nt}', True, COLOR_NV)
        self.screen.blit(nd_txt, nd_txt.get_rect(right=ndctr_x - 5, top=mtr_y + 15))
        rrw_tp_y = mtr_y + 9
        rrw_bt_y = mtr_y + 22
        hd_pts = [(ndctr_x, rrw_tp_y), (ndctr_x - 4, rrw_tp_y + 5), (ndctr_x + 4, rrw_tp_y + 5)]
        pygame.draw.polygon(self.screen, COLOR_NV, hd_pts)
        pygame.draw.line(self.screen, COLOR_NV, (ndctr_x, rrw_tp_y), (ndctr_x, rrw_bt_y + 7), 1)

    def _render_fo4(self, player_data):
        COLOR_LIGHT = settings.PIP_BOY_LIGHT
        COLOR_DARK = settings.PIP_BOY_DARK
        DANGER_COLOR = self._get_danger_color(COLOR_LIGHT)
        dspl_rds, _ = self._get_rad_values(player_data)
        rd_rsst = player_data.get('rad_resist', getattr(settings, 'RAD_RESIST', 10))
        mgn = 8
        gg_w = self.draw_space.width - mgn * 2
        gg_h = 126 # similaar to geiger counter (but opposite in a way)
        gg_bx = pygame.Rect(self.draw_space.left + mgn, self.draw_space.top + 2, gg_w, gg_h)
        pygame.draw.rect(self.screen, COLOR_DARK, gg_bx)
        pygame.draw.rect(self.screen, COLOR_LIGHT, gg_bx, 1)
        cx = gg_bx.centerx
        cy = gg_bx.top + 98
        radius = 78
        self._draw_smooth_arc(self.screen, COLOR_LIGHT, (cx, cy), radius=radius, start_deg=51, end_deg=155, width=2)
        self._draw_smooth_arc(self.screen, DANGER_COLOR, (cx, cy), radius=radius, start_deg=25, end_deg=51.5, width=2)
        tcks = [0, 200, 400, 600, 800, 1000]
        for val in tcks:
            frc = val / 1000.0
            ngl_dg = 155 - frc * 130
            ngl_rd = math.radians(ngl_dg)
            col = DANGER_COLOR if val >= 800 else COLOR_LIGHT
            x1 = cx + (radius + 1) * math.cos(ngl_rd)
            y1 = cy - (radius + 1) * math.sin(ngl_rd)
            x2 = cx + (radius - 11) * math.cos(ngl_rd)
            y2 = cy - (radius - 11) * math.sin(ngl_rd)
            pygame.draw.line(self.screen, col, (int(x1), int(y1)), (int(x2), int(y2)), 2)
            xl = cx + (radius - 24) * math.cos(ngl_rd)
            yl = cy - (radius - 24) * math.sin(ngl_rd)
            t_srf = self.font.render(str(val), True, col)
            t_rct = t_srf.get_rect(center=(int(xl), int(yl)))
            self.screen.blit(t_srf, t_rct)
        for val in range(50, 1000, 50):
            if val in tcks:
                continue
            frc = val / 1000.0
            ngl_dg = 155 - frc * 130
            ngl_rd = math.radians(ngl_dg)
            col = DANGER_COLOR if val >= 800 else COLOR_LIGHT
            tck_ln = 8 if val % 100 == 0 else 5
            x1 = cx + (radius + 1) * math.cos(ngl_rd)
            y1 = cy - (radius + 1) * math.sin(ngl_rd)
            x2 = cx + (radius - tck_ln) * math.cos(ngl_rd)
            y2 = cy - (radius - tck_ln) * math.sin(ngl_rd)
            pygame.draw.line(self.screen, col, (int(x1), int(y1)), (int(x2), int(y2)), 1)
        nt_srf = self.font.render('RAD / h', True, COLOR_LIGHT)
        self.screen.blit(nt_srf, nt_srf.get_rect(center=(cx, cy - 30)))
        ndl_frc = max(0.0, min(1.0, dspl_rds / 1000.0))
        ndl_ngl_dg = 155 - ndl_frc * 130
        ndl_ngl_rd = math.radians(ndl_ngl_dg)
        nx = cx + (radius - 3) * math.cos(ndl_ngl_rd)
        ny = cy - (radius - 3) * math.sin(ndl_ngl_rd)
        pygame.draw.line(self.screen, COLOR_LIGHT, (cx, cy), (int(nx), int(ny)), 2)
        pygame.draw.circle(self.screen, COLOR_LIGHT, (cx, cy), 4)
        pygame.draw.circle(self.screen, COLOR_DARK, (cx, cy), 2)
        rdt_srf = self.font_large.render(f'{dspl_rds:.1f}', True, COLOR_LIGHT)
        self.screen.blit(rdt_srf, rdt_srf.get_rect(center=(cx, cy + 14)))
        bttm_tp = gg_bx.bottom + 6
        bx_w = (gg_w - 8) // 2
        bx_h = 44
        ff_bx = pygame.Rect(gg_bx.left, bttm_tp, bx_w, bx_h)
        pygame.draw.rect(self.screen, COLOR_DARK, ff_bx)
        pygame.draw.rect(self.screen, COLOR_LIGHT, ff_bx, 1)
        if dspl_rds >= 800:
            ff_ttl = 'CRITICAL POISONING'
            ff_dsc = '-3 END, -2 AGI, -2 STR'
        elif dspl_rds >= 600:
            ff_ttl = 'SEVERE POISONING'
            ff_dsc = '-2 END, -2 AGI'
        elif dspl_rds >= 400:
            ff_ttl = 'MODERATE POISONING'
            ff_dsc = '-2 END, -1 AGI'
        elif dspl_rds >= 200:
            ff_ttl = 'MINOR POISONING'
            ff_dsc = '-1 END'
        else:
            ff_ttl = 'NORMAL STATUS'
            ff_dsc = 'No Rad Effects'
        e_ttl_srf = self.font.render(ff_ttl, True, COLOR_LIGHT)
        e_dsc_srf = self.font.render(ff_dsc, True, COLOR_LIGHT)
        self.screen.blit(e_ttl_srf, (ff_bx.left + 6, ff_bx.top + 5))
        self.screen.blit(e_dsc_srf, (ff_bx.left + 6, ff_bx.top + 22))
        aid_bx = pygame.Rect(ff_bx.right + 8, bttm_tp, bx_w, bx_h)
        pygame.draw.rect(self.screen, COLOR_DARK, aid_bx)
        pygame.draw.rect(self.screen, COLOR_LIGHT, aid_bx, 1)
        r_rs_srf = self.font.render(f'RAD RESIST: {rd_rsst}%', True, COLOR_LIGHT)
        r_d1 = self.font.render('RadAway: (2)  Rad-X: (1)', True, COLOR_LIGHT)
        self.screen.blit(r_rs_srf, (aid_bx.left + 6, aid_bx.top + 5))
        self.screen.blit(r_d1, (aid_bx.left + 6, aid_bx.top + 22))