import os
import random
import settings
class PlaylistManager:

    def __init__(self):
        self.station_playlists = {}
    def add_intermissions_to_playlist(self, playlist): # need to learn how this works for FNV radios
        if not playlist:
            return playlist
        frq = settings.INTERMISSION_FREQUENCY
        mx_cnt = min(frq * 2, len(playlist) // 3)
        cnt = random.randint(1, mx_cnt) if mx_cnt >= 1 else 0
        if cnt == 0:
            return playlist
        ndcs = random.sample(range(len(playlist)), cnt)
        ntrmssn_chcs = {}
        base_path = settings.DCR_INTERMISSIONS_BASE_FOLDER
        for i in ndcs:
            sng = playlist[i]
            file_name = os.path.splitext(os.path.basename(sng))[0]
            prts = file_name.split('_')
            if len(prts) < 2:
                continue
            rtst = prts[-2]
            sng_nm = prts[-1]
            artist_path = os.path.join(base_path, rtst)
            pr_ptns = []
            ftr_ptns = []
            def gather_ogg_files(path):
                if os.path.exists(path):
                    for ntr in os.scandir(path):
                        if ntr.is_file() and ntr.name.endswith('.ogg'):
                            yield ntr.path
            pr_ptns.extend(gather_ogg_files(artist_path))
            ftr_ptns.extend(gather_ogg_files(artist_path))
            pre_dir = os.path.join(artist_path, 'pre')
            pr_ptns.extend(gather_ogg_files(pre_dir))
            after_dir = os.path.join(artist_path, 'after')
            ftr_ptns.extend(gather_ogg_files(after_dir))
            song_dir = os.path.join(artist_path, sng_nm)
            pr_ptns.extend(gather_ogg_files(song_dir))
            ftr_ptns.extend(gather_ogg_files(song_dir))
            song_pre_dir = os.path.join(song_dir, 'pre')
            pr_ptns.extend(gather_ogg_files(song_pre_dir))
            song_after_dir = os.path.join(song_dir, 'after')
            ftr_ptns.extend(gather_ogg_files(song_after_dir))
            hs_pr = len(pr_ptns) > 0
            hs_ftr = len(ftr_ptns) > 0
            if not (hs_pr or hs_ftr):
                continue
            choice = random.choice(['pre', 'after']) if hs_pr and hs_ftr else 'pre' if hs_pr else 'after'
            if choice == 'pre':
                slctd = random.choice(pr_ptns)
                ntrmssn_chcs.setdefault(sng, {})['pre'] = slctd
            else:
                slctd = random.choice(ftr_ptns)
                ntrmssn_chcs.setdefault(sng, {})['after'] = slctd
        nw_pllst = []
        for sng in playlist:
            if sng in ntrmssn_chcs and 'pre' in ntrmssn_chcs[sng]:
                nw_pllst.append(ntrmssn_chcs[sng]['pre'])
            nw_pllst.append(sng)
            if sng in ntrmssn_chcs and 'after' in ntrmssn_chcs[sng]:
                nw_pllst.append(ntrmssn_chcs[sng]['after'])
        return nw_pllst
    def generate_station_playlist_for_station(self, station, station_name=None):
        playlist = list(station['music_files'].keys())
        if not station['ordered']:
            random.shuffle(playlist)
        if station_name and station_name == 'Diamond City Radio':
            playlist = self.add_intermissions_to_playlist(playlist)
        return playlist