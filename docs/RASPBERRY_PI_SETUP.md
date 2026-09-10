# Raspberry Pi 5 Deployment Guide — KrishiDrishti Edge

> **Target Platform:** Raspberry Pi 5 (8GB / 4GB RAM)  
> **Operating System:** Raspberry Pi OS 64-bit (Debian 12 "Bookworm")  
> **AI Accelerator:** Raspberry Pi AI HAT+ (Hailo-8 / Hailo-8L on PCIe Gen 3)  
> **Deployment Constraint:** 100% Offline Edge Operation, Zero Cloud Dependency.

---

## 1. Operating System & Prerequisites

### Recommended OS Image
- **OS**: Raspberry Pi OS (64-bit) with desktop (or Lite for headless edge kiosk).
- **Kernel**: Linux 6.6+ with PCIe Gen 3 / Gen 2 overlay support.

### System Package Dependencies
```bash
sudo apt update && sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    libopencv-dev \
    git \
    curl \
    v4l-utils \
    libcamera-tools \
    pciutils
```

### Node.js & Vite Runtime
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## 2. Raspberry Pi AI HAT+ (Hailo-8) Setup

The Raspberry Pi AI HAT+ connects directly to the Raspberry Pi 5 via the 16-pin PCIe FPC connector.

### Step 1: Enable PCIe Gen 3 in `/boot/firmware/config.txt`
```ini
# Add to /boot/firmware/config.txt
dtparam=pciex1
dtparam=pciex1_gen=3
```

### Step 2: Install HailoRT Software & Kernel Drivers
```bash
sudo apt install -y hailo-all
```

### Step 3: Verify Hardware Detection
```bash
# Verify PCIe enumeration
lspci -nn | grep -i hailo

# Verify device node
ls -l /dev/hailo0

# Run Hailo hardware test
hailortcli fw-control identify
```
*If Hailo-8 is not detected, KrishiDrishti Edge automatically engages optimized CPU Fallback without crashing.*

---

## 3. Serial & RS485 Interface Setup

The 6-parameter soil sensor connects to a USB-RS485 adapter (FTDI / CH340 / CP2102).

### User Permissions for Serial Bus
```bash
# Add current user to dialout group for RS485 access
sudo usermod -aG dialout $USER

# Configure udev rule for persistent RS485 symlink (/etc/udev/rules.d/99-krishi-rs485.rules)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="krishi_soil_sensor"
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## 4. Application Installation & Build

```bash
# Clone or transfer repository
cd ~
git clone <repo-url> krishidrishti-edge
cd krishidrishti-edge

# Configure Python Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Configure Production Environment File
cp .env.example .env
# Edit .env to set DEMO_MODE=false for physical hardware

# Build Frontend Assets
cd frontend
npm install
npm run build
cd ..
```

---

## 5. Production systemd Service Configuration

Create `krishidrishti.service` to start on boot:

```ini
# /etc/systemd/system/krishidrishti.service
[Unit]
Description=KrishiDrishti Edge Portable AI Farming Assistant
After=network.target local-fs.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/krishidrishti-edge
Environment="PATH=/home/pi/krishidrishti-edge/venv/bin"
ExecStart=/home/pi/krishidrishti-edge/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir /home/pi/krishidrishti-edge/backend
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable krishidrishti.service
sudo systemctl start krishidrishti.service
```

---

## 6. Offline Kiosk / Touchscreen Mode

To launch the UI in fullscreen Chromium kiosk on the attached 7-inch DSI/HDMI touchscreen:

```bash
# ~/.config/wayfire.ini or autostart
[autostart]
chromium = chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://localhost:8000
```
