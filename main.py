# Before any of you smartasses say "Use C! It's faster than micropython!"
# : Shut up
# ----------------------------------------
# Dealing with UART string in C is already a pain in the ass
# Using "".split() in python or anything not C is much much more convenient
# Also, this ESP32's job is to control DC motors. and ONLY DC motors.

import time
import machine
import math
import _thread

from dcmotor import DCMotor 
from machine import Pin

uart = machine.UART(2, 15200, bits=8, stop=2, parity=None)
mode = "MBOT" # MBOT = gamepad UART (manual mode), PI = OpenCV
              # We just happen to have many makeblock gamepads
              # [Makeblock gamepad]-> [mbot1] --(UART 12tx 13rx)--> [ESP32]
debug_mode = False

motfl = DCMotor(15, 2, 4)    # FRONT LEFT
motfr = DCMotor(12, 14, 27)  # FRONT RIGHT
motrl = DCMotor(26, 25, 33)  # REAR LEFT
motrr = DCMotor(5, 18, 19)   # REAR RIGHT

def run(fl:int, fr:int, rl:int, rr:int):
    motfl.set_speed(fl)
    motfr.set_speed(fr)
    motfl.set_speed(rl)
    motfl.set_speed(rr)
    print("-------")
    
def dir_debug(fl: int, fr: int, rl: int, rr: int):
    print(f"[motor power]\n{fl}     {fr}\n{rl}     {rr}")
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

def recv_uart():
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
    if debug_mode == True: dir_debug(fl, fr, rl, rr)
    run(fl, fr, rl, rr)
    pass

print("Micrpython PWM test")
time.sleep(1)


thread1 = _thread.start_new_thread(recv_uart, ())

while True:
    time.sleep(5)
    print(">>>>>>> Interrupt 0")