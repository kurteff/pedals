import math
import numpy as np

# Brightness scaling constants: green is perceptually brightest
k_r = 1.0
k_g = 0.6
k_b = 0.8
gamma = 2.2


def rgb_to_resistors(r, g, b, brightness=1.0,
                     norm=255,
                     voltage=9.0,
                     vf_r=2.1,
                     vf_g=3.1,
                     vf_b=3.1,
                     max_current=0.018,
                     min_current=0.0005,
                     swatch=True):
    '''
    Returns resistor values for an input RGB value

    Arguments
    ----------
    r, g, b : int
        red/green/blue values for desired LED color
    brightness : float 0-1
        Desired brightness of LED, where 1 is max brightness and
        0 is max dim.
    norm : int, default 255
        Max value for r/g/b. Set to 1 if you are passing
        RGB values 0-1 for example.
    voltage : float, default 9.0
        DC voltage of power supply
    vf_r, vf_g, vf_b : float, defaults 2.1, 3.1, 3.1
        Forward voltages of R/G/B anodes on LED. Check your datasheet.
        Defaults are approximations for shitty Amazon RGB LEDs.
    max_current : float, default 0.018 (18mA)
        Max amperage of LED. Check your datasheet. It is recommended
        that you underestimate this value for safety.
    min_current : float, default of 0.0005 (0.5 mA)
        Min amperage of LED. This is a soft limit based on the plausible
        range of visible brightness. If your LEDs are too dim at their
        dimmest then increase this value.
    swatch : bool, default True
        Prints input color swatch in Terminal.
    '''
    if swatch:
        print_swatch(r,g,b,label=True)

    # Normalize passed rgb
    r_n = r/norm
    g_n = g/norm
    b_n = b/norm

    # If black
    if r_n == g_n == b_n == 0:
        print("For black, don't use any resistors LOL? Might burn out your LED though...")
        return None, None, None

    # Gamma correction
    r_l = r_n ** gamma
    g_l = g_n ** gamma
    b_l = b_n ** gamma
    brightness = brightness ** gamma

    # Convert to current
    i_r = r_l / k_r
    i_g = g_l / k_g
    i_b = b_l / k_b

    # Scale to max current
    i_max = max(i_r, i_g, i_b)
    i_r = (i_r / i_max) * max_current if i_r > 0 else 0
    i_g = (i_g / i_max) * max_current if i_g > 0 else 0
    i_b = (i_b / i_max) * max_current if i_b > 0 else 0

    # Apply brightness scaling
    i = min_current + brightness * (max_current - min_current)
    i_r *= i
    i_g *= i
    i_b *= i

    # Convert current to resistor values
    r_r = (voltage - vf_r) / i_r if i_r > 0 else None
    g_r = (voltage - vf_g) / i_g if i_g > 0 else None
    b_r = (voltage - vf_b) / i_b if i_b > 0 else None

    return r_r, g_r, b_r

def resistors_to_rgb(r_r, g_r, b_r, brightness=1.0,
                     norm=255,
                     voltage=9.0,
                     vf_r=2.1,
                     vf_g=3.1,
                     vf_b=3.1,
                     swatch=False):


    # Resistor values to current
    i_r = (voltage - vf_r) / r_r if r_r else 0
    i_g = (voltage - vf_g) / g_r if g_r else 0
    i_b = (voltage - vf_b) / b_r if b_r else 0

    # Compensate for brightness constants
    r_l = k_r * i_r
    g_l = k_g * i_g
    b_l = k_b * i_b

    # Normalize
    max_l = max(r_l, g_l, b_l)
    if max_l == 0:
        return(0, 0, 0)
    r_l = r_l / max_l
    g_l = g_l / max_l
    b_l = b_l / max_l

    # Brightness scaling
    brightness = brightness ** gamma
    r_l *= brightness
    g_l *= brightness
    b_l *= brightness

    # Encode gamma
    r = int((r_l ** (1/gamma)) * norm)
    g = int((g_l ** (1/gamma)) * norm)
    b = int((b_l ** (1/gamma)) * norm)

    if swatch:
        print_swatch(r,g,b,label=True)

    return(r,g,b)

def print_swatch(r, g, b, label=True):
    '''
    Displays RGB color swatch in terminal using 24-bit ANSI.
    '''
    block = "      "
    print(f"\033[48;2;{r};{g};{b}m{block}\033[0m")
    if label:
        print(f"  RGB({r}, {g}, {b})")
    else:
        print()

if __name__ == '__main__':
    r = float(input("Input R value (0-255):\n> "))
    g = float(input("Input G value (0-255):\n> "))
    b = float(input("Input B value (0-255):\n> "))
    rr, gr, br = rgb_to_resistors(r,g,b, swatch=True)
    print("Use these resistor values:")
    print("\t Red anode:", rr)
    print("\t Blue anode:", br)
    print("\t Green anode:", gr)

