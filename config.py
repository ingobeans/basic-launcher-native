import platform, os, json

def get_system():
    return platform.system()

def get_app_data_directory():
    system = get_system()
    if system == "Windows":
        app_data_dir = os.getenv('APPDATA')
    elif system == "Darwin":
        app_data_dir = os.path.expanduser('~/Library/Application Support')
    else:
        app_data_dir = os.path.expanduser('~/.config')
    
    return os.path.join(app_data_dir, "basic-launcher")

def get_default_config():
    return {
        "sort": "alphabetical", # How to sort games. Options are 'alphabetical', 'source'
        "input":{
            "disable_keyboard_navigation": False, # Disable movement by arrow keys (on windows, if primarily using controller for input, setting this to True can fix buggy joystick input)
            "disable_controller": False, # Disables controller input (on windows, controller may still give input as arrow keys. I hate that.)
            "axis_threshold": 0.1 # Threshold for axis movement on controllers
        },
        
        "source settings": {
            "steam":{
                "enabled": True, # Enable this source?
                "path":None, # Path to your steam folder. None will be default path. The steam folder should contain a folder named "steamapps".
                "extra paths":[], # List of additional "SteamLibrary" folders. Use if you have ex. multiple disks with games on them.
                "aliases": {}, # Aliases for executables. Key is the default name, value is new name
                "illustration overrides": {}, # Overrides illustration. Key is display name (the alias if configured, otherwise default), value is path to image
                "disabled games":["Steamworks Common Redistributables","Steam Linux Runtime 1.0 (scout)","Steam Linux Runtime 2.0 (soldier)","Spacewar"], # Game names that aren't shown
                "show non steam games":True, # Whether to include non steam games that you have added to your steam library
            },
            "raw":{
                "enabled": True, # Enable this source?
                "paths":[], # Path to raw executables
                "aliases": {}, # Aliases for executables. Key is the default name, value is new name
                "illustration overrides": {}, # Overrides illustration. Key is display name (the alias if configured, otherwise default), value is path to image
                "disabled games":[],
            }
        }
    }

def merge_dicts(a, b):
    for key, value in b.items():
        if isinstance(value, dict) and key in a:
            a[key] = merge_dicts(a.get(key, {}), value)
        else:
            a[key] = value
    return a

def save_config():
    with open(os.path.join(get_app_data_directory(), "settings.json"), "w", encoding="utf-8") as f:
        json.dump(active_config, f, indent=4)

def load_config():
    with open(os.path.join(get_app_data_directory(), "settings.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def verify_config():
    # function to verify and fix the config file
    # this includes fixing invalid json and adding missing keys
    with open(os.path.join(get_app_data_directory(), "settings.json"), "r", encoding="utf-8") as f:
        data = f.read()

    bad = False
    if not data:
        data = "{}"
    try:
        j = json.loads(data)
    except ValueError:
        # config json is invalid
        import json_repair
        j = json_repair.repair_json(data, return_objects=True)
        bad = True

    # make sure no keys included in the default config are missing
    default = get_default_config()
    new = merge_dicts(default, j)
    if new != j:
        bad = True
    if bad:
        print("current config is bad")
        with open(os.path.join(get_app_data_directory(), "settings.json"), "w", encoding="utf-8") as f:
            json.dump(new, f, indent=4)

if not os.path.exists(get_app_data_directory()):
    os.mkdir(get_app_data_directory())
    active_config = get_default_config()
    save_config()
    print(f"created {get_app_data_directory()}")
else:
    print(f"data dir {get_app_data_directory()}")
    verify_config()
    active_config = load_config()
print(active_config)