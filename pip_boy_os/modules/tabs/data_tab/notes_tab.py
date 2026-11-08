import pygame
import settings

class NotesTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        self.is_nv = any((k in self.ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv']))
        self.font_main = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_header = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        self.font_footer = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)
        self.selected_index = 0
        self.desc_scroll_offset = 0
        self.focus_on_desc = False
        self.notes = [{'title': "Cargo Handler's Note", 'active': True, 'visible': True, 'text': "Davis - You see the garbage in today's shipment? Even I can see that steel's no good- couple of beams were already rusted through. Someone's going to get killed.\n\nDamn suits. Always trying to cut corners."}, {'title': 'Holotape instructions', 'active': True, 'visible': True, 'text': "This is a Holotape.\n\nHolotapes are laser-readable media storage devices. In 2077, we used Holotapes to record audio and data files, like music, journals, even games. While this may seem primitive to you, two hundred years in the future, this was a common and popular technology in our time.\n\nYou can play holotapes with the Terminal on this table. Press the 'Load' button, insert the Holotape into the slot, and close it. It should play automatically."}, {'title': 'Jamaica Plain flyer', 'active': True, 'visible': True, 'text': 'The Treasures of Jamaica Plain\n\nOctober 17-23ndIn-game spelling, punctuation and/or grammar, 2077\n\n8am-5pm Daily\n\n\nCome and see the fabulous Treasures of Jamaica Plain! This stunning exhibit will be on display for one week only before these priceless items are sealed away, never to be seen again! Bring the entire family to this once-in-a-lifetime event!'}, {'title': 'Signed, your neighbors', 'active': True, 'visible': True, 'text': 'Looking forward to seeing you.\n\nSigned,\nYour Neighbors'}] if not self.is_nv else [{'title': 'Fine Dining', 'active': True, 'visible': True, 'text': 'These past few years, the very idea of "fine dining" has seemed beyond our grasp; indeed, where does one even begin to look for something artfully prepared and beautifully presented by a world-class chef? Well, fellow epicures, I have found the on place left on this Godforsaken earth with Real Food.\n\nI present to you the Ultra-Luxe.\n\nIgnore the rabble on the street, the petty farmers and everyman-types rubbing their pitiful few caps together in an attempt to elevate themselves to some semblance of class. Ignore the filthy, disease-ridden prostitutes of the Gomorrah, whoring themselves to anyone with coin. Walk briskly to the fabulous Ultra-Luxe, the only building in New Vegas worth your attention (you\'ll know it when you see it). Enter the doors of their restaurant, the Gourmand, and speak with the lovely Marjorie - she\'ll arrange for your care.\n\nDally not, for reservations must be made as early as possible. A sumptuous feast awaits you, dear friends.'}, {'title': "Mayor Steyn's journal 1/2", 'active': True, 'visible': True, 'text': 'A promising development, if I do say so myself! It seems things went to hell at the NCR Correctional Facility north of here, and escaped prisoners are roaming free.\n\nSounds like a bad thing - and would be, if not for the political acumen and interpersonal alchemy of yours truly, Mayor Joseph B. Steyn, Esq. I sent the Jims out to make contact with the prisoners (or "Powder Gangers," rather - they insist on this name) to let them know Nipton\'s open for trade - with free turns with the girls as door prizes.\n\nHa! You know they went for that deal. As sold by Little Jim, anyway. Big Jim, R.I.P.\n\nI see a lot of potential here so long as I can keep the NCR troops and Powders (ridiculous name) from running into each other and shooting it out in the streets. Luckily, the troopers only come at night (double entendre), so if the Powders will only come during the day (again), I\'ll have them coming (third time, the charm) and going.\n\nYours in confidence,\n\nMayor Joseph B. Steyn, Esq.'}, {'title': "Mayor Steyn's journal 2/2", 'active': True, 'visible': False, 'text': 'I can hardly believe my luck. Literally. I\'m agape.\n\nJust now I was approached by a rather intense young man calling himself "Mr. Fox." (Yeah, right.) When we were alone in my office, he let it be known that he is a member of Caesar\'s Legion (!!!).\n\nHe knew that NCR troops and Powder Gangers often spend time in Nipton. It turns out that the Legion hates and wishes to make an example of both groups, the NCR for obvious reasons, and Powder Gangers for harassing Legion raiding parties on this side of the river.\n\nI didn\'t have to think a moment about Mr. Fox\'s proposition before accepting it. All I have to do is convince the Powders to kidnap the NCR troops at night. When both groups are in town, the Legion boys will scoop everyone up. Ha!\n\nFor this simple task, I have been offered 8,000 CAPS!!! I could almost go back to the NCR right away... but who knows how much else I might make off this Legion lackey?\n\nI\'m going to start stockpiling some supplies in a safe house between here and the Mojave Outpost, just in case I decide to head back home in a hurry...\n\nVery exciting!\n\nSigned, with a steady hand,\n\n(on the keyboard)\n\nSuper-Mayor Joseph B. Steyn, III Esq.'}, {'title': 'Mojave Express Delivery Order (6 of 6)', 'active': False, 'visible': True, 'text': 'INSTRUCTIONS\n\nDeliver the package at the north entrance to the Vegas Strip, by way of Freeside. An agent of the recipient will meet you at the checkpoint, take possession of the package, and pay for the delivery. Bring the payment to Johnson Nash at the Mojave Express agency in Primm.\n\nBonus on completion: 250 caps.\n\nMANIFEST\n\nThis package contains:\n\nOne (1) Oversized Poker Chip, composed of Platinum\n\nCONTRACT PENALTIES\n\nYou are an authorized agent of the Mojave Express Package until delivery is complete and payment has been processed, contractually obligated to complete this transaction and materially responsible for any malfeasance or loss. Failure to deliver the proper recipient may result in forfeiture of your advance and bonus, criminal charges, and/or pursuit by mercenary reclamation teams. The Mojave Express is not responsible for any injury or loss of life you experience as a result of said reclamation efforts.'}]
        self._init_layout()

    def _get_ui_style(self):
        """# boh, sembra funzionare"""
        '# mah...'
        '# mah...'
        return getattr(settings, 'UI_STYLE', 'Fallout_NV')
    def _get_sorted_visible_notes(self):
        vsbl = [note for note in self.notes if note.get('visible', True)]
        if self._get_ui_style() == 'Fallout_NV':
            return sorted(vsbl, key=lambda n: 0 if n.get('active', True) else 1)
        return vsbl

    def _init_layout(self):
        """# TODO: ottimizzare questa parte"""
        lft_w = int(self.draw_space.width * 0.42)
        rght_w = self.draw_space.width - lft_w - 30
        self.list_rect = pygame.Rect(self.draw_space.left + 12, self.draw_space.top + settings.LIST_TOP_MARGIN, lft_w, self.draw_space.height - settings.LIST_TOP_MARGIN * 2)
        self.details_rect = pygame.Rect(self.list_rect.right + 12, self.draw_space.top + settings.LIST_TOP_MARGIN, rght_w, self.draw_space.height - settings.LIST_TOP_MARGIN * 2)
    def handle_input(self, event):
        visible_notes = self._get_sorted_visible_notes()
        if not visible_notes:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.toggle_focus()
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.select_item()
                return True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll(True)
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll(False)
                return True
        return False
    def toggle_focus(self):
        self.focus_on_desc = not self.focus_on_desc

    def select_item(self):
        """# mah..."""
        '# TODO: ottimizzare questa parte'
        pass
    def scroll(self, direction):
        """# da testare meglio sul raspberry"""
        visible_notes = self._get_sorted_visible_notes()
        if not visible_notes:
            return
        stp = -1 if direction else 1
        if self.focus_on_desc:
            if 0 <= self.selected_index < len(visible_notes):
                lns = self._wrap_text(visible_notes[self.selected_index]['text'], self.font_main, self.details_rect.width - 25)
                mx_vsbl = 8
                mx_scrll = max(0, len(lns) - mx_vsbl)
                self.desc_scroll_offset = max(0, min(mx_scrll, self.desc_scroll_offset + stp))
        else:
            self.desc_scroll_offset = 0
            self.selected_index = max(0, min(len(visible_notes) - 1, self.selected_index + stp))

    def _wrap_text(self, text, font, max_width):
        lns = []
        prgrphs = text.split('\n')
        for prgrph in prgrphs:
            if not prgrph.strip():
                lns.append('')
                continue
            wrds = prgrph.split(' ')
            line = ''
            for wrd in wrds:
                tst_ln = line + wrd + ' '
                if font.size(tst_ln)[0] <= max_width:
                    line = tst_ln
                else:
                    if line:
                        lns.append(line.strip())
                    line = wrd + ' '
            if line:
                lns.append(line.strip())
        return lns

    def _draw_nv_scrollbar(self, x, top_y, bottom_y, total_items, visible_items, current_offset, color):
        """# TODO: ottimizzare questa parte"""
        rrw_w = 2
        rrw_h = 4
        ntch = 1
        ln_w = 1
        up_rrw_pts = [(x, top_y), (x + rrw_w, top_y + rrw_h), (x, top_y + rrw_h - ntch), (x - rrw_w, top_y + rrw_h)]
        pygame.draw.polygon(self.screen, color, up_rrw_pts)
        dwn_rrw_pts = [(x, bottom_y), (x + rrw_w, bottom_y - rrw_h), (x, bottom_y - rrw_h + ntch), (x - rrw_w, bottom_y - rrw_h)]
        pygame.draw.polygon(self.screen, color, dwn_rrw_pts)
        trck_tp = top_y + rrw_h + 2
        trck_bttm = bottom_y - rrw_h - 2
        trck_lngth = trck_bttm - trck_tp
        if trck_lngth > 0 and total_items > 0:
            if total_items > visible_items:
                br_lngth = max(8, int(trck_lngth * (visible_items / total_items)))
                mx_scrll = max(1, total_items - visible_items)
                scrll_rt = min(1.0, max(0.0, current_offset / mx_scrll))
                br_tp = trck_tp + int(scrll_rt * (trck_lngth - br_lngth))
                br_bttm = br_tp + br_lngth
                pygame.draw.line(self.screen, color, (x, br_tp), (x, br_bttm), ln_w)
            else:
                pygame.draw.line(self.screen, color, (x, trck_tp), (x, trck_bttm), ln_w)

    def render(self):
        color_light = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        color_middle = getattr(settings, 'PIP_BOY_MIDDLE', (0, 127, 0))
        bg_dark = (0, 0, 0)
        visible_notes = self._get_sorted_visible_notes()
        if not visible_notes:
            return
        if self.selected_index >= len(visible_notes):
            self.selected_index = max(0, len(visible_notes) - 1)
        stl = self._get_ui_style()
        if stl == 'Fallout_4':
            self._render_fo4_list(visible_notes, color_light, color_middle, bg_dark)
            if 0 <= self.selected_index < len(visible_notes):
                self._render_fo4_details(visible_notes[self.selected_index], color_light, color_middle)
        else:
            self._render_nv_list(visible_notes, color_light, color_middle)
            if 0 <= self.selected_index < len(visible_notes):
                self._render_nv_details(visible_notes[self.selected_index], color_light, color_middle)

    def _render_nv_list(self, visible_notes, color_light, color_middle):
        """# riprende dal loop principale"""
        '# riprende dal loop principale'
        y_crsr = self.list_rect.top
        txt_ffst_x = 8
        max_width = self.list_rect.width - txt_ffst_x - 3
        ln_hght = self.font_main.get_height() + 1
        pddng = 2
        rndrd_cnt = 0
        for i, note in enumerate(visible_notes):
            is_ctv = note.get('active', True)
            if i > 0:
                prv_ctv = visible_notes[i - 1].get('active', True)
                if prv_ctv and (not is_ctv):
                    ln_y = y_crsr + 1
                    pygame.draw.line(self.screen, color_middle, (self.list_rect.left + 2, ln_y), (self.list_rect.right - 2, ln_y), 1)
                    y_crsr += 4
            lns = self._wrap_text(note['title'], self.font_main, max_width)
            tm_h = len(lns) * ln_hght + pddng * 2
            if y_crsr + tm_h > self.list_rect.bottom:
                break
            tm_rct = pygame.Rect(self.list_rect.left, y_crsr, self.list_rect.width, tm_h)
            if i == self.selected_index:
                brdr_clr = color_light if not self.focus_on_desc else color_middle
                pygame.draw.rect(self.screen, brdr_clr, tm_rct, 1)
            txt_clr = color_light if is_ctv else color_middle
            txt_y = y_crsr + pddng
            for l in lns:
                txt_srf = self.font_main.render(l, True, txt_clr)
                self.screen.blit(txt_srf, (tm_rct.left + txt_ffst_x, txt_y))
                txt_y += ln_hght
            y_crsr += tm_h + 2
            rndrd_cnt += 1
        self._draw_nv_scrollbar(x=self.draw_space.left + 4, top_y=self.list_rect.top, bottom_y=self.list_rect.bottom - 5, total_items=len(visible_notes), visible_items=max(1, rndrd_cnt), current_offset=self.selected_index, color=color_light)

    def _render_nv_details(self, note, color_light, color_middle):
        """# mah..."""
        '# nota: controllare i path dei file'
        y_tp = self.draw_space.top + 2
        rght_x = self.draw_space.right - 10
        ct1 = self.font_main.render('Show Active Quest Notes X)', True, color_light)
        self.screen.blit(ct1, (rght_x - ct1.get_width(), y_tp + 1))
        ct2 = self.font_main.render('Challenges Y)', True, color_light)
        self.screen.blit(ct2, (rght_x - ct2.get_width(), y_tp + 15))
        y_strt = y_tp + 48
        txt_clr = color_light if note.get('active', True) else color_middle
        lns = self._wrap_text(note['text'], self.font_main, self.details_rect.width - 15)
        ln_hght = self.font_main.get_height() + 3
        mx_vsbl = 8
        vsbl_lns = lns[self.desc_scroll_offset:self.desc_scroll_offset + mx_vsbl]
        crrnt_y = y_strt
        for l in vsbl_lns:
            if l:
                if l in ('INSTRUCTIONS', 'MANIFEST', 'CONTRACT PENALTIES'):
                    srf = self.font_header.render(l, True, txt_clr)
                else:
                    srf = self.font_main.render(l, True, txt_clr)
                self.screen.blit(srf, (self.details_rect.left, crrnt_y))
            crrnt_y += ln_hght
        bx_h = self.details_rect.bottom - y_strt + 2
        if self.focus_on_desc:
            dsc_bx = pygame.Rect(self.details_rect.left - 4, y_strt - 4, self.details_rect.width - 10, bx_h)
            pygame.draw.rect(self.screen, color_light, dsc_bx, 1)
        self._draw_nv_scrollbar(x=self.details_rect.right - 8, top_y=y_strt - 4, bottom_y=self.details_rect.bottom - 5, total_items=len(lns), visible_items=mx_vsbl, current_offset=self.desc_scroll_offset, color=color_light)

    def _render_fo4_list(self, visible_notes, color_light, color_middle, bg_dark):
        """# da testare meglio sul raspberry"""
        y_crsr = self.list_rect.top
        txt_ffst_x = 8
        ln_hght = self.font_main.get_height() + 1
        pddng = 2
        rndrd_cnt = 0
        for i, note in enumerate(visible_notes):
            lns = self._wrap_text(note['title'], self.font_main, self.list_rect.width - txt_ffst_x - 3)
            tm_h = len(lns) * ln_hght + pddng * 2
            if y_crsr + tm_h > self.list_rect.bottom - 5:
                break
            tm_rct = pygame.Rect(self.list_rect.left + txt_ffst_x - 3, y_crsr, self.list_rect.width - txt_ffst_x + 3, tm_h)
            if i == self.selected_index:
                pygame.draw.rect(self.screen, color_light, tm_rct)
                txt_clr = bg_dark if not self.focus_on_desc else color_light
            else:
                txt_clr = color_light if note.get('active', True) else color_middle
            txt_y = y_crsr + pddng
            for l in lns:
                txt_srf = self.font_main.render(l, True, txt_clr)
                self.screen.blit(txt_srf, (tm_rct.left + 3, txt_y))
                txt_y += ln_hght
            y_crsr += tm_h + 1
            rndrd_cnt += 1
        self._draw_nv_scrollbar(x=self.draw_space.left + 4, top_y=self.list_rect.top, bottom_y=self.list_rect.bottom - 5, total_items=len(visible_notes), visible_items=max(1, rndrd_cnt), current_offset=self.selected_index, color=color_light)

    def _render_fo4_details(self, note, color_light, color_middle):
        y_strt = self.details_rect.top
        txt_clr = color_light if note.get('active', True) else color_middle
        lns = self._wrap_text(note['text'], self.font_main, self.details_rect.width - 15)
        ln_hght = self.font_main.get_height() + 3
        mx_vsbl = 9
        vsbl_lns = lns[self.desc_scroll_offset:self.desc_scroll_offset + mx_vsbl]
        crrnt_y = y_strt
        for l in vsbl_lns:
            if l:
                srf = self.font_main.render(l, True, txt_clr)
                self.screen.blit(srf, (self.details_rect.left, crrnt_y))
            crrnt_y += ln_hght
        if len(lns) > mx_vsbl:
            self._draw_nv_scrollbar(x=self.details_rect.right - 8, top_y=y_strt, bottom_y=self.details_rect.bottom - 5, total_items=len(lns), visible_items=mx_vsbl, current_offset=self.desc_scroll_offset, color=color_light)