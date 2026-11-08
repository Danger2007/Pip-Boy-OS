import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils
class WeaponsTab(InvBase):
# mmmh... Guns, I'm not american but who doesn't like them!
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Weapon', enable_dot=True)
        self.item_grid = None
        if self.no_items:
            return
        self.ammo_icon = Utils.load_svg(self.small_icon_size, settings.AMMO_ICON) if hasattr(settings, 'AMMO_ICON') else None
        self.gun_icon = Utils.load_svg(self.big_icon_size, settings.GUN_ICON) if hasattr(settings, 'GUN_ICON') else None
        self.item_grid = ItemGrid(draw_space=self.calculate_grid_space(), font=self.inv_font, padding=1)
        if self.unique_items and 0 <= self.inv_list.selected_index < len(self.unique_items):
            ntrs = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(ntrs)

    def init_footer_text(self):
        wght_srfc = self.init_footer_weight()
        cps_srfc = self.init_footer_caps()
        dmg_srfc = self.init_footer_damage()
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ftr_srfc.blit(wght_srfc, (0, 0))
        ftr_srfc.blit(cps_srfc, (0, 0))
        ftr_srfc.blit(dmg_srfc, (0, 0))
        return ftr_srfc

    def calculate_damage(self, weapon):
        if not weapon:
            return {'base': 0, 'types': {}}
        bs_dmg = getattr(weapon, 'damage', 0) or 0
        dmg_brkdwn = {'base': bs_dmg, 'types': {}}
        dmg_tps = getattr(weapon, 'damage_types', []) or []
        for damage_type in dmg_tps:
            tp_dmg = damage_type.value * bs_dmg // 100
            cn = self.damage_icons.get(damage_type.path) if hasattr(self, 'damage_icons') and isinstance(self.damage_icons, dict) else None
            dmg_brkdwn['types'][damage_type.path] = {'value': tp_dmg, 'icon': cn}
        return dmg_brkdwn
    def get_damage_display_data(self, weapon):
        if not weapon:
            return []
        dmg_dt = self.calculate_damage(weapon)
        dspl_dt = []
        mm_tp = getattr(weapon, 'ammo_type', None)
        bs_cn = None
        if mm_tp and hasattr(settings, 'items') and (mm_tp in settings.items):
            mm_tm = settings.items[mm_tp]
            if hasattr(mm_tm, 'damage_type') and hasattr(self, 'damage_icons') and isinstance(self.damage_icons, dict):
                bs_cn = self.damage_icons.get(mm_tm.damage_type)
        dspl_dt.append({'label': 'Damage', 'value': dmg_dt.get('base', 0), 'icon': bs_cn, 'is_base': True})
        if 'types' in dmg_dt and dmg_dt['types']:
            for _, tp_nf in dmg_dt['types'].items():
                dspl_dt.append({'label': '', 'value': tp_nf['value'], 'icon': tp_nf['icon'], 'is_base': False})
        return dspl_dt

    def init_footer_damage(self):
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        if self.no_items or not self.item_selected or self.active_item_index is None or (not self.unique_items):
            return ftr_srfc
        if 0 <= self.active_item_index < len(self.unique_items):
            ctv_wpn = self.unique_items[self.active_item_index]
            dmg_dt = self.get_damage_display_data(ctv_wpn)
            x_ps = settings.SCREEN_WIDTH - settings.BOTTOM_BAR_MARGIN
            for ntr in reversed(dmg_dt):
                vl_txt = str(ntr['value'])
                vl_srfc = self.footer_font.render(vl_txt, True, settings.PIP_BOY_LIGHT)
                x_ps -= vl_srfc.get_width()
                ftr_srfc.blit(vl_srfc, (x_ps, 2))
                if ntr.get('icon') is not None:
                    cn = ntr['icon']
                    x_ps -= cn.get_width() + 1
                    y_ps = (settings.BOTTOM_BAR_HEIGHT - cn.get_height()) // 2
                    ftr_srfc.blit(cn, (x_ps, y_ps))
                    x_ps -= settings.BOTTOM_BAR_MARGIN
            if hasattr(self, 'gun_icon') and self.gun_icon:
                x_ps -= self.gun_icon.get_width()
                ftr_srfc.blit(self.gun_icon, (x_ps, 4))
        return ftr_srfc

    def get_grid_entries(self, item):
        ntrs = []
        dmg_dt = self.get_damage_display_data(item)
        dmg_lns = []
        for ntr in dmg_dt:
            ln_dt = {'value': ntr['value'], 'is_base': ntr.get('is_base', False)}
            if ntr.get('icon') is not None:
                ln_dt['icon'] = ntr['icon']
            dmg_lns.append(ln_dt)
        ntrs.append({'label': 'Damage', 'lines': dmg_lns, 'highlight': True, 'split': True})
        mm_tp = getattr(item, 'ammo_type', None)
        if mm_tp and hasattr(settings, 'items') and (mm_tp in settings.items):
            mm_cnt = settings.TOTAL_AMMO.get(mm_tp, 0) if hasattr(settings, 'TOTAL_AMMO') else 0
            mm_tp_nm = settings.items[mm_tp].name
            mm_ntr = {'label': mm_tp_nm, 'icon_front': True, 'value': mm_cnt, 'highlight': True}
            if hasattr(self, 'ammo_icon') and self.ammo_icon is not None:
                mm_ntr['icon'] = self.ammo_icon
            ntrs.append(mm_ntr)
        stndrd = [('Fire Rate', getattr(item, 'fire_rate', 0)), ('Range', getattr(item, 'range', 0)), ('Accuracy', getattr(item, 'accuracy', 0)), ('Weight', getattr(item, 'weight', 0)), ('Value', getattr(item, 'value', 0))]
        for lbl, value in stndrd:
            ntrs.append({'label': lbl, 'value': value})
        return ntrs

    def scroll(self, direction):
        if self.no_items or self.item_grid is None:
            return
        prv_ndx = self.inv_list.selected_index
        super().scroll(direction)
        if prv_ndx != self.inv_list.selected_index and self.unique_items and (0 <= self.inv_list.selected_index < len(self.unique_items)):
            ntrs = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(ntrs)
    def select_item(self):
        if self.no_items:
            return
        super().select_item()
        if not self.is_nv:
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())
    def render(self):
        super().render()
        if self.no_items or self.item_grid is None or self.is_nv:
            return
        self.item_grid.render(self.screen)