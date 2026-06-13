import asyncio
import json
import importlib
import os
import sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bus import DataBus
from utils.registry import load_all_processors

CONFIG_FILE = "config.json"
SETUP_SCRIPT = "setup.py"


def get_class(module_path, class_name):
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)
    except Exception as e:
        print(f"[CRITICAL] Error loading {module_path}.{class_name}: {e}")
        raise


async def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"[SYSTEM] Config not found. Launching {SETUP_SCRIPT}...")
        subprocess.run([sys.executable, SETUP_SCRIPT], check=True)

        if not os.path.exists(CONFIG_FILE):
            print("[CRITICAL] Configuration was not created. Exiting.")
            sys.exit(1)

    with open(CONFIG_FILE, "r") as f:
        cfg = json.load(f)

    load_all_processors()

    bus = DataBus()

    src_cfg = cfg.get("source", {})
    tracker_cls = get_class(src_cfg["module"], src_cfg["class"])

    tracker = tracker_cls(**{k: v for k, v in src_cfg.items() if k not in ["module", "class"]})

    for name, p_cfg in cfg.get("plugins", {}).items():
        if p_cfg.get("enabled"):
            sink_cls = get_class(p_cfg["module"], p_cfg["class"])

            params = {k: v for k, v in p_cfg.items() if k not in ["enabled", "module", "class"]}
            bus.subscribe(sink_cls(**params))
            print(f"[SYSTEM] Plugin {name} initialized successfully.")

    print("[SYSTEM] System started.")
    await tracker.start(bus)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SYSTEM] Program stopped.")
        sys.exit(0)