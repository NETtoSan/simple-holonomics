# simple-holonomics
Easily control your holonomic robot, or DC motors!


## Hardwares used
For testing both DC motors and holonomic capabilties, we use.

* mBot | mCore board with its bluetooth gamepad
* ESP-WROOM32
* Smile PRIK KEE NU, DC motor controller with PWM capabilities
* 4 generic DC motors
* Step down | Buck controller. from nV -> 5V
* 30V LiFePO4 battery

**You can use your own hardware for your own conveniences**
* mBot | mCore & bluetooth gamepad -> **UART compatible hardware with it's required packet**
* Smile PRIK KEE NU -> **Any DC motor controller**
* 30V LifePO4 battery -> **Whatever power source you have**
## Setup
This is the diagram

```
[Bluetooth gamepad] -> [mBot | mCore] <- uart -> [ESP-WROOM32]
-> [4x DC motor controller]
```

**Where**
* The mBot | mCore talks to ESP-WROOM32 through UART, with 15200 bits per second.
* The Bluetooth gamepad is connected to mBot | mCore through Bluetooth.
* Connect the battery to each of DC motor controllers and a step down converter.
* Connect the output of step down coonverter to ESP-WROOM32 voltage and ground pin respectively.
* The DC motor controller & ESP-WROOM32 have a common ground cable. (Otherwise the motors wont spin!)

## UART serial communication
With our lack of bluetooth controllers. We have set up the perimeter of UART serial data by
* The UART are **simplex method**, where the transmitting side is shouting the data, without data correction.
* The baud rate is 15200 bits per second.
* The UART data consists of
    * **[ int int int int int int ]**
    * These UART data are hooked with mBot | mCore
    * Where all ints are within their 32 bit limits.
    * **[ - - x x x -]**
        * Where 1st X is for X axis.
        * Where 2nd X is for Y axis.
        * Where 3rd X is for rotation axis.
    * **[ x x - - - - ]**
        * These 2 X's are parity datas. You can customize both transmitting and recipient's end.
    * **[ - - - - - x ]**
        * This X has no use (for now...)
* The second UART data packet consists of
    * **[ int int int ]**
    * These UART data are hooked with the raspberry pi System, for computer vision systems
    * Where it can be transmitted via USB-TTL adapter or directly from GPIO pins
    * **[ x x - ]**
        * Where 1st X is the object's X coordinate.
        * Where 2nd X is the object's Y coordinate.
        * The motors will move through provided X and Y without rotating.
    * **[ - - x ]**
        * This X is for rotation, or object's velocity i cant remember.
        * This X ain't implemented yet.