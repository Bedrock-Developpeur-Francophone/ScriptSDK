from endstone.event import ActorDamageEvent
from endstone.plugin import Plugin
from endstone import Player
import re

class Rule:
    NO_PVP = 0
    NO_DAMAGE = 1
    PVP_ONLY_GROUP = 3
    NO_PVP_NO_DAMAGE = 4
    NO_PVP_ONLY_GROUP = 5

class Group:
    def __init__(self, name : str, rule : int, plugin : Plugin):
        self.name = name
        self.rule = rule
        self.plugin = plugin
        self.players = []

    def add_player(self, player_name: str):
        self.players.append(player_name)

    def remove_player(self, player_name: str):
        self.players.remove(player_name)

    @staticmethod
    def exist(name: str, groups):
        for g in groups:
            if g.name == name:
                return True
        return False
    
    @staticmethod
    def get(name: str, groups):
        for g in groups:
            if g.name == name:
                return g
        return None

    def handle(self, event : ActorDamageEvent):
        
        victim = event.actor
        damager = event.damage_source.damaging_actor

        if isinstance(victim, Player):
            match self.rule:
                case Rule.NO_PVP:
                    if isinstance(damager, Player) and damager.name in self.players:
                        event.cancel()
                case Rule.NO_DAMAGE:
                    if victim.name in self.players:
                        event.cancel()
                case Rule.NO_PVP_NO_DAMAGE:
                    if victim.name in self.players or (isinstance(damager, Player) and damager.name in self.players):
                        event.cancel()
                case Rule.PVP_ONLY_GROUP:
                    if isinstance(damager, Player) and ((victim.name in self.players and damager.name not in self.players) or (victim.name not in self.players and damager.name in self.players)):
                        event.cancel()
                case Rule.NO_PVP_ONLY_GROUP:
                    if isinstance(damager, Player) and victim.name in self.players and damager.name in self.players:
                        event.cancel()

    @staticmethod
    def request(handler, uuid, action, message):
        match action:
            case 'createGroup':
                '''
                    Body: name;#;rule
                '''
                result = re.match(r'^(.*);#;(\d)$', message)
                name = result[1]
                rule = int(result[2])

                if(Group.exist(name, handler.groups)):
                    return handler.response(uuid, False, 409, ['a group with this name already exists'])

                group = Group(name, rule, handler.plugin)
                handler.groups.append(group)

                return handler.response(uuid, True, 201, ['group created'])
            
            case 'addPlayerToGroup':
                '''
                    Body: groupName;#;playerName
                '''
                result = re.match(r'^(.*);#;(.*)$', message)
                group_name = result[1]
                player_name = result[2]

                group : Group = Group.get(group_name, handler.groups)
                if group is None:
                    return handler.response(uuid, False, 404, ['group not found'])
                
                if player_name not in group.players:
                    group.add_player(player_name)

                return handler.response(uuid, True, 200, ['player added to the group'])
            
            case 'removePlayerToGroup':
                '''
                    Body: groupName;#;playerName
                '''
                result = re.match(r'^(.*);#;(.*)$', message)
                group_name = result[1]
                player_name = result[2]

                group : Group = Group.get(group_name, handler.groups)
                if group is None:
                    return handler.response(uuid, False, 404, ['group not found'])
                
                if player_name in group.players:
                    group.remove_player(player_name)

                return handler.response(uuid, True, 200, ['player removed to the group'])

            case 'deleteGroup':
                '''
                    Body: groupName
                '''
                
                group : Group = Group.get(message, handler.groups)
                if group is None:
                    return self.response(uuid, False, 404, ['group not found'])
                
                handler.groups.remove(group)
                return handler.response(uuid, True, 201, ['group deleted'])