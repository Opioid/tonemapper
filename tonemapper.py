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

    denom = pow(hdr_max, ad) * mid_out - pow(mid_in, ad) * mid_out
    
    b = -((-pow(mid_in, a) + (mid_out * (pow(hdr_max, ad) * pow(mid_in, a) - pow(hdr_max, a) * pow(mid_in, ad) * mid_out)) / denom) / (pow(mid_in, ad) * mid_out))

    c = (pow(hdr_max, ad) * pow(mid_in, a) - pow(hdr_max, a) * pow(mid_in, ad) * mid_out) / denom

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

for x in numpy.logspace(-3, 5, num=256, base=2):
    color = x - math.pow(2, -3)
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

plt.axis([0, 31, 0, 1.05])
plt.legend(loc=2)
plt.xlabel('Input [0, 32]')
plt.ylabel('Tonemapped')

ax = plt.axes()

ax.xaxis.grid()
ax.tick_params(which='both', # Options for both major and minor ticks
               top='off', # turn off top ticks
               left='off', # turn off left ticks
               right='off',  # turn off right ticks
               bottom='off') # turn off bottom ticks
# plt.show()                      

plt.savefig('tonemapper.png', bbox_inches='tight')
