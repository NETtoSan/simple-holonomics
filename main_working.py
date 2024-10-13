import time
import machine
import math
import _thread

from machine import Pin

uart = machine.UART(2, 15200, bits=8, stop=2, parity=None)
mode = "MBOT"

m11 = machine.Pin(15, Pin.OUT)
m12 = machine.Pin(2, Pin.OUT)
pwm1 = machine.PWM(machine.Pin(4), 30000)
m21 = machine.Pin(12, Pin.OUT)
m22 = machine.Pin(14, Pin.OUT)
pwm2 = machine.PWM(machine.Pin(27), 30000)
m31 = machine.Pin(26, Pin.OUT)
m32 = machine.Pin(25, Pin.OUT)
pwm3 = machine.PWM(machine.Pin(33), 30000)
m41 = machine.Pin(5, Pin.OUT)
m42 = machine.Pin(18, Pin.OUT)
pwm4 = machine.PWM(machine.Pin(19), 30000)

def run(fl:int, fr:int, rl:int, rr:int):
    fl = map_range(fl, -100, 100, -255, 255)
    fr = map_range(fr, -100, 100, -255, 255)
    rl = map_range(rl, -100, 100, -255, 255)
    rr = map_range(rr, -100, 100, -255, 255)
    if fl == 0:
        m11.value(1)
        m12.value(1)
        pwm1.duty(0)
    elif fl < 0:
        m11.value(1)
        m12.value(0)
        pwm1.duty(-1 * fl)
    elif fl > 0:
        m11.value(0)
        m12.value(1)
        pwm1.duty(fl)
        
    if fr == 0:
        m21.value(1)
        m22.value(1)
        pwm2.duty(0)
    elif fr < 0:
        m21.value(1)
        m22.value(0)
        pwm2.duty(-1 * fr)
    elif fr > 0:
        m21.value(0)
        m22.value(1)
        pwm2.duty(fr)
        
    if rl == 0:
        m31.value(1)
        m32.value(1)
        pwm3.duty(0)
    elif rl < 0:
        m31.value(1)
        m32.value(0)
        pwm3.duty(-1 * rl)
    elif rl > 0:
        m31.value(0)
        m32.value(1)
        pwm3.duty(rl)
    
    if rr == 0:
        m41.value(1)
        m42.value(1)
        pwm4.duty(0)
    elif rr < 0:
        m41.value(1)
        m42.value(0)
        pwm4.duty(-1 * rr)
    elif rr > 0:
        m41.value(0)
        m42.value(1)
        pwm4.duty(rr)
        
def drive(fl: int, fr: int, rl: int, rr: int):
    left = "stop"
    right = "stop"
    if fl > 0 and rl > 0:
        left = "fwd"
    elif fl < 0 and rl < 0:
        left = "bwd"
    elif fl > 0 and rl < 0:
        left = "right"
    elif fl < 0 and rl > 0:
        left = "left"

    if rl > 0 and rr > 0:
        right = "fwd"
    elif rl < 0 and rr < 0:
        right = "bwd"
    elif rl > 0 and rr < 0:
        right = "left"
    elif rl < 0 and rr > 0:
        right = "right"

    if left == right:
        print(f"{left}\n---------------")
    pass

def test_uart():
    global mode
    buffer = ""
    dies = 0
    while True:
        if uart.any():
            try:
                while uart.any(): buffer += uart.read().decode('utf-8')
                    
                lines = buffer.splitlines()
                for line in lines:
                    if line:
                        pkg = line.split()
                        if mode == "PI":
                            if(len(pkg) < 3):
                                pass
                            else:
                                pkg[0] = int(float(pkg[0]))
                                pkg[1] = -1 * int(float(pkg[1]))
                                print(f"uart data: {line}\nx: {pkg[0]} y: {pkg[1]}")
                                #pure_pursuit(pkg[0], pkg[1], 0, "WHAT")

                        elif mode == "MBOT":
                            if(len(pkg) < 6):
                                pass
                            else:
                                x = int(float(pkg[2]))
                                y = int(float(pkg[3]))
                                rot = -1 * int(float(pkg[4]))
                                pure_pursuit(x, y, rot, "FIXED")
                                #print(pkg)
                            

            except Exception as e:
                print(f"!!!! decode error {e}")
        else:
            if dies < 10:
                dies += 1
            else:
                print("UART dead")
                dies = 0
        
        buffer = ""
        time.sleep(0.05)

def seek_uart():
    data_arr = []
    buffer = ""
    dies = 0
    while True:

        if uart.any():
            try:
                while uart.any(): buffer += uart.read().decode('utf-8')
                    
                lines = buffer.splitlines()
                for line in lines:
                    if line:
                        data_arr = line.split()
                        if(len(data_arr) < 6):
                            pass
                        else:
                            print(data_arr)
                            try:
                                x1 = data_arr[0]
                                y1 = data_arr[1]
                                x2 = data_arr[2]
                                y2 = data_arr[3]
                                i = data_arr[4]
                                rgbdata = data_arr[5]
                            except:
                                pass
                            buffer = ""
                            data_arr = []
            except:
                 print("!!!! stream error")
        else:
            if(dies < 10):
                dies += 1
            else:
                print(">>>> UART dead")
                dies = 0
            pass
        time.sleep(0.05)

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
def constrain(v, mn, mx):
    if v < mn: return mn
    if v > mx: return mx
    return v
def thr_curve(v:int, s:float, e:int):
    return s * (v ** e)

def pure_pursuit(x:int, y:int, rot:int, hdg:str):
    SENS = 0.3 # Control sensitivity
    t_hdg = 0
    # < 1.0 FAST ------------------> 0.1 SLOW > #

    if hdg != "FIXED" and hdg != "ADAPT":
        #Default hdg to FIXED if value is not recognized
        #print("Wrong hdg mode! Defaulting to FIXED...\nUse FIXED for normal controls,\nUse ADAPT for headless control\n-----------------")
        hdg = "FIXED"
    if hdg == "FIXED":
        t_hdg = 90
    elif hdg ==  "ADAPT":
        t_hdg = 0

    x = SENS * x
    y = SENS * y

    t_angle = t_hdg - math.degrees(math.atan2(y, x))
    pct = constrain(thr_curve(math.sqrt((x * x) + (y * y)), 0.005, 2) * 10, -100, 100)
    mot_translate(pct, x, y, rot, t_angle)
    pass
def mot_translate(pct, dirX, dirY, rotX, t_angle):
    #print(f"{pct} {dirX} {dirY} {rotX} {t_angle}\n------------------")

    t_angle = (t_angle + 180) % 360 - 180
    angle_rad = math.radians(- t_angle)

    vx = round(pct * math.cos(angle_rad))
    vy = round(pct * math.sin(angle_rad))

    fl = constrain((vx - vy) - rotX, -100, 100)
    fr = constrain((vx + vy) + rotX, -100, 100)
    rl = constrain((vx + vy) - rotX, -100, 100)
    rr = constrain((vx - vy) + rotX, -100, 100)
    drive(fl, fr, rl, rr)
    run(fl, fr, rl, rr)
    print(f"[motor power]\n{fl}     {fr}\n{rl}     {rr}")
    pass

print("Micrpython PWM test")
time.sleep(1)

pwm1.duty(0)
pwm2.duty(0)

thread1 = _thread.start_new_thread(test_uart, ())

while True:
    time.sleep(5)
    print(">>>>>>> Interrupt 0")
