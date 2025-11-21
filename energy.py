import struct
import time
from pyModbusTCP.client import ModbusClient

class Energy:
    def __init__(self, address: str, port: int = 502):
        """
        Initialize a instance and establish the communication

        :param address: The IP address.
        :type address: str
        :param port: The port for Modbus TCP communication (default is 502).
        :type port: int
        """
        self.address = address
        self.client = ModbusClient(host=address, port=port, timeout=1)
        self.is_connected = self.client.open()

    def connect(self):
        self.client.open()

    def __del__(self):
        """
        Close current TCP connection.

        :return: None
        """
        self.client.close()
    
    def decode_modbus_float(self, registers):
        if len(registers) != 2:
            raise ValueError("Zwei Register erforderlich")
        b = registers[0].to_bytes(2, 'little') + registers[1].to_bytes(2, 'little')
        return struct.unpack('<f', b)[0]

    def decode_modbus_uint32(self, registers):
        if len(registers) != 2:
            raise ValueError("Zwei Register erforderlich")
        b = registers[0].to_bytes(2,'little') + registers[1].to_bytes(2, 'little')
        return struct.unpack('<I',b)[0]
    
    def decode_modbus_bool(self, registers):
        if len(registers) != 1:
            raise ValueError("Ein Register erforderlich")
        return bool(registers[0])
    
    def decode_registers(self, registers, dtype):
        if dtype == "float":
            return self.decode_modbus_float(registers)
        elif dtype == "bool":
            return self.decode_modbus_bool(registers)
        elif dtype == "uint32":
            return self.decode_modbus_uint32(registers)
        else:
            raise ValueError(f"Unbekannter Datentyp: {dtype}")
    
    def read_all(self):
        results = []
        # kleinste und größte Adresse bestimmen
        start = min(r["addr"] for r in self.REGISTERS)
        end = max(r["addr"] + r["len"] - 1 for r in self.REGISTERS)
        count = end - start + 1

        # Blockweise lesen
        regs = self.client.read_input_registers(start, count)
        if not regs:
            return None

        # Werte aus Mapping dekodieren
        for r in self.REGISTERS:
            temp_dict = {}
            offset = r["addr"] - start
            chunk = regs[offset: offset + r["len"]]
            temp_dict = {"name": r["name"]}
            temp_dict["type"] = r["type"]
            temp_dict["value"] = self.decode_registers(chunk, r["type"])
            # results[r["name"]] = self.decode_registers(chunk, r["type"])
            # results[r["name"]] = {
            # "value": self.decode_registers(chunk, r["type"]),
            # "type": r["type"]
            # }
            #print(temp_dict)
            results.append(temp_dict)
        return results    
   

    REGISTERS = [
        {"name": "timestamp_update", "addr": 1000, "type": "uint32", "len":2},
        {"name": "phase_a_meter_error", "addr": 1002, "type": "bool", "len": 1},
        {"name": "phase_b_meter_error", "addr": 1003, "type": "bool", "len": 1},
        {"name": "phase_c_meter_error", "addr": 1004, "type": "bool", "len": 1},
        {"name": "neutral_meter_error", "addr": 1005, "type": "bool", "len": 1},
        {"name": "phase_sequence_error", "addr": 1006, "type": "bool", "len": 1},
        {"name": "neutral_current", "addr": 1007, "type": "float", "len": 2},
        {"name": "neutral_current_mismatch", "addr": 1009, "type": "bool", "len": 1},
        {"name": "neutral_overcurrent_error", "addr": 1010, "type": "bool", "len": 1},
        {"name": "total_current", "addr": 1011, "type": "float", "len": 2},
        {"name": "total_active_power", "addr": 1013, "type": "float", "len": 2},
        {"name": "total_apparent_power", "addr": 1015, "type": "float", "len": 2},
        
        {"name": "phase_a_voltage", "addr": 1020, "type": "float", "len": 2},
        {"name": "phase_a_current", "addr": 1022, "type": "float", "len": 2},
        {"name": "phase_a_active_power", "addr": 1024, "type": "float", "len": 2},
        {"name": "phase_a_apparent_power", "addr": 1026, "type": "float", "len": 2},
        {"name": "phase_a_power_factor", "addr": 1028, "type": "float", "len": 2},
        {"name": "phase_a_overpower_error", "addr": 1030, "type": "bool", "len": 1},
        {"name": "phase_a_overvoltage_error", "addr": 1031, "type": "bool", "len": 1},
        {"name": "phase_a_overcurrent_error", "addr": 1032, "type": "bool", "len": 1},
        {"name": "phase_a_frequency", "addr": 1033, "type": "float", "len": 2},

        {"name": "phase_b_voltage", "addr": 1040, "type": "float", "len": 2},
        {"name": "phase_b_current", "addr": 1042, "type": "float", "len": 2},
        {"name": "phase_b_active_power", "addr": 1044, "type": "float", "len": 2},
        {"name": "phase_b_apparent_power", "addr": 1046, "type": "float", "len": 2},
        {"name": "phase_b_power_factor", "addr": 1048, "type": "float", "len": 2},
        {"name": "phase_b_overpower_error", "addr": 1050, "type": "bool", "len": 1},
        {"name": "phase_b_overvoltage_error", "addr": 1051, "type": "bool", "len": 1},
        {"name": "phase_b_overcurrent_error", "addr": 1052, "type": "bool", "len": 1},
        {"name": "phase_b_frequency", "addr": 1053, "type": "float", "len": 2},
        
        {"name": "phase_c_voltage", "addr": 1060, "type": "float", "len": 2},
        {"name": "phase_c_current", "addr": 1062, "type": "float", "len": 2},
        {"name": "phase_c_active_power", "addr": 1064, "type": "float", "len": 2},
        {"name": "phase_c_apparent_power", "addr": 1066, "type": "float", "len": 2},
        {"name": "phase_c_power_factor", "addr": 1068, "type": "float", "len": 2},
        {"name": "phase_c_overpower_error", "addr": 1070, "type": "bool", "len": 1},
        {"name": "phase_c_overvoltage_error", "addr": 1071, "type": "bool", "len": 1},
        {"name": "phase_c_overcurrent_error", "addr": 1072, "type": "bool", "len": 1},
        {"name": "phase_c_frequency", "addr": 1073, "type": "float", "len": 2}
    ]

if __name__ == "__main__":
    energy = Energy('192.168.2.120')
    x = energy.read_all()
    #print(x)
    for item in x:
        name = item.get("name")
        value = item.get("value")
        type = item.get("type")
        print(f'{name} ({type}): {value:.3f}' if type == "float" else f'{name} ({type}): {value}')    
#    for name in x:
#       print(f"{name} ({type}): {value}")
    #for name, value in x.items():
     #   print(f"{name}: {value}")
    #print(f"Spannung: {v:.3f} V")





