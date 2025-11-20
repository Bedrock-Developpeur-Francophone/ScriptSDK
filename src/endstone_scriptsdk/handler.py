from endstone import Player
from endstone.plugin import Plugin
from endstone.event import event_handler, ScriptMessageEvent
from endstone.boss import BossBar, BarFlag, BarColor, BarStyle
from endstone.command import CommandSenderWrapper
from colorama import Fore
import json, re
from endstone_scriptsdk.src.utils import sendCustomNameToPlayerForPlayer

class EventHandler:

    bossBars : dict[Player, BossBar] = {}
    nameTagCache : dict[str, dict[str, str]] = {}

    def __init__(self, plugin : Plugin):
        self.plugin = plugin
        self.logger = plugin.logger
        plugin.register_events(self)
        plugin.logger.info('EventHandler listening...')

    def send_script_event(self, uuid, body):
        sender = CommandSenderWrapper(self.plugin.server.command_sender)
        self.plugin.server.dispatch_command(sender, f'scriptevent scriptsdkresult:{uuid} {body}')
        self.logger.debug(f'Result send ! ({Fore.CYAN}{uuid}{Fore.RED} => {Fore.GREEN}{body}{Fore.RESET})')
    
    def response(self, uuid: str, success: bool, code: int, response: str):
        return self.send_script_event(uuid, f'{"true" if success else "false"};#;{code};#;{response}')

    @event_handler
    def on_script_message(self, event : ScriptMessageEvent):

        message_id = event.message_id
        message = event.message
        parsed_id = message_id.replace('-', ':').split(':')
        if len(parsed_id) == 3 and parsed_id[0] == 'scriptsdk':
            event.cancel()
            uuid = parsed_id[1]
            action = parsed_id[2]
            self.logger.debug(f'Valid message received! ({Fore.CYAN}{uuid}{Fore.RED} -> {Fore.YELLOW}{action}{Fore.RED} => {Fore.GREEN}{message}{Fore.RESET})')

            # --> Result Body : success:boolean;#;code:number;#;result:any
            
            # try:
            match action:
                case 'getIp':
                    '''
                        body: playerName
                    '''
                    player = self.plugin.server.get_player(message)
                    if not player:
                        return self.response(uuid, False, 404, 'player not found');
                    return self.response(uuid, True, 200, player.address.hostname)

                case 'setBossBar':
                    '''
                        body: barName;#;color;#;style;#;pourcent;#;playerName
                    '''
                    result = re.match(r"^(.*);#;(\d);#;(\d);#;(\d{1,3});#;(.*)$", message, re.DOTALL)
                    title = result[1]
                    color_code = int(result[2])
                    style_code = int(result[3])
                    pourcent = int(result[4])
                    playerName = result[5]

                    player = self.plugin.server.get_player(playerName)
                    if not player:
                        return self.response(uuid, False, 404, 'player not found');
                    
                    colors = [
                        BarColor.BLUE,
                        BarColor.GREEN,
                        BarColor.PINK,
                        BarColor.PURPLE,
                        BarColor.REBECCA_PURPLE,
                        BarColor.RED,
                        BarColor.WHITE,
                        BarColor.YELLOW
                    ]

                    styles = [
                        BarStyle.SOLID,
                        BarStyle.SEGMENTED_6,
                        BarStyle.SEGMENTED_10,
                        BarStyle.SEGMENTED_12,
                        BarStyle.SEGMENTED_20
                    ]

                    color = colors[color_code]
                    style = styles[style_code]

                    if player in self.bossBars:
                        self.bossBars[player].remove_all()
                        del self.bossBars[player]

                    bossBar = self.plugin.server.create_boss_bar(title, color, style)
                    bossBar.progress = pourcent / 100
                    bossBar.add_player(player)

                    self.bossBars[player] = bossBar

                    return self.response(uuid, True, 201, 'BossBar created !')
                
                case 'setPlayerNameForPlayer':
                    '''
                        Body: targetName;#;playerName;#;newPlayerName
                    '''
                    result = re.match(r'^(.*);#;(.*);#;(.*)$', message, re.DOTALL)
                    target = self.plugin.server.get_player(result[1])
                    if not target:
                        return self.response(uuid, False, 404, 'target not found');
                    player = self.plugin.server.get_player(result[2])
                    if not player:
                        return self.response(uuid, False, 404, 'player not found');

                    if player.name in self.nameTagCache:
                        self.nameTagCache[player.name][target.name] = result[3]
                    else:
                        self.nameTagCache[player.name] = {
                            target.name: result[3]
                        }
                    
                    return self.response(uuid, True, 200, 'Name set !')
                
                case 'resetPlayerNameForPlayer':
                    '''
                        Body: targetName;#;playerName
                    '''
                    result = re.match(r'^(.*);#;(.*)$', message)
                    target = self.plugin.server.get_player(result[1])
                    if not target:
                        return self.response(uuid, False, 404, 'target not found');
                    player = self.plugin.server.get_player(result[2])
                    if not player:
                        return self.response(uuid, False, 404, 'player not found');

                    if player.name in self.nameTagCache and target.name in self.nameTagCache[player.name]:
                        del self.nameTagCache[player.name][target.name]

                    sendCustomNameToPlayerForPlayer(target, player.runtime_id, player.name_tag)
                    
                    return self.response(uuid, True, 200, 'Name reset !')



            # except Exception as e:
            #     self.response(uuid, False, 500, str(e))