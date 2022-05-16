import os
import time
import subprocess
from PIL import Image
# import RPi.GPIO as GPIO # на Raspberry

pc_test_mode = 1 # 0 - на Raspberry

class Log():
    def __init__(self, path):
        self.path = path

    def log(self, data):
        with open(self.path, 'a') as f:
            f.write(time.strftime('%Y.%m.%d %H:%M', time.localtime()) + ' - ' + data + '\n')

    def get(self):
        with open(self.path, 'r') as f:
            return f.read()

    def clear(self):
        open(self.path, 'w')


class EasyPrint():
    def __init__(self, main_dir, pin, to_size=696):
        self.pin      = pin
        self.main_dir = main_dir
        self.img_path = self.main_dir + '/image.jpg'        
        self.to_size  = to_size
        self.access_log = Log(self.main_dir + '/access.log')
        self.error_log  = Log(self.main_dir + '/error.log')
        if not pc_test_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)

    def __del__(self):
        if not pc_test_mode:
            GPIO.cleanup()

    def save(self, file):
        with open(self.img_path, 'wb') as f:
            f.write(file)
        return 0

    def load(self):
        with open(self.img_path, 'rb') as f:
            return f.read()

    def resize(self):
        if not os.path.exists(self.img_path):
            return -1

        img = Image.open(self.img_path)
        w, h = img.size
        size = (self.to_size, int(h / w * self.to_size))
        res = img.resize(size)
        res.save(self.img_path)
        return 0

    def remove(self):
        if os.path.exists(self.img_path):
            os.remove(self.img_path)
        return 0

    def print(self):
        if not pc_test_mode:
            if os.system('brother_ql -b linux_kernel -p file:///dev/usb/lp0 -m QL-700 print -l 62 %s' % (self.img_path)):
                return -1
        return 0

    def status(self):
        if not pc_test_mode:
            res = subprocess.run('lsusb | grep Brother', shell=True, stdout=subprocess.DEVNULL)
            return not bool(res.returncode)
        return 2

    def switch(self):
        if not pc_test_mode:
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(self.pin, GPIO.LOW)