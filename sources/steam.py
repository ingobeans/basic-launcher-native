import config, os, vdf, subprocess, vdf_bin
from . import source
from . import game
from . import raw

class Steam(source.Source):
    name:str = "steam"
    
    def __init__(self) -> None:
        super().__init__()
        
        self.path = config.active_config["source settings"]["steam"].get("path",None) or self.get_default_path()
        if not self.valid_path(self.path):
            self.enabled = False
        self.extra_paths = []
        for path in config.active_config["source settings"]["steam"].get("extra paths",[]):
            if self.valid_path(path):
                self.extra_paths.append(path)
        self.show_non_steam_games = config.active_config["source settings"]["steam"].get("show non steam games",True)

    def valid_path(self, path):
        valid = os.path.isdir(path) and os.path.isdir(os.path.join(path, "steamapps", "common"))
        return valid
    
    def game_exists(self, name):
        path = self.get_path()
        if not path:
            return []
        
        apps = os.path.join(path, "common")
        return name in os.listdir(apps)

    def get_default_path(self):
        system = config.get_system()
        if system == "Windows":
            return os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),"Steam")
        elif system == "Darwin":
            return os.path.expanduser('~/Library/Application Support/Steam')
        else:
            old_path = os.path.expanduser('~/.local/share/Steam')
            if os.path.exists(old_path):
                return old_path
            return os.path.expanduser('~/.steam/steam')
    
    def get_game_illustraton_path(self, game_id):
        if not self.path:
            return None
        
        library_path = os.path.join(self.path, "appcache", "librarycache")
        illustration_path = os.path.join(library_path, f"{game_id}_library_600x900.jpg")
        if os.path.isfile(illustration_path):
            return illustration_path
        return None
    
    def get_non_steam_illustration_path(self,game_id,grids_path):
        files = os.listdir(grids_path)
        for file in files:
            if file.startswith(str(game_id)) and not file.endswith("json"):
                path = os.path.join(grids_path,file)
                return path
        return None
    
    def get_non_steam_games(self):
        games = []
        userdata_path = os.path.join(self.path,"userdata")
        for user in os.listdir(userdata_path):
            config_path = os.path.join(userdata_path,user,"config")
            grids_path = os.path.join(config_path,"grid")
            with open(os.path.join(config_path, "shortcuts.vdf"), "rb") as f:
                data = vdf_bin.parse_vdf(bytearray(list(f.read())))
                for key in data["shortcuts"]:
                    shortcut = data["shortcuts"][key]
                    illustration = self.get_non_steam_illustration_path(shortcut['appid'],grids_path)
                    g = game.Game(self, shortcut["AppName"], f"n{shortcut['Exe'].strip('"')}", illustration)
                    games.append(g)
        return games


    def get_games(self):
        games = []
        for path in self.extra_paths+[self.path]:
            if not path:
                continue
            apps_path = os.path.join(path, "steamapps")

            # load all steam app manifests
            files = os.listdir(apps_path)
            filtered_files = [x for x in files if x.startswith("appmanifest_")]
            
            for manifest in filtered_files:
                # load the (vdf formatted) manifests 
                with open(os.path.join(apps_path, manifest), "r", encoding="utf-8") as f:
                    data = vdf.load(f)["AppState"]
                g = game.Game(self, data["name"], data["appid"], self.get_game_illustraton_path(data["appid"]))
                games.append(g)
        if self.show_non_steam_games:
            games += self.get_non_steam_games()
        return games
    
    def run_game(self,id):
        if self.show_non_steam_games and str(id).startswith("n"):
            raw.exec_path(id.removeprefix("n"))
            return
        system = config.get_system()
        if system == "Windows":
            command = f"start steam://rungameid/{id}"
        elif system == "Darwin":
            command = f"open steam://rungameid/{id}"
        else:
            command = f"steam steam://rungameid/{id}"
        
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)