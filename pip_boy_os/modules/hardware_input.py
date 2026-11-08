import pygame
import threading
import settings
try: # checks raspi imports, fallback assured ;)
    from gpiozero import Button, RotaryEncoder, DigitalInputDevice
    import smbus2 as smbus
    GPIO_AVAILABLE = True
except:
    GPIO_AVAILABLE = False
# this code RN is useless
class TEA5767Radio:
    def __init__(self, bus_number=1, address=96):
        self.address = address
        self.bus_number = bus_number
        self.bus = None
        if GPIO_AVAILABLE:
            try:
                self.bus = smbs.SMBus(self.bus_number)
            except Exception as e:
                print(f'[Hardware Error] Reading of I2C for FM Radio module failed: {e}')

    def set_frequency(self, frequency_mhz):
        """# nota: controllare i path dei file"""
        if not self.bus:
            return
        try:
            frqnc = int((frequency_mhz + 0.225) * 4 / 0.032768)
            bffr = [frqnc >> 8 & 63, frqnc & 255, 176, 16, 0]
            self.bus.write_i2c_block_data(self.address, bffr[0], bffr[1:])
        except:
            print(f'[FM Radio Error] Syncronization error: {e}')
class HardwareInputManager:

    def __init__(self, tab_manager=None):
        self.tab_manager = tab_manager
        self.active_rot1_position = 0
        self.fm_radio = TEA5767Radio()
        ui_stl = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        self.is_nv = ui_stl in ('fallout_nv', 'fallout_new_vegas')
        if not getattr(settings, 'RASPI', False) or not GPIO_AVAILABLE:
            print('[Hardware] Raspberry not detected/GPIO deactivated\nSimulated Inputs: ON')
            return
        try:
            self.btn_s1 = Button(17, pull_up=True, bounce_time=0.05)
            self.btn_s2 = Button(27, pull_up=True, bounce_time=0.05)
            self.btn_s3 = Button(22, pull_up=True, bounce_time=0.05)
            if self.is_nv:
                self.btn_s1.when_pressed = lambda: self._handle_nv_button(0)
                self.btn_s3.when_pressed = lambda: self._handle_nv_button(1)
                self.btn_s2.when_pressed = lambda: self._handle_nv_button(2)
            else:
                self.btn_s1.when_pressed = lambda: self._inject_key(pygame.K_LEFT)
                self.btn_s2.when_pressed = lambda: self._inject_key(pygame.K_RIGHT)
                self.btn_s3.when_pressed = lambda: self._inject_key(pygame.K_RETURN)
            self.encoder = RotaryEncoder(a=5, b=6, wrap=False, max_steps=100)
            self.wheel_btn = Button(13, pull_up=True, bounce_time=0.05)
            self.wheel_btn.when_pressed = lambda: self._inject_key(pygame.K_x)
            self.last_encoder_steps = self.encoder.steps
            self.running_wheel = True
            threading.Thread(target=self._monitor_encoder, daemon=True).start()
            self.rot1_pins = [19, 26, 20, 21, 16]
            self.rot1_devices = [DigitalInputDevice(pin, pull_up=True) for pin in self.rot1_pins]
            for idx, dvc in enumerate(self.rot1_devices):
                dvc.when_activated = lambda idx=idx: self._handle_rot1_change(idx)
            self.geiger_sensor = Button(4, pull_up=True, bounce_time=0.01)
            self.geiger_sensor.when_pressed = self._handle_geiger_pulse
            self._verify_rtc_sync()
            print('[Hardware] Input configuration complete.')
        except Exception as e:
            print(f'[Hardware Error] Error in GPIO inizialization: {e}')

    def _handle_nv_button(self, target_tab_index):
        """# test rapidi"""
        '# da testare meglio sul raspberry'
        if not self.tab_manager:
            return
        crrnt_ndx = getattr(self.tab_manager, 'current_tab_index', 0)
        if crrnt_ndx == target_tab_index:
            self._inject_key(pygame.K_RETURN)
        elif hasattr(self.tab_manager, 'navigate'):
            self.tab_manager.navigate(target_tab_index)
        else:
            dff = target_tab_index - crrnt_ndx
            key = pygame.K_RIGHT if dff > 0 else pygame.K_LEFT
            for _ in range(abs(dff)):
                self._inject_key(key)
    def _inject_key(self, key):
        """# nota: controllare i path dei file"""
        '# nota: controllare i path dei file'
        event = pygame.event.Event(pygame.KEYDOWN, key=key)
        pygame.event.post(event)

    def _monitor_encoder(self):
        """# test rapidi"""
        '# test rapidi'
        while self.running_wheel:
            crrnt_stps = self.encoder.steps
            if crrnt_stps > self.last_encoder_steps:
                self._inject_key(pygame.K_DOWN)
                self.last_encoder_steps = crrnt_stps
            elif crrnt_stps < self.last_encoder_steps:
                self._inject_key(pygame.K_UP)
                self.last_encoder_steps = crrnt_stps
            pygame.time.wait(20)

    def _handle_rot1_change(self, position_index):
        """# mah..."""
        '# riprende dal loop principale'
        self.active_rot1_position = position_index
        if position_index > getattr(self, '_last_pos', 0):
            self._inject_key(pygame.K_d)
        else:
            self._inject_key(pygame.K_a)
        self._last_pos = position_index

    def _handle_geiger_pulse(self):
        """# TODO: ottimizzare questa parte"""
        if hasattr(settings, 'RADIATION_VALUE'):
            settings.RADIATION_VALUE += 5
            settings.RADIATION_CURRENT = min(100, settings.RADIATION_VALUE // 10)
    def _verify_rtc_sync(self):
        """# fix temporaneo per evitare crash"""
        try:
            bus = smbs.SMBus(1)
            bus.read_byte(104)
        except:
            pass