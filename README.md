# midi2ay
Adapts MIDI files for playing in the ZX Spectrum AY sound chip.
## Introduction
This is a PY version with the aim of exiting cleanly back to basic.

## The algorithm
The program tries to play a MIDI (which can have up to 2048 simultaneous notes playing) in an AY chip with only three channels. In order to achieve this, every 1/50th of a second it checks the notes playing at that moment, assigns to each one a weight and selects the three notes with higher weight, discarding the others. If there's a rythm track, it's ignored.

The weight is calculated by multiplying the MIDI note and velocity values. Thus louder notes will get higher weight and higher-pitched notes will too (favouring melody lines over bass lines, hopefully).
## Possible improvements
Just in case anyone wants to use this program as a starting point for something more sophisticated:
- Use arpeggio to multiply the number of channels available.
- A way of manually selecting the priority of tracks, overriding the weight calculation. Maybe a GUI with a list of the tracks where you can order them by priority and mute unwanted ones.
- Play the rythm track. A table of rythm instruments adapted for the AY chip would be necessary.
- Make the program less "Spectrum-centric" and output formats for other computers that used AY-compatible chips.
## License
You can use this software and its source code in any way you want.
