from data_models import WeaponItem, ApparelItem, AidItem, MiscItem, IconConfig, AmmoItem, JunkItem
from configparser import ConfigParser
from typing import Tuple, Dict

class Inventory:
    _instance = None
    def __new__(cls, *args, **kwargs): # old?
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.items = {}
        return cls._instance

    def add_item(self, item, quantity=1):
        if item.name in self.items:
            self.items[item.name] = (item, self.items[item.name][1] + quantity)
        else:
            self.items[item.name] = (item, quantity)
    def get_all_items(self, category=None):
        xpndd_lst = []
        for item, quantity in self.items.values():
            if category and item.category != category:
                continue
            xpndd_lst.extend([item] * quantity)
        return xpndd_lst
    def get_unique_items(self, category=None):
        nq_lst = []
        for item, _ in self.items.values():
            if category and item.category != category:
                continue
            if item not in nq_lst:
                nq_lst.append(item)
        return nq_lst

    def get_item_names(self, category=None):
        tm_nms = []
        for name, (item, quantity) in self.items.items():
            if category and item.category != category:
                continue
            if quantity > 1:
                tm_nms.append(f'{name} ({quantity})')
            else:
                tm_nms.append(name)
        return tm_nms
class ItemLoader:

    def __init__(self, ini_file):
        import os
        self.config = ConfigParser()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ini_path = os.path.join(current_dir, ini_file)
        self.config.read(ini_path)
        self.items = {}

    def _parse_icon_configs(self, value):
        if not value:
            return ()
        return tuple((IconConfig(path=ic.split(':')[0], value=int(ic.split(':')[1])) for ic in [x.strip() for x in value.split(',')]))
    def _parse_dicts(self, value):
        if not value:
            return {}
        return dict(((prt.split(':')[0].strip(), int(prt.split(':')[1])) for prt in value.split(',')))
    def load_items(self):
        for sctn in self.config.sections():
            data = dict(self.config[sctn])
            tm_tp = data.get('category', 'Misc')
            bs_dt = {'name': sctn, 'weight': float(data.get('weight', 0)), 'value': int(data.get('value', 0)), 'icons': data.get('icons', ''), 'description': data.get('description', ''), 'category': tm_tp}
            if tm_tp == 'Weapon':
                wpn = WeaponItem(**bs_dt, damage=int(data.get('damage', 0)), fire_rate=int(data.get('fire_rate', 0)), range=int(data.get('range', 0)), accuracy=int(data.get('accuracy', 0)), ammo_type=data.get('ammo_type', ''), damage_types=self._parse_icon_configs(data.get('damage_types', '')))
                mds_rw = data.get('mods', '')
                wpn.mods = [m.strip() for m in mds_rw.split(',')] if mds_rw else []
                self.items[sctn] = wpn
            elif tm_tp == 'Apparel':
                self.items[sctn] = ApparelItem(**bs_dt, defense=int(data.get('defense', 0)), damage_resist=self._parse_icon_configs(data.get('damage_resist', '')), special_bonuses=self._parse_dicts(data.get('special_bonuses', '')))
            elif tm_tp == 'Aid':
                self.items[sctn] = AidItem(**bs_dt, health=int(data.get('health', 0)), rads=int(data.get('rads', 0)), ap=int(data.get('ap', 0)), addiction_risk=data.get('addiction_risk', 'None'), special_bonuses=self._parse_dicts(data.get('special_bonuses', '')))
            elif tm_tp == 'Ammo':
                self.items[sctn] = AmmoItem(**bs_dt, damage_type=data.get('damage_type', ''))
            elif tm_tp == 'Junk':
                self.items[sctn] = JunkItem(**bs_dt, components=self._parse_dicts(data.get('components', '')))
            elif tm_tp in ('Misc', 'Weapon Mod'):
                self.items[sctn] = MiscItem(**bs_dt, type=data.get('type', ''))
            else:
                raise ValueError(f'Unknown item type: {tm_tp}')
        return self.items
if __name__ == '__main__':
    loader = ItemLoader('items.ini')
    items = loader.load_items()