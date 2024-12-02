import config, os, subprocess
from . import source
from . import game
from PIL import Image
if config.get_system() == "Windows":
    import win32api, win32ui, win32com, win32gui, win32con

class Raw(source.Source):
    name:str = "raw"
    games_registry = {}

    def __init__(self) -> None:
        pass

    def game_exists(self, path):
        return os.path.isfile(path)

    def get_icon_from_exe(self, path):
        if config.get_system() != "Windows":
            return None
        path = path.replace("\\", "/")
        filename = os.path.basename(path)
        icoX = win32api.GetSystemMetrics(win32con.SM_CXICON)

        large, small = win32gui.ExtractIconEx(path, 0)
        win32gui.DestroyIcon(small[0])

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, icoX, icoX)
        hdc = hdc.CreateCompatibleDC()

        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0,0), large[0])

        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            (32,32),
            bmpstr, 'raw', 'BGRA', 0, 1
        )
        path = os.path.join(os.getenv('TEMP'), filename+'.png')
        img.save(path)
        return path

    def get_game_illustraton_path(self, game_id):
        return os.path.join(os.getenv('TEMP'), game_id+'.png')

    def get_games(self):
        games = []
        games_paths = config.active_config["source settings"]["raw"]["paths"]
        for path in games_paths:
            name = os.path.basename(path).split(".")[0]
            game_id = os.path.basename(path)
            self.games_registry[game_id] = path
            if name in self.get_illustration_overrides():
                illustration_path = None
            else:
                illustration_path = self.get_icon_from_exe(path)
            g = game.Game(self,name,game_id,illustration_path)
            games.append(g)
        return games
    
    def run_game(self,id):
        system = config.get_system()
        path = self.games_registry[id]
        
        subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.path.dirname(path))