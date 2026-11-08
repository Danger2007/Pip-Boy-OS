import datetime
import pygame
import settings
import os
import xml.etree.ElementTree as ET
import re

class Utils:

    @staticmethod
    def tint_image(image, color=settings.PIP_BOY_LIGHT):
        tntd = image.copy()
        tntd.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGB_MULT) #mmh... Cat :3
        return tntd
    @staticmethod
    def scale_image(image, scale):
        return pygame.transform.smoothscale_by(image, scale)

    @staticmethod
    def scale_image_abs(image, width=None, height=None):
        if width is None and height is None:
            return image
        if width is None:
            width = image.get_width() * (height / image.get_height())
        elif height is None:
            height = image.get_height() * (width / image.get_width())
        return pygame.transform.smoothscale(image, (int(width), int(height)))
    @staticmethod
    def load_images(folder, tint=settings.PIP_BOY_LIGHT):
        try:
            mgs = [Utils.tint_image(pygame.image.load(os.path.join(folder, f)).convert_alpha(), tint) for f in sorted(os.listdir(folder)) if f.endswith('.png')]
            return mgs
        except:
            return []

    @staticmethod
    def load_svgs_dict(folder, scale, tint=settings.PIP_BOY_LIGHT): # this works only for pngs, a ton of svgs for nothing :(
        try:
            mgs = {f: Utils.tint_image(pygame.image.load_sized_svg(os.path.join(folder, f), (scale, scale)).convert_alpha(), tint) for f in sorted(os.listdir(folder)) if f.endswith('.svg')}
            mgs = {k.replace('.svg', ''): v for k, v in mgs.items()}
            return mgs
        except:
            return {}

    @staticmethod
    def get_date():
        now = datetime.datetime.now()
        try:
            import user_config
        except:
            user_config = None
        dt_md = getattr(user_config, 'DATE_MODE', None) if user_config else None
        if dt_md is None:
            dt_md = getattr(settings, 'DATE_MODE', 'Game')
        ui_stl = getattr(user_config, 'UI_STYLE', None) if user_config else None
        if ui_stl is None:
            ui_stl = getattr(settings, 'UI_STYLE', '')
        ui_stl = str(ui_stl).lower()
        crrnt_dt = f'{now.day}.{now.month}'
        if str(dt_md).lower() == 'real':
            crrnt_year = now.strftime('%Y')
        elif 'nv' in ui_stl or 'vegas' in ui_stl:
            crrnt_year = '2281'
        else:
            crrnt_year = '2287'
        return f'{crrnt_dt}.{crrnt_year}'

    @staticmethod
    def load_svgs(folder, scale, tint=settings.PIP_BOY_LIGHT, load_transforms=False): 
        try:
            svg_files = [f for f in sorted(os.listdir(folder)) if f.endswith('.svg')]
            if not svg_files:
                return []
            first_svg_path = os.path.join(folder, svg_files[0])
            frst_wdth, frst_hght = Utils._get_svg_dimensions(first_svg_path)
            if load_transforms:
                frst_tx, frst_ty = Utils._get_svg_transform(first_svg_path)
            if frst_wdth <= 0 or frst_hght <= 0:
                scl_fctr = 1.0
            else:
                scl_fctr = scale / frst_wdth
            mgs = []
            trnsfrms = []
            for f in svg_files:
                svg_path = os.path.join(folder, f)
                width, height = Utils._get_svg_dimensions(svg_path)
                trgt_wdth = int(width * scl_fctr)
                trgt_hght = int(height * scl_fctr)
                trgt_sz = (trgt_wdth, trgt_hght)
                if load_transforms:
                    tx, ty = Utils._get_svg_transform(svg_path)
                    dlt_tx = tx - frst_tx
                    dlt_ty = ty - frst_ty
                    scld_tx = dlt_tx * scl_fctr
                    scld_ty = dlt_ty * scl_fctr
                    trnsfrms.append((scld_tx, scld_ty))
                img = pygame.image.load_sized_svg(svg_path, trgt_sz).convert_alpha()
                tntd_mg = Utils.tint_image(img, tint)
                mgs.append(tntd_mg)
            return (mgs, trnsfrms) if load_transforms else mgs
        except:
            return []
    @staticmethod
    def _get_svg_dimensions(svg_path): 
        try:
            tr = ET.parse(svg_path)
            rt = tr.getroot()
            vwbx = rt.get('viewBox')
            if vwbx:
                prts = vwbx.strip().split()
                if len(prts) >= 4:
                    vb_wdth = prts[2]
                    vb_hght = prts[3]
                    vb_wdth = re.sub('[^\\d.]', '', vb_wdth) if vb_wdth else '0'
                    vb_hght = re.sub('[^\\d.]', '', vb_hght) if vb_hght else '0'
                    return (float(vb_wdth), float(vb_hght))
            width = rt.get('width', '0')
            height = rt.get('height', '0')
            width = re.sub('[^\\d.]', '', width)
            height = re.sub('[^\\d.]', '', height)
            return (float(width or 0), float(height or 0))
        except:
            return (0.0, 0.0)

    @staticmethod
    def _get_svg_transform(svg_path):
        try:
            tr = ET.parse(svg_path)
            rt = tr.getroot()
            tx, ty = (0.0, 0.0)
            transform_str = rt.get('transform', '')
            if transform_str:
                tx, ty = Utils._parse_transform(transform_str)
            if tx == 0 and ty == 0:
                for lm in rt.iter():
                    if lm == rt:
                        continue
                    transform_str = lm.get('transform', '')
                    if transform_str:
                        lm_tx, lm_ty = Utils._parse_transform(transform_str)
                        if lm_tx != 0 or lm_ty != 0:
                            tx, ty = (lm_tx, lm_ty)
                            break
            return (tx, ty)
        except:
            return (0.0, 0.0)

    @staticmethod
    def _parse_transform(transform_str):
        if not transform_str:
            return (0.0, 0.0)
        trnslt_mtch = re.match('translate\\(\\s*([-\\d.]+)(?:\\s*,\\s*|\\s+)([-\\d.]+)\\s*\\)', transform_str)
        if trnslt_mtch:
            tx = float(trnslt_mtch.group(1))
            ty = float(trnslt_mtch.group(2))
            return (tx, ty)
        mtrx_mtch = re.match('matrix\\(\\s*([-\\d.]+)[,\\s]+([-\\d.]+)[,\\s]+([-\\d.]+)[,\\s]+([-\\d.]+)[,\\s]+([-\\d.]+)[,\\s]+([-\\d.]+)\\s*\\)', transform_str)
        if mtrx_mtch:
            tx = float(mtrx_mtch.group(5))
            ty = float(mtrx_mtch.group(6))
            return (tx, ty)
        return (0.0, 0.0)

    @staticmethod
    def load_svg(scale, path, tint=settings.PIP_BOY_LIGHT):
        if path.endswith('.svg'):
            width, height = Utils._get_svg_dimensions(path)
            scl_fctr = scale / width
            trgt_wdth = int(width * scl_fctr)
            trgt_hght = int(height * scl_fctr)
            trgt_sz = (trgt_wdth, trgt_hght)
            return Utils.tint_image(pygame.image.load_sized_svg(path, trgt_sz).convert_alpha(), tint)

    @staticmethod
    def play_sfx(sound_file, volume=settings.VOLUME, start=0, channel=None):
        if settings.SOUND_ON:
            snd = pygame.mixer.Sound(sound_file)
            snd.set_volume(volume)
            if channel is None:
                snd.play(start)
            else:
                ch = pygame.mixer.Channel(channel)
                ch.stop()
                ch.play(snd)
    @staticmethod
    def lerp(start, end, start_range, end_range, value):
        return start + (end - start) * ((value - start_range) / (end_range - start_range))

    @staticmethod
    def get_time(): # have to rework with raspi port
        now = datetime.datetime.now()
        crrnt_tm = now.strftime('%I:%M%p')
        return crrnt_tm
    @staticmethod
    def file_exists(path): # the backbone of fallbacks
        return os.path.isfile(path)