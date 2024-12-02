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
        "disabled sources":[],
        
        "source settings": {
            "steam":{
                "path":None, # None means default path for the system. Path should be a folder containing 'steamapps'
                "aliases": {}, # Aliases for executables. Key is the default name, value is new name
                "illustration overrides": {}, # Overrides illustration. Key is display name (the alias if configured, otherwise default), value is path to image
                "disabled games":["Steamworks Common Redistributables"], # Game names that aren't shown
            },
            "raw":{
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