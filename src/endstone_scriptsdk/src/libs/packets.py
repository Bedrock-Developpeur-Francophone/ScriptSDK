from bstream import BinaryStream, ReadOnlyBinaryStream
from bedrock_protocol.packets.packet.packet_base import Packet
from bedrock_protocol.packets.minecraft_packet_ids import MinecraftPacketIds

class SetActorDataPacket(Packet):
    targetRuntimeId: int
    actorData: list
    intProperties: list
    floatProperties: list
    tick: int

    def __init__(self, targetRuntimeId: int = 0, actorData: list = [], intProperties = [], floatProperties = [], tick = 0) -> None:
        super().__init__()
        self.targetRuntimeId = targetRuntimeId
        self.actorData = actorData
        self.intProperties = intProperties
        self.floatProperties = []
        self.tick = tick

    def get_packet_id(self) -> MinecraftPacketIds:
        return MinecraftPacketIds.SetActorData

    def get_packet_name(self) -> str:
        return "SetActorData"

    def write(self, stream: BinaryStream) -> None:
        stream.write_unsigned_varint64(self.targetRuntimeId)
        stream.write_unsigned_varint(len(self.actorData))
        for item in self.actorData:
            stream.write_unsigned_varint(item["id"])
            stream.write_unsigned_varint(item["type"])
            stream.write_unsigned_varint(4)
            self._write_value(stream, item["type"], item["value"])
        
        stream.write_unsigned_varint(len(self.intProperties))
        for prop in self.intProperties:
            stream.write_unsigned_varint(prop["index"])
            stream.write_varint(prop["value"])
        stream.write_unsigned_varint(len(self.floatProperties))
        for prop in self.floatProperties:
            stream.write_unsigned_varint(prop["index"])
            stream.write_float(prop["value"])
        stream.write_unsigned_varint64(self.tick)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.targetRuntimeId = stream.get_unsigned_varint64()
        count = stream.get_unsigned_varint()
        self.actorData = []
        for _ in range(count):
            data_id = stream.get_unsigned_varint()
            data_type = stream.get_unsigned_varint()
            
            value = self._read_value(stream, data_type)
            self.actorData.append({
                "id": data_id,
                "type": data_type,
                "value": value
            })
        self.intProperties = []
        int_count = stream.get_unsigned_varint()
        for _ in range(int_count):
            idx = stream.get_unsigned_varint()
            val = stream.get_varint()
            self.intProperties.append({"index": idx, "value": val})

        self.floatProperties = []
        float_count = stream.get_unsigned_varint()
        for _ in range(float_count):
            idx = stream.get_unsigned_varint()
            val = stream.get_float()
            self.floatProperties.append({"index": idx, "value": val})
        self.tick = stream.get_unsigned_varint64()
    def _read_value(self, stream: ReadOnlyBinaryStream, type_id: int):
        if type_id == 0:   # Byte
            return stream.get_byte()
        elif type_id == 1: # Short
            return stream.get_signed_short()
        elif type_id == 2: # VarInt
            return stream.get_varint()
        elif type_id == 3: # Float
            return stream.get_float()
        elif type_id == 4: # String
            return stream.get_string()
        elif type_id == 5: 
            return stream.get_bytes()  
        elif type_id == 6: 
            x = stream.get_varint()
            y = stream.get_varint()
            z = stream.get_varint()
            return (x, y, z)
        elif type_id == 7: 
            return stream.get_varint64()
        elif type_id == 8: 
            return (
                stream.get_float(),
                stream.get_float(),
                stream.get_float(),
            )
        else:
            return stream.get_left_buffer()


    def _write_value(self, stream: BinaryStream, type_id: int, value):
        if type_id == 0:   
            stream.write_byte(value)
        elif type_id == 1: 
            stream.write_signed_short(value)
        elif type_id == 2: 
            stream.write_varint(value)
        elif type_id == 3: 
            stream.write_float(value)
        elif type_id == 4: 
            stream.write_string(value)
        elif type_id == 5:
            stream.write_bytes(value) 
        elif type_id == 6:
            x, y, z = value
            stream.write_varint(x)
            stream.write_varint(y)
            stream.write_varint(z)
        elif type_id == 7:
            stream.write_varint64(value)
        elif type_id == 8: 
            x, y, z = value
            stream.write_float(x)
            stream.write_float(y)
            stream.write_float(z)
        else:
            if isinstance(value, (bytes, bytearray)):
                stream.write_bytes(value)
            else:
                raise ValueError(f"Unsupported type {type_id} with value {value!r}")
