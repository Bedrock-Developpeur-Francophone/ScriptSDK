from endstone import Player
import typing

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler

class PlayerData:
    @staticmethod
    def request(handler : "EventHandler", uuid : str, action : str, message : str):

        if action.startswith('getPlayer'):
            player : Player = handler.plugin.server.get_player(message)
            if not player:
                return handler.response(uuid, False, 404, ['player not found']);
            match action:
                case 'getPlayerIp':
                    return handler.response(uuid, True, 200, [player.address.hostname])
                case 'getPlayerPing':
                    return handler.response(uuid, True, 200, [str(player.ping)])
                case 'getPlayerXuid':
                    return handler.response(uuid, True, 200, [player.xuid])
                case 'getPlayerOS':
                    return handler.response(uuid, True, 200, [player.device_os])
        
        match action:
            case 'sendToast':
                '''
                    Body: playerName;#;title;#;content
                '''
                result = handler.deserializer(message, 3)
                player : Player = handler.plugin.server.get_player(result[1])
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);

                player.send_toast(result[2], result[3])
                return handler.response(uuid, True, 200, [])
            
            case 'sendPopup':
                '''
                    Body: playerName
                '''
                result = handler.deserializer(message, 2)
                player : Player = handler.plugin.server.get_player(result[1])
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);

                player.send_popup(result[2])
                return handler.response(uuid, True, 200, [])