import pygame
import settings
# Moved from ui.py
class EffSubtab:
    def __init__(self, screen, draw_space):
        self.screen = screen
        self.draw_space = draw_space
        self.font = pygame.font.Font(settings.MAIN_FONT_PATH, 11)
        self.font_large = pygame.font.Font(settings.MAIN_FONT_PATH, 13) # shold make it more customizable
        self.default_effects = [('Boxing Times', 'Unarmed +20 (53s)'), ('Buffout', 'HP +60 (233s), END +3 (233s)'), ('Hoarder Penalty', 'STR -1, PER -1, LCK -1, INT -1, END -1, CHR -1, AGL -1'), ('Legion Praetorian Armor', 'Unarmed +10, Melee Weap. +5, AGL +1'), ('Merchant Outfit', 'Barter +5'), ('Sunset Sarsaparilla', 'HP +2 (25s)'), ('Weapon Binding Ritual', 'Unarm. Dam. +10 (233s), HP -2 (1s)')]
    def render(self, player_data, ui_style):
        COLOR_NV = settings.PIP_BOY_LIGHT
        scrn_w = self.screen.get_width()
        scrn_h = self.screen.get_height()
        ffcts = player_data.get('effects', self.default_effects)
        if not ffcts:
            mpt_txt = self.font_large.render('NO ACTIVE EFFECTS', True, COLOR_NV)
            self.screen.blit(mpt_txt, mpt_txt.get_rect(center=(scrn_w // 2 + 20, scrn_h // 2)))
            return
        strt_x = 40
        mx_w = scrn_w - strt_x - 10
        crr_y = 37
        nm_cl_w = 110
        pygame.draw.line(self.screen, COLOR_NV, (strt_x, crr_y), (strt_x + mx_w, crr_y), 1)
        crr_y += 4
        nm_ffcts = len(ffcts)
        for idx, (nm, dsc) in enumerate(ffcts):
            nm_txt = self.font.render(nm, True, COLOR_NV)
            self.screen.blit(nm_txt, (strt_x, crr_y))
            dsc_x = strt_x + nm_cl_w
            dsc_mx_w = mx_w - nm_cl_w
            wrds = dsc.split(' ')
            lns = []
            crrnt_ln = ''
            for wrd in wrds:
                tst_ln = crrnt_ln + (' ' if crrnt_ln else '') + wrd
                if self.font.size(tst_ln)[0] <= dsc_mx_w:
                    crrnt_ln = tst_ln
                else:
                    lns.append(crrnt_ln)
                    crrnt_ln = wrd
            if crrnt_ln:
                lns.append(crrnt_ln)
            ln_y = crr_y
            for line in lns:
                l_srfc = self.font.render(line, True, COLOR_NV)
                self.screen.blit(l_srfc, (dsc_x, ln_y))
                ln_y += 14
            tm_hght = max(18, ln_y - crr_y + 2)
            crr_y += tm_hght
            if idx < nm_ffcts - 1:
                pygame.draw.line(self.screen, COLOR_NV, (strt_x, crr_y), (strt_x + mx_w, crr_y), 1)
                crr_y += 3