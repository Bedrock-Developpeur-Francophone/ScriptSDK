from endstone import Player
from endstone_scriptsdk.src.libs.packets import SetActorDataPacket
from bedrock_protocol.packets import MinecraftPacketIds

def sendCustomNameToPlayerForEntity(viewver : Player, target_id : int, name: str):
    packet = SetActorDataPacket(
        int(target_id),
        [{'id': 4, 'type': 4, 'value': name}]
    ).serialize()
    viewver.send_packet(MinecraftPacketIds.SetActorData, packet)