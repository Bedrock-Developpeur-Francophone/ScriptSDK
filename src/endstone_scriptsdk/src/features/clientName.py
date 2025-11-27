from endstone_scriptsdk.src.utils import sendCustomNameToPlayerForPlayer
import typing

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler

class ClientName:
    @staticmethod
    def request(handler : "EventHandler", uuid, action, message):
        match action:
            case 'setPlayerNameForPlayer':
                '''
                    Body: targetName;#;playerName;#;newPlayerName
                '''
                result = handler.deserializer(message, 3)
                target = handler.plugin.server.get_player(result[1])
                if not target:
                    return handler.response(uuid, False, 404, ['target not found']);
                player = handler.plugin.server.get_player(result[2])
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);

                if player.name in handler.nameTagCache:
                    handler.nameTagCache[player.name][target.name] = result[3]
                else:
                    handler.nameTagCache[player.name] = {
                        target.name: result[3]
                    }
                
                return handler.response(uuid, True, 200, ['name set'])
            
            case 'resetPlayerNameForPlayer':
                '''
                    Body: targetName;#;playerName
                '''
                result = handler.deserializer(message, 2)
                target = handler.plugin.server.get_player(result[1])
                if not target:
                    return handler.response(uuid, False, 404, ['target not found']);
                player = handler.plugin.server.get_player(result[2])
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);

                if player.name in handler.nameTagCache and target.name in handler.nameTagCache[player.name]:
                    del handler.nameTagCache[player.name][target.name]

                sendCustomNameToPlayerForPlayer(target, player.runtime_id, player.name_tag)
                
                return handler.response(uuid, True, 200, ['name reset'])