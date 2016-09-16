import matplotlib.pyplot as plt
import math
import numpy

# Generic like in http://32ipi028l5q82yhj72224m8j.wpengine.netdna-cdn.com/wp-content/uploads/2016/03/GdcVdrLottes.pdf
# but with corrections like in https://bartwronski.com/2016/09/01/dynamic-range-and-evs/comment-page-1/#comment-2360
def generic(x, hdr_max):
    a = 1 # contrast
    d = 1 # shoulder

    mid_in = 0.18
    mid_out = 0.18

    ad = a * d
    
    b = -((-math.pow(mid_in,a) + (mid_out*(math.pow(hdr_max,ad)*math.pow(mid_in,a) - math.pow(hdr_max,a)*pow(mid_in,ad)*mid_out))/ (math.pow(hdr_max,ad)*mid_out - math.pow(mid_in,ad)*mid_out))/ (math.pow(mid_in,ad)*mid_out))

    c = (math.pow(hdr_max, ad) * math.pow(mid_in, a) - math.pow(hdr_max, a) * math.pow(mid_in, ad) * mid_out) / (math.pow(hdr_max,ad) * mid_out - math.pow(mid_in, ad) * mid_out)

    z = math.pow(x, a)
    y = z / (math.pow(z, d) * b + c)

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

# Plot the tonemapping curves
plt.figure(figsize=(12.8, 7.2), dpi=120)

color_in = []
color_generic = []
color_uncharted = []
color_aces = []

hdr_max = 256.0

for x in numpy.logspace(-8, 8, num=64, base=2):
    color = x - math.pow(2, -8)
    color_in.append(color)
    color_generic.append(generic(color, hdr_max))
    #color_uncharted.append(uncharted(color))
    color_uncharted.append(normalized_uncharted(color, hdr_max))
    #color_aces.append(aces(color))
    color_aces.append(normalized_aces(color, hdr_max))

plt.semilogx(color_in, color_generic, basex=2, label='Generic')
plt.plot(color_in, color_uncharted, label='Uncharted (normalized)')
plt.plot(color_in, color_aces, label='ACES (normalized)')

plt.axis([0, 255, 0, 1.4])
plt.legend()
plt.xlabel('Input [0, 256]')
plt.ylabel('Tonemapped')
plt.grid(True)

plt.show()

