"""
PhotocellWaver
Reads a photocell and turns a servo to keep the lights on.
"""
try:
    from typing import List
except ImportError:
    pass
# noinspection PyPackageRequirements
from machine import ADC, Pin

try:
    from OutsideModules.picozero import Button, Speaker, pico_temp_sensor
    from OutsideModules.servo import Servo
except ImportError:
    from picozero import Button, Speaker
    from servo import Servo
from time import sleep, sleep_ms
from utime import sleep as u_sleep


def Wave(servo_pin: int = 0, led: Pin = Pin(25, Pin.OUT), **kwargs):
    print("this is a wave")
    servo = Servo(pin_id=servo_pin)
    delay_ms = 15  # Amount of milliseconds to wait between servo movements

    if kwargs:
        if 'delay_ms' in kwargs:
            if type(kwargs['delay_ms']) != int:
                raise TypeError('delay_ms must be an integer.')
            else:
                delay_ms = kwargs['delay_ms']

    for position in range(0, 180):
        """ Step the position forward from 0deg to 180deg. """
        # print(position)  # Show the current position in the Shell/Plotter
        servo.write(position)  # Set the Servo to the current position
        sleep_ms(delay_ms)  # wait delay_ms before moving to the next number

    for position in reversed(range(0, 180)):
        """ Step the position in reverse from 180deg to 0deg. """
        # print(position)  # Show the current position in the Shell/Plotter
        servo.write(position)  # Set the Servo to the current position
        sleep_ms(delay_ms)  # wait delay_ms before moving to the next number

    LED_Blink(led)


def LED_Blink(led: Pin = Pin(25, Pin.OUT), sleep_length: float = 0.5):
    led.on()
    # print("LED on")
    sleep(sleep_length)
    led.off()
    # print("LED off")
    sleep(sleep_length)


def TestButton():
    test_b = Button(13)
    while True:
        print(test_b.is_active)


def StartStop(button_pin: int = 13, reverse=False):
    start_stop_button = Button(button_pin)

    if start_stop_button.is_active:
        print("start/stop activated.")
        try:
            if speaker:
                OnUpOffDown(reverse)
        except UnboundLocalError as e:
            print(e)
            pass
        return start_stop_button
    else:
        return False


def ReadPhotoCell(**kwargs):
    onboard_led_pin = Pin(25, Pin.OUT)
    photocell_pin = 27
    dark_threshold = 1000
    manual_button_pin = 18

    if kwargs:
        if 'photocell_pin' in kwargs and type(kwargs['photocell_pin']) == int:
            photocell_pin = kwargs['photocell_pin']
        if 'dark_threshold' in kwargs and type(kwargs['dark_threshold']) == int:
            dark_threshold = kwargs['dark_threshold']
        if 'manual_button_pin' in kwargs and type(kwargs['manual_button_pin']) == int:
            manual_button_pin = kwargs['manual_button_pin']

    ldr = ADC(photocell_pin)
    wave_button = Button(manual_button_pin)

    while True:
        has_waved = False
        if wave_button.is_active:
            InfoBeep()
            Wave(led=onboard_led_pin)
            has_waved = True

        photo_cell_reading = ldr.read_u16()
        print(f"Photocell reading: {photo_cell_reading}")

        if photo_cell_reading >= dark_threshold and not has_waved:
            Wave(led=onboard_led_pin)
            has_waved = True
        if has_waved:
            print("has waved")

        sleep(1)

        stop = StartStop(reverse=True)
        if stop:
            break
    WaitForStart()


def WaitForStart():
    print("Waiting for Start.")
    while True:
        LED_Blink()
        go = StartStop()
        if go:
            break
    ReadPhotoCell()


def OnUpOffDown(reverse=False):
    """ play a note starting at 1000Hz, go to 4000 with steps of 100 or reverse that."""
    if not reverse:
        for i in range(1000, 4000, 100):
            speaker.play(i, 0.05)
    if reverse:
        for i in reversed(range(1000, 4000, 100)):
            speaker.play(i, 0.05)


def InfoBeep():
    speaker.play(880, 0.1)
    sleep(0.05)
    speaker.play(880, 0.05)


def StepperMotor(pin_list: List[Pin] = None):
    def _validate_pins() -> List[Pin]:
        if pin_list:
            if isinstance(pin_list, List):
                pass
            else:
                raise TypeError("pin_list must be a list.")
            if [x for x in pin_list if isinstance(x, Pin)]:
                pins = pin_list
            else:
                raise TypeError("pin_list must be a list CONTAINING Pin's.")
        else:
            pins = [Pin(2, Pin.OUT),
                    Pin(3, Pin.OUT),
                    Pin(4, Pin.OUT),
                    Pin(5, Pin.OUT)]
        return pins

    pins = _validate_pins()

    step_seq: List[List[int]] = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

    while True:
        for step in step_seq:
            for i in range(len(pins)):
                pins[i].value(step[i])
                u_sleep(0.001)


if __name__ == '__main__':
    speaker = Speaker(15)
    WaitForStart()
    # StepperMotor()
