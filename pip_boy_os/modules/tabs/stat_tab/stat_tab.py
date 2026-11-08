import pygame
import settings
from .status_tab import StatusTab
from .special_tab import SpecialTab
from .perks_tab import PerksTab
from .general_tab import GeneralTab
from tab import ThreadHandler
import ui as ui
from .skills_tab import draw_skills_tab
class StatTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.current_sub_tab_index = 0
        self.dynamic_footer_text = [('HP', settings.HP_CURRENT, settings.HP_MAX), ('LEVEL', settings.LEVEL), ('AP', settings.AP_CURRENT, settings.AP_MAX), ('XP', settings.XP_CURRENT)]
        self.footer_font = tab_instance.footer_font
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 2), self.init_footer_text())
        self.status_tab = StatusTab(self.screen, self.tab_instance, self.draw_space)
        self.special_tab = SpecialTab(self.screen, self.tab_instance, self.draw_space)
        self.perks_tab = PerksTab(self.screen, self.tab_instance, self.draw_space)
        self.general_tab = GeneralTab(self.screen, self.tab_instance, self.draw_space)
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv':
            sb_tb_mp = {0: self.status_tab, 1: self.special_tab, 2: None, 3: self.perks_tab, 4: self.general_tab}
        else:
            sb_tb_mp = {0: self.status_tab, 1: self.special_tab, 2: self.perks_tab, 3: self.status_tab.rad_subtab}
        self.sub_tab_thread_handler = ThreadHandler(sb_tb_mp, self.current_sub_tab_index)
    def is_editing(self):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv' and self.current_sub_tab_index == 4:
            return self.general_tab.is_editing()
        return False
    def get_active_subtab(self):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv':
            match self.current_sub_tab_index:
                case 0:
                    return self.status_tab
                case 1:
                    return self.special_tab
                case 3:
                    return self.perks_tab
                case 4:
                    return self.general_tab
        else:
            match self.current_sub_tab_index:
                case 0:
                    return self.status_tab
                case 1:
                    return self.special_tab
                case 2:
                    return self.perks_tab
                case 3:
                    return self.status_tab.rad_subtab
        return self
    def init_footer_text(self):
        hp_strng = f'{self.dynamic_footer_text[0][0]} {self.dynamic_footer_text[0][1]}/{self.dynamic_footer_text[0][2]}'
        lvl_strng = f'{self.dynamic_footer_text[1][0]} {self.dynamic_footer_text[1][1]}'
        ap_strng = f'{self.dynamic_footer_text[2][0]} {self.dynamic_footer_text[2][1]}/{self.dynamic_footer_text[2][2]}'
        hp_srfc = self.footer_font.render(hp_strng, True, settings.PIP_BOY_LIGHT)
        lvl_srfc = self.footer_font.render(lvl_strng, True, settings.PIP_BOY_LIGHT)
        ap_srfc = self.footer_font.render(ap_strng, True, settings.PIP_BOY_LIGHT)
        xp_rct_bs = pygame.Rect(lvl_srfc.get_width() + settings.SCREEN_WIDTH // 3.6, settings.BOTTOM_BAR_HEIGHT // 1.7 // 2, settings.SCREEN_WIDTH // 3.2, settings.BOTTOM_BAR_HEIGHT - settings.BOTTOM_BAR_HEIGHT // 1.8)
        xp_rct = xp_rct_bs.copy()
        xp_rct.width = xp_rct.width * (settings.XP_CURRENT / 100)
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ftr_srfc.blit(hp_srfc, (2, 2))
        ftr_srfc.blit(lvl_srfc, (settings.SCREEN_WIDTH // 3.8, 2))
        pygame.draw.rect(ftr_srfc, settings.PIP_BOY_LIGHT, xp_rct)
        pygame.draw.rect(ftr_srfc, settings.PIP_BOY_DARKER, xp_rct_bs, 1)
        ftr_srfc.blit(ap_srfc, (settings.SCREEN_WIDTH // 1.2, 2))
        return ftr_srfc

    def change_sub_tab(self, sub_tab):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)
    def handle_threads(self, tab_selected):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)
    def handle_input(self, event):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv':
            if self.current_sub_tab_index == 4:
                return self.general_tab.handle_input(event)
            elif self.current_sub_tab_index == 3:
                return self.perks_tab.handle_input(event) if hasattr(self.perks_tab, 'handle_input') else False
        elif self.current_sub_tab_index == 2:
            return self.perks_tab.handle_input(event) if hasattr(self.perks_tab, 'handle_input') else False
        return False
    def _scroll_skills(self, direction):
        sklls_cnt = len(getattr(settings, 'DEFAULT_SKILLS', []))
        if sklls_cnt > 0:
            dlt = -1 if direction else 1
            self.selected_skill_index = (getattr(self, 'selected_skill_index', 0) + dlt) % sklls_cnt
    def scroll(self, direction):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv':
            match self.current_sub_tab_index:
                case 0:
                    self.status_tab.scroll(direction)
                case 1:
                    self.special_tab.scroll_special(direction)
                case 2:
                    self._scroll_skills(direction)
                case 3:
                    self.perks_tab.scroll_perks(direction)
                case 4:
                    self.general_tab.scroll_general(direction)
                case _:
                    pass
        else:
            match self.current_sub_tab_index:
                case 0:
                    self.status_tab.scroll(direction)
                case 1:
                    self.special_tab.scroll_special(direction)
                case 2:
                    self.perks_tab.scroll_perks(direction)
                case 3:
                    pass

    def select_item(self):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv' and self.current_sub_tab_index == 4:
            return self.general_tab.select_item()
        return False

    def handle_x_press(self): # too many X press functions, should rework later
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv' and self.current_sub_tab_index == 4:
            self.general_tab.handle_x_press()
    def render(self):
        ui_stl = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_stl == 'fallout_nv':
            match self.current_sub_tab_index:
                case 0:
                    self.status_tab.render()
                case 1:
                    self.special_tab.render()
                case 2:
                    sklls_dt = getattr(settings, 'DEFAULT_SKILLS', [])
                    slctd_dx = getattr(self, 'selected_skill_index', 0)
                    draw_skills_tab(self.screen, sklls_dt, slctd_dx, settings.PIP_BOY_LIGHT, self.footer_font, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
                case 3:
                    self.perks_tab.render()
                case 4:
                    self.general_tab.render()
        else:
            self.tab_instance.render_footer(self)
            match self.current_sub_tab_index:
                case 0:
                    self.status_tab.render()
                case 1:
                    self.special_tab.render()
                case 2:
                    self.perks_tab.render()
                case 3:
                    p_dt = getattr(self.tab_instance, 'player_data', {})
                    self.status_tab.rad_subtab.render(p_dt, ui_stl)