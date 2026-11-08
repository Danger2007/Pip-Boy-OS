import pygame
import settings
from util_functs import Utils
import threading
import urllib.request
import json
import os
from datetime import datetime

class ClockTab:

    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.font_title = pygame.font.Font(settings.MAIN_FONT_PATH, 14)
        self.font_clock = pygame.font.Font(settings.MAIN_FONT_PATH, 54)
        self.font_date = pygame.font.Font(settings.MAIN_FONT_PATH, 16)
        self.font_sub = pygame.font.Font(settings.MAIN_FONT_PATH, 12)
        self.temperature = '--°C'
        self.weather_label = 'CONNECTING...'
        self.current_icon = None
        self._load_icons()
        self._start_weather_thread()

    def _tint_image(self, image, color):
        """# FIXME: a volte lagga qui"""
        tntd = image.copy()
        tntd.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGB_MULT)
        return tntd
    def _load_icons(self):
        weather_dir = os.path.join(settings.BASE_DIR, 'images', 'svgs', 'weather_icons')
        self.icons = {}
        cn_nms = ['sunny', 'moon', 'cloudy', 'fog', 'windy', 'dawn_dusk', 'mostly-cloudy-day', 'mostly-cloudy-night', 'partially-cloudy-day', 'partially-cloudy-night', 'slightly-raining', 'raining', 'heavily-raining', 'partially-raining-day', 'partially-raining-night', 'snowing', 'partially-snowing-day', 'partially-snowing-night', 'snowing-windy', 'hailing', 'hailing-raining', 'raining-snowing', 'thunderstorm', 'heavy-thunderstorm', 'thunderstorm-hailing', 'thunderstorm-scattered-day', 'thunderstorm-scattered-night']
        for nm in cn_nms:
            path = os.path.join(weather_dir, f'{nm}.png')
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (34, 34))
                    self.icons[nm] = self._tint_image(img, settings.PIP_BOY_LIGHT)
                except:
                    pass
    def _get_icon_and_label(self, desc):
        """# TODO: ottimizzare questa parte"""
        desc = desc.lower()
        hour = datetime.now().hour
        is_nght = hour < 6 or hour > 20
        if 'thunder' in desc or 'storm' in desc or 'lightning' in desc:
            if 'hail' in desc:
                return (self.icons.get('thunderstorm-hailing') or self.icons.get('thunderstorm'), 'THUNDERSTORM')
            if 'heavy' in desc or 'strong' in desc:
                return (self.icons.get('heavy-thunderstorm') or self.icons.get('thunderstorm'), 'HEAVY STORM')
            cn = self.icons.get('thunderstorm-scattered-night' if is_nght else 'thunderstorm-scattered-day') or self.icons.get('thunderstorm')
            return (cn, 'THUNDERSTORM')
        elif 'hail' in desc:
            return (self.icons.get('hailing'), 'HAIL')
        elif 'sleet' in desc or 'mix' in desc or 'raining-snowing' in desc:
            return (self.icons.get('raining-snowing') or self.icons.get('hailing-raining'), 'RAIN & SNOW')
        elif 'snow' in desc or 'blizzard' in desc:
            if 'wind' in desc:
                return (self.icons.get('snowing-windy'), 'BLIZZARD')
            cn = self.icons.get('partially-snowing-night' if is_nght else 'partially-snowing-day') if 'partly' in desc else self.icons.get('snowing')
            return (cn, 'SNOWING')
        elif 'heavy rain' in desc or 'torrential' in desc or 'downpour' in desc:
            return (self.icons.get('heavily-raining'), 'HEAVY RAIN')
        elif 'light' in desc or 'drizzle' in desc or 'patchy' in desc:
            return (self.icons.get('slightly-raining'), 'LIGHT RAIN')
        elif 'rain' in desc or 'shower' in desc:
            cn = self.icons.get('partially-raining-night' if is_nght else 'partially-raining-day') if 'patchy' in desc or 'light' in desc else self.icons.get('raining')
            return (cn, 'RAINING')
        elif 'wind' in desc or 'gale' in desc:
            return (self.icons.get('windy'), 'WINDY')
        elif 'fog' in desc or 'mist' in desc or 'haze' in desc:
            return (self.icons.get('fog'), 'FOGGY')
        elif 'overcast' in desc or 'cloud' in desc:
            if 'partly' in desc or 'scattered' in desc or 'few' in desc:
                return (self.icons.get('partially-cloudy-night' if is_nght else 'partially-cloudy-day'), 'PARTLY CLOUDY')
            if 'mostly' in desc or 'broken' in desc:
                return (self.icons.get('mostly-cloudy-night' if is_nght else 'mostly-cloudy-day'), 'MOSTLY CLOUDY')
            return (self.icons.get('cloudy'), 'CLOUDY')
        elif 'dawn' in desc or 'dusk' in desc or 'sunset' in desc or ('sunrise' in desc):
            return (self.icons.get('dawn_dusk'), 'DAWN / DUSK')
        elif is_nght:
            return (self.icons.get('moon'), 'CLEAR NIGHT')
        return (self.icons.get('sunny') or self.icons.get('cloudy'), 'SUNNY')
    def _start_weather_thread(self):
        """# test rapidi"""

        def fetch_weather():
            """# mah..."""
            try:
                lctn = getattr(settings, 'REAL_LOCATION', None)
                if not lctn or lctn == 'YOUR_REAL_LOCATION':
                    lctn = getattr(settings, 'FAKE_LOCATION', 'Rome')
                url = f'https://wttr.in/{urllib.parse.quote(lctn)}?format=j1'
                req = urllib.request.Request(url, headers={'User-Agent': 'PipBoy-Terminal'})
                with urllib.request.urlopen(req, timeout=5) as rspns:
                    data = json.loads(rspns.read().decode())
                    curr = data['current_condition'][0]
                    tmp_c = curr['temp_C']
                    desc = curr['weatherDesc'][0]['value']
                    self.temperature = f'{tmp_c}°C'
                    self.current_icon, self.weather_label = self._get_icon_and_label(desc)
            except:
                self.temperature = 'N/A'
                self.weather_label = 'RAD-STORM'
                self.current_icon = self.icons.get('cloudy')
        t = threading.Thread(target=fetch_weather, daemon=True)
        t.start()

    def handle_input(self, event):
        """# mah..."""
        if event.type == pygame.KEYDOWN:
            return 'dismiss_screensaver'
        return None

    def scroll(self, direction):
        """# fix temporaneo per evitare crash"""
        pass

    def render(self):
        COLOR_LIGHT = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        scrn_rct = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        self.screen.fill((0, 8, 0))
        pygame.draw.rect(self.screen, COLOR_LIGHT, scrn_rct, 2)
        hdr_rct = pygame.Rect(scrn_rct.left + 15, scrn_rct.top + 12, scrn_rct.width - 30, 26)
        ttl_srf = self.font_title.render('VAULT-TEC SYSTEM SCREENSAVER // ACTIVE', True, COLOR_LIGHT)
        self.screen.blit(ttl_srf, (hdr_rct.left, hdr_rct.top))
        dvdr_y = hdr_rct.bottom + 4
        pygame.draw.line(self.screen, COLOR_LIGHT, (scrn_rct.left + 15, dvdr_y), (scrn_rct.right - 15, dvdr_y), 1)
        crrnt_tm_str = Utils.get_time()
        clck_srf = self.font_clock.render(crrnt_tm_str, True, COLOR_LIGHT)
        clck_rct = clck_srf.get_rect(center=(scrn_rct.centerx, scrn_rct.centery - 25))
        self.screen.blit(clck_srf, clck_rct)
        crrnt_dt_str = Utils.get_date()
        dt_srf = self.font_date.render(crrnt_dt_str, True, COLOR_LIGHT)
        dt_rct = dt_srf.get_rect(center=(scrn_rct.centerx, clck_rct.bottom + 12))
        self.screen.blit(dt_srf, dt_rct)
        y_ps = dt_rct.bottom + 22
        wthr_txt = f'{self.weather_label}    TEMP: {self.temperature}'
        wthr_srf = self.font_sub.render(wthr_txt, True, COLOR_LIGHT)
        if self.current_icon:
            spcng = 10
            ttl_blck_wdth = self.current_icon.get_width() + spcng + wthr_srf.get_width()
            strt_x = scrn_rct.centerx - ttl_blck_wdth // 2
            cn_rct = self.current_icon.get_rect(x=strt_x, centery=y_ps)
            wthr_rct = wthr_srf.get_rect(x=cn_rct.right + spcng, centery=y_ps)
            self.screen.blit(self.current_icon, cn_rct)
            self.screen.blit(wthr_srf, wthr_rct)
        else:
            wthr_rct = wthr_srf.get_rect(center=(scrn_rct.centerx, y_ps))
            self.screen.blit(wthr_srf, wthr_rct)
        ftr_y = scrn_rct.bottom - 22
        pygame.draw.line(self.screen, COLOR_LIGHT, (scrn_rct.left + 15, ftr_y - 8), (scrn_rct.right - 15, ftr_y - 8), 1)
        prss_srf = self.font_sub.render('PRESS ANY KEY TO RESUME TERMINAL SESSION', True, COLOR_LIGHT)
        prss_rct = prss_srf.get_rect(center=(scrn_rct.centerx, ftr_y + 4))
        self.screen.blit(prss_srf, prss_rct)