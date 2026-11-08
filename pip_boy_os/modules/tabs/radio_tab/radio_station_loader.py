import os
import configparser
import time
from concurrent.futures import ThreadPoolExecutor
from tinytag import TinyTag
VALID_EXTENSIONS = ('.ogg', '.mp3', '.wav', '.webm', '.m4a', '.flac')

class RadioStationLoader:
    def __init__(self, base_folder, intermissions_base_folder):
        self.base_folder = base_folder
        self.intermissions_base_folder = intermissions_base_folder
        self.radio_stations = {}
        self.intermissions = {}

    def load_music_files(self, station_folder):
        music_files = {}
        try:
            for entry in os.scandir(station_folder):
                if entry.is_file() and entry.name.lower().endswith(VALID_EXTENSIONS):
                    try:
                        tag = TinyTag.get(entry.path)
                        music_files[entry.path] = int(tag.duration * 1000) if tag.duration else 180000
                    except:
                        music_files[entry.path] = 180000
        except:
            pass
        return music_files
    def load_intermissions(self, base_path=None):
        intermissions = {}
        intermissions_path = base_path or self.intermissions_base_folder
        if not os.path.exists(intermissions_path):
            return intermissions
        for entry in os.scandir(intermissions_path):
            if entry.is_dir():
                intermissions.update(self.load_intermissions(entry.path))
            elif entry.is_file() and entry.name.lower().endswith(VALID_EXTENSIONS):
                try:
                    tag = TinyTag.get(entry.path)
                    intermissions[entry.path] = int(tag.duration * 1000) if tag.duration else 10000
                except:
                    intermissions[entry.path] = 10000
        return intermissions

    def load_radio_stations(self): # future optimiztion
        def load_single_station(entry):
            if not entry.is_dir():
                return None
            ini_path = os.path.join(entry.path, 'station.ini')
            sttn_nm = entry.name.replace('_', ' ')
            rdrd = False
            if os.path.exists(ini_path):
                try:
                    cnfg = configparser.ConfigParser()
                    with open(ini_path) as f:
                        cnfg.read_file(f)
                    sttn_nm = cnfg.get('metadata', 'station_name', fallback=sttn_nm)
                    rdrd = cnfg.getboolean('metadata', 'ordered', fallback=False)
                except:
                    pass
            music_files = self.load_music_files(entry.path)
            if not music_files:
                return None
            sttn_dt = {'ordered': rdrd, 'music_files': music_files, 'start_timestamp': time.time()}
            return (sttn_nm, sttn_dt)
        try:
            if os.path.exists(self.base_folder):
                with os.scandir(self.base_folder) as ntrs:
                    with ThreadPoolExecutor(max_workers=4) as xctr:
                        self.radio_stations = {name: data for rslt in xctr.map(load_single_station, ntrs) if rslt for name, data in [rslt]}
        except:
            self.radio_stations = {}
        try:
            self.intermissions = self.load_intermissions()
        except:
            self.intermissions = {}