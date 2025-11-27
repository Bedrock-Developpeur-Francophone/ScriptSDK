from endstone import Player
from endstone.plugin import Plugin
from endstone.event import event_handler, ScriptMessageEvent, ActorDamageEvent
from endstone.boss import BossBar
from endstone.command import CommandSenderWrapper
from colorama import Fore
import typing
from endstone_scriptsdk.src.features.groups import Group
from endstone_scriptsdk.src.features.bossBar import BossBar
from endstone_scriptsdk.src.features.clientName import ClientName
from endstone_scriptsdk.src.features.player import PlayerData

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.scriptsdk import ScriptSDK

class EventHandler:

    bossBars : dict[Player, BossBar] = {}
    groups : list[Group] = []
    nameTagCache : dict[str, dict[str, str]] = {}

    def __init__(self, plugin : "ScriptSDK"):
        self.plugin = plugin
        self.logger = plugin.logger
        plugin.register_events(self)
        plugin.logger.info('EventHandler listening...')

    def send_script_event(self, uuid, body):
        sender = CommandSenderWrapper(self.plugin.server.command_sender)
        self.plugin.server.dispatch_command(sender, f'scriptevent scriptsdkresult:{uuid} {body}')
        self.logger.debug(f'Result send ! ({Fore.CYAN}{uuid}{Fore.RED} => {Fore.GREEN}{body}{Fore.RESET})')
    
    def response(self, uuid: str, success: bool, code: int, response: list[str]):
        return self.send_script_event(uuid, f'{"true" if success else "false"};#;{code};#;{";#;".join(response)}')

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
            try:
                
                Group.request(self, uuid, action, message)
                BossBar.request(self, uuid, action, message)
                ClientName.request(self, uuid, action, message)
                PlayerData.request(self, uuid, action, message)

            except Exception as e:
                self.response(uuid, False, 500, [str(e)])

    @event_handler
    def on_damage(self, event : ActorDamageEvent):
        for g in self.groups:
            g.handle(event)