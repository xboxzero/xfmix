# xfmix – Computer Music History Synthesizer + Drum Machine

A software synthesizer for Raspberry Pi 5 grounded in computer music history, from IRCAM physical modeling to Xenakis stochastic composition.

![xfmix](https://img.shields.io/badge/computer_music-history-brightgreen)

## What Is xfmix?

**Two instruments on one page:**

1. **Water Drop Drum Machine** – Physical modeling percussion inspired by Karplus-Strong algorithms and granular synthesis (Ge Wang, Perry Cook). Each drum voice simulates water drops hitting surfaces with natural decay and resonance.

2. **Internal Combustion Engine Synthesizer** – Modal synthesis of mechanical systems (IRCAM tradition, Yamaha VL series). Models piston-driven impulse trains with resonant chamber filtering, RPM control, and load/throttle parameters.

3. **Quantum Stochasticity (Qubit)** – Xenakis-inspired probability fields for injecting controlled randomness into synthesis parameters. Visualized as a Bloch sphere for intuitive manipulation.

4. **Lissajous ⊗ Camera Display** – Oscilloscope-style Lissajous figure (Mary Ellen Bute / Ben Laposky tradition) overlaid on the Pi camera feed via `rpicam-vid` MJPEG. The figure tracks the engine note frequency, reacts to drum hits, and can be made audible through Web Audio.

**Browser-based controller** runs in Safari on any device on your network. **Pure Data synthesis engine** runs on the Pi itself using libpd and FUDI protocol.

## Quick Start

### 1. Install

```bash
cd ~/xfmix
bash install.sh
```

This will prompt for your password and install:
- Pure Data (`puredata puredata-extra`)
- Configure systemd user service
- Create the `xfmix` terminal command

### 2. Run

```bash
xfmix
```

Open http://<your-pi-ip>:8866 in Safari (or any browser on your network).

### 3. Play!

- **Drum pads:** Click to trigger water drop percussion
- **Keyboard:** Play notes (C-B) to drive the engine synth
- **Sliders:** Adjust pitch, decay, RPM, load, resonance
- **Qubit sphere:** Click or drag to inject stochasticity

## Terminal Commands

```bash
xfmix              # Start (or show status)
xfmix status       # Check if running
xfmix log          # View live logs (Ctrl+C to exit)
xfmix stop         # Stop the service
xfmix restart      # Restart the service
```

## Architecture

```
Browser (Safari on network)
    ↓ WebSocket
Python Server (localhost:8866)
    ↓ FUDI protocol (localhost:9001)
Pure Data (pd -nogui)
    ↓ Audio synthesis
Pi 5 Audio Output (ALSA/JACK)
```

**Ports:**
- **8866** – HTTP/WebSocket (browser UI)
- **9001** – FUDI (Pure Data inter-process communication)

## File Structure

```
~/xfmix/
├── patches/              # Pure Data synthesis engine
│   ├── main.pd          # Top-level patch (loads all)
│   ├── water_drum.pd    # Percussion synthesizer
│   └── engine_synth.pd  # Engine model synthesizer
├── static/              # Web UI
│   └── index.html       # Browser controller (self-contained)
├── server.py            # Python WebSocket bridge
├── install.sh           # Setup script
├── setup-xfmix.sh       # Full installation with sudo
├── xfmix.service        # systemd unit file
└── README.md
```

## Design Philosophy

**Computer music history as a design language:**

- **Pure Data** (Miller Puckette, 1996) – Core synthesis engine, direct descendant of Max at IRCAM
- **Physical modeling** (IRCAM, 1980s; Yamaha VL, 1989) – Simulating physical systems to generate sound
- **Granular synthesis** (Ge Wang, Perry Cook, 2000s) – Karplus-Strong tradition of feedback-based synthesis
- **Stochastic composition** (Iannis Xenakis, 1954+) – Probability and chance as compositional tools
- **Modal synthesis** – Resonance modeling of vibrating systems

The result is a system that *is* computer music history, not just inspired by it.

## Troubleshooting

### Pure Data not found
```bash
sudo apt install puredata puredata-extra
```

### Port 8866 already in use
Change the port in `server.py` (search for `HTTP_PORT`).

### WebSocket connection fails
Check that `pd` is running:
```bash
systemctl --user status xfmix
```

View logs for errors:
```bash
xfmix log
```

### No audio output
- Check audio device: `aplay -l`
- Verify ALSA is working: `speaker-test -t sine -f 1000 -l 1`
- Check Pure Data is receiving messages: `xfmix log`

### Camera shows "NO CAM"
The display section uses `rpicam-vid` to stream MJPEG at `/camera.mjpg`. If you don't have a Pi camera attached (or `rpicam-vid` isn't installed), the badge flips to "NO CAM" and only the Lissajous half of the display renders. Install with `sudo apt install rpicam-apps` or use the in-page **Camera** toggle to hide it.

## References

The instruments and control scheme are grounded in:

- **Puckette, M.** (1991). "Combining event and signal processing in the MAX graphical programming environment". ICMC.
- **Schaeffer, P.** (1966). *Traité des objets musicaux*. Éditions du Seuil.
- **Xenakis, I.** (1971). *Formalized Music*. Indiana University Press.
- **Smith, J. O.** (2010). *Physical Audio Signal Processing*. W3K Publishing.
- **Karplus, K. & Strong, A.** (1983). "Digital synthesis of plucked-string and drum timbres". JAES.

## Project Links

- **GitHub:** https://github.com/xboxzero/xfmix
- **Pure Data:** http://puredata.info
- **Raspberry Pi:** https://www.raspberrypi.com

## License

MIT – Open source, open synthesis.

## Author

xboxzero (2026)

---

Built on the Pi 5 Solarpunk computing platform. Grounded in the history of IRCAM, Bell Labs, and algorithmic composition.
