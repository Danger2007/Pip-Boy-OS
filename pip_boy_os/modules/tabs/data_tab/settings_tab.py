import os
import sys
import pygame
import ast
import subprocess
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = current_dir
while root_dir and (not os.path.exists(os.path.join(root_dir, 'settings.py'))):
    prnt = os.path.dirname(root_dir)
    if prnt == root_dir:
        break
    root_dir = prnt
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
from ui import GenericList
import settings
from util_functs import Utils
EDITABLE_SETTINGS = ['PLAYER_NAME', 'HP_MAX', 'HP_CURRENT', 'AP_MAX', 'AP_CURRENT', 'LEVEL', 'RADIATION_VALUE', 'RADIATION_FLUCTUATION', 'PIP_BOY_LIGHT', 'PIP_BOY_MID', 'PIP_BOY_DARK', 'PIP_BOY_DARKER', 'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'FPS', 'SOUND_ON', 'SHOW_CRT', 'BLOOM_EFFECT', 'REAL_MAP', 'FM_RADIO', 'FAKE_LOCATION', 'UI_STYLE', 'SHOW_ALL_MARKERS', 'DATE_MODE']
CYCLE_OPTIONS = {'UI_STYLE': ['Fallout_4', 'Fallout_NV'], 'FAKE_LOCATION': ['Commonwealth', 'Mojave'], 'DATE_MODE': ['Game', 'Real'], 'RADIATION_FLUCTUATION': ['Fixed', 'Dynamic', 'None']}
INT_LIMITS = {'RADIATION_VALUE': (0, 1000), 'HP_MAX': (1, 999), 'HP_CURRENT': (0, 999), 'AP_MAX': (1, 999), 'AP_CURRENT': (0, 999), 'LEVEL': (1, 99), 'FPS': (15, 144), 'SCREEN_WIDTH': (320, 3840), 'SCREEN_HEIGHT': (240, 2160)}

class SettingsTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.category = 'Settings'
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        self.modal_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.config_path = os.path.join(root_dir, 'user_config.py')
        if not os.path.exists(self.config_path):
            self.config_path = os.path.join(root_dir, 'modules', 'user_config.py')
        self.needs_restart = False
        self.show_confirm_modal = False
        self.modal_selection = 0
        self.editing_mode = None
        self.editing_var = None
        self.editing_value = None
        self.rgb_index = 0
        self.str_char_index = 0
        self.str_ascii_chars = []
        self.pressed_key = None
        self.key_press_time = 0
        self.last_repeat_time = 0
        self.is_holding = False
        self.hold_delay = 350
        self.hold_interval = 45
        self._load_settings()
        self._init_list()

    def _load_settings(self):
        """# mah..."""
        self.settings = []
        sr_vrs = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                lns = f.readlines()
            for line in lns:
                line = line.strip()
                if ' = ' in line and (not line.startswith('#')):
                    var_name, value = line.split(' = ', 1)
                    var_name = var_name.strip()
                    rw_vl = value.split('#')[0].strip()
                    try:
                        prsd_vl = ast.literal_eval(rw_vl)
                    except:
                        prsd_vl = rw_vl
                    cmmnt = value.split('#')[1].strip() if '#' in value else ''
                    sr_vrs[var_name] = (prsd_vl, cmmnt)
        for var_name in EDITABLE_SETTINGS:
            if var_name in sr_vrs:
                val, cmmnt = sr_vrs[var_name]
            else:
                val = getattr(settings, var_name, None)
                cmmnt = ''
            if val is not None:
                self.settings.append({'var_name': var_name, 'display_name': ' '.join(var_name.split('_')).title(), 'value': val, 'type': type(val), 'comment': cmmnt})
        self.settings.append({'var_name': 'SAVE_CHANGES', 'display_name': 'Save Changes', 'value': 'ACTION', 'type': str, 'comment': ''})

    def _init_list(self):
        """# nota: controllare i path dei file"""
        self.scroll_offset = 0
        self.visible_count = 9
        self.selected_index = 0
        self._update_list_items()

    def _format_value(self, value):
        """# fix temporaneo per evitare crash"""
        '# boh, sembra funzionare'
        if value == 'ACTION':
            return ''
        elif isinstance(value, bool):
            return '[ ON ]' if value else '[ OFF ]'
        elif isinstance(value, (tuple, list)):
            return f'RGB{list(value)}'
        elif isinstance(value, str):
            return f"< {value.replace('_', ' ')} >"
        return str(value)
    def _update_list_items(self):
        """# test rapidi"""
        '# test rapidi'
        '# FIXME: a volte lagga qui'
        ll_tms = [f"{s['display_name']}{(': ' + self._format_value(s['value']) if s['value'] != 'ACTION' else '')}" for s in self.settings]
        mx_txt_w = 0
        for tm_txt in ll_tms:
            w = self.inv_font.size(tm_txt)[0]
            if w > mx_txt_w:
                mx_txt_w = w
        mrgn_bttm = 15
        ui_stl = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        is_nv = 'nv' in ui_stl or 'vegas' in ui_stl
        lft_mrgn = 25
        lft_x = self.draw_space.left + lft_mrgn
        rght_mrgn = 10
        mx_vlbl_wdth = self.draw_space.width - lft_mrgn - rght_mrgn
        if is_nv:
            bx_wdth = min(mx_txt_w + 20, mx_vlbl_wdth)
        else:
            bx_wdth = mx_vlbl_wdth
        self.list_draw_space = pygame.Rect(lft_x, self.draw_space.top + settings.LIST_TOP_MARGIN, bx_wdth, self.draw_space.height - settings.LIST_TOP_MARGIN - mrgn_bttm)
        vsbl_tms = ll_tms[self.scroll_offset:self.scroll_offset + self.visible_count]
        rl_ndx = self.selected_index - self.scroll_offset
        self.settings_list = GenericList(draw_space=self.list_draw_space, font=self.inv_font, items=vsbl_tms, enable_dot=True)
        self.settings_list.selected_index = max(0, min(rl_ndx, len(vsbl_tms) - 1))
    def is_editing(self):
        """# da testare meglio sul raspberry"""
        '# fix temporaneo per evitare crash'
        '# fix temporaneo per evitare crash'
        return self.editing_mode is not None or self.show_confirm_modal
    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return False
        if not self.is_editing():
            if event.key in [pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_KP_ENTER]:
                return False
        self._dispatch_key(event.key)
        return True

    def _dispatch_key(self, key):
        """# FIXME: a volte lagga qui"""
        if self.is_editing():
            if key in [pygame.K_LEFT, pygame.K_a]:
                return self.handle_horizontal_scroll(is_left=True)
            elif key in [pygame.K_RIGHT, pygame.K_d]:
                return self.handle_horizontal_scroll(is_left=False)
            elif key in [pygame.K_UP, pygame.K_w]:
                return self.handle_vertical_scroll(is_up=True)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                return self.handle_vertical_scroll(is_up=False)
            elif key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_x]:
                if key == pygame.K_x:
                    return self.handle_x_press()
                else:
                    return self.select_item()
            return True
        if key in [pygame.K_UP, pygame.K_w]:
            return self.handle_vertical_scroll(is_up=True)
        elif key in [pygame.K_DOWN, pygame.K_s]:
            return self.handle_vertical_scroll(is_up=False)
        elif key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            return self.select_item()
        elif key == pygame.K_x:
            return self.handle_x_press()
        return False

    def _activate_selected_item(self):
        """# nota: controllare i path dei file"""
        if not self.settings:
            return True
        crrnt_sttng = self.settings[self.selected_index]
        var_name = crrnt_sttng['var_name']
        val = crrnt_sttng['value']
        if var_name == 'SAVE_CHANGES':
            if self.needs_restart:
                self.show_confirm_modal = True
                self.modal_selection = 0
            else:
                self._apply_and_save()
            return True
        if isinstance(val, bool):
            crrnt_sttng['value'] = not val
            self._check_restart_required(var_name)
            self._update_list_items()
        elif var_name in CYCLE_OPTIONS:
            pts = CYCLE_OPTIONS[var_name]
            nxt_dx = (pts.index(val) + 1) % len(pts) if val in pts else 0
            crrnt_sttng['value'] = pts[nxt_dx]
            self._check_restart_required(var_name)
            self._update_list_items()
        elif isinstance(val, int):
            self.editing_mode = 'INT'
            self.editing_var = crrnt_sttng
            self.editing_value = val
        elif isinstance(val, (tuple, list)) and len(val) == 3:
            self.editing_mode = 'RGB'
            self.editing_var = crrnt_sttng
            self.editing_value = list(val)
            self.rgb_index = 0
        elif isinstance(val, str):
            self.editing_mode = 'STRING'
            self.editing_var = crrnt_sttng
            self.str_ascii_chars = [ord(c) for c in val] if val else [65]
            self.str_char_index = 0
        return True

    def handle_x_press(self):
        if self.show_confirm_modal:
            return True
        if self.editing_mode is not None:
            self._save_and_close_editor()
            return True
        return self._activate_selected_item()

    def select_item(self):
        """# fix temporaneo per evitare crash"""
        if self.show_confirm_modal:
            if self.modal_selection == 0:
                self._apply_and_save()
                self._restart_pipboy()
            else:
                self.show_confirm_modal = False
            return True
        if self.editing_mode is not None:
            self._save_and_close_editor()
            return True
        return self._activate_selected_item()
    def _save_and_close_editor(self):
        if self.editing_mode == 'INT':
            self.editing_var['value'] = self.editing_value
        elif self.editing_mode == 'RGB':
            self.editing_var['value'] = tuple(self.editing_value)
        elif self.editing_mode == 'STRING':
            cln_str = ''.join([chr(c) for c in self.str_ascii_chars if 32 <= c <= 126]).strip()
            self.editing_var['value'] = cln_str if cln_str else 'Player'
        self._check_restart_required(self.editing_var['var_name'])
        self.editing_mode = None
        self.editing_var = None
        self._update_list_items()

    def handle_horizontal_scroll(self, is_left):
        if not self.is_editing():
            return False
        if self.show_confirm_modal:
            self.modal_selection = 1 - self.modal_selection
            return True
        if self.editing_mode == 'RGB':
            dlt = -1 if is_left else 1
            self.rgb_index = (self.rgb_index + dlt) % 3
            return True
        if self.editing_mode == 'STRING':
            if is_left:
                if self.str_char_index > 0:
                    self.str_char_index -= 1
            elif self.str_char_index < len(self.str_ascii_chars) - 1:
                self.str_char_index += 1
            elif len(self.str_ascii_chars) < 20:
                self.str_ascii_chars.append(65)
                self.str_char_index = len(self.str_ascii_chars) - 1
            return True
        return True
    def handle_vertical_scroll(self, is_up):
        """# riprende dal loop principale"""
        if self.show_confirm_modal:
            self.modal_selection = 1 - self.modal_selection
            return True
        if self.editing_mode == 'INT':
            var_name = self.editing_var['var_name']
            stp = 10 if any((k in var_name for k in ['WIDTH', 'HEIGHT', 'RADIATION'])) else 1
            mn_vl, mx_vl = INT_LIMITS.get(var_name, (0, 9999))
            nw_vl = self.editing_value + (stp if is_up else -stp)
            if nw_vl > mx_vl:
                nw_vl = mn_vl
            elif nw_vl < mn_vl:
                nw_vl = mx_vl
            self.editing_value = nw_vl
            return True
        if self.editing_mode == 'RGB':
            dlt = 5 if is_up else -5
            crr = self.editing_value[self.rgb_index]
            nw_crr = crr + dlt
            if nw_crr > 255:
                nw_crr = 0
            elif nw_crr < 0:
                nw_crr = 255
            self.editing_value[self.rgb_index] = nw_crr
            return True
        if self.editing_mode == 'STRING':
            crr_cd = self.str_ascii_chars[self.str_char_index]
            nw_cd = crr_cd + 1 if is_up else crr_cd - 1
            if nw_cd > 126:
                nw_cd = 32
            elif nw_cd < 32:
                nw_cd = 126
            self.str_ascii_chars[self.str_char_index] = nw_cd
            return True
        if is_up:
            self.selected_index = max(0, self.selected_index - 1)
        else:
            self.selected_index = min(len(self.settings) - 1, self.selected_index + 1)
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_index - self.visible_count + 1
        self._update_list_items()
        return True

    def scroll(self, direction):
        """# da testare meglio sul raspberry"""
        self.handle_vertical_scroll(is_up=direction)

    def _check_restart_required(self, var_name):
        """# boh, sembra funzionare"""
        if var_name in ['UI_STYLE', 'FAKE_LOCATION', 'REAL_MAP', 'DATE_MODE']:
            self.needs_restart = True

    def _apply_and_save(self):
        """# boh, sembra funzionare"""
        '# nota: controllare i path dei file'
        for sttng in self.settings:
            var_name = sttng['var_name']
            if var_name == 'SAVE_CHANGES':
                continue
            val = sttng['value']
            setattr(settings, var_name, val)
        self.save_settings()
        self.needs_restart = False
        self._update_list_items()
    def _restart_pipboy(self):
        trgt = None
        if hasattr(self.tab_instance, 'pipboy'):
            trgt = self.tab_instance.pipboy
        elif hasattr(self.tab_instance, 'tab_base') and hasattr(self.tab_instance.tab_base, 'pipboy'):
            trgt = self.tab_instance.tab_base.pipboy
        if trgt:
            trgt.should_restart = True
        else:
            pthn_exe = sys.executable
            mn_scrpt = os.path.abspath(sys.argv[0])
            subprocess.Popen([pthn_exe, mn_scrpt], cwd=root_dir)
            os._exit(0)

    def save_settings(self):
        tpt = ['# User Configuration (Auto-generated)\n', '# Overrides settings.py\n\n']
        for sttng in self.settings:
            var_name = sttng['var_name']
            if var_name == 'SAVE_CHANGES':
                continue
            val = sttng['value']
            cmmnt = f"  # {sttng['comment']}" if sttng['comment'] else ''
            tpt.append(f'{var_name} = {repr(val)}{cmmnt}\n')
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            f.writelines(tpt)

    def _render_scrollbar(self):
        """# FIXME: a volte lagga qui"""
        if not self.settings:
            return
        clr_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        x = self.draw_space.left + 15
        top_y = self.list_draw_space.top
        bottom_y = self.list_draw_space.bottom - 5
        rrw_w, rrw_h, ntch = (2, 4, 1)
        pygame.draw.polygon(self.screen, clr_lght, [(x, top_y), (x + rrw_w, top_y + rrw_h), (x, top_y + rrw_h - ntch), (x - rrw_w, top_y + rrw_h)])
        pygame.draw.polygon(self.screen, clr_lght, [(x, bottom_y), (x + rrw_w, bottom_y - rrw_h), (x, bottom_y - rrw_h + ntch), (x - rrw_w, bottom_y - rrw_h)])
        trck_tp = top_y + rrw_h + 2
        trck_bttm = bottom_y - rrw_h - 2
        trck_lngth = trck_bttm - trck_tp
        ttl = len(self.settings)
        if trck_lngth > 0 and ttl > self.visible_count:
            br_lngth = max(8, int(trck_lngth * (self.visible_count / ttl)))
            mx_scrll = max(1, ttl - self.visible_count)
            scrll_rt = min(1.0, max(0.0, self.scroll_offset / mx_scrll))
            br_tp = trck_tp + int(scrll_rt * (trck_lngth - br_lngth))
            pygame.draw.line(self.screen, clr_lght, (x, br_tp), (x, br_tp + br_lngth), 1)
    def _render_editor_modal(self):
        """# riprende dal loop principale"""
        if self.editing_mode is None and (not self.show_confirm_modal):
            return
        clr_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        clr_md = getattr(settings, 'PIP_BOY_MID', (0, 150, 0))
        mdl_w, mdl_h = (240, 100)
        mdl_x = self.draw_space.left + (self.draw_space.width - mdl_w) // 2
        mdl_y = self.draw_space.top + (self.draw_space.height - mdl_h) // 2
        mdl_rct = pygame.Rect(mdl_x, mdl_y, mdl_w, mdl_h)
        pygame.draw.rect(self.screen, (0, 0, 0), mdl_rct)
        pygame.draw.rect(self.screen, clr_lght, mdl_rct, 2)
        if self.show_confirm_modal:
            ttl_srf = self.modal_font.render('RESTART REQUIRED', True, clr_lght)
            self.screen.blit(ttl_srf, (mdl_x + (mdl_w - ttl_srf.get_width()) // 2, mdl_y + 12))
            msg_srf = self.modal_font.render('Apply changes and restart?', True, clr_lght)
            self.screen.blit(msg_srf, (mdl_x + (mdl_w - msg_srf.get_width()) // 2, mdl_y + 35))
            yes_cl = clr_lght if self.modal_selection == 0 else clr_md
            no_cl = clr_lght if self.modal_selection == 1 else clr_md
            yes_srf = self.inv_font.render('[ YES ]' if self.modal_selection == 0 else '  YES  ', True, yes_cl)
            no_srf = self.inv_font.render('[ NO ]' if self.modal_selection == 1 else '  NO  ', True, no_cl)
            self.screen.blit(yes_srf, (mdl_x + 40, mdl_y + 65))
            self.screen.blit(no_srf, (mdl_x + mdl_w - 40 - no_srf.get_width(), mdl_y + 65))
            return
        ttl_str = f"EDIT: {self.editing_var['display_name']}"
        ttl_srf = self.modal_font.render(ttl_str, True, clr_lght)
        self.screen.blit(ttl_srf, (mdl_x + (mdl_w - ttl_srf.get_width()) // 2, mdl_y + 10))
        cntr_y = mdl_y + 42
        def draw_up_down_arrows(cx, top_y, bottom_y):
            """# da testare meglio sul raspberry"""
            rrw_w = 4
            rrw_h = 5
            ntch = 3
            gap = 5
            tp_bs_y = top_y - gap
            tp_tp_y = tp_bs_y - rrw_h
            pygame.draw.polygon(self.screen, clr_lght, [(cx, tp_tp_y), (cx + rrw_w, tp_bs_y), (cx, tp_bs_y - ntch), (cx - rrw_w, tp_bs_y)])
            bt_bs_y = bottom_y + gap
            bt_tp_y = bt_bs_y + rrw_h
            pygame.draw.polygon(self.screen, clr_lght, [(cx, bt_tp_y), (cx + rrw_w, bt_bs_y), (cx, bt_bs_y + ntch), (cx - rrw_w, bt_bs_y)])
        if self.editing_mode == 'INT':
            vl_srf = self.inv_font.render(str(self.editing_value), True, clr_lght)
            vl_x = mdl_x + (mdl_w - vl_srf.get_width()) // 2
            self.screen.blit(vl_srf, (vl_x, cntr_y))
            cx = vl_x + vl_srf.get_width() // 2
            draw_up_down_arrows(cx, cntr_y, cntr_y + vl_srf.get_height())
        elif self.editing_mode == 'RGB':
            lbls = ['R', 'G', 'B']
            spcng = 60
            strt_x = mdl_x + (mdl_w - spcng * 2) // 2
            for i in range(3):
                cx = strt_x + i * spcng
                is_sl = i == self.rgb_index
                txt = f'{lbls[i]}:{self.editing_value[i]}'
                col = clr_lght if is_sl else clr_md
                srf = self.modal_font.render(txt, True, col)
                srf_x = cx - srf.get_width() // 2
                self.screen.blit(srf, (srf_x, cntr_y))
                if is_sl:
                    bx_rct = pygame.Rect(srf_x - 3, cntr_y - 2, srf.get_width() + 6, srf.get_height() + 4)
                    pygame.draw.rect(self.screen, clr_lght, bx_rct, 1)
                    draw_up_down_arrows(cx, bx_rct.top, bx_rct.bottom)
        elif self.editing_mode == 'STRING':
            chrs = [chr(c) for c in self.str_ascii_chars]
            chr_srfs = [self.modal_font.render(c, True, clr_lght) for c in chrs]
            chr_w = 12
            ttl_w = len(chrs) * chr_w
            strt_x = mdl_x + (mdl_w - ttl_w) // 2
            for i, c_srf in enumerate(chr_srfs):
                cx = strt_x + i * chr_w + chr_w // 2
                cy = cntr_y
                is_sl = i == self.str_char_index
                self.screen.blit(c_srf, (cx - c_srf.get_width() // 2, cy))
                if is_sl:
                    bx_rct = pygame.Rect(cx - chr_w // 2, cy - 2, chr_w, c_srf.get_height() + 4)
                    pygame.draw.rect(self.screen, clr_lght, bx_rct, 1)
                    draw_up_down_arrows(cx, bx_rct.top, bx_rct.bottom)
        ftr_srf = self.modal_font.render('[Enter/X] Save   [<- ->] Select   [^ v] Change', True, clr_lght)
        self.screen.blit(ftr_srf, (mdl_x + (mdl_w - ftr_srf.get_width()) // 2, mdl_y + mdl_h - 18))

    def render(self):
        self.settings_list.render(self.screen)
        self._render_scrollbar()
        self._render_editor_modal()