import json
import os
import re
import sys

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "debug": True,
    "source": {
        "module": "SPHENDR.plugins.dummy_source",
        "class": "DummySource",
        "port": 0
    },
    "plugins": {}
}


def load_config():
    if not os.path.exists(CONFIG_FILE): return None
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
        print("\n[OK] Configuration saved.")
    except Exception as e:
        print(f"\n[ERROR] Save failed: {e}")


def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("[!] Invalid input. Please enter a number.")


def menu():
    while True:
        try:
            cfg = load_config()
            if not cfg: save_config(DEFAULT_CONFIG); continue

            print("\n--- CONFIG MANAGER ---")
            print("1. Show settings | 2. Add plugin | 3. Remove | 4. Reset | 5. Exit")
            choice = input("Select: ")

            if choice == "1":
                print(json.dumps(cfg, indent=4))

            elif choice == "2":
                base_dir = os.path.dirname(os.path.abspath(__file__))
                plugins_dir = os.path.join(base_dir, "plugins")

                if not os.path.exists(plugins_dir):
                    print(f"[ERROR] Directory not found: {plugins_dir}")
                    continue

                files = [f for f in os.listdir(plugins_dir) if f.endswith(".py") and f != "__init__.py"]
                if not files:
                    print("[!] No plugins found in folder.")
                    continue

                for i, f in enumerate(files): print(f"{i + 1}. {f}")

                try:
                    idx = int(input("Select file number: ")) - 1
                    if idx < 0 or idx >= len(files): raise ValueError
                    filename = files[idx]
                except ValueError:
                    print("[!] Invalid selection.")
                    continue

                module_path = f"SPHENDR.plugins.{filename[:-3]}"

                with open(os.path.join(plugins_dir, filename), 'r') as f:
                    classes = re.findall(r'class (\w+)', f.read())

                cls = classes[0] if classes else "Unknown"
                name = input("Local plugin name: ").strip()
                if not name: print("[!] Name cannot be empty."); continue

                port = get_int_input("Port: ")

                cfg["plugins"][name] = {
                    "enabled": True,
                    "module": module_path,
                    "class": cls,
                    "port": port
                }
                save_config(cfg)

            elif choice == "3":
                if not cfg["plugins"]:
                    print("[!] No plugins to remove.")
                    continue

                print("\nCurrent plugins:")
                for name in cfg["plugins"]:
                    print(f"- {name}")

                name = input("\nEnter plugin name to remove: ").strip()
                if name in cfg["plugins"]:
                    del cfg["plugins"][name]
                    save_config(cfg)
                else:
                    print("[!] Plugin not found.")

            elif choice == "4":
                save_config(DEFAULT_CONFIG)

            elif choice == "5":
                break

        except (EOFError, KeyboardInterrupt):
            print("\n[SYSTEM] Exiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    menu()