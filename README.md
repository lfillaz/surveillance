# Ghostbyte Surveillance Matrix

animated GIF generator — 3840×2160 — pure Python

---

## what is this

a script that renders a full 4K animated GIF from scratch, no templates, no after effects, just code.
the vibe is cyber surveillance — glowing threads, moving boxes with random usernames, and a central "Ghostbyte" text that breaks apart into particles and reassembles.

## how it works

everything is drawn frame by frame using **Pillow** (PIL) and **numpy**.

- **40 boxes** spawn randomly on screen, each one holds a username that types in letter by letter then glitches and swaps to a new one
- every box **moves** toward a random target position, then picks a new one — nonstop
- **all boxes are connected** with neon green lines to the center Ghostbyte box
- nearby boxes also connect to each other with cyan threads
- behind everything there's a **spiderweb network** of nodes and edges that pulses
- the center box shows **"Ghostbyte"** with chromatic aberration, and the text explodes into ~2500 particles then reassembles on a loop
- **matrix rain**, **scan lines**, **cryptic hex/binary strings** fade in and out
- a **glitch engine** slices horizontal bands and shifts RGB channels
- **vignette** darkens the edges for that cinematic look

## the animation phases (10 second loop)

1. **0–1.5s** — network fades in, nodes start pulsing
2. **1–3s** — boxes appear, start moving, threads light up
3. **2.5–6s** — Ghostbyte text appears, particles cycle
4. **3–7s** — cryptic symbols pop in/out
5. **7–8.5s** — high activity, everything glows brighter, more glitch
6. **8.5–10s** — fade to black, loop restarts

## run it

```
pip install Pillow numpy
python ghostbyte.py
```

output: `ghostbyte_surveillance.gif`

set `PREVIEW_MODE = True` on line 15 for a fast 960×540 test render (~10s).
full 4K takes a few minutes depending on your CPU.

you can also do `python ghostbyte.py frames` to export individual PNGs and stitch them with ffmpeg.

## tech stuff

- 150 frames, 15 fps, 10s loop
- all colors are pre-multiplied alpha on black — no actual transparency needed
- boxes avoid the center zone so they don't overlap the main text
- particle positions are sampled from the rendered text mask using numpy
- glitch effect uses numpy array rolling for speed
- GIF is quantized to 256 colors per frame

---

made by **@lfillaz**
