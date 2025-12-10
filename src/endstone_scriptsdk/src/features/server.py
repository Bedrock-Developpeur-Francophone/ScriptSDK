import threading, typing
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

                def ping():
                    try:
                        ping = ping_bedrock(ip, port)
                        handler.plugin.server.scheduler.run_task(handler.plugin, lambda: handler.response(uuid, True, 200, [str(ping.ping), str(ping.edition), str(ping.gameMode), str(ping.mapName), str(ping.name), str(ping.players.online), str(ping.players.max), str(ping.serverId), str(ping.version.minecraftVersion)]))
                    except Exception as e:
                        err_msg = str(e)
                        handler.plugin.server.scheduler.run_task(
                            handler.plugin,
                            lambda msg=err_msg: handler.response(uuid, False, 500, [msg])
                        )
                
                threading.Thread(target=ping).start()
                return None