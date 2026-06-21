#  <img src="assets/logo.png" width="38" height="38" valign="middle"> SPHENDR — Asynchronous Modular Tracking Data Pipeline

A high-performance, asynchronous middleware framework built on Python's `asyncio`. **SPHENDR** is designed as an extensible, event-driven pipeline to capture raw orientation data from hardware or software sources (Sources), clean and transform it via dynamically attached mathematical filters (Processors), and broadcast the finalized telemetry to end-node consumers (Sinks) like OpenTrack or VRChat with zero latency.

---

## ▫️ Features

* **AsyncIO Core & DataBus:** Fully non-blocking architecture driven by a Pub/Sub pattern (Data Bus). Guarantees handling of high-frequency data streams (100Hz+) without I/O bottlenecks or redundant CPU overhead.
* **Strict Separation of Concerns (Decoupling):** Network I/O interfaces are entirely isolated from trigonometry, smoothing filters, and coordinate stabilization algorithms.
* **Dynamic Registry (Runtime Registry):** Automatic scanning, detection, and lazy loading of mathematical cores at runtime using Python decorators (`@register_processor`).
* **Interactive CLI Configuration Utility:** The `setup.py` tool allows adding new plugins, modifying ports, and hot-swapping math processors on the fly without manual JSON editing.
* **Pipeline Fault Tolerance:** Isolated task handling via the data bus protects the system core from crashes — if a specific plugin throws an exception, the rest of the pipeline continues running smoothly.

---

## ▫️ Architecture: Why Processors and Plugins?

To eliminate over-engineered monolithic scripts where network sockets are mixed up with raw math, the tracking data lifecycle in SPHENDR is divided into three independent layers:

1. **Sources (Data Ingestion):** Manage network protocols (UDP/TCP sockets), handshakes, and keep-alive pings (heartbeats). Their sole job is to receive a raw packet, extract the baseline coordinates (e.g., quaternion `[w, x, y, z]`), and publish it to the `DataBus`.
2. **Mathematical Processors (Computation Layer):** Sit between the data bus and the output. They intercept raw coordinates and apply mathematics: eliminating micro-vibrations, compensating for physical mounting tilts, and translating Quaternions to Euler Angles.
* *The benefit?* You write a complex filter (e.g., a Kalman filter) once inside the `utils/` directory, then bind it to *any* output plugin via configuration.


3. **Sinks (Data Egress):** Responsible exclusively for packaging processed data into the target application's specific payload format and broadcasting it to the destination IP/port (e.g., packing a 6-`double` native endian structure for OpenTrack or generating OSC messages for VRChat).

---

##  Project Structure

```text
SPHENDR/
│
├── core/
│   ├── base.py          # Base class BaseSink (automatically binds Math and Sink)
│   └── bus.py           # Event-driven DataBus framework (Pub/Sub)
│
├── plugins/             # Directory for network I/O plugins
│ └── dummy_source.py # Raw plugin
│
├── utils/               # Directory for mathematical modules and filters
│   ├── registry.py      # Meta-registry for automatic processor discovery
│   ├── math_processor.py# Implementation of math engines (Default, Advanced)
│   └── basmath.py       # Axis filters (AxisFilter) and trigonometric helper functions
│
├── config.json          # Dynamic system configuration state
├── setup.py             # Interactive CLI configuration utility
└── __main__.py          # Main bootstrap runner to initialize the framework

```

---

## ▫️ Configuration (`config.json`)

The platform's operational parameters are automatically generated and managed via the interactive `setup.py` script. A typical configuration structure looks like this:

```json
{
  "debug": true,
  "source": {
    "module": "plugins.source_owo",
    "class": "OwoTrackSource",
    "port": 9185
  },
  "plugins": {
    "OpenTrackSink": {
      "enabled": true,
      "module": "plugins.sink_opentrack",
      "class": "OpenTrackSink",
      "ip": "127.0.0.1",
      "port": 4242,
      "math": {
        "active_processor": "Advanced",
        "settings": {
          "yaw": {"weight": 1.0, "smooth": 0.3},
          "pitch": {"weight": 1.0, "smooth": 0.3},
          "roll": {"weight": 1.0, "smooth": 0.3}
        }
      }
    }
  }
}

```

### Main Parameter Blocks:

* `debug` — Global toggle for real-time telemetry logs and debug outputs in the terminal console.
* `source` — Parameters for the active network input (module, class name, and local listening port for incoming packets).
* `plugins` — Registry of active destination outputs (Sinks). Each sink contains its own independent `"math"` configuration block.
* `active_processor` — The name of the math core from `utils/` assigned to process data individually for this specific sink.
* `settings` — Axis-specific factors for weights (`weight`), exponential smoothing (`smooth`), or filter multipliers.

---

## 🛠 Developer Guide: Extending the System

### 1. Adding a Custom Mathematical Processor

Place your new file into the `utils/` directory. Register the class using the `@register_processor` decorator and implement the `process(self, data)` method.

```python
# utils/my_kalman.py
from utils.registry import register_processor

@register_processor("KalmanFilter")
class KalmanProcessor:
    def __init__(self, settings):
        self.settings = settings # Read custom values from config.json
        print("[SYSTEM] Kalman filter successfully initialized.")

    def process(self, data):
        # 'data' contains raw dictionaries from the Source (e.g., {"w": ..., "x": ...})
        processed = data.copy()
        
        # --- Your custom mathematical axis processing goes here ---
        
        return processed # Returns the modified dict ready for the Sink

```

### 2. Adding a Custom Destination Plugin (Sink)

Place your file into the `plugins/` folder. Inherit from `BaseSink` and override the `on_init` and `send_data` methods.

```python
# plugins/sink_vrc_osc.py
import socket
from core.base import BaseSink

class VRCSink(BaseSink):
    def on_init(self, ip="127.0.0.1", port=9000, **kwargs):
        # BaseSink automatically initializes the correct math engine before this step
        self.target = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, data):
        # This receives data that has already been cleaned by the math processor
        try:
            yaw = data.get("yaw", 0.0)
            payload = f"/avatar/parameters/tracking/yaw {yaw}".encode("utf-8")
            self.sock.sendto(payload, self.target)
        except Exception as e:
            print(f"[VRCSink] Broadcast error: {e}")

```

---

##  Using the Configuration Manager (`setup.py`)

Instead of manual JSON editing, use the built-in CLI tool:

```bash
python setup.py

```

* **Option 2 (Add Plugin):** Scans the `plugins/` directory, detects the plugin type based on its class structure, requests the network port, and registers it. Sinks automatically receive a default math configuration layout.
* **Option 4 (Configure Math):** Scans the `utils/` directory, lists all available math engines registered via decorators, and lets you bind a processor to any active output plugin.
---

> ⚠️ **Important Configuration Rule:** Modifying or binding math modules (Option 4) is only available when at least one destination plugin (Sink) is registered in the system. Add your receiver first, then configure its computing core.

---

## ▫️ Quick Start

1. Ensure Python version **3.14** or newer is installed on your system.
2. Set up your pipeline environment and attach necessary plugins using the configuration manager:
```bash
python setup.py

```


3. Run the main asynchronous engine to initialize data routing and processing:
```bash
python __main__.py

```
---

## Dont forget to visit our Official Plugin Catalog on GitHub Gist:
  > https://gist.github.com/Baspod/4c0d9aff5c68824ab18d91bdab537296 
  
---
