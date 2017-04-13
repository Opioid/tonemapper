import matplotlib.pyplot as plt
import math
import numpy

# Lottes Generic like in http://32ipi028l5q82yhj72224m8j.wpengine.netdna-cdn.com/wp-content/uploads/2016/03/GdcVdrLottes.pdf
# but with corrections like in https://bartwronski.com/2016/09/01/dynamic-range-and-evs/comment-page-1/#comment-2360

# Setting similar to Uncharted:
# contrast = 1.25
# shoulder = 0.975
# mid_in = 0.25
# mid_out = 0.18

class Generic():
    def __init__(self, hdr_max):
        a = 1.2 # contrast
        d = 0.97 # shoulder

        mid_in = 0.3
        mid_out = 0.18

        ad = a * d

        midi_pow_a  = pow(mid_in, a)
        midi_pow_ad = pow(mid_in, ad)
        hdrm_pow_a  = pow(hdr_max, a)
        hdrm_pow_ad = pow(hdr_max, ad)
        u = hdrm_pow_ad * mid_out - midi_pow_ad * mid_out
        v = midi_pow_ad * mid_out

        self.a = a
        self.d = d
        self.b = -((-midi_pow_a + (mid_out * (hdrm_pow_ad * midi_pow_a - hdrm_pow_a * v)) / u) / v)
        self.c = (hdrm_pow_ad * midi_pow_a - hdrm_pow_a * v) / u
        self.hdr_max = hdr_max

    def evaluate(self, x):
        x = min(x, self.hdr_max)
        z = pow(x, self.a)
        y = z / (pow(z, self.d) * self.b + self.c)

        return y

class Piecewise():
    
    class Segment():
        offset_x = 0.0
        scale_x = 1.0
        offset_y = 0.0
        scale_y = 1.0
        ln_a = 0.0
        b = 1.0
        
        # def __init__(self):

        def evaluate(self, x):
            x0 = (x - self.offset_x) * self.scale_x
            y0 = 0.0

            if x0 > 0.0:
                y0 = math.exp(self.ln_a + self.b * math.log(x0))
            
            return y0 * self.scale_y + self.offset_y
        
    def __init__(self, hdr_max):
        self.segments = [self.Segment(), self.Segment(), self.Segment()]

        x0 = 0.25
        y0 = 0.25
        x1 = 0.6
        y1 = 0.6

        overshoot_x = hdr_max * 4.0
        overshoot_y = 1.5
        

        norm_x0 = x0 / hdr_max
        norm_x1 = x1 / hdr_max
        norm_overshoot_x = overshoot_x / hdr_max

        self.x0 = norm_x0
        self.x1 = norm_x1
        
        # mid segment
        m, b = Piecewise.as_slope_intercept(norm_x0, norm_x1, y0, y1)

        self.segments[1].offset_x = -(b / m)
        self.segments[1].offset_y = 0.0
        self.segments[1].scale_x = 1.0
        self.segments[1].scale_y = 1.0
        self.segments[1].ln_a = math.log(m)
        self.segments[1].b = 1.0

        # toe segment
        toe_m = m
        ln_a, b = Piecewise.solve_a_b(norm_x0, y0, toe_m)
        self.segments[0].offset_x = 0.0
        self.segments[0].offset_y = 0.0
        self.segments[0].scale_x = 1.0
        self.segments[0].scale_y = 1.0
        self.segments[0].ln_a = ln_a
        self.segments[0].b = b

        # shoulder segment
        shoulder_x0 = (1.0 + norm_overshoot_x) - norm_x1
        shoulder_y0 = (1.0 + overshoot_y) - y1
        
        shoulder_m = m
        ln_a, b = Piecewise.solve_a_b(shoulder_x0, shoulder_y0, shoulder_m)

        self.segments[2].offset_x = 1.0 + norm_overshoot_x
        self.segments[2].offset_y = 1.0 + overshoot_y
        self.segments[2].scale_x = -1.0
        self.segments[2].scale_y = -1.0        
        self.segments[2].ln_a = ln_a
        self.segments[2].b = b

        # Normalize so that we hit 1.0 at white point
        scale = self.segments[2].evaluate(1.0)
        inv_scale = 1.0 / scale

        self.segments[0].offset_y *= inv_scale
        self.segments[0].scale_y *= inv_scale

        self.segments[1].offset_y *= inv_scale
        self.segments[1].scale_y *= inv_scale

        self.segments[2].offset_y *= inv_scale
        self.segments[2].scale_y *= inv_scale
        
        self.hdr_max = hdr_max
        
    def evaluate(self, x):
        norm_x = x / self.hdr_max
        
        index = 0 if norm_x < self.x0 else (1 if norm_x < self.x1 else 2)
        
        return self.segments[index].evaluate(norm_x)

    @staticmethod
    def as_slope_intercept(x0, x1, y0, y1):
        dy = y1 - y0
        dx = x1 - x0

        m = 1.0
        if 0.0 != dx:
            m = dy / dx

        b = y0 - x0 * m

        return m, b
        
    
    @staticmethod
    def solve_a_b(x0, y0, m):
        b = (m * x0) / y0
        ln_a = math.log(y0) - b * math.log(x0)
        return ln_a, b
    
# Uncharted like in http://filmicgames.com/archives/75Jo
def uncharted(x):
    a = 0.22
    b = 0.30
    c = 0.10
    d = 0.20
    e = 0.01
    f = 0.30

    return ((x * (a * x + c * b) + d * e) / (x * (a * x + b) + d * f)) - e / f

def normalized_uncharted(x, hdr_max):
    return uncharted(x) / uncharted(hdr_max)

# ACES like in https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
def aces(x):
    a = 2.51
    b = 0.03
    c = 2.43
    d = 0.59
    e = 0.14

    return (x * (a * x + b)) / (x * (c * x + d) + e)

def normalized_aces(x, hdr_max):
    return aces(x) / aces(hdr_max)

def normalized_linear(x, hdr_max):
    return x / hdr_max

def plot_linear():
    color_in = []
    # Plot the tonemapping curves
    plt.figure(figsize=(12, 6))

    color_in = []
    color_generic = []
    color_piecewise = []
    color_uncharted = []
    color_aces = []
    color_linear = []

    hdr_max = 2.0

    generic = Generic(hdr_max)
    piecewise = Piecewise(hdr_max)
    
    for x in numpy.linspace(0, 2.1, num=256):
        color = x
        color_in.append(color)
        color_generic.append(generic.evaluate(color))
        color_piecewise.append(piecewise.evaluate(color))
        #color_uncharted.append(uncharted(color))
        color_uncharted.append(normalized_uncharted(color, hdr_max))
        #color_aces.append(aces(color))
        color_aces.append(normalized_aces(color, hdr_max))
        color_linear.append(normalized_linear(color, hdr_max))

    plt.plot(color_in, color_generic, label='Generic')
    plt.plot(color_in, color_piecewise, label='Piecewise')
    plt.plot(color_in, color_uncharted, label='Uncharted (normalized)')
    plt.plot(color_in, color_aces, label='ACES (normalized)')
    plt.plot(color_in, color_in, label='Linear (clamped)')
    plt.plot(color_in, color_linear, label='Linear (normalized)')

    plt.axis([0, 2.04, 0, 1.04])
    plt.legend(loc=4, bbox_to_anchor=[0.975, 0.0])
    plt.xlabel('Input')
    plt.ylabel('Tonemapped')

    ax = plt.axes()
    ax.tick_params(which='both', # Options for both major and minor ticks
                   direction='out',
                   top='off', # turn off top ticks
                   left='on', # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='on') # turn off bottom ticks

    ax.axhline(1.0,  linestyle='--', color='k')
    ax.axvline(1.0, linestyle=':', color='k')
    ax.axvline(2.0, linestyle='--', color='k')

    plt.savefig('tonemapper_linear.png', bbox_inches='tight')

def plot_log():
    # Plot the tonemapping curves
    plt.figure(figsize=(12, 6))

    color_in = []
    color_generic = []
    color_piecewise = []
    color_uncharted = []
    color_aces = []
    color_linear = []

    hdr_max = 16.0

    generic = Generic(hdr_max)
    piecewise = Piecewise(hdr_max)
    
    for x in numpy.logspace(-1, 5, num=256, base=2):
        color = x - math.pow(2, -1)
        color_in.append(color)
        color_generic.append(generic.evaluate(color))
        color_piecewise.append(piecewise.evaluate(color))
        #color_uncharted.append(uncharted(color))
        color_uncharted.append(normalized_uncharted(color, hdr_max))
        #color_aces.append(aces(color))
        color_aces.append(normalized_aces(color, hdr_max))
        color_linear.append(normalized_linear(color, hdr_max))

    plt.semilogx(color_in, color_generic, basex=2, label='Generic')
    plt.plot(color_in, color_piecewise, label='Piecewise')
    plt.plot(color_in, color_uncharted, label='Uncharted (normalized)')
    plt.plot(color_in, color_aces, label='ACES (normalized)')
    plt.plot(color_in, color_in, label='Linear (clamped)')
    plt.plot(color_in, color_linear, label='Linear (normalized)')

    plt.axis([0, 18.66, 0, 1.04])
    plt.legend(loc=2, bbox_to_anchor=[0.0, 0.95])
    plt.xlabel('Input')
    plt.ylabel('Tonemapped')

    ax = plt.axes()

    xlabels = ['', '', '0.015625', '0.03125', '0.0625', '0.125',
               '0.25', '0.5', '1.0', '2.0', '4.0', '8.0', '16.0']

    ax.set_xticklabels(xlabels)

    ax.tick_params(which='both', # Options for both major and minor ticks
                   direction='out',
                   top='off', # turn off top ticks
                   left='on', # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='on') # turn off bottom ticks

    ax.axhline(1.0,  linestyle='--', color='k')
    ax.axvline(1.0, linestyle=':', color='k')
    ax.axvline(16.0, linestyle='--', color='k')

    plt.savefig('tonemapper_log.png', bbox_inches='tight')

plot_linear()
plot_log()
