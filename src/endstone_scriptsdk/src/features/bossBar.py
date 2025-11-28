from endstone.boss import BarColor, BarStyle
import typing

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler

class BossBar:
    @staticmethod
    def request(handler : "EventHandler", uuid, action, message):
        match action:
            case 'setBossBar':
                '''
                    body: barName;#;color;#;style;#;pourcent;#;playerName
                '''
                result = handler.deserializer(message, 5)
                title = result[1]
                color_code = int(result[2])
                style_code = int(result[3])
                pourcent = int(result[4])
                playerName = result[5]

                player = handler.plugin.server.get_player(playerName)
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);
                
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

                if player in handler.bossBars:
                    handler.bossBars[player].remove_all()
                    del handler.bossBars[player]

                bossBar = handler.plugin.server.create_boss_bar(title, color, style)
                bossBar.progress = pourcent / 100
                bossBar.add_player(player)

                handler.bossBars[player] = bossBar

                return handler.response(uuid, True, 201, ['bossBar created'])
            case 'resetBossBar':
                '''
                    Body : playerName
                '''

                player = handler.plugin.server.get_player(message)
                if not player:
                    return handler.response(uuid, False, 404, ['player not found']);

                if player in handler.bossBars:
                    handler.bossBars[player].remove_all()
                    del handler.bossBars[player]

                return handler.response(uuid, True, 201, ['bossBar deleted'])