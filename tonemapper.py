import matplotlib.pyplot as plt
import math
import numpy

# Lottes Generic like in http://32ipi028l5q82yhj72224m8j.wpengine.netdna-cdn.com/wp-content/uploads/2016/03/GdcVdrLottes.pdf
# but with corrections like in https://bartwronski.com/2016/09/01/dynamic-range-and-evs/comment-page-1/#comment-2360

# Setting similar to Uncharted:
# contrast = 1.15
# shoulder = 0.995
# mid_in = 0.33
# mid_out = 0.18

def lottes(x, hdr_max):
    a = 1.15 # contrast
    d = 0.995 # shoulder

    mid_in = 0.33
    mid_out = 0.18

    ad = a * d

    midi_pow_a  = pow(mid_in, a)
    midi_pow_ad = pow(mid_in, ad)
    hdrm_pow_a  = pow(hdr_max, a)
    hdrm_pow_ad = pow(hdr_max, ad)
    u = hdrm_pow_ad * mid_out - midi_pow_ad * mid_out
    v = midi_pow_ad * mid_out
    
    b = -((-midi_pow_a + (mid_out * (hdrm_pow_ad * midi_pow_a - hdrm_pow_a * v)) / u) / v)

    c = (hdrm_pow_ad * midi_pow_a - hdrm_pow_a * v) / u

    x = min(x, hdr_max)
    z = pow(x, a)
    y = z / (pow(z, d) * b + c)

    return y

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

# Plot the tonemapping curves
plt.figure(figsize=(12, 6))

color_in = []
color_lottes = []
color_uncharted = []
color_aces = []
color_linear = []

hdr_max = 16.0

for x in numpy.logspace(-1, 5, num=256, base=2):
    color = x - math.pow(2, -1)
    color_in.append(color)
    color_lottes.append(lottes(color, hdr_max))
    #color_uncharted.append(uncharted(color))
    color_uncharted.append(normalized_uncharted(color, hdr_max))
    #color_aces.append(aces(color))
    color_aces.append(normalized_aces(color, hdr_max))
    color_linear.append(normalized_linear(color, hdr_max))

plt.semilogx(color_in, color_lottes, basex=2, label='Lottes')
plt.plot(color_in, color_uncharted, label='Uncharted (normalized)')
plt.plot(color_in, color_aces, label='ACES (normalized)')
plt.plot(color_in, color_in, label='Linear (clamped)')
plt.plot(color_in, color_linear, label='Linear (normalized)')

plt.axis([0, 19, 0, 1.04])
plt.legend(loc=2)
plt.xlabel('Input')
plt.ylabel('Tonemapped')

ax = plt.axes()

xlabels = ['', '', '0.015625', '0.03125', '0.0625', '0.125',
           '0.25', '0.5', '1.0', '2.0', '4.0', '8.0', '16.0']

ax.set_xticklabels(xlabels)

#ax.xaxis.grid()
ax.tick_params(which='both', # Options for both major and minor ticks
               direction='out',
               top='off', # turn off top ticks
               left='on', # turn off left ticks
               right='off',  # turn off right ticks
               bottom='on') # turn off bottom ticks

ax.axhline(1.0,  linestyle='--', color='k')
ax.axvline(1.0, linestyle=':', color='k')
ax.axvline(16.0, linestyle='--', color='k')

# plt.show()                      

plt.savefig('tonemapper.png', bbox_inches='tight')
