import typing
from endstone_scriptsdk.src.libs.MCBEPing import ping_bedrock

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler

class ServerData:
    @staticmethod
    def request(handler : "EventHandler", uuid : str, action, message):
        match action:
            case 'getExternalServerInfo':
                '''
                    Body: ip;#;port
                '''
                result = handler.deserializer(message, 2)
                ip = result[1]
                port = int(result[2])

                ping = ping_bedrock(ip, port)
                
                return handler.response(uuid, True, 200, [str(ping.ping), str(ping.edition), str(ping.gameMode), str(ping.mapName), str(ping.name), str(ping.players.online), str(ping.players.max), str(ping.serverId), str(ping.version)])