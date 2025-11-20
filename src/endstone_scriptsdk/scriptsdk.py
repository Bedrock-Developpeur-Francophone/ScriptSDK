from endstone.plugin import Plugin
from colorama import Fore
from endstone_scriptsdk.handler import EventHandler
from endstone_scriptsdk.src.utils import sendCustomNameToPlayerForPlayer

class ScriptSDK(Plugin):
    api_version = "0.10"
    authors = ["TheDreWen"]
    name = "scriptsdk"
    description = "Use certain Endstone features directly in your Bedrock add-ons through a JavaScript API. ScriptSDK bridges the gap between Minecraft Bedrock add-ons and Endstone plugin capabilities."
    website = "https://discord.gg/kQU9p4ZHbR"

    plugin_mc_prefix = "§e[Script§1SDK] §r"
    prefix = f"{Fore.YELLOW}Script{Fore.BLUE}SDK{Fore.RESET}"

    commands = {
        "debug" : {
            "description" : "Enable/Disable debugging (Console)",
            "usages" : ["/debug"],
            "permissions" : ["debug.command.default"]
        }
    }

    permissions = {
        "debug.command.default": {
            "description": "OP Permission",
            "default" : "op"
        }
    }

    isDebug = False

    def on_load(self):
        self.logger.set_level(self.logger.INFO)
        self.logger.info(f'Loaded !')
    
    def on_enable(self):
        self.register_events(self)
        self.handler = EventHandler(self)

        self.server.scheduler.run_task(self, self.clock, 0, 1)
    
    def on_disable(self):
        for player, bar in self.handler.bossBars.items():
            bar.remove_all()
        self.logger.info(f'Unloaded !')

    def clock(self):

        for player_name, views in self.handler.nameTagCache.items():
            for target_name, newName in views.items():
                player = self.server.get_player(player_name)
                target = self.server.get_player(target_name)
                if player == None:
                    del self.handler.nameTagCache[player_name]
                if target == None:
                    continue
                sendCustomNameToPlayerForPlayer(target, player.runtime_id, newName)
    
    def on_command(self, sender, command, args):

        if command.name == "debug":
            if not self.isDebug:
                self.logger.set_level(self.logger.DEBUG)
                self.isDebug = True
                sender.send_message(self.plugin_mc_prefix+"§aDebug enabled!")
            else:
                self.isDebug = False
                self.logger.set_level(self.logger.INFO)
                sender.send_message(self.plugin_mc_prefix+"§cDebug disabled!")

        return True