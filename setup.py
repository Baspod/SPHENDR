import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "debug": True,
    "source": {
        "module": "plugins.dummy_source",
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


def select_python_file():
    plugins_dir = os.path.join(BASE_DIR, "plugins")

    if not os.path.exists(plugins_dir):
        print(f"[ERROR] Directory not found: {plugins_dir}")
        return None, None, None

    files = [f for f in os.listdir(plugins_dir) if f.endswith(".py") and f != "__init__.py"]
    if not files:
        print("[!] No plugins found in folder.")
        return None, None, None

    for i, f in enumerate(files):
        print(f"{i + 1}. {f}")

    try:
        idx = int(input("Select file number: ")) - 1
        if idx < 0 or idx >= len(files): raise ValueError
        filename = files[idx]
    except ValueError:
        print("[!] Invalid selection.")
        return None, None, None

    module_path = f"plugins.{filename[:-3]}"

    with open(os.path.join(plugins_dir, filename), 'r', encoding='utf-8') as f:
        content = f.read()
        classes = re.findall(r'class (\w+)', content)

    cls = classes[0] if classes else "Unknown"
    return filename, module_path, cls


def select_math_processor():
    utils_dir = os.path.join(BASE_DIR, "utils")
    if not os.path.exists(utils_dir):
        return "Default"

    processors = []
    for root, _, files in os.walk(utils_dir):
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        found = re.findall(r'@register_processor\([\'"](\w+)[\'"]\)', content)
                        processors.extend(found)
                except:
                    continue

    processors = list(set(processors))
    if not processors:
        return "Default"

    print("\nAvailable Math Processors:")
    for i, proc in enumerate(processors):
        print(f"{i + 1}. {proc}")

    try:
        idx = int(input("Select processor number: ")) - 1
        if 0 <= idx < len(processors):
            return processors[idx]
    except ValueError:
        pass
    return "Default"


def menu():
    while True:
        try:
            cfg = load_config()
            if not cfg:
                save_config(DEFAULT_CONFIG)
                continue

            print("\n--- CONFIG MANAGER ---")
            print("1. Show settings | 2. Add Plugin | 3. Remove Plugin | 4. Configure Math | 5. Reset | 6. Exit")
            choice = input("Select: ")

            if choice == "1":
                print(json.dumps(cfg, indent=4))

            elif choice == "2":
                print("\n--- ADD PLUGIN ---")
                res = select_python_file()
                if res[0] is None: continue
                filename, module_path, cls = res

                name = input("Plugin name: ").strip()
                if not name:
                    print("[!] Name cannot be empty.")
                    continue

                port = get_int_input("Port: ")

                if "Source" in cls or "source" in filename.lower():
                    cfg["plugins"][name] = {
                        "enabled": True,
                        "type": "source",
                        "module": module_path,
                        "class": cls,
                        "port": port
                    }
                    cfg["source"] = {
                        "module": module_path,
                        "class": cls,
                        "port": port
                    }
                    save_config(cfg)
                    print(f"[OK] Detected as SOURCE. Plugin '{name}' added and assigned as main data source.")

                else:
                    processor = select_math_processor()

                    cfg["plugins"][name] = {
                        "enabled": True,
                        "type": "sink",
                        "module": module_path,
                        "class": cls,
                        "port": port,
                        "math": {
                            "active_processor": processor,
                            "settings": {
                                "yaw": {"weight": 1.0, "smooth": 0.5},
                                "pitch": {"weight": 1.0, "smooth": 0.5},
                                "roll": {"weight": 1.0, "smooth": 0.5}
                            }
                        }
                    }
                    save_config(cfg)
                    print(f"[OK] Detected as SINK. Plugin '{name}' added with math processor '{processor}'.")

            elif choice == "3":
                if not cfg["plugins"]:
                    print("[!] No plugins to remove.")
                    continue

                print("\nCurrent plugins:")
                for p_name in cfg["plugins"]:
                    print(f"- {p_name}")

                name = input("\nEnter plugin name to remove: ").strip()
                if name in cfg["plugins"]:
                    del cfg["plugins"][name]
                    save_config(cfg)
                else:
                    print("[!] Plugin not found.")

            elif choice == "4":
                if not cfg["plugins"]:
                    print("[!] No active plugins to configure math.")
                    continue

                print("\nSelect plugin to update math engine:")
                plugins_list = list(cfg["plugins"].keys())
                for i, p_name in enumerate(plugins_list):
                    print(f"{i + 1}. {p_name}")

                try:
                    p_idx = int(input("Select number: ")) - 1
                    if 0 <= p_idx < len(plugins_list):
                        target_plugin = plugins_list[p_idx]
                        new_processor = select_math_processor()

                        if "math" not in cfg["plugins"][target_plugin]:
                            cfg["plugins"][target_plugin]["math"] = {}

                        cfg["plugins"][target_plugin]["math"]["active_processor"] = new_processor
                        if "settings" not in cfg["plugins"][target_plugin]["math"]:
                            cfg["plugins"][target_plugin]["math"]["settings"] = {
                                "yaw": {"weight": 1.0, "smooth": 0.5},
                                "pitch": {"weight": 1.0, "smooth": 0.5},
                                "roll": {"weight": 1.0, "smooth": 0.5}
                            }
                        save_config(cfg)
                        print(f"[OK] Math processor for '{target_plugin}' changed to '{new_processor}'.")
                    else:
                        print("[!] Invalid selection.")
                except ValueError:
                    print("[!] Invalid input.")

            elif choice == "5":
                save_config(DEFAULT_CONFIG)

            elif choice == "6":
                break

        except (EOFError, KeyboardInterrupt):
            print("\n[SYSTEM] Exiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    menu()
