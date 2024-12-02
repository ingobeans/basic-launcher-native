import config

class Source:
    name:str
    path:str
    disabled_games:list[str]
    installed:bool = True
    def __init__(self) -> None:
        self.path = config.active_config["source settings"][self.name]["path"]
        self.disabled_games = config.active_config["source settings"][self.name]["disabled games"]
    def get_games(self)->list:
        raise NotImplemented(f"Source {self.name} not implemented")
    def get_disabled_games(self):
        if "disabled games" in config.active_config["source settings"][self.name]:
            return config.active_config["source settings"][self.name]["disabled games"]
        return []
    def get_illustration_overrides(self):
        if "illustration overrides" in config.active_config["source settings"][self.name]:
            return config.active_config["source settings"][self.name]["illustration overrides"]
        return []
    def get_aliases(self):
        if "aliases" in config.active_config["source settings"][self.name]:
            return config.active_config["source settings"][self.name]["aliases"]
        return []