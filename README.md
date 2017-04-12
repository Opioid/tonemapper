# tonemapper

A python script to debug tonemapping operators.
It compares the following tonemappers:

1. [Timothy Lottes Generic](http://32ipi028l5q82yhj72224m8j.wpengine.netdna-cdn.com/wp-content/uploads/2016/03/GdcVdrLottes.pdf) with [Fixes from Bart Wronski](https://bartwronski.com/2016/09/01/dynamic-range-and-evs/comment-page-1/)
2. [John Hable "Uncharted" Filmic](http://filmicgames.com/archives/75)
3. [Krzysztof Narkowicz ACES approximation](https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/)

![Tonemapper comparison](https://github.com/Opioid/tonemapper/blob/master/tonemapper.svg "Tonemapper comparison")

The settings for the Generic Tonemapper are:

- Contrast = 1.15
- Shoulder = 0.995
- Mid in   = 0.33
- Mid out  = 0.18
- HDR max  = 16.0

Both the Uncharted and ACES curve have been normalized to 16, 
which is the same value as HDR max for the Generic tonemapper.

Linear curves are included for reference. Clamped to 1 and normalized to [0, 16], respectively.
