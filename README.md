# tonemapper

A python script to debug tonemapping operators.
It compares the following tonemappers:

1. [Timothy Lottes Generic](http://32ipi028l5q82yhj72224m8j.wpengine.netdna-cdn.com/wp-content/uploads/2016/03/GdcVdrLottes.pdf)
2. [John Hable "Uncharted" Filmic](http://filmicgames.com/archives/75Jo)
3. [Krzysztof Narkowicz ACES approximation](https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/)

![Tonemapper comparison](https://github.com/Opioid/tonemapper/blob/master/tonemapper.png "Tonemapper comparison")

The settings for the Generic Tonemapper are:

- Contrast = 1
- Shoulder = 1
- Mid in   = 0.18
- Mit out  = 0.18
- HDR max  = 1

Clearly, there is something wrong here...