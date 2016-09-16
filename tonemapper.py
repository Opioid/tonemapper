import matplotlib.pyplot as plt
import math
import numpy

# Generic like in http://32ipi028l5q82yhj72224m8j.wpengine.netdna-cdn.com/wp-content/uploads/2016/03/GdcVdrLottes.pdf
def generic(x):
    a = 1 # contrast
    d = 1 # shoulder

    mid_in = 0.18
    mid_out = 0.18

    hdr_max = 1

    denom = math.pow(math.pow(hdr_max, a), d) - math.pow(math.pow(mid_in, a), d) * mid_out
    
    b = (-math.pow(mid_in, a) + math.pow(hdr_max, a) * mid_out) / denom

    c = (math.pow(math.pow(hdr_max, a), d) * math.pow(mid_in, a) - math.pow(hdr_max, a) * math.pow(math.pow(mid_in, a), d) * mid_out) / denom

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

# ACES like in https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
def aces(x):
    a = 2.51
    b = 0.03
    c = 2.43
    d = 0.59
    e = 0.14

    return (x * (a * x + b)) / (x * (c * x + d) + e)

# Plot the tonemapping curves
plt.figure(figsize=(12.8, 7.2), dpi=120)

color_in = []
color_generic = []
color_uncharted = []
color_aces = []

for x in numpy.logspace(-8, 8, num=64, base=2):
    color = x - math.pow(2, -8)
    color_in.append(color)
    color_generic.append(generic(color))
    color_uncharted.append(uncharted(color))
    color_aces.append(aces(color))

plt.semilogx(color_in, color_generic, basex=2, label='Generic')
plt.plot(color_in, color_uncharted, label='Uncharted')
plt.plot(color_in, color_aces, label='ACES')

plt.axis([0, 255, 0, 1.4])
plt.legend()
plt.xlabel('Input')
plt.ylabel('Tonemapped')
plt.grid(True)

plt.show()

