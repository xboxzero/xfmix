# xfmix – Computer Music History Synthesizer + Drum Machine

A solarpunk-inspired software synthesizer for Raspberry Pi 5, following the history of computer music from IRCAM and Bell Labs to the present day.

## Instruments

### Water Drop Drum Machine
Physical modeling percussion synthesizer inspired by:
- **Karplus-Strong algorithm** (1983) – plucked string synthesis via feedback delay
- **Granular synthesis** – Ge Wang, Perry Cook (Princeton)
- **Musique concrète** – Pierre Schaeffer's resonant object approach

Each drum voice simulates water drops hitting surfaces at different pitches with natural decay.

### Internal Combustion Engine Synthesizer
Physical modeling synthesis inspired by:
- **IRCAM physical modeling** (1980s-90s) – Modalys, Pd~
- **Yamaha VL synthesis** – modal synthesis of wind instruments applied to mechanical systems
- **Stochastic misfires** – Iannis Xenakis' probabilistic approach to composition

The engine model includes:
- Piston-driven impulse trains (4, 6, or 8 cylinders)
- Resonant chamber modeling (bandpass filters)
- RPM control → fundamental frequency mapping
- Load/throttle → spectral character

### Quantum Stochasticity (Qubit)
A Bloch sphere-inspired probability field that injects randomness and superposition into synthesis parameters, grounded in:
- **Xenakis stochastic music** (1954+)
- **Chance operations** – John Cage's influence on algorithmic composition
- **Quantum mechanics metaphor** – superposition as creative synthesis control

## Quick Start

### Installation
```bash
cd ~/xfmix
bash install.sh
```

Dependencies installed:
- `puredata` + `puredata-extra` (synthesis engine)
- `python3-aiohttp` + `python3-websockets` (web server)

### Running

Start the synthesizer:
```bash
xfmix
```

Open in Safari on your network:
```
http://<pi-ip>:8866
```

Commands:
```bash
xfmix start       # Start service
xfmix stop        # Stop service
xfmix status      # Check status
xfmix log         # View live logs
```

## Technical Architecture

```
Browser (Safari)
    ↓ WebSocket
Python Server (asyncio + aiohttp)
    ↓ FUDI protocol on localhost:9001
Pure Data (pd -nogui)
    ↓ Audio synthesis
Pi 5 ALSA Audio Output
```

**Ports:**
- **8866** – HTTP/WebSocket (browser UI)
- **9001** – FUDI (Pure Data inter-process communication)

## File Structure

```
~/xfmix/
├── patches/           # Pure Data synthesis patches
│   ├── main.pd       # Top-level patch
│   ├── water_drum.pd # Percussion synth
│   └── engine_synth.pd # Engine modeling synth
├── static/           # Web UI assets
│   └── index.html    # Self-contained controller UI
├── server.py         # Python WebSocket bridge
├── install.sh        # Setup script
├── xfmix.service     # systemd unit
└── README.md
```

## Design Philosophy

**Computer music history as a design language:** Each component references a foundational technique in algorithmic and electronic music:
- **Physical modeling** as a synthesis paradigm (IRCAM tradition)
- **Pure Data** as the core engine (Miller Puckette, 1996 — continuation of Max)
- **Stochastic processes** for controlled randomness (Xenakis)
- **Modal synthesis** for realistic instrumental/mechanical modeling
- **Granular synthesis** for textural percussion

The result is a system that *is* computer music history, not just *inspired by* it.

## References

- Puckette, M. (1991). "Combining event and signal processing in the MAX graphical programming environment". ICMC.
- Schaeffer, P. (1966). *Traité des objets musicaux*. Éditions du Seuil.
- Xenakis, I. (1971). *Formalized Music*. Indiana University Press.
- Cook, P., & Karjoth, G. (2006). "Modeling vocal tract mechanics". ICMC.
- Smith, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing.

## License

MIT

## Author

xboxzero (2026)
