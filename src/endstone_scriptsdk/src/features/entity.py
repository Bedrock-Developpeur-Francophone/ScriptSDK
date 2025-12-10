from endstone_scriptsdk.src.utils import sendCustomNameToPlayerForEntity
import typing

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler

class EntityData:
    @staticmethod
    def request(handler : "EventHandler", uuid, action, message):
        match action:
            case 'setEntityNameForPlayer':
                '''
                    Body: targetName;#;id;#;newPlayerName
                '''
                result = handler.deserializer(message, 3)
                target = handler.plugin.server.get_player(result[1])
                if not target:
                    return handler.response(uuid, False, 404, ['target not found']);

                if result[2] in handler.nameTagCache:
                    handler.nameTagCache[result[2]][target.name] = result[3]
                else:
                    handler.nameTagCache[result[2]] = {
                        target.name: result[3]
                    }
                
                return handler.response(uuid, True, 200, ['name set'])
            
            case 'resetEntityNameForPlayer':
                '''
                    Body: targetName;#;id;#;originalName
                '''
                result = handler.deserializer(message, 3)
                target = handler.plugin.server.get_player(result[1])
                if not target:
                    return handler.response(uuid, False, 404, ['target not found']);

                if result[2] in handler.nameTagCache and target.name in handler.nameTagCache[result[2]]:
                    del handler.nameTagCache[result[2]][target.name]

                for entity in handler.plugin.server.level.actors:
                    if entity.id == int(result[2]):
                        sendCustomNameToPlayerForEntity(target, entity.runtime_id, result[3])
                
                return handler.response(uuid, True, 200, ['name reset'])