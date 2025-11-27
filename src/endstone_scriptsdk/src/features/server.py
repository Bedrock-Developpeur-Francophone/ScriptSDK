import typing, re
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
                result = re.match(r'^(.*);#;(\d*)', message)
                ip = result[1]
                port = result[2]

                ping = ping_bedrock(ip, port)
                