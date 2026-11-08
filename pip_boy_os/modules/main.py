# INFO: this code comments are in english for maximum understanding from other people
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import subprocess
import pygame
import settings
import boot
import threading
from pipboy import PipBoy
from input_manager import InputManager
from hardware_input import HardwareInputManager
def run_app():
    #Raspberry e.p. for future port
    if settings.RASPI:
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['DISPLAY'] = ':0'
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=5)
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.FULLSCREEN if settings.RASPI else 0)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('Pip-Boy')
    clck = pygame.time.Clock()
    bt_sqnc = boot.Boot(screen)
    bt_sqnc.run()
    input_manager = InputManager()
    hw_npts = HardwareInputManager()
    pipboy = PipBoy(screen, clck, input_manager)
    ppb_thrd = threading.Thread(target=pipboy.run)
    ppb_thrd.daemon = True
    ppb_thrd.start()
    ppb_thrd_lck = threading.Lock()
    rnnng = True
    shld_rstrt = False
    while rnnng:
        input_manager.run()
        with ppb_thrd_lck:
            pipboy.render()
        if getattr(pipboy, 'should_restart', False):
            shld_rstrt = True
            rnnng = False
            break
        clck.tick(settings.FPS)
    pipboy.done = True
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.display.quit()
        pygame.quit()
    except:
        pass
    return shld_rstrt

def main():
    while True:
        import importlib
        importlib.reload(settings)
        rstrt_rqstd = run_app()
        if not rstrt_rqstd:
            break
if __name__ == '__main__':
    main()