# Bill of Materials (BOM) — KrishiDrishti Edge

> **Zero Hardware Hallucination Policy:**  
> This BOM documents verified architecture components, required engineering specifications, and hardware acquisition status. No arbitrary model numbers, prices, or fabricated specs are included.

---

## 1. Physical Hardware Matrix

| Category | Component Description | Purpose / Role | Required Specification | Status |
|---|---|---|---|---|
| **Single Board Computer (SBC)** | Raspberry Pi 5 (4GB or 8GB) | Host computational controller running Linux, FastAPI backend, Vite frontend, and SQLite. | Broadcom BCM2712 Quad-Core Cortex-A76, PCIe 2.0/3.0 interface, 4GB+ LPDDR4X RAM. | **CONFIRMED ARCHITECTURE** |
| **Edge AI Accelerator** | Raspberry Pi AI HAT+ | Hardware NPU accelerating neural network crop pathology vision models. | Hailo-8 (26 TOPS) or Hailo-8L (13 TOPS) M.2 module with 16-pin PCIe FPC interface. | **CONFIRMED ARCHITECTURE** |
| **Visual Sensor** | Raspberry Pi Camera Module 3 or USB UVC Camera | High-resolution crop leaf imagery capture for edge vision pipeline. | Minimum 1080p resolution, autofocus, V4L2/libcamera compatible. | **SPECIFIED (Pending Purchase)** |
| **Soil Sensor Probe** | 6-Parameter Soil Sensor | In-situ physical/chemical telemetry ($N$, $P$, $K$, $\text{pH}$, Moisture, Temperature). | RS485 Modbus-RTU protocol, stainless steel probes, 9-24V DC input. | **SPECIFIED (Pending Datasheet)** |
| **Serial Transceiver** | USB to RS485 Converter | Bridges Raspberry Pi USB host port to industrial RS485 differential bus. | FTDI / CH340 / CP2102 chipset with A+, B-, GND terminals. | **CONFIRMED ARCHITECTURE** |
| **Display & Touch** | 7-inch Touchscreen Display | Rugged on-device operator console for multilingual UI and diagnostics. | 7-inch capacitive touch, DSI or HDMI+USB interface, 800x480 or 1024x600 resolution. | **SPECIFIED (Pending Purchase)** |
| **Power Delivery** | Commercial USB-C PD Power Bank / Supply | Portable, safe field power source. | 5V @ 5A (25W-27W) USB-C PD with continuous power delivery. | **SPECIFIED (Commercial PD Unit)** |
| **Sensor Power Boost** | 5V to 12V DC Step-Up Module | Supplies operating voltage to 12V RS485 soil sensor. | 12V DC @ 500mA isolated output. | **SPECIFIED (Pending Purchase)** |
| **Enclosure** | Weather-Resistant Field Shell | Protects SBC, touchscreen, and cabling from dust and moisture. | Polycarbonate / 3D-printed PETG casing with silicone port seals. | **SPECIFIED (Design Phase)** |
| **Cabling & Hardware** | 16-pin PCIe FPC, RS485 shielded twisted pair, USB cables | Peripheral interconnects. | Shielded twisted pair for RS485, PCIe Gen 3 impedance matched FPC. | **CONFIRMED SPECIFICATION** |

---

## 2. Component Confirmation Checklist

- [x] Host Platform Selected: **Raspberry Pi 5**
- [x] Edge AI NPU Architecture Selected: **Raspberry Pi AI HAT+ (Hailo-8)**
- [x] Serial Communication Standard: **RS485 Modbus-RTU**
- [x] Soil Sensor Parameter Count: **Exactly 6 parameters ($N, P, K, \text{pH}, \text{Moisture}, \text{Temperature}$)**
- [ ] Physical Soil Sensor Datasheet: **Awaiting physical unit acquisition for register population**
- [ ] Physical Camera Unit: **Awaiting physical connection**
- [ ] Physical AI HAT+ Unit: **Awaiting physical connection**
