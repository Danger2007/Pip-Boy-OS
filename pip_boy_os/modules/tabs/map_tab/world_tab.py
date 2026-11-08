import hashlib
import io
import json
import math
import os
import random
from threading import Lock, Thread
import requests
import pygame
import settings
import urllib.request
from typing import Tuple, List, Dict, Optional
from pygame.math import Vector2
from PIL import Image
from util_functs import Utils
def update_and_save_position(): # I'm trying to make it so it tracks the position irl, but I'm having some problems, might use it only for the Pip-Boy hw
    api_key = getattr(settings, 'GEOAPIFY_API_KEY', '') or getattr(settings, 'GEOAPIFY_KEY', '')
    if not api_key or api_key == 'YOUR_GEOAPIFY_KEY':
        return False
    try:
        url = f'https://api.geoapify.com/v1/ipinfo?apiKey={api_key}'
        req = urllib.request.Request(url, headers={'User-Agent': 'PipBoy-Terminal'})
        with urllib.request.urlopen(req, timeout=5) as rspns:
            data = json.loads(rspns.read().decode())
            loc = data.get('location', {})
            lat = loc.get('latitude')
            lon = loc.get('longitude')
            ct = data.get('city', {}).get('name', None)
            if lat and lon:
                crrnt_lt = getattr(settings, 'LATITUDE', 0.0)
                crrnt_ln = getattr(settings, 'LONGITUDE', 0.0)
                if abs(crrnt_lt - lat) > 0.0001 or abs(crrnt_ln - lon) > 0.0001:
                    settings.LATITUDE = lat
                    settings.LONGITUDE = lon
                    secrets_path = os.path.join(settings.BASE_DIR, 'settings_secrets.py')
                    if os.path.exists(secrets_path):
                        with open(secrets_path, 'r', encoding='utf-8') as f:
                            lns = f.readlines()
                        nw_lns = []
                        lt_wrttn, ln_wrttn, lc_wrttn = (False, False, False)
                        for ln in lns:
                            strppd = ln.strip()
                            if strppd.startswith('LATITUDE'):
                                nw_lns.append(f'LATITUDE = {lat}\n')
                                lt_wrttn = True
                            elif strppd.startswith('LONGITUDE'):
                                nw_lns.append(f'LONGITUDE = {lon}\n')
                                ln_wrttn = True
                            elif ct and strppd.startswith('REAL_LOCATION'):
                                nw_lns.append(f"REAL_LOCATION = '{ct}'\n")
                                lc_wrttn = True
                            else:
                                nw_lns.append(ln)
                        if not lt_wrttn:
                            nw_lns.append(f'LATITUDE = {lat}\n')
                        if not ln_wrttn:
                            nw_lns.append(f'LONGITUDE = {lon}\n')
                        if ct and (not lc_wrttn):
                            nw_lns.append(f"REAL_LOCATION = '{ct}'\n")
                        with open(secrets_path, 'w', encoding='utf-8') as f:
                            f.writelines(nw_lns)
                        print(f'[Geo] Position updated and saved in settings_secrets.py: {ct} ({lat}, {lon})')
                    return True
    except Exception as e:
        print(f'[Geo IP Error]: {e}')
    return False
class BaseMap:

    def __init__(self, screen, draw_space, map_image):
        self.screen = screen
        self.draw_space = draw_space
        self.map_image = map_image
        self.map_surface = map_image.copy()
        self.min_zoom = self._calculate_min_zoom()
        self.max_zoom = settings.MIN_MAP_ZOOM
        self.map_zoom = max(min(settings.INITIAL_MAP_ZOOM, self.max_zoom), self.min_zoom)
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = Vector2(self._calculate_initial_offset())
        self.directions = [(-settings.MAP_MOVE_SPEED, 0), (0, -settings.MAP_MOVE_SPEED), (0, settings.MAP_MOVE_SPEED), (settings.MAP_MOVE_SPEED, 0)]
        self.is_initialized = True

    def _calculate_initial_offset(self):
        return Vector2((self.zoomed_map_surface.get_width() - self.draw_space.width) / 2, (self.zoomed_map_surface.get_height() - self.draw_space.height) / 2)

    def _update_zoomed_surface(self):
        nw_sz = Vector2(self.map_surface.get_size()) * self.map_zoom
        return pygame.transform.smoothscale(self.map_surface, nw_sz.xy)
    def _calculate_min_zoom(self):
        mg_sz = Vector2(self.map_surface.get_size())
        drw_sz = Vector2(self.draw_space.size)
        return max(drw_sz.x / mg_sz.x, drw_sz.y / mg_sz.y)
    def clamp_offset(self):
        zmd_sz = Vector2(self.zoomed_map_surface.get_size())
        drw_sz = Vector2(self.draw_space.size)
        mx_ffst = zmd_sz - drw_sz
        if not isinstance(self.map_offset, Vector2):
            self.map_offset = Vector2(self.map_offset)
        for xs in [0, 1]:
            if zmd_sz[xs] < drw_sz[xs]:
                self.map_offset[xs] = (zmd_sz[xs] - drw_sz[xs]) / 2
            else:
                self.map_offset[xs] = max(0, min(self.map_offset[xs], mx_ffst[xs]))

    def zoom(self, zoom_in):
        ld_zm = self.map_zoom
        zm_stp = ld_zm * settings.MAP_ZOOM_SPEED
        nw_zm = ld_zm + zm_stp if zoom_in else ld_zm - zm_stp
        nw_zm = max(self.min_zoom, min(self.max_zoom, nw_zm))
        if nw_zm == ld_zm:
            return
        vw_cntr = Vector2(self.draw_space.center) - Vector2(self.draw_space.topleft)
        rg_cntr = (Vector2(self.map_offset) + vw_cntr) / ld_zm
        self.map_zoom = nw_zm
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = rg_cntr * nw_zm - vw_cntr
        self.clamp_offset()

    def navigate(self, direction):
        if 0 <= direction < 4:
            if not isinstance(self.map_offset, Vector2):
                self.map_offset = Vector2(self.map_offset)
            dx, dy = self.directions[direction]
            self.map_offset += Vector2(dx, dy)
            self.clamp_offset()
    def render(self):
        src_rct = pygame.Rect(*self.map_offset, *self.draw_space.size)
        src_rct.clamp(self.zoomed_map_surface.get_rect())
        self.screen.blit(self.zoomed_map_surface, self.draw_space.topleft, src_rct)
class WorldMap(BaseMap):
    def __init__(self, screen, draw_space):
        fk_lc = str(getattr(settings, 'FAKE_LOCATION', 'Commonwealth')).lower()
        shw_mrkrs = getattr(settings, 'SHOW_ALL_MARKERS', True)
        if 'mojave' in fk_lc:
            map_path = settings.MOJAVE_MAP_MARKERS if shw_mrkrs else settings.MOJAVE_MAP
        else:
            map_path = getattr(settings, 'COMMONWEALTH_MAP_MARKERS', '') if shw_mrkrs else getattr(settings, 'COMMONWEALTH_MAP', '')
        if not map_path or not os.path.exists(map_path):
            bs_no_xt, _ = os.path.splitext(map_path)
            for ext in ['.webp', '.png', '.jpg', '.jpeg']:
                test_path = bs_no_xt + ext
                if os.path.exists(test_path):
                    map_path = test_path
                    break
        map_image = Utils.tint_image(pygame.image.load(map_path).convert_alpha())
        super().__init__(screen, draw_space, map_image)

class RealMap(BaseMap):

    def __init__(self, screen, draw_space, api_zoom=13):
        self.screen = screen
        update_and_save_position()
        self.lat, self.lon = (settings.LATITUDE, settings.LONGITUDE)
        self.api_zoom = api_zoom
        self.draw_space = draw_space
        if hasattr(settings, 'MAP_ICONS_BASE_FOLDER') and os.path.exists(settings.MAP_ICONS_BASE_FOLDER):
            self.icons = Utils.load_svgs_dict(settings.MAP_ICONS_BASE_FOLDER, settings.MAP_ICON_SIZE)
        else:
            self.icons = {}
        self.failed_connection = False
        self._cache_lock = Lock()
        self._places_cache_lock = Lock()
        self.rendered_map_lock = Lock()
        self.is_initialized = False
        Thread(target=self.init_map, daemon=True).start()
    def zoom(self, zoom_in):
        if self.failed_connection:
            return
        super().zoom(zoom_in)

    def navigate(self, direction):
        if self.failed_connection:
            return
        super().navigate(direction)
    def init_map(self):
        image = self._fetch_map_image()
        places = self._fetch_places(image) if not self.failed_connection else []
        rndrd_mp = self._draw_markers(image, places) if not self.failed_connection else image
        super().__init__(self.screen, self.draw_space, rndrd_mp)

    def _invert_surface(self, surface):
        rw_str = pygame.image.tostring(surface, 'RGBA')
        pl_mg = Image.frombytes('RGBA', surface.get_size(), rw_str)
        gr_mg = pl_mg.convert('L')
        nv_gr = Image.eval(gr_mg, lambda x: 255 - x)
        nv_rgb = nv_gr.convert('RGBA')
        return pygame.image.fromstring(nv_rgb.tobytes(), nv_rgb.size, 'RGBA')
    def _fetch_map_image(self): 
        os.makedirs(settings.MAP_CACHE, exist_ok=True)
        filename = f'{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{settings.MAP_SIZE}.png'
        cache_path = os.path.join(settings.MAP_CACHE, filename)
        if os.path.exists(cache_path):
            mp_mg = pygame.image.load(cache_path).convert_alpha()
            self.failed_connection = False
            mp_mg_nvrtd = self._invert_surface(mp_mg)
            return Utils.tint_image(mp_mg_nvrtd)
        api_key = getattr(settings, 'GEOAPIFY_API_KEY', '') or getattr(settings, 'GEOAPIFY_KEY', '')
        url = f'https://maps.geoapify.com/v1/staticmap?style=klokantech-basic&width={settings.MAP_SIZE}&height={settings.MAP_SIZE}&center=lonlat:{self.lon},{self.lat}&zoom={self.api_zoom}&apiKey={api_key}'
        try:
            rspns = requests.get(url, timeout=10)
            rspns.raise_for_status()
            if os.path.exists(settings.MAP_CACHE):
                for cached_file in os.listdir(settings.MAP_CACHE):
                    if cached_file.endswith('.png') and cached_file != filename:
                        try:
                            os.remove(os.path.join(settings.MAP_CACHE, cached_file))
                        except:
                            pass
            with open(cache_path, 'wb') as f:
                f.write(rspns.content)
            mp_mg = pygame.image.load(io.BytesIO(rspns.content)).convert_alpha()
            self.failed_connection = False
            mp_mg_nvrtd = self._invert_surface(mp_mg)
            return Utils.tint_image(mp_mg_nvrtd)
        except Exception as e:
            print(f'ERROR MAP API: {e}')
            self.failed_connection = True
            mp_mg = pygame.Surface((settings.MAP_SIZE, settings.MAP_SIZE))
            if hasattr(settings, 'PIP_BOY_DARK'):
                mp_mg.fill(settings.PIP_BOY_DARK)
            return mp_mg

    def _fetch_places(self, map_image):
        return []
    def _draw_markers(self, map_image, places):
        """# da testare meglio sul raspberry"""
        surface = map_image.copy()
        cntr_x = surface.get_width() // 2
        cntr_y = surface.get_height() // 2
        clr = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        pnts = [(cntr_x, cntr_y - 8), (cntr_x - 6, cntr_y + 6), (cntr_x + 6, cntr_y + 6)]
        pygame.draw.polygon(surface, clr, pnts)
        return surface
    def render(self):
        if self.failed_connection:
            bg_clr = settings.PIP_BOY_DARK if hasattr(settings, 'PIP_BOY_DARK') else (0, 0, 0)
            self.screen.fill(bg_clr, self.draw_space)
            bx_w, bx_h = (160, 50)
            bx_x = self.draw_space.x + (self.draw_space.width - bx_w) // 2
            bx_y = self.draw_space.y + (self.draw_space.height - bx_h) // 2
            pygame.draw.rect(self.screen, settings.PIP_BOY_LIGHT, (bx_x, bx_y, bx_w, bx_h), 2)
            mp_fnt = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 12)
            txt_srfc = mp_fnt.render('NO CONNECTION', True, settings.PIP_BOY_LIGHT)
            txt_x = bx_x + (bx_w - txt_srfc.get_width()) // 2
            txt_y = bx_y + (bx_h - txt_srfc.get_height()) // 2
            self.screen.blit(txt_srfc, (txt_x, txt_y))
        else:
            super().render()