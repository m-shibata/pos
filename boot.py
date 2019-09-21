import lcd
import image
import time
import uos
from Maix import GPIO
from fpioa_manager import *

lcd.init()
lcd.rotation(2) #Rotate the lcd 180deg

try:
    img = image.Image("/sd/startup.jpg")
    lcd.display(img)
except:
    lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Cannot find start.jpg", lcd.WHITE, lcd.RED)

from Maix import I2S, GPIO
import audio

fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

wav_dev = I2S(I2S.DEVICE_0)

def ring_bell(wav_dev = None):
    if wav_dev == None:
        return

    try:
        player = audio.Audio(path = "/sd/ding.wav")
        player.volume(50)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
               break
            elif ret==0:
               break
        player.finish()
    except:
        pass

ring_bell(wav_dev)

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

if but_a.value() == 0: #If dont want to run the demo
    sys.exit()

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.LED_W, fm.fpioa.GPIO3)
led_w = GPIO(GPIO.GPIO3, GPIO.OUT)
led_w.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_R, fm.fpioa.GPIO4)
led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
led_r.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_G, fm.fpioa.GPIO5)
led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
led_g.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1) #RGBW LEDs are Active Low


time.sleep(0.5) # Delay for few seconds to see the start-up screen :p

import sensor

err_counter = 0

while True:
    try:
        sensor.reset() #Reset sensor may failed, let's try sometimes
        break
    except:
        err_counter = err_counter + 1
        if err_counter == 20:
            lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)
        time.sleep(0.1)
        continue

sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA) #QVGA=320x240
sensor.run(1)

lcd.draw_string(0, 2, "POS for LXD BOOK", lcd.WHITE, lcd.BLACK)
print("POS for LXD BOOK")

book1 = image.Image("/sd/lxdbook_print.jpg")
book2 = image.Image("/sd/lxdbook_ebook.jpg")

def buy(item = None):
    with open("/sd/sales.csv", mode="a") as f:
        f.write("{}, {}\n".format(time.time(), item))
    ring_bell(wav_dev)

try:
    while True:
        img = sensor.snapshot() # Take an image from sensor
        res = img.find_qrcodes()
        if len(res) > 0:
            if res[0].payload() == "lxdbook_print":
                lcd.display(book1)
            elif res[0].payload() == "lxdbook_ebook":
                lcd.display(book2)
            else:
                continue

            while True:
                if but_b.value() == 0:
                    lcd.draw_string(2, 110, "CANCEL", lcd.WHITE, lcd.BLACK)
                    break
                if but_a.value() == 0:
                    lcd.draw_string(2, 110, "CONFIRM", lcd.WHITE, lcd.BLACK)
                    buy(res[0].payload())
                    break
                time.sleep(0.3)
        lcd.display(img)

except KeyboardInterrupt:
    sys.exit()
