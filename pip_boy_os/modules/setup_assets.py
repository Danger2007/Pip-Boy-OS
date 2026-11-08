import os
import zipfile
import io
import requests
import pip_boy_os
import importlib.util
import shutil
import tempfile

def main():
    # Takes a lot of time to load, FIX LATER
    print('Downloading assets from GitHub...')
    url = 'https://github.com/Danger2007/Pip-Boy-OS/archive/refs/heads/main.zip'
    try:
        rspns = requests.get(url)
        rspns.raise_for_status()
        if hasattr(pip_boy_os, '__file__') and pip_boy_os.__file__:
            pkg_dir = os.path.dirname(os.path.abspath(pip_boy_os.__file__))
        else:
            spc = importlib.util.find_spec('pip_boy_os')
            pkg_dir = os.path.dirname(spc.origin) if spc and spc.origin else os.getcwd()
        print('Extraction and configuration of assets in progress...')
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(io.BytesIO(rspns.content)) as z:
                z.extractall(temp_dir)
            tp_fldr = z.namelist()[0].split('/')[0]
            src_ppb = os.path.join(temp_dir, tp_fldr, 'pip_boy_os')
            for fldr_nm in ['fonts', 'images', 'sounds', 'objs']:
                src_fldr = os.path.join(src_ppb, fldr_nm)
                dst_fldr = os.path.join(pkg_dir, fldr_nm)
                if os.path.exists(src_fldr):
                    if os.path.exists(dst_fldr):
                        shutil.rmtree(dst_fldr)
                    shutil.copytree(src_fldr, dst_fldr)
        print('Assets configured successfully! You can now start pipboy-os.')
    except:
        print(f'Error during asset download: {e}') # E
if __name__ == '__main__':
    main()