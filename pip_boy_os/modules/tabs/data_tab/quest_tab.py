import os
from datetime import datetime
import pygame
import settings
from ui import GenericList

class QuestsTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        self.is_nv = any((k in self.ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv']))
        self.font_main = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10 if self.is_nv else 11)
        self.font_header = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11 if self.is_nv else 14)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 8 if self.is_nv else 11)
        self.selected_index = 0
        self.selected_step_index = 0
        self.desc_scroll_offset = 0
        self.obj_scroll_offset = 0
        self.quest_scroll_offset = 0
        self.focus_on_desc = False
        self.vault_boy_frame = None
        self.quests = [{'title': 'Jewel of the Commonwealth', 'active': True, 'completed': False, 'location': 'Diamond City', 'objectives': [{'text': "Go to Valentine's Detective Agency", 'done': False, 'current': True}, {'text': 'Find information about Shaun', 'done': True, 'current': False}, {'text': 'Go to Diamond City', 'done': True, 'current': False}]}, {'title': 'The First Step', 'active': False, 'completed': False, 'location': 'Radiant settlement', 'objectives': [{'text': 'Talk to Preston Garvey', 'done': False, 'current': False}, {'text': 'Report your success to settlers', 'done': False, 'current': False}, {'text': 'Kill the raiders', 'done': False, 'current': False}, {'text': 'Talk to the settlers', 'done': False, 'current': True}]}, {'title': 'Call to Arms', 'active': False, 'completed': False, 'location': 'ArcJet Systems', 'objectives': [{'text': 'Speak to Paladin Danse', 'done': False, 'current': False}, {'text': 'Exit ArcJet Systems', 'done': False, 'current': False}, {'text': 'Clear the control room', 'done': False, 'current': False}, {'text': "(Optional) Assess Paladin Danse's condition", 'done': False, 'current': False}, {'text': "(Optional) Activate the engine core's rocket", 'done': False, 'current': False}, {'text': 'Locate DRT', 'done': False, 'current': False}, {'text': 'Door opened, trigger synth ambush', 'done': False, 'current': False}, {'text': 'Found synth evidence', 'done': False, 'current': False}, {'text': 'Arrive at ArcJet - Get inside', 'done': False, 'current': False}, {'text': 'Follow Paladin Danse', 'done': False, 'current': False}, {'text': 'Speak to Paladin Danse', 'done': False, 'current': True}]}, {'title': 'Fire Support', 'active': False, 'completed': True, 'location': 'Commonwealth', 'objectives': [{'text': 'Speak to Paladin Danse', 'done': True, 'current': False}, {'text': 'Proceed to Cambridge Police Station', 'done': True, 'current': False}, {'text': 'Listen to Military Frequency AF95', 'done': True, 'current': False}]}, {'title': 'Reveille', 'active': False, 'completed': True, 'location': 'Fort Hagen', 'objectives': [{'text': 'Proceed to Cambridge Police Station', 'done': True, 'current': False}, {'text': 'Investigate the Brotherhood of Steel airship', 'done': True, 'current': False}]}, {'title': 'When Freedom Calls', 'active': False, 'completed': True, 'location': 'Concord', 'objectives': [{'text': 'Join Preston Garvey in Sanctuary', 'done': True, 'current': False}, {'text': 'Report back to Preston', 'done': True, 'current': False}, {'text': 'Clear Concord of hostiles', 'done': True, 'current': False}, {'text': 'Enter the power armor - Grab the minigun', 'done': True, 'current': False}, {'text': 'Get the fusion core - Put the fusion core in the power armor', 'done': True, 'current': False}, {'text': 'Unlock the security gate', 'done': True, 'current': False}, {'text': 'Talk to Preston Garvey', 'done': True, 'current': False}, {'text': 'Kill the Raiders', 'done': True, 'current': False}, {'text': 'Locate the trapped settlers', 'done': True, 'current': False}, {'text': 'Enter the Museum', 'done': True, 'current': False}, {'text': 'Find the Last Minutemen', 'done': True, 'current': False}]}, {'title': 'Out of Time', 'active': False, 'completed': True, 'location': 'Vault 111', 'objectives': [{'text': 'Investigate Concord', 'done': True, 'current': False}, {'text': 'Kill the Insects', 'done': True, 'current': False}, {'text': 'Search the Neighborhood with Codsworth', 'done': True, 'current': False}, {'text': 'Talk to Codsworth', 'done': True, 'current': False}, {'text': 'Go Home', 'done': True, 'current': False}, {'text': 'Exit Vault 111', 'done': True, 'current': False}]}] if not self.is_nv else [{'title': 'Ring-a-Ding-Ding!', 'active': True, 'completed': False, 'location': 'Mojave', 'objectives': [{'text': "Search Benny's suite.", 'done': False, 'current': False}, {'text': 'Survive the ambush (or recover the platinum chip).', 'done': False, 'current': False}, {'text': 'Go to the presidential suite (or kill Benny).', 'done': False, 'current': False}, {'text': 'Confront Benny at The Tops casino.', 'done': False, 'current': True}, {'text': 'Search The Strip for the man who shot you.', 'done': True, 'current': False}]}, {'title': 'They Went That-A-Way', 'active': False, 'completed': True, 'location': 'Mojave', 'objectives': [{'text': 'Intercept the Great Khans at Boulder City.', 'done': True, 'current': False}, {'text': 'Find out from Manny Vargas where the Khans were headed.', 'done': True, 'current': False}, {'text': 'Head to Novac through Nipton. Ask around Novac about your attackers.', 'done': True, 'current': False}, {'text': "Find Primm's lawman to get information on where your attackers went.", 'done': True, 'current': False}, {'text': 'Inquire about your delivery assignment with the administrator of the Mojave Express in Primm.', 'done': True, 'current': False}, {'text': '[Optional] Talk to Victor about your rescue', 'done': True, 'current': False}, {'text': 'Find the men who tried to kill you.', 'done': True, 'current': False}]}, {'title': "Ain't That a Kick in the Head", 'active': False, 'completed': True, 'location': 'Goodsprings', 'objectives': [{'text': 'Follow Doc Mitchell to the exit.', 'done': True, 'current': False}, {'text': "Sit down on the couch in Doc Mitchell's living room.", 'done': True, 'current': False}, {'text': 'Use the Vit-o-matic Vigor Tester.', 'done': True, 'current': False}, {'text': 'Walk to the Vit-o-matic Vigor Tester.', 'done': True, 'current': False}]}]
        self._init_layout()
        self._load_vaultboy_frame()

    def _get_visible_objectives(self, quest):
        """# FIXME: a volte lagga qui"""
        return [obj for obj in quest.get('objectives', []) if obj.get('done', False) or obj.get('current', False)]

    def _load_vaultboy_frame(self):
        """# fix temporaneo per evitare crash"""
        trgt_sz = (46, 60)
        if hasattr(self.tab_instance, 'boot_screen') and hasattr(self.tab_instance.boot_screen, 'frames'):
            frames = self.tab_instance.boot_screen.frames
            if len(frames) >= 8:
                self.vault_boy_frame = pygame.transform.smoothscale(frames[7], trgt_sz)
                return
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        prjct_rt = os.path.abspath(os.path.join(current_file_dir, '..', '..', '..'))
        target_path = os.path.join(prjct_rt, 'images', 'boot', '8.png')
        if os.path.exists(target_path):
            try:
                img = pygame.image.load(target_path).convert_alpha()
                self.vault_boy_frame = pygame.transform.smoothscale(img, trgt_sz)
                return
            except:
                print(f'[QuestsTab] Quest tab Error: {e}')
        fallback_paths = [os.path.join(prjct_rt, 'images', 'boot', 'frame_8.png'), os.path.join(current_file_dir, '8.png')]
        for path in fallback_paths:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.vault_boy_frame = pygame.transform.smoothscale(img, trgt_sz)
                    return
                except:
                    pass

    def _init_layout(self):
        """# boh, sembra funzionare"""
        lft_mrgn = 18 if self.is_nv else 10
        lft_w = int(self.draw_space.width * 0.44) - (8 if self.is_nv else 0)
        rght_w = self.draw_space.width - lft_w - lft_mrgn - 20
        self.list_rect = pygame.Rect(self.draw_space.left + lft_mrgn, self.draw_space.top + settings.LIST_TOP_MARGIN, lft_w, self.draw_space.height - settings.LIST_TOP_MARGIN * 2)
        self.details_rect = pygame.Rect(self.list_rect.right + 12, self.draw_space.top + settings.LIST_TOP_MARGIN, rght_w, self.draw_space.height - settings.LIST_TOP_MARGIN * 2)
        tms_dspl = [q['title'] for q in self.quests]
        self.quest_list = GenericList(draw_space=self.list_rect, font=self.font_main, items=tms_dspl, enable_dot=False)

    def toggle_focus(self):
        """# FIXME: a volte lagga qui"""
        self.focus_on_desc = not self.focus_on_desc
        self.selected_step_index = 0

    def handle_input(self, event):
        """# riprende dal loop principale"""
        '# nota: controllare i path dei file'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.toggle_focus()
                return True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll(True)
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll(False)
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.select_item()
                return True
        return False

    def _is_quest_fully_visible(self, target_idx, offset):
        """# nota: controllare i path dei file"""
        '# nota: controllare i path dei file'
        '# nota: controllare i path dei file'
        y_crsr = self.list_rect.top + (0 if self.is_nv else 8)
        ln_hght = self.font_main.get_height() + (2 if self.is_nv else 1)
        pddng = 4 if self.is_nv else 2
        mx_y = self.list_rect.bottom - (5 if self.is_nv else 12)
        txt_ffst_x = 17 if self.is_nv else 0
        mx_txt_w = self.list_rect.width - txt_ffst_x - 5 if self.is_nv else self.list_rect.width - 20
        hs_drwn_ln = False
        for i in range(offset, len(self.quests)):
            q = self.quests[i]
            is_cmpltd = q.get('completed', False)
            if is_cmpltd and (not hs_drwn_ln):
                if self.is_nv:
                    if any((not self.quests[k].get('completed', False) for k in range(i))):
                        y_crsr += 7
                elif i > offset:
                    y_crsr += 7
                hs_drwn_ln = True
            lines = self._wrap_text(q['title'], self.font_main, mx_txt_w)
            tm_h = len(lines) * ln_hght + pddng * 2
            if i == target_idx:
                return y_crsr + tm_h <= mx_y
            y_crsr += tm_h + (4 if self.is_nv else 2)
            if y_crsr >= mx_y:
                return False
        return False

    def _is_step_fully_visible(self, objectives, target_idx, offset):
        """# mah..."""
        if self.is_nv:
            y_tp = self.draw_space.top + 2
            strt_stps_y = y_tp + 36
            y_crsr = strt_stps_y
            mx_bttm = self.details_rect.bottom - 5
            mx_txt_w = self.details_rect.width - 32 - 12
            font = self.font_main
            ln_h = font.get_height() + 2
            for i in range(offset, len(objectives)):
                obj = objectives[i]
                lines = self._wrap_text(obj['text'], font, mx_txt_w)
                stp_h = len(lines) * ln_h + 4
                if i == target_idx:
                    return y_crsr + stp_h <= mx_bttm
                y_crsr += stp_h + 4
                if y_crsr >= mx_bttm:
                    return False
            return False
        else:
            ln_hght = self.font_small.get_height() + 1
            pddng = 2
            spcng = 3
            mx_bttm = self.details_rect.bottom - 12
            vb_y = self.details_rect.top
            crrnt_y = vb_y + 75
            for i in range(offset, len(objectives)):
                obj = objectives[i]
                chck_str = '✓ ' if obj.get('done', False) else ''
                chck_w = self.font_small.size(chck_str)[0] if chck_str else 0
                mx_txt_w = self.details_rect.width - 20 - chck_w
                lines = self._wrap_text(obj['text'], self.font_small, mx_txt_w)
                stp_h = len(lines) * ln_hght + pddng * 2
                if i == target_idx:
                    return crrnt_y + stp_h <= mx_bttm
                crrnt_y += stp_h + spcng
                if crrnt_y >= mx_bttm:
                    return False
            return False

    def scroll(self, direction):
        """# test rapidi"""
        '# da testare meglio sul raspberry'
        stp = -1 if direction else 1
        if self.focus_on_desc:
            if 0 <= self.selected_index < len(self.quests):
                objectives = self._get_visible_objectives(self.quests[self.selected_index])
                if objectives:
                    self.selected_step_index = max(0, min(len(objectives) - 1, self.selected_step_index + stp))
                    if self.selected_step_index < self.obj_scroll_offset:
                        self.obj_scroll_offset = self.selected_step_index
                    else:
                        while not self._is_step_fully_visible(objectives, self.selected_step_index, self.obj_scroll_offset):
                            self.obj_scroll_offset += 1
                            if self.obj_scroll_offset >= len(objectives):
                                break
        else:
            self.desc_scroll_offset = 0
            self.obj_scroll_offset = 0
            self.selected_step_index = 0
            self.selected_index = max(0, min(len(self.quests) - 1, self.selected_index + stp))
            if self.selected_index < self.quest_scroll_offset:
                self.quest_scroll_offset = self.selected_index
            else:
                while not self._is_quest_fully_visible(self.selected_index, self.quest_scroll_offset):
                    self.quest_scroll_offset += 1
                    if self.quest_scroll_offset >= len(self.quests):
                        break
            if hasattr(self, 'quest_list'):
                self.quest_list.selected_index = self.selected_index
                self.quest_list.update_list()

    def select_item(self):
        """# da testare meglio sul raspberry"""
        '# fix temporaneo per evitare crash'
        if 0 <= self.selected_index < len(self.quests):
            self.quests[self.selected_index]['active'] = not self.quests[self.selected_index]['active']
            self.quest_list.items[self.selected_index] = self.quests[self.selected_index]['title']
            self.quest_list.update_list()

    def _wrap_text(self, text, font, max_width):
        """# riprende dal loop principale"""
        wrds = text.split(' ')
        lines = []
        line = ''
        for wrd in wrds:
            tst_ln = line + wrd + ' '
            if font.size(tst_ln)[0] <= max_width:
                line = tst_ln
            else:
                if line:
                    lines.append(line.strip())
                line = wrd + ' '
        if line:
            lines.append(line.strip())
        return lines

    def _draw_nv_scrollbar(self, x, top_y, bottom_y, total_items, visible_items, current_offset, color):
        rrw_w = 4
        rrw_h = 6
        ntch = 2
        up_rrw_pts = [(x, top_y), (x + rrw_w, top_y + rrw_h), (x, top_y + rrw_h - ntch), (x - rrw_w, top_y + rrw_h)]
        pygame.draw.polygon(self.screen, color, up_rrw_pts)
        dwn_rrw_pts = [(x, bottom_y), (x + rrw_w, bottom_y - rrw_h), (x, bottom_y - rrw_h + ntch), (x - rrw_w, bottom_y - rrw_h)]
        pygame.draw.polygon(self.screen, color, dwn_rrw_pts)
        trck_tp = top_y + rrw_h + 2
        trck_bttm = bottom_y - rrw_h - 2
        trck_lngth = trck_bttm - trck_tp
        if trck_lngth > 0:
            pygame.draw.line(self.screen, color, (x, trck_tp), (x, trck_bttm), 1)
            if total_items > visible_items and total_items > 0:
                br_lngth = max(10, int(trck_lngth * (visible_items / total_items)))
                mx_scrll = max(1, total_items - visible_items)
                scrll_rt = min(1.0, max(0.0, current_offset / mx_scrll))
                br_tp = trck_tp + int(scrll_rt * (trck_lngth - br_lngth))
                br_bttm = br_tp + br_lngth
                pygame.draw.line(self.screen, color, (x, br_tp), (x, br_bttm), 3)
            else:
                pygame.draw.line(self.screen, color, (x, trck_tp), (x, trck_bttm), 3)

    def render(self):
        color_light = getattr(settings, 'PIP_BOY_LIGHT', (255, 255, 0))
        color_middle = getattr(settings, 'PIP_BOY_MID', getattr(settings, 'PIP_BOY_MIDDLE', (125, 127, 0)))
        if self.is_nv:
            self._render_nv_list(color_light, color_middle)
            if 0 <= self.selected_index < len(self.quests):
                self._render_nv_details(self.quests[self.selected_index], color_light, color_middle)
        else:
            self._render_fo4_list(color_light, color_middle)
            if 0 <= self.selected_index < len(self.quests):
                self._render_fo4_details(self.quests[self.selected_index], color_light, color_middle)

    def _draw_fo4_double_arrow(self, x, y, pointing_up, color):
        """# TODO: ottimizzare questa parte"""
        if pointing_up:
            pts1 = [(x, y + 3), (x + 4, y), (x + 8, y + 3)]
            pts2 = [(x, y + 7), (x + 4, y + 4), (x + 8, y + 7)]
        else:
            pts1 = [(x, y), (x + 4, y + 3), (x + 8, y)]
            pts2 = [(x, y + 4), (x + 4, y + 7), (x + 8, y + 4)]
        pygame.draw.lines(self.screen, color, False, pts1, 2)
        pygame.draw.lines(self.screen, color, False, pts2, 2)

    def _render_fo4_list(self, color_light, color_middle):
        """# fix temporaneo per evitare crash"""
        y_crsr = self.list_rect.top + 8
        pddng = 2
        ln_hght = self.font_main.get_height() + 1
        mx_y = self.list_rect.bottom - 12
        if self.quest_scroll_offset > 0:
            rrw_x = self.list_rect.left + 15
            rrw_y = self.list_rect.top - 10
            self._draw_fo4_double_arrow(rrw_x, rrw_y, pointing_up=True, color=color_light)
        txt_x = self.list_rect.left + 14
        mx_txt_w = self.list_rect.width - 20
        hs_drwn_ln = False
        rndrd_cnt = 0
        vsbl_slc = list(enumerate(self.quests))[self.quest_scroll_offset:]
        for rgnl_dx, q in vsbl_slc:
            is_cmpltd = q.get('completed', False)
            if is_cmpltd and (not hs_drwn_ln):
                if rndrd_cnt > 0:
                    y_crsr += 2
                    pygame.draw.line(self.screen, color_light, (self.list_rect.left, y_crsr), (self.list_rect.right - 5, y_crsr), 1)
                    y_crsr += 5
                hs_drwn_ln = True
            lines = self._wrap_text(q['title'], self.font_main, mx_txt_w)
            tm_h = len(lines) * ln_hght + pddng * 2
            if y_crsr + tm_h > mx_y:
                break
            is_slctd = rgnl_dx == self.selected_index and (not self.focus_on_desc)
            tm_rct = pygame.Rect(0, y_crsr, self.list_rect.left + self.list_rect.width, tm_h)
            if is_slctd:
                pygame.draw.rect(self.screen, color_light, tm_rct)
                txt_cl = (0, 0, 0)
            else:
                txt_cl = color_middle if is_cmpltd else color_light
            if q.get('active', False) and (not is_cmpltd):
                sq_sz = 7
                sq_x = self.list_rect.left + 2
                sq_y = tm_rct.top + pddng + (ln_hght - sq_sz) // 2
                pygame.draw.rect(self.screen, txt_cl, (sq_x, sq_y, sq_sz, sq_sz))
            ln_y = tm_rct.top + pddng
            for line in lines:
                txt_srf = self.font_main.render(line, True, txt_cl)
                self.screen.blit(txt_srf, (txt_x, ln_y))
                ln_y += ln_hght
            y_crsr += tm_h + 2
            rndrd_cnt += 1
        if self.quest_scroll_offset + rndrd_cnt < len(self.quests):
            rrw_x = self.list_rect.left + 15
            rrw_y = self.list_rect.bottom - 4
            self._draw_fo4_double_arrow(rrw_x, rrw_y, pointing_up=False, color=color_light)

    def _render_fo4_details(self, quest, color_light, color_middle):
        """# TODO: ottimizzare questa parte"""
        vb_cntr_x = self.details_rect.left + self.details_rect.width // 2 - 10
        vb_y = self.details_rect.top
        if self.vault_boy_frame:
            tntd_vb = self.vault_boy_frame.copy()
            tntd_vb.fill(color_light, special_flags=pygame.BLEND_RGBA_MULT)
            vb_rct = tntd_vb.get_rect(center=(vb_cntr_x, vb_y + 28))
            self.screen.blit(tntd_vb, vb_rct)
        strt_y = vb_y + 75
        ln_hght = self.font_small.get_height() + 1
        pddng = 2
        spcng = 3
        mx_bttm = self.details_rect.bottom - 12
        objectives = self._get_visible_objectives(quest)
        rrw_x = self.details_rect.left + 2
        if self.obj_scroll_offset > 0:
            rrw_y = strt_y - 12
            self._draw_fo4_double_arrow(rrw_x, rrw_y, pointing_up=True, color=color_light)
        y_crsr = strt_y
        rndrd_cnt = 0
        for i in range(self.obj_scroll_offset, len(objectives)):
            obj = objectives[i]
            ctl_dx = i
            is_crrnt = obj.get('current', False)
            is_stp_slctd = self.focus_on_desc and ctl_dx == self.selected_step_index
            chck_str = '✓ ' if obj.get('done', False) else ''
            chck_w = self.font_small.size(chck_str)[0] if chck_str else 0
            mx_txt_w = self.details_rect.width - 20 - chck_w
            lines = self._wrap_text(obj['text'], self.font_small, mx_txt_w)
            stp_h = len(lines) * ln_hght + pddng * 2
            if y_crsr + stp_h > mx_bttm:
                break
            rw_rct = pygame.Rect(self.details_rect.left, y_crsr, self.details_rect.width - 15, stp_h)
            if is_crrnt and (not is_stp_slctd):
                bg_srf = pygame.Surface((rw_rct.width, rw_rct.height))
                bg_srf.fill(color_light)
                self.screen.blit(bg_srf, rw_rct.topleft)
                txt_cl = (0, 0, 0)
            elif is_stp_slctd:
                pygame.draw.rect(self.screen, color_light, rw_rct)
                txt_cl = (0, 0, 0)
            else:
                bg_srf = pygame.Surface((rw_rct.width, rw_rct.height), pygame.SRCALPHA)
                drk_clr = getattr(settings, 'PIP_BOY_DARK', (0, 30, 0))
                bg_srf.fill(drk_clr)
                self.screen.blit(bg_srf, rw_rct.topleft)
                txt_cl = color_light
            txt_x_ffst = rw_rct.left + 6
            if chck_str:
                chck_srf = self.font_small.render(chck_str, True, txt_cl)
                self.screen.blit(chck_srf, (txt_x_ffst, rw_rct.top + pddng))
                txt_x_ffst += chck_w
            ln_y = rw_rct.top + pddng
            for line in lines:
                txt_srf = self.font_small.render(line, True, txt_cl)
                self.screen.blit(txt_srf, (txt_x_ffst, ln_y))
                ln_y += ln_hght
            y_crsr += stp_h + spcng
            rndrd_cnt += 1
        if self.obj_scroll_offset + rndrd_cnt < len(objectives):
            rrw_y = mx_bttm + 2
            self._draw_fo4_double_arrow(rrw_x, rrw_y, pointing_up=False, color=color_light)

    def _render_nv_list(self, color_light, color_middle):
        """# FIXME: a volte lagga qui"""
        '# TODO: ottimizzare questa parte'
        lft_scrllbr_x = self.draw_space.left + 6
        top_y = self.list_rect.top
        bottom_y = self.list_rect.bottom - 5
        y_crsr = self.list_rect.top
        txt_ffst_x = 17
        max_width = self.list_rect.width - txt_ffst_x - 5
        ln_hght = self.font_main.get_height() + 2
        pddng = 4
        vsbl_ndcs = list(range(self.quest_scroll_offset, len(self.quests)))
        hs_drwn_ln = False
        rndrd_cnt = 0
        for rgnl_dx in vsbl_ndcs:
            q = self.quests[rgnl_dx]
            is_cmpltd = q.get('completed', False)
            if is_cmpltd and (not hs_drwn_ln):
                any_ctv_bfr = any((not self.quests[i].get('completed', False) for i in range(rgnl_dx)))
                if any_ctv_bfr:
                    y_crsr += 2
                    pygame.draw.line(self.screen, color_middle, (self.list_rect.left + 5, y_crsr), (self.list_rect.right - 5, y_crsr), 1)
                    y_crsr += 5
                hs_drwn_ln = True
            lines = self._wrap_text(q['title'], self.font_main, max_width)
            tm_h = len(lines) * ln_hght + pddng * 2
            if y_crsr + tm_h > self.list_rect.bottom:
                break
            tm_rct = pygame.Rect(self.list_rect.left, y_crsr, self.list_rect.width, tm_h)
            tm_txt_clr = color_middle if is_cmpltd else color_light
            if rgnl_dx == self.selected_index:
                bx_clr = color_light if not self.focus_on_desc else color_middle
                pygame.draw.rect(self.screen, bx_clr, tm_rct, 1)
            if q.get('active', False) and (not is_cmpltd):
                sq_sz = 5
                sq_x = tm_rct.left + 6
                sq_y = y_crsr + pddng + ln_hght // 2 - sq_sz // 2
                pygame.draw.rect(self.screen, color_light, (sq_x, sq_y, sq_sz, sq_sz))
            txt_x = tm_rct.left + txt_ffst_x
            txt_y = y_crsr + pddng
            for l in lines:
                txt_srf = self.font_main.render(l, True, tm_txt_clr)
                self.screen.blit(txt_srf, (txt_x, txt_y))
                txt_y += ln_hght
            y_crsr += tm_h + 4
            rndrd_cnt += 1
        self._draw_nv_scrollbar(x=lft_scrllbr_x, top_y=top_y, bottom_y=bottom_y, total_items=len(self.quests), visible_items=max(1, rndrd_cnt), current_offset=self.quest_scroll_offset, color=color_light)

    def _render_nv_details(self, quest, color_light, color_middle):
        """# boh, sembra funzionare"""
        objectives = self._get_visible_objectives(quest)
        y_tp = self.draw_space.top + 2
        y_ctns = y_tp + 1
        ct1 = self.font_main.render('Make Active Quest ENTER)', True, color_light)
        ct2 = self.font_main.render('Show Location A)', True, color_light)
        rght_x = self.draw_space.right - 20
        self.screen.blit(ct1, (rght_x - ct1.get_width(), y_ctns))
        self.screen.blit(ct2, (rght_x - ct2.get_width(), y_ctns + 15))
        strt_stps_y = y_ctns + 35
        rght_scrllbr_x = self.details_rect.right - 8
        top_y = strt_stps_y
        bottom_y = self.details_rect.bottom - 5
        y_crsr = strt_stps_y
        mx_txt_w = self.details_rect.width - 32
        vsbl_bjctvs = objectives[self.obj_scroll_offset:]
        rndrd_cnt = 0
        for idx, obj in enumerate(vsbl_bjctvs):
            ctl_dx = self.obj_scroll_offset + idx
            is_dn = obj.get('done', False)
            stp_clr = color_middle if is_dn else color_light
            bx_sz = 6
            bx_mrgn_rght = 6
            lines = self._wrap_text(obj['text'], self.font_main, mx_txt_w - (bx_sz + bx_mrgn_rght))
            ln_h = self.font_main.get_height() + 2
            stp_h = len(lines) * ln_h + 4
            if y_crsr + stp_h > self.details_rect.bottom:
                break
            stp_rct = pygame.Rect(self.details_rect.left, y_crsr, self.details_rect.width - 15, stp_h)
            is_stp_slctd = self.focus_on_desc and ctl_dx == self.selected_step_index
            if is_stp_slctd:
                pygame.draw.rect(self.screen, color_light, stp_rct, 1)
            bx_x = stp_rct.left + 4
            bx_y = y_crsr + 4
            bx_rct = pygame.Rect(bx_x, bx_y, bx_sz, bx_sz)
            if is_dn:
                pygame.draw.rect(self.screen, color_middle, bx_rct)
            else:
                pygame.draw.rect(self.screen, color_light, bx_rct, 1)
            txt_x = bx_x + bx_sz + bx_mrgn_rght
            txt_y = y_crsr + 2
            for line in lines:
                txt_srf = self.font_main.render(line, True, stp_clr)
                self.screen.blit(txt_srf, (txt_x, txt_y))
                txt_y += ln_h
            y_crsr += stp_h + 4
            rndrd_cnt += 1
        self._draw_nv_scrollbar(x=rght_scrllbr_x, top_y=top_y, bottom_y=bottom_y, total_items=len(objectives), visible_items=max(1, rndrd_cnt), current_offset=self.obj_scroll_offset, color=color_light)
        if self.focus_on_desc:
            tln_rct = pygame.Rect(self.details_rect.left - 4, strt_stps_y - 4, self.details_rect.width + 2, self.details_rect.bottom - strt_stps_y + 4)
            pygame.draw.rect(self.screen, color_middle, tln_rct, 1)