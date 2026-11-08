import os
import re
import random
from threading import Lock
import pygame
import settings
from ui import GenericList
from items import Inventory
from util_functs import Utils
class InvBase:

    def __init__(self, screen, tab_instance, draw_space, category, enable_turntable=True, enable_dot=False):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.enable_turntable = enable_turntable
        self.ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        self.is_nv = any((k in self.ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv']))
        if self.is_nv:
            self.header_text_left = ') ITEMS'
            self.top_margin_spacing = 18
            if hasattr(self.tab_instance, 'header_text_left'):
                setattr(self.tab_instance, 'header_text_left', ') ITEMS')
            if hasattr(self.tab_instance, 'top_margin_spacing'):
                setattr(self.tab_instance, 'top_margin_spacing', 18)
            self._suppress_fo4_tab_rendering()
        if isinstance(category, (list, tuple)):
            self.category = [c.strip().title() for c in category if isinstance(c, str)]
        elif isinstance(category, str):
            self.category = category.strip().title()
        else:
            self.category = category
        self._anim_cache = {}
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.footer_font = getattr(tab_instance, 'footer_font', self.inv_font)
        nvntr = Inventory()
        if isinstance(self.category, (list, tuple)):
            self.inv_items = []
            cmbnd_prs = []
            for cat in self.category:
                self.inv_items.extend(nvntr.get_all_items(cat))
                u_tms = nvntr.get_unique_items(cat)
                nms = nvntr.get_item_names(cat)
                for item, name in zip(u_tms, nms):
                    cmbnd_prs.append((item, name))
            cmbnd_prs.sort(key=lambda pair: getattr(pair[0], 'name', '').lower())
            self.unique_items = [p[0] for p in cmbnd_prs]
            tm_nms = [p[1] for p in cmbnd_prs]
        else:
            self.inv_items = nvntr.get_all_items(self.category)
            self.unique_items = nvntr.get_unique_items(self.category) if self.inv_items else []
            tm_nms = nvntr.get_item_names(self.category) if self.inv_items else []
        self.weight = sum((getattr(item, 'weight', 0) for item in nvntr.get_all_items()))
        self._init_icons()
        self.no_items = not bool(self.inv_items)
        self.active_item_index = 0 if self.unique_items else None
        self.previous_item_index = None
        self.item_selected = bool(self.unique_items and self.active_item_index is not None)
        if not self.is_nv and hasattr(self.tab_instance, 'init_footer'):
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())
        if self.no_items:
            return
        is_qppbl = self._is_equippable_category()
        if self.is_nv:
            lft_mrgn = 20
            self.list_draw_space = pygame.Rect(self.draw_space.left + lft_mrgn, self.draw_space.top + 8, int(self.draw_space.width * 0.35), self.draw_space.height - 16)
            self.inv_list = GenericList(draw_space=self.list_draw_space, font=self.inv_font, items=[], enable_dot=False)
            self.refresh_list_display()
            self._setup_nv_list_style()
        else:
            self.list_draw_space = pygame.Rect(self.draw_space.left, self.draw_space.top + 2 * settings.LIST_TOP_MARGIN, self.draw_space.centerx + self.draw_space.centerx // 6 - 10, self.draw_space.height - 2 * settings.LIST_TOP_MARGIN)
            self.inv_list = GenericList(draw_space=self.list_draw_space, font=self.inv_font, items=tm_nms, enable_dot=enable_dot and is_qppbl)
            self._setup_fo4_list_style(enable_dot=is_qppbl)
        self.static_image = None
        if self.enable_turntable:
            self._init_turntable()
        if self.unique_items:
            self.update_item_display()

    def _is_equippable_category(self):
        ct_str = ''
        if isinstance(self.category, (list, tuple)):
            ct_str = ' '.join((str(c) for c in self.category)).lower()
        elif isinstance(self.category, str):
            ct_str = self.category.lower()
        return any((k in ct_str for k in ['weapon', 'arm', 'apparel', 'armor', 'clothing']))

    def refresh_list_display(self):
        if not hasattr(self, 'inv_list') or not self.inv_list or (not self.is_nv):
            return
        dspl_nms = []
        if self.unique_items:
            for item in self.unique_items:
                hs_mds = bool(getattr(item, 'mods', None) or getattr(item, 'installed_mods', None) or getattr(item, 'weapon_mods', None))
                md_sffx = ' +' if hs_mds else ''
                dspl_nms.append(f'{item.name}{md_sffx}')
        self.inv_list.items = dspl_nms
    def _setup_nv_list_style(self): # ehy functions must be recognizable at first glance, don't judge
        if not self.is_nv or not hasattr(self, 'inv_list') or (not self.inv_list):
            return
        setattr(self.inv_list, 'is_nv', True)
        setattr(self.inv_list, 'outline_only', True)
        setattr(self.inv_list, 'selection_style', 'outline')
        def custom_nv_render(screen, selected_index=None, *args, **kwargs):
            if selected_index is None:
                selected_index = getattr(self.inv_list, 'selected_index', 0)
            items = getattr(self.inv_list, 'items', [])
            font = getattr(self.inv_list, 'font', self.inv_font)
            draw_space = getattr(self.inv_list, 'draw_space', self.list_draw_space)
            pp_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
            if not items:
                return
            rw_hght = font.get_linesize() + 5
            vsbl_cnt = max(1, draw_space.height // rw_hght)
            scrll_ffst = getattr(self.inv_list, 'scroll_offset', 0)
            if selected_index < scrll_ffst:
                scrll_ffst = selected_index
            elif selected_index >= scrll_ffst + vsbl_cnt:
                scrll_ffst = selected_index - vsbl_cnt + 1
            setattr(self.inv_list, 'scroll_offset', scrll_ffst)
            is_qppbl = self._is_equippable_category()
            y = draw_space.top
            for i in range(scrll_ffst, min(len(items), scrll_ffst + vsbl_cnt)):
                tm_txt = items[i].rstrip()
                is_slctd = i == selected_index
                tm_rct = pygame.Rect(draw_space.left - 4, y - 1, draw_space.width + 6, rw_hght - 2)
                if is_slctd:
                    pygame.draw.rect(screen, pp_lght, tm_rct, width=1)
                sq_sz = 5
                sq_x = draw_space.left + 2
                sq_y = tm_rct.centery - sq_sz // 2
                if is_qppbl:
                    is_qppd = False
                    if self.unique_items and i < len(self.unique_items):
                        tm_bj = self.unique_items[i]
                        is_qppd = bool(getattr(tm_bj, 'equipped', False) or getattr(tm_bj, 'is_equipped', False))
                    if is_qppd:
                        pygame.draw.rect(screen, pp_lght, (sq_x, sq_y, sq_sz, sq_sz))
                txt_x = sq_x + sq_sz + 5
                txt_srf = font.render(tm_txt, True, pp_lght)
                txt_rct = txt_srf.get_rect(midleft=(txt_x, tm_rct.centery))
                screen.blit(txt_srf, txt_rct)
                y += rw_hght
        self.inv_list.render = custom_nv_render
    def _setup_fo4_list_style(self, enable_dot=True):
        if self.is_nv or not hasattr(self, 'inv_list') or (not self.inv_list):
            return

        def custom_fo4_render(screen, selected_index=None, *args, **kwargs):
            if selected_index is None:
                selected_index = getattr(self.inv_list, 'selected_index', 0)
            items = getattr(self.inv_list, 'items', [])
            font = getattr(self.inv_list, 'font', self.inv_font)
            draw_space = getattr(self.inv_list, 'draw_space', self.list_draw_space)
            pp_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
            pp_drk = getattr(settings, 'PIP_BOY_DARK', (0, 30, 0))
            if not items:
                return
            rw_hght = font.get_linesize() + 6
            vsbl_cnt = max(1, draw_space.height // rw_hght)
            scrll_ffst = getattr(self.inv_list, 'scroll_offset', 0)
            if selected_index < scrll_ffst:
                scrll_ffst = selected_index
            elif selected_index >= scrll_ffst + vsbl_cnt:
                scrll_ffst = selected_index - vsbl_cnt + 1
            setattr(self.inv_list, 'scroll_offset', scrll_ffst)
            is_qppbl = self._is_equippable_category()
            y = draw_space.top
            for i in range(scrll_ffst, min(len(items), scrll_ffst + vsbl_cnt)):
                tm_txt = items[i].rstrip()
                is_slctd = i == selected_index
                tm_rct = pygame.Rect(draw_space.left, y, draw_space.width, rw_hght - 2)
                if is_slctd:
                    pygame.draw.rect(screen, pp_lght, tm_rct)
                    txt_clr = (0, 0, 0)
                    sq_clr = pp_drk
                else:
                    txt_clr = pp_lght
                    sq_clr = pp_lght
                sq_sz = 6
                sq_x = draw_space.left + 6
                if is_qppbl and enable_dot:
                    is_qppd = False
                    if self.unique_items and i < len(self.unique_items):
                        tm_bj = self.unique_items[i]
                        is_qppd = bool(getattr(tm_bj, 'equipped', False) or getattr(tm_bj, 'is_equipped', False))
                    sq_y = tm_rct.centery - sq_sz // 2
                    if is_qppd:
                        pygame.draw.rect(screen, sq_clr, (sq_x, sq_y, sq_sz, sq_sz))
                    txt_x = sq_x + sq_sz + 6
                else:
                    txt_x = draw_space.left + 6
                txt_srf = font.render(tm_txt, True, txt_clr)
                txt_rct = txt_srf.get_rect(midleft=(txt_x, tm_rct.centery))
                screen.blit(txt_srf, txt_rct)
                y += rw_hght
        self.inv_list.render = custom_fo4_render

    def toggle_equip(self):
        if self.no_items or not self.unique_items or self.active_item_index is None:
            return
        if not self._is_equippable_category():
            return
        slctd_tm = self.unique_items[self.active_item_index]
        is_crrntl_qppd = bool(getattr(slctd_tm, 'equipped', False) or getattr(slctd_tm, 'is_equipped', False))
        if is_crrntl_qppd:
            setattr(slctd_tm, 'equipped', False)
            setattr(slctd_tm, 'is_equipped', False)
        else:
            slctd_slt = getattr(slctd_tm, 'slot', None)
            for item in self.unique_items:
                tm_slt = getattr(item, 'slot', None)
                if slctd_slt is None or tm_slt == slctd_slt:
                    setattr(item, 'equipped', False)
                    setattr(item, 'is_equipped', False)
            setattr(slctd_tm, 'equipped', True)
            setattr(slctd_tm, 'is_equipped', True)
        self.item_selected = True
        if self.is_nv:
            self.refresh_list_display()
        elif hasattr(self.tab_instance, 'init_footer'):
            self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.toggle_equip()

    def _suppress_fo4_tab_rendering(self):
        if not self.is_nv or not hasattr(self, 'tab_instance') or (not self.tab_instance):
            return
        mthds_to_dsbl = ['render_footer', 'draw_footer', 'render_stats', 'draw_stats', 'render_grid', 'draw_grid', 'render_stats_grid', 'draw_stats_grid', 'render_item_stats', 'draw_item_stats']
        for mthd_nm in mthds_to_dsbl:
            if hasattr(self.tab_instance, mthd_nm):
                setattr(self.tab_instance, mthd_nm, lambda *args, **kwargs: None)
    def _get_project_root(self):
        crr = os.path.abspath(__file__)
        while crr != os.path.dirname(crr):
            crr = os.path.dirname(crr)
            if os.path.exists(os.path.join(crr, 'images')):
                return crr
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _init_turntable(self):
        trntbl_wdth = self.draw_space.right - self.list_draw_space.right - getattr(settings, 'GRID_RIGHT_MARGIN', 10) - 15
        trntbl_hght = self.list_draw_space.height // 2
        if self.is_nv:
            rght_pnl_x = self.list_draw_space.right + 10
            rght_pnl_wdth = self.draw_space.right - rght_pnl_x - 10
            mg_area_hght = int((self.draw_space.height - 16) * 0.5)
            self.turntable_draw_space = pygame.Rect(rght_pnl_x, self.draw_space.top + 8, rght_pnl_wdth, mg_area_hght)
        else:
            cntr_x = settings.SCREEN_WIDTH // 2 + 80
            self.turntable_draw_space = pygame.Rect(0, 0, trntbl_wdth, trntbl_hght)
            self.turntable_draw_space.center = (cntr_x, self.draw_space.top + trntbl_hght // 2)
        self.turntable_lock = Lock()
        self.item_turntable = None
    def _init_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - settings.BOTTOM_BAR_HEIGHT // 4
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - settings.BOTTOM_BAR_HEIGHT // 2
        self.weight_icon = Utils.load_svg(self.big_icon_size, settings.WEIGHT_ICON)
        self.caps_icon = Utils.load_svg(self.big_icon_size, settings.CAPS_ICON)
        if hasattr(settings, 'DAMAGE_TYPES_ICONS'):
            self.damage_icons = {dtp: Utils.load_svg(self.small_icon_size, path) for dtp, path in settings.DAMAGE_TYPES_ICONS.items()}
    def _create_fallback_image(self):
        h = max(20, self.turntable_draw_space.height - 50)
        if self.is_nv:
            w = max(20, self.turntable_draw_space.width - 50)
        else:
            w = max(20, self.turntable_draw_space.width + 10)
        srf = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
        clr_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        if not self.is_nv:
            srf.fill(clr_lght)# Fallback (if image name is not found)
            txt_srf_2 = self.inv_font.render('IMAGE NOT FOUND', True, (0, 0, 0))
        else:
            pygame.draw.rect(srf, clr_lght, srf.get_rect(), width=1)
            txt_srf_2 = self.inv_font.render('IMAGE NOT FOUND', True, clr_lght)
        txt_rct_2 = txt_srf_2.get_rect(center=(w // 2, h // 2))
        srf.blit(txt_srf_2, txt_rct_2)
        return srf

    def select_item(self):
        if self.no_items:
            return
        self.active_item_index = self.inv_list.selected_index
        self.toggle_equip()
    def scroll(self, direction):
        if self.no_items:
            return
        prv_ndx = self.inv_list.change_selection(direction)
        self.active_item_index = self.inv_list.selected_index
        if self.inv_list.selected_index != prv_ndx:
            self.item_selected = bool(self.unique_items and self.active_item_index is not None and (0 <= self.active_item_index < len(self.unique_items)))
            self.update_item_display()
    def update_item_display(self):
        if self.is_nv:
            if self.unique_items and self.inv_list.selected_index < len(self.unique_items):
                slctd_tm = self.unique_items[self.inv_list.selected_index]
                self.static_image = self._load_nv_static_image(slctd_tm)
                if not self.static_image:
                    self.static_image = self._create_fallback_image()
        else:
            if hasattr(self.tab_instance, 'init_footer'):
                self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())
            if self.enable_turntable:
                self.start_item_animation()
    def _load_nv_static_image(self, item):
        root_dir = self._get_project_root()
        nv_icons_dir = os.path.join(root_dir, 'images', 'new_vegas_icons')
        ct_str = ''
        if isinstance(self.category, (list, tuple)):
            ct_str = ' '.join((str(c) for c in self.category)).lower()
        elif isinstance(self.category, str):
            ct_str = self.category.lower()
        ct_sbfldrs = []
        if 'apparel' in ct_str or 'armor' in ct_str or 'clothing' in ct_str:
            ct_sbfldrs = ['apparel', 'armor', 'clothing', 'apparel_icons']
        elif 'weapon' in ct_str or 'arm' in ct_str:
            ct_sbfldrs = ['weapons', 'weapon', 'weapons_icons']
        elif 'aid' in ct_str or 'food' in ct_str:
            ct_sbfldrs = ['aid', 'food', 'medical', 'aid_icons']
        elif 'misc' in ct_str:
            ct_sbfldrs = ['misc', 'miscellaneous', 'misc_icons']
        elif 'ammo' in ct_str or 'junk' in ct_str:
            ct_sbfldrs = ['ammo', 'junk', 'ammo_icons']
        direct_paths = []
        for ttr in ['image', 'icon', 'icon_path', 'img', 'texture', 'path']:
            val = getattr(item, ttr, None)
            if isinstance(val, str) and val:
                direct_paths.extend([val, os.path.join(root_dir, val), os.path.join(root_dir, 'images', val), os.path.join(nv_icons_dir, val), os.path.join(root_dir, 'images', 'inventory', val)])
                for sub in ct_sbfldrs:
                    direct_paths.append(os.path.join(nv_icons_dir, sub, val))
        for p in direct_paths:
            if os.path.isfile(p):
                return self._process_loaded_image(p)
        cnddt_strngs = []
        for ttr in ['name', 'icon', 'icons', 'image', 'icon_path', 'id']:
            val = getattr(item, ttr, None)
            if isinstance(val, (list, tuple)):
                cnddt_strngs.extend([e for e in val if isinstance(e, str)])
            elif isinstance(val, str) and val:
                cnddt_strngs.append(val)

        def normalize(text):
            return re.sub('[^a-zA-Z0-9]', '', str(text)).lower() if text else ''
        def extract_words(text):
            return set(re.findall('[a-zA-Z0-9]+', str(text).lower()))
        cnddt_nrms = []
        cnddt_wrds = set()
        for c_str in cnddt_strngs:
            cln_str = os.path.splitext(os.path.basename(c_str))[0]
            nrm = normalize(cln_str)
            if nrm:
                cnddt_nrms.append(nrm)
                cnddt_wrds.update(extract_words(cln_str))
        if not cnddt_nrms:
            return None
        search_dirs = []
        for sub in ct_sbfldrs:
            sub_path = os.path.join(nv_icons_dir, sub)
            if os.path.exists(sub_path):
                search_dirs.append((sub_path, 30))
        if os.path.exists(nv_icons_dir):
            search_dirs.append((nv_icons_dir, 15))
        inv_dir = os.path.join(root_dir, 'images', 'inventory')
        if os.path.exists(inv_dir):
            search_dirs.append((inv_dir, 0))
        best_match_path = None
        bst_scr = 0
        for base_dir, fldr_bns in search_dirs:
            for rt, _, files in os.walk(base_dir):
                for file in files:
                    if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
                        continue
                    nm_no_xt = os.path.splitext(file)[0]
                    clean_file = re.sub('(_icon|icon)$', '', nm_no_xt, flags=re.IGNORECASE)
                    file_norm = normalize(clean_file)
                    file_words = extract_words(clean_file)
                    if not file_norm:
                        continue
                    scr = 0
                    for c_nrm in cnddt_nrms:
                        if file_norm == c_nrm:
                            scr = max(scr, 100)
                        elif file_norm.startswith(c_nrm) or c_nrm.startswith(file_norm):
                            scr = max(scr, 80)
                        elif file_norm in c_nrm or c_nrm in file_norm:
                            scr = max(scr, 70)
                    if scr == 0 and cnddt_wrds and file_words:
                        vrlp = len(cnddt_wrds & file_words) / float(len(cnddt_wrds))
                        if vrlp > 0.3:
                            scr = int(vrlp * 60)
                    if scr > 0:
                        ttl_scr = scr + fldr_bns
                        if ttl_scr > bst_scr:
                            bst_scr = ttl_scr
                            best_match_path = os.path.join(rt, file)
        if best_match_path and os.path.exists(best_match_path):
            return self._process_loaded_image(best_match_path)
        return None
    def _process_loaded_image(self, img_path):
        try:
            img = pygame.image.load(img_path).convert_alpha()
            clr_lght = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
            tnt_srf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            tnt_srf.fill((*clr_lght[:3], 255))
            img.blit(tnt_srf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            ct_str = ''
            if isinstance(self.category, (list, tuple)):
                ct_str = ' '.join((str(c) for c in self.category)).lower()
            elif isinstance(self.category, str):
                ct_str = self.category.lower()
            is_wpn_or_pprl = any((k in ct_str for k in ['weapon', 'arm', 'apparel', 'armor', 'clothing']))
            scl_fctr = 0.88 if is_wpn_or_pprl else 0.8
            w, h = img.get_size()
            mx_w = int(self.turntable_draw_space.width * scl_fctr)
            mx_h = int(self.turntable_draw_space.height * scl_fctr)
            scl = min(mx_w / max(1, w), mx_h / max(1, h))
            nw_wdth = max(1, int(w * scl))
            nw_hght = max(1, int(h * scl))
            return pygame.transform.smoothscale(img, (nw_wdth, nw_hght))
        except:
            return None
    def start_item_animation(self):
        if self.is_nv or not self.enable_turntable:
            return
        if self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None
        if not self.unique_items or self.inv_list.selected_index >= len(self.unique_items):
            return
        slctd_tm = self.unique_items[self.inv_list.selected_index]
        tm_key = getattr(slctd_tm, 'name', 'unknown')
        if tm_key in self._anim_cache:
            cns = self._anim_cache[tm_key]
        else:
            folder_path = self._find_item_folder(slctd_tm)
            cns = []
            if folder_path:
                loaded = Utils.load_images(folder_path)
                if loaded:
                    if isinstance(loaded, dict):
                        cns = list(loaded.values())
                    elif isinstance(loaded, list) and len(loaded) > 0 and isinstance(loaded[0], tuple):
                        cns = [item[1] for item in loaded]
                    elif isinstance(loaded, list):
                        cns = loaded
                    cns = [Utils.scale_image_abs(img, height=self.turntable_draw_space.height) for img in cns if img]
            if not cns:
                cns = [self._create_fallback_image()]
            self._anim_cache[tm_key] = cns
        class Animation2D: # repetitive names are useful for not forgetting

            def __init__(self, screen, center_pos, images, frame_duration):
                self.screen = screen
                self.center_pos = center_pos
                self.images = images
                self.frame_duration = frame_duration
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()
            def start(self):
                pass
            def stop(self):
                pass
            def render(self):
                now = pygame.time.get_ticks()
                if now - self.last_update > self.frame_duration:
                    self.current_frame = (self.current_frame + 1) % len(self.images)
                    self.last_update = now
                img = self.images[self.current_frame]
                mg_rct = img.get_rect(center=self.center_pos)
                self.screen.blit(img, mg_rct)
        self.item_turntable = Animation2D(self.screen, self.turntable_draw_space.center, cns, frame_duration=getattr(settings, 'SPEED', 1) * 100)
        self.item_turntable.start()
    def _find_item_folder(self, item):
        root_dir = self._get_project_root()
        inv_base_dir = os.path.join(root_dir, 'images', 'inventory')
        if not os.path.exists(inv_base_dir):
            return None

        def normalize(text):
            return re.sub('[^a-zA-Z0-9]', '', text).lower() if text else ''
        trgts = {normalize(getattr(item, 'icons', '')), normalize(getattr(item, 'name', ''))}
        trgts.discard('')
        if not trgts:
            return None
        for rt, dirs, _ in os.walk(inv_base_dir):
            for dir_name in dirs:
                if normalize(dir_name) in trgts:
                    return os.path.join(rt, dir_name)
        return None

    def init_footer_text(self):
        wght_srfc = self.init_footer_weight()
        cps_srfc = self.init_footer_caps()
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ftr_srfc.blit(wght_srfc, (0, 0))
        ftr_srfc.blit(cps_srfc, (0, 0))
        return ftr_srfc

    def init_footer_weight(self):
        wght_txt = f'{self.weight}/{settings.MAX_CARRY_WEIGHT}'
        wght_srfc = self.footer_font.render(wght_txt, True, settings.PIP_BOY_LIGHT)
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        cn_y = (settings.BOTTOM_BAR_HEIGHT - self.weight_icon.get_height()) // 2
        txt_y = (settings.BOTTOM_BAR_HEIGHT - wght_srfc.get_height()) // 2
        ftr_srfc.blit(self.weight_icon, (settings.BOTTOM_BAR_MARGIN, cn_y))
        ftr_srfc.blit(wght_srfc, (self.weight_icon.get_width() + settings.BOTTOM_BAR_MARGIN * 2, txt_y))
        return ftr_srfc
    def init_footer_caps(self):
        cps_txt = f'{settings.CAPS}'
        cps_srfc = self.footer_font.render(cps_txt, True, settings.PIP_BOY_LIGHT)
        ftr_srfc = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        cn_y = (settings.BOTTOM_BAR_HEIGHT - self.caps_icon.get_height()) // 2
        txt_y = (settings.BOTTOM_BAR_HEIGHT - cps_srfc.get_height()) // 2
        strt_x = settings.SCREEN_WIDTH // 4 + 4
        ftr_srfc.blit(self.caps_icon, (strt_x, cn_y))
        ftr_srfc.blit(cps_srfc, (strt_x + self.caps_icon.get_width() + settings.BOTTOM_BAR_MARGIN, txt_y))
        return ftr_srfc

    def handle_threads(self, tab_selected):
        if self.no_items:
            return
        if tab_selected and self.enable_turntable:
            self.update_item_display()
        elif not tab_selected and self.enable_turntable and self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None

    def calculate_grid_space(self):
        if self.is_nv:
            grd_tp = self.turntable_draw_space.bottom + 4
            grd_wdth = self.turntable_draw_space.width
            grd_hght = self.draw_space.bottom - grd_tp - 8
            return pygame.Rect(self.turntable_draw_space.left, grd_tp, grd_wdth, grd_hght)
        lst_spc = self.list_draw_space
        grd_tp = lst_spc.top + lst_spc.height * 0.38
        grd_hght = lst_spc.bottom - grd_tp
        cntr_x = settings.SCREEN_WIDTH // 2 + 80
        grd_wdth = self.draw_space.right - lst_spc.right - getattr(settings, 'GRID_RIGHT_MARGIN', 10) - 20
        grd_rct = pygame.Rect(0, 0, grd_wdth, grd_hght)
        grd_rct.centerx = cntr_x
        grd_rct.top = grd_tp
        return grd_rct
    def _draw_nv_stats_grid(self, rect, item):
        clr = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        bg_clr = (0, 0, 0)
        ct_str = ''
        if isinstance(self.category, (list, tuple)):
            ct_str = ' '.join((str(c) for c in self.category)).lower()
        elif isinstance(self.category, str):
            ct_str = self.category.lower()
        is_wpn = 'weapon' in ct_str or 'arm' in ct_str
        is_pprl = 'apparel' in ct_str or 'armor' in ct_str or 'clothing' in ct_str
        hs_cnd = is_wpn or is_pprl or hasattr(item, 'cnd')
        rw_h = 17
        if is_wpn or is_pprl:
            m_srf = self.inv_font.render('Maintain R)', True, clr)
            x_m = self.turntable_draw_space.right - m_srf.get_width() - 2
            y_m = self.turntable_draw_space.top - 2
            self.screen.blit(m_srf, (x_m, y_m))
            if is_wpn:
                md_prmpt = self.inv_font.render('Mod X)', True, clr)
                self.screen.blit(md_prmpt, (self.turntable_draw_space.right - md_prmpt.get_width() - 2, y_m + 20))
        if is_wpn:
            dps = str(getattr(item, 'dps', 0))
            vw = f"{getattr(item, 'vw', 0.0):.1f}"
            str_rq = str(getattr(item, 'str_req', 0))
            dam = str(getattr(item, 'damage', 0))
            wg = f"{getattr(item, 'weight', 0.0):.2f}"
            val = str(getattr(item, 'value', 0))
            rws = [[('DPS', dps), ('V/W', vw), ('STR', str_rq)], [('DAM', dam), ('WG', wg), ('VAL', val)]]
        elif is_pprl:
            dr = str(getattr(item, 'dr', getattr(item, 'damage_res', 0)))
            dt = str(getattr(item, 'dt', getattr(item, 'damage_threshold', 0)))
            wg = f"{getattr(item, 'weight', 0.0):.1f}"
            val = str(getattr(item, 'value', 0))
            rws = [[('DR', dr), ('DT', dt)], [('WG', wg), ('VAL', val)]]
        else:
            wg = f"{getattr(item, 'weight', 0.0):.1f}"
            val = str(getattr(item, 'value', 0))
            rws = [[('WG', wg), ('VAL', val)]]
        y_crrnt = rect.top
        for rw_dt in rws:
            y_tp = y_crrnt
            y_bttm = y_tp + rw_h
            nm_cls = len(rw_dt)
            if nm_cls == 3:
                cl_wdths = [int(rect.width * 0.33), int(rect.width * 0.39), rect.width - int(rect.width * 0.33) - int(rect.width * 0.39)]
            elif nm_cls == 2:
                cl_wdths = [rect.width // 2, rect.width - rect.width // 2]
            else:
                cl_wdths = [rect.width]
            x_lft = rect.left
            for c_dx, (lbl, vl_str) in enumerate(rw_dt):
                cr_w = cl_wdths[c_dx]
                x_rght = x_lft + cr_w if c_dx < nm_cls - 1 else rect.right
                pygame.draw.line(self.screen, clr, (x_lft + 6, y_tp), (x_rght, y_tp), 1)
                pygame.draw.line(self.screen, clr, (x_rght, y_tp), (x_rght, y_bttm - 6), 1)
                lbl_srf = self.inv_font.render(lbl, True, clr)
                vl_srf = self.inv_font.render(vl_str, True, clr)
                self.screen.blit(lbl_srf, (x_lft + 6, y_tp + 2))
                self.screen.blit(vl_srf, (x_rght - vl_srf.get_width() - 5, y_tp + 2))
                x_lft = x_rght
            y_crrnt = y_bttm
        if hs_cnd:
            y_tp = y_crrnt
            y_bttm = y_tp + rw_h
            cnd_w = int(rect.width * 0.33)
            x_lft_cnd = rect.left
            x_rght_cnd = rect.left + cnd_w
            pygame.draw.line(self.screen, clr, (x_lft_cnd + 6, y_tp), (x_rght_cnd, y_tp), 1)
            pygame.draw.line(self.screen, clr, (x_rght_cnd, y_tp), (x_rght_cnd, y_bttm - 6), 1)
            cnd_lbl = self.inv_font.render('CND', True, clr)
            self.screen.blit(cnd_lbl, (x_lft_cnd + 6, y_tp + 2))
            br_x = x_lft_cnd + 6 + cnd_lbl.get_width() + 4
            br_y = y_tp + 5
            br_w = max(10, x_rght_cnd - br_x - 5)
            br_h = 7
            cnd_mx = getattr(item, 'cnd_max', 100)
            if hasattr(item, 'cnd') and item.cnd is not None:
                cnd_vl = item.cnd
            else:
                if not hasattr(item, '_random_cnd'):
                    item._random_cnd = random.randint(15, 100)
                cnd_vl = item._random_cnd
            cndtn_pct = min(1.0, max(0.0, float(cnd_vl) / max(1, float(cnd_mx))))
            pygame.draw.rect(self.screen, clr, (br_x, br_y, br_w, br_h), 1)
            fll_w = int((br_w - 2) * cndtn_pct)
            if fll_w > 0:
                pygame.draw.rect(self.screen, clr, (br_x + 1, br_y + 1, fll_w, br_h - 2))
            ntch_x = br_x + 1 + int((br_w - 2) * 0.8)
            ntch_dpth = 2
            if cndtn_pct < 0.8:
                pygame.draw.line(self.screen, clr, (ntch_x, br_y), (ntch_x, br_y + ntch_dpth), 1)
                pygame.draw.line(self.screen, clr, (ntch_x, br_y + br_h - 1), (ntch_x, br_y + br_h - 1 - ntch_dpth), 1)
            else:
                pygame.draw.line(self.screen, bg_clr, (ntch_x, br_y), (ntch_x, br_y + ntch_dpth), 1)
                pygame.draw.line(self.screen, bg_clr, (ntch_x, br_y + br_h - 1), (ntch_x, br_y + br_h - 1 - ntch_dpth), 1)
            if is_wpn:
                x_lft_mm = x_rght_cnd
                x_rght_mm = rect.right
                pygame.draw.line(self.screen, clr, (x_lft_mm + 6, y_tp), (x_rght_mm, y_tp), 1)
                pygame.draw.line(self.screen, clr, (x_rght_mm, y_tp), (x_rght_mm, y_bttm - 6), 1)
                mm_tp = getattr(item, 'ammo_type', None) or getattr(item, 'ammo', None)
                if mm_tp:
                    mm_cnt = getattr(item, 'ammo_count', None)
                    if mm_cnt is None:
                        if hasattr(settings, 'TOTAL_AMMO') and mm_tp in settings.TOTAL_AMMO:
                            mm_cnt = settings.TOTAL_AMMO[mm_tp]
                        else:
                            mm_cnt = 0
                    mm_txt = f'{mm_tp} ({mm_cnt})'
                    mm_srf = self.inv_font.render(mm_txt, True, clr)
                    self.screen.blit(mm_srf, (x_rght_mm - mm_srf.get_width() - 5, y_tp + 2))
            y_crrnt = y_bttm
        if is_wpn:
            mds_vl = getattr(item, 'mods', None) or getattr(item, 'installed_mods', None) or getattr(item, 'weapon_mods', None)
            if mds_vl:
                if isinstance(mds_vl, (list, tuple)):
                    mds_lst = [str(m).strip() for m in mds_vl if str(m).strip()]
                elif isinstance(mds_vl, str):
                    mds_lst = [m.strip() for m in mds_vl.split(',') if m.strip()]
                else:
                    mds_lst = [str(mds_vl).strip()]
                if mds_lst:
                    md_rw_h = 13
                    y_tp = y_crrnt
                    ttl_h = len(mds_lst) * md_rw_h + 2
                    y_bttm = y_tp + ttl_h
                    x_lft = rect.left
                    x_rght = rect.right
                    pygame.draw.line(self.screen, clr, (x_lft + 6, y_tp), (x_rght, y_tp), 1)
                    pygame.draw.line(self.screen, clr, (x_rght, y_tp), (x_rght, y_bttm - 31), 1)
                    for idx, md_nm in enumerate(mds_lst):
                        md_y = y_tp + idx * md_rw_h
                        mx_vl_w = x_rght - (x_lft + 6) - 5
                        vl_srf = self.inv_font.render(md_nm, True, clr)
                        if vl_srf.get_width() > mx_vl_w and mx_vl_w > 10:
                            trnctd_txt = md_nm
                            while len(trnctd_txt) > 3 and self.inv_font.render(trnctd_txt + '...', True, clr).get_width() > mx_vl_w:
                                trnctd_txt = trnctd_txt[:-1]
                            vl_srf = self.inv_font.render(trnctd_txt + '...', True, clr)
                        self.screen.blit(vl_srf, (x_rght - vl_srf.get_width() - 5, md_y + 1))
                    y_crrnt = y_bttm

    def render(self):
        if self.no_items:
            return
        if self.is_nv:
            self.inv_list.render(self.screen, self.active_item_index, False)
            if self.static_image:
                rect = self.static_image.get_rect(center=self.turntable_draw_space.center)
                rect.centerx -= 20
                self.screen.blit(self.static_image, rect)
            if self.unique_items and self.active_item_index is not None and (self.active_item_index < len(self.unique_items)):
                slctd_tm = self.unique_items[self.active_item_index]
                grd_rct = self.calculate_grid_space()
                self._draw_nv_stats_grid(grd_rct, slctd_tm)
        else:
            self.tab_instance.render_footer(self)
            self.inv_list.render(self.screen, self.active_item_index, False)
            if self.enable_turntable and self.item_turntable:
                self.item_turntable.render()
            if hasattr(self.tab_instance, 'render_stats') and self.item_selected:
                if self.unique_items and self.active_item_index is not None and (self.active_item_index < len(self.unique_items)):
                    self.tab_instance.render_stats(self.unique_items[self.active_item_index])