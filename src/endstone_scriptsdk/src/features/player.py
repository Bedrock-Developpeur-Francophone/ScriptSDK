from endstone import Player
import typing

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler

class PlayerData:
    @staticmethod
    def request(handler : "EventHandler", uuid, action, message):
        match action:
            case 'getPlayerIp':
                '''
                    body: playerName
                '''
                player : Player = handler.plugin.server.get_player(message)
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);
                return handler.response(uuid, True, 200, [player.address.hostname])
            
            case 'getPlayerPing':
                '''
                    Body: playerName
                '''
                player : Player = handler.plugin.server.get_player(message)
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);
                return handler.response(uuid, True, 200, [str(player.ping)])
            
            case 'getPlayerXuid':
                '''
                    Body: playerName
                '''
                player : Player = handler.plugin.server.get_player(message)
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);
                return handler.response(uuid, True, 200, [player.xuid])
            
            case 'getPlayerOS':
                '''
                    Body: playerName
                '''
                player : Player = handler.plugin.server.get_player(message)
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);
                return handler.response(uuid, True, 200, [player.device_os])