#!/usr/bin/env python3
"""
xfmix: Computer music history synthesizer + drum machine
Runs Pure Data patches on Pi 5, serves browser UI via WebSocket bridge
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import socket
import struct
import subprocess
import sys
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

XFMIX_DIR = Path(__file__).parent
PATCHES_DIR = XFMIX_DIR / "patches"
STATIC_DIR = XFMIX_DIR / "static"
PD_FUDI_PORT = 9001
PD_FUDI_ADDR = "127.0.0.1"
HTTP_PORT = 8866
CAMERA_CMD = [
    "rpicam-vid",
    "--codec", "mjpeg",
    "--width", "640",
    "--height", "480",
    "--framerate", "15",
    "--timeout", "0",
    "--nopreview",
    "-o", "-",
]

# Global state
pd_process = None
fudi_sock = None
ws_clients = set()
ws_server = None


class WebSocketHandler:
    """Simple WebSocket handler without external dependencies"""

    def __init__(self, sock):
        self.sock = sock
        self.is_connected = False

    def handle_handshake(self, sec_key):
        """Perform WebSocket handshake. `sec_key` is the client's Sec-WebSocket-Key."""
        try:
            if not sec_key:
                return False

            # WebSocket handshake
            magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
            accept_key = base64.b64encode(
                hashlib.sha1((sec_key + magic).encode()).digest()
            ).decode()

            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n"
                "\r\n"
            )
            self.sock.send(response.encode())
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Handshake error: {e}")
            return False

    def recv_frame(self):
        """Receive WebSocket frame"""
        try:
            data = self.sock.recv(1024)
            if not data:
                return None

            # Parse frame header
            opcode = data[0] & 0x0f
            masked = (data[1] & 0x80) >> 7
            payload_len = data[1] & 0x7f

            if payload_len == 126:
                payload_len = struct.unpack('>H', data[2:4])[0]
                payload_start = 4
            elif payload_len == 127:
                payload_len = struct.unpack('>Q', data[2:10])[0]
                payload_start = 10
            else:
                payload_start = 2

            if masked:
                mask = data[payload_start:payload_start + 4]
                payload = data[payload_start + 4:payload_start + 4 + payload_len]
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            else:
                payload = data[payload_start:payload_start + payload_len]

            if opcode == 1:  # Text frame
                return payload.decode()
            elif opcode == 8:  # Close frame
                return None
            return None
        except Exception as e:
            logger.error(f"Frame receive error: {e}")
            return None

    def send_frame(self, data):
        """Send WebSocket text frame"""
        try:
            if isinstance(data, str):
                data = data.encode()

            frame = bytearray()
            frame.append(0x81)  # Text frame, FIN

            payload_len = len(data)
            if payload_len < 126:
                frame.append(payload_len)
            elif payload_len < 65536:
                frame.append(126)
                frame.extend(struct.pack('>H', payload_len))
            else:
                frame.append(127)
                frame.extend(struct.pack('>Q', payload_len))

            frame.extend(data)
            self.sock.send(bytes(frame))
            return True
        except Exception as e:
            logger.error(f"Frame send error: {e}")
            return False


def send_fudi(message: str):
    """Send FUDI message to Pure Data"""
    if fudi_sock:
        try:
            fudi_sock.send((message + ";\n").encode())
            logger.debug(f"→ Pd: {message}")
        except Exception as e:
            logger.error(f"FUDI send error: {e}")


async def start_pd():
    """Start Pure Data headless process"""
    global pd_process
    main_patch = PATCHES_DIR / "main.pd"
    if not main_patch.exists():
        raise FileNotFoundError(f"Patch not found: {main_patch}")

    # pd flag notes:
    #   -r (not -samplerate); -rt needs setuid so we skip it; XFMIX_NOAUDIO
    #   lets you boot without an audio device (useful for headless dev/CI).
    cmd = ["pd", "-nogui"]
    if os.environ.get("XFMIX_NOAUDIO") == "1":
        cmd += ["-noaudio"]
    else:
        cmd += ["-alsa", "-channels", "2", "-r", "48000", "-audiobuf", "20"]
    cmd += ["-open", str(main_patch)]

    try:
        pd_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(PATCHES_DIR),
            text=True,
        )
        logger.info(f"✓ Pure Data started (PID {pd_process.pid})")
        await asyncio.sleep(0.5)
    except FileNotFoundError:
        logger.error("✗ Pure Data not found. Install with: sudo apt install puredata puredata-extra")
        raise


async def connect_fudi():
    """Connect to Pure Data FUDI port"""
    global fudi_sock
    for attempt in range(10):
        try:
            fudi_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fudi_sock.connect((PD_FUDI_ADDR, PD_FUDI_PORT))
            logger.info(f"✓ Connected to Pure Data (port {PD_FUDI_PORT})")
            return True
        except ConnectionRefusedError:
            await asyncio.sleep(0.2)
    logger.error("✗ Could not connect to Pure Data")
    return False


def handle_message(data: str):
    """Route message to Pure Data"""
    try:
        msg = json.loads(data)
        msg_type = msg.get("type")

        if msg_type == "water":
            lane = msg.get("lane", 0)
            velocity = msg.get("velocity", 0.8)
            send_fudi(f"water {lane} {velocity}")

        elif msg_type == "engine":
            note = msg.get("note", 60)
            velocity = msg.get("velocity", 1.0)
            rpm = msg.get("rpm", 100)
            load = msg.get("load", 0.5)
            cylinders = msg.get("cylinders", 4)
            send_fudi(f"engine {note} {velocity} {rpm} {load} {cylinders}")

        elif msg_type == "qubit":
            value = msg.get("value", 0.5)
            send_fudi(f"qubit {value}")

        elif msg_type == "mix":
            drum = msg.get("drum", 0.5)
            synth = msg.get("synth", 0.5)
            send_fudi(f"mix {drum} {synth}")

        elif msg_type == "master":
            volume = msg.get("volume", 0.7)
            send_fudi(f"master {volume}")

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON: {data}")


class FileHandler(SimpleHTTPRequestHandler):
    """HTTP handler for static files + WebSocket upgrade"""

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        if self.path == '/ws':
            self.handle_websocket()
        elif self.path.startswith('/camera.mjpg'):
            self.handle_camera()
        else:
            # Serve static files
            self.path = self.path if self.path != '/' else '/index.html'
            if '..' not in self.path:  # Security
                try:
                    fpath = STATIC_DIR / self.path.lstrip('/')
                    if fpath.exists() and fpath.is_file():
                        with open(fpath, 'rb') as f:
                            self.send_response(200)
                            if self.path.endswith('.html'):
                                self.send_header('Content-type', 'text/html')
                            elif self.path.endswith('.css'):
                                self.send_header('Content-type', 'text/css')
                            elif self.path.endswith('.js'):
                                self.send_header('Content-type', 'application/javascript')
                            self.end_headers()
                            self.wfile.write(f.read())
                    else:
                        # Fallback to index.html
                        with open(STATIC_DIR / 'index.html', 'rb') as f:
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(f.read())
                except Exception as e:
                    logger.error(f"File serving error: {e}")
                    self.send_error(500)
            else:
                self.send_error(403)

    def handle_camera(self):
        """Stream Pi camera as multipart MJPEG (one rpicam-vid per client)"""
        proc = None
        try:
            proc = subprocess.Popen(
                CAMERA_CMD,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            logger.error("✗ rpicam-vid not found")
            self.send_error(503, "Camera unavailable")
            return

        try:
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "multipart/x-mixed-replace; boundary=xfmixframe",
            )
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.end_headers()

            buf = b""
            while True:
                chunk = proc.stdout.read(8192)
                if not chunk:
                    break
                buf += chunk
                while True:
                    soi = buf.find(b"\xff\xd8")
                    if soi < 0:
                        buf = b""
                        break
                    eoi = buf.find(b"\xff\xd9", soi + 2)
                    if eoi < 0:
                        if soi > 0:
                            buf = buf[soi:]
                        break
                    frame = buf[soi : eoi + 2]
                    buf = buf[eoi + 2 :]
                    self.wfile.write(b"--xfmixframe\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(
                        f"Content-Length: {len(frame)}\r\n\r\n".encode()
                    )
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            logger.error(f"Camera stream error: {e}")
        finally:
            if proc:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def handle_websocket(self):
        """Handle WebSocket connection. BaseHTTPRequestHandler has already
        parsed the request line and headers into self.headers — do NOT re-read
        from rfile, that would block forever waiting for bytes that aren't
        coming."""
        try:
            sec_key = self.headers.get('Sec-WebSocket-Key')
            ws = WebSocketHandler(self.request)
            if not ws.handle_handshake(sec_key):
                return

            ws_clients.add(ws)
            logger.info(f"✓ Client connected ({len(ws_clients)} total)")

            # Message loop
            try:
                while ws.is_connected:
                    msg = ws.recv_frame()
                    if msg is None:
                        break

                    handle_message(msg)
                    ws.send_frame('{"status":"ok"}')
            finally:
                ws_clients.discard(ws)
                logger.info(f"✓ Client disconnected ({len(ws_clients)} remaining)")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


async def run_server():
    """Run HTTP server"""
    loop = asyncio.get_event_loop()

    def make_handler(*args, **kwargs):
        return FileHandler(*args, directory=STATIC_DIR, **kwargs)

    server = ThreadingHTTPServer(('0.0.0.0', HTTP_PORT), make_handler)
    server.daemon_threads = True

    try:
        hostname = os.popen("hostname -I").read().strip().split()[0]
        logger.info(f"✓ Web UI: http://{hostname}:{HTTP_PORT}")
        logger.info(f"✓ Listening on port {HTTP_PORT}...")

        # Run server in background
        await loop.run_in_executor(None, server.serve_forever)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


async def main():
    """Main entry point"""
    logger.info("━" * 50)
    logger.info("  xfmix – Computer Music Synthesizer")
    logger.info("━" * 50)

    try:
        # Start Pure Data
        await start_pd()

        # Connect to FUDI
        if not await connect_fudi():
            sys.exit(1)

        # Run HTTP server
        await run_server()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if fudi_sock:
            fudi_sock.close()
        if pd_process:
            pd_process.terminate()
            try:
                pd_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pd_process.kill()
            logger.info("✓ Pure Data stopped")


if __name__ == "__main__":
    asyncio.run(main())
