from asyncua import Server, ua
from asyncua.common.methods import uamethod
import asyncio
from energy import Energy
import inspect
from influx_writer import InfluxWriter
from datetime import time

# create connector to energy device/station used by server
#energy_station0 = Energy('192.168.2.120')

# InfluxDB Writer
""" influx = InfluxWriter(
    url="http://localhost:8086",
    token="supersecrettoken",
    org="home",
    bucket="shelly"
)
 """



#
SHELLY_DEVICES = {
    "Modul1": "192.168.2.120",
    "Modul2": "192.168.2.120",
    # "Modul3": "192.168.2.122",
    # "Modul4": "192.168.2.123",
    # "Modul5": "192.168.2.124",
    # "Modul6": "192.168.2.125",
    # "Modul7": "192.168.2.126",
}


energy_stations = {
    name: Energy(ip) 
    for name, ip in SHELLY_DEVICES.items()
}

# Influx Writer für jedes Gerät
influx_writers = {
    device_name: InfluxWriter(
        url="http://localhost:8086",
        token="supersecrettoken",
        org="home",
        bucket="shelly",
        device_id=device_name
    )
    for device_name in SHELLY_DEVICES.keys()
}

@uamethod
def some_method(_, var1, var2):
    print(var1)
    print(var2)
    return 0


async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/energy/")

    uri = "energy"
    idx = await server.register_namespace(uri)

    node_start = None

    status = await server.nodes.objects.add_object(idx, "status")
    control = await server.nodes.objects.add_object(idx, "control")
    #station0 = await server.nodes.objects.add_object(idx, "station0")
    # funktioniert? Fehlt noch etwas?
    global device_var_nodes
    device_var_nodes = {}
    
    for device_name in energy_stations.keys():
        device_obj = await server.nodes.objects.add_object(idx, device_name)
        print(f"Created OPC UA object for energy station: {device_name}")
        device_var_nodes[device_name] = {}
        for register in energy_stations[device_name].REGISTERS:
            var_name = register["name"]
            var_type = register["type"]
            if var_type == "float":
                initial_value = 0.0
            elif var_type == "bool":
                initial_value = False
            elif var_type == "uint32":
                initial_value = 0
            else:
                initial_value = 0
            variable_node = await device_obj.add_variable(idx, var_name, initial_value)
            device_var_nodes[device_name][var_name] = variable_node
            print(f"Created OPC UA variable: {var_name} ({var_type})")

    '''
    for name in energy_station0.REGISTERS:
        i = 0
        initial_value = 0 
        var_name = name["name"]
        type = name["type"]
        #print("read type:", type)
        #print("read variable name:", var_name)
        if type == "float":
            initial_value = 0.0
        elif type == "bool":
            initial_value = False
        elif type == "uint32":
            initial_value = 0
        variable = await station0.add_variable(idx, var_name, initial_value)
        if i == 0:
            node_start = variable
            i += 1
        #print(f"Created OPC UA variable:", variable)
    '''

    async with server:
        print("OPC UA Server started on opc.tcp://0.0.0.0:4840/energy/")
        while True:
            for device_name, station in energy_stations.items():
                data = station.read_all()
                #print(f"Read data from energy station '{device_name}':", data)
                if not data:
                    continue
                try:
                    influx_writers[device_name].write_measurements(data)
                    # influx.write_measurements(data)
                except Exception as e:
                    print(f"Error writing to InfluxDB for device '{device_name}': {e}")
                
                for item in data:
                    name = item.get("name")
                    value = item.get("value")
                    type = item.get("type")
                    if type == "float":
                        value = float(value)
                    elif type == "bool":
                        value = bool(value)
                    else:
                        value = int(value)

                    node = device_var_nodes[device_name].get(name)
                    if node:
                        await node.write_value(value)
                        #if type == "float":
                            # print(f"Updated {device_name}.{name} to {value:.3f}")
                        # else:
                            # print(f"Updated {device_name}.{name} to {value}")
            
            await asyncio.sleep(15)
            print("Server alive and healthy at:")
            '''
            data = energy_station0.read_all()
            print("Read data from energy station:", data)
            if data:
                influx.write_measurements(data)
                for item in data:
                    name = item.get("name")
                    value = item.get("value")
                    type = item.get("type")
                    if type == "float":
                        value = float(value)
                    elif type == "bool":
                        value = bool(value)
                    else:
                        value = int(value)
                    node = await station0.get_child(f"{idx}:{name}")
                    await node.write_value(value)
                    if type == "float":
                        print(f"Updated {name} to {value:.3f}")
                    else:
                        print(f"Updated {name} to {value}")
            '''


if __name__ == "__main__":
    for name, energy_station in energy_stations.items():
        print(f"Connecting to energy station ({energy_station.address})...")
        print("Connected:", energy_station.is_connected)
    asyncio.run(main(), debug=False)

