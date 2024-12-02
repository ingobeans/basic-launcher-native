import config
from . import source
from . import game
from . import steam
from . import raw

source_steam = steam.Steam()
source_raw = raw.Raw()

sources:list[source.Source] = [source_steam,source_raw]

def get_games():
    games = []
    for s in sources:
        if s.name in config.active_config["disabled sources"] or not s.installed:
            continue
        illustration_overrides = s.get_illustration_overrides()
        aliases = s.get_aliases()
        for g in s.get_games():
            if g.name in aliases:
                g.name = aliases[g.name]
            if g.name in s.get_disabled_games():
                continue
            if g.name in illustration_overrides:
                g.illustration_path = illustration_overrides[g.name]
            games.append(g)
    if config.active_config["sort"] == "alphabetical":
        games = sorted(games,key=lambda g : g.name)
    return games