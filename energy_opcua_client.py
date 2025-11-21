import asyncio
from time import sleep
# from asyncio import sleep
from asyncua.sync import Client

#URL = "opc.tcp://192.168.3.140:4840/energy/"
URL = "opc.tcp://localhost:4840/energy/"

class Energy:
    def __init__(self, url = URL):
        self.client = Client(url, 50)

        self.namespace = "energy"
        self._is_connected = False

        self.subscription = None
        self.handles = []

        self.nodes_to_monitor = {}
        self.current_values = {}

        self.connect()

    def connect(self):
        if self._is_connected:
            self.control.call_method(f"{self.nsidx}:connect")
        else:
            try:
                self.client.connect()
                print("Client connected")
                self.nsidx = self.client.get_namespace_index(self.namespace)
                self.status = self.client.nodes.root.get_child(
                    ["0:Objects", f"{self.nsidx}:status"]
                )
                objects = self.client.nodes.objects
                children = objects.get_children()
                self.modules = {}
                for child in children:
                    name = child.read_display_name().Text or ""
                    if name.startswith("Modul"):
                        print(f"Found module: {name}")
                        self.modules[name] = child
                self.module_vars = {}
                for module_name, module_node in self.modules.items():
                    children = module_node.get_children()
                    var_map = {}
                    for var_node in children:
                        var_name = var_node.read_display_name().Text
                        var_map[var_name] = var_node
                    self.module_vars[module_name] = var_map

                self.control = self.client.nodes.root.get_child(
                    ["0:Objects", f"{self.nsidx}:control"]
                )
                self.nodes_to_monitor = {
                    
                }

                self.start_subscription()
                self._is_connected = True
            except:
                pass

    def exit(self):
        try:
            if self._is_connected:
                self.client.disconnect()
            self.client.tloop.stop() # type: ignore
            self.stop_subscription()
        except:
            pass

    def start_subscription(self):
        self.subscription = self.client.create_subscription(100, self) #type: ignore
        self.handles = []

        for module_name, varmap in self.module_vars.items():
            for vname, vnode in varmap.items():
                handle = self.subscription.subscribe_data_change(vnode)
                # print(f"Subscribed to {module_name}.{vname}")
                self.handles.append(handle)
        print(f"Subscribed to {len(self.handles)} variables.")
        # print(f"self.module_vars.__len__(): {self.module_vars.__len__()}")
        if (self.module_vars.__len__() * varmap.__len__()) == len(self.handles):
            print("Subscription to all module variables successful.")
        else:
            print("Warning: Number of subscription variables does not match.")

    def stop_subscription(self):
        if self.subscription:
            #self.subscription.unsubscribe(self.handles)
            temp = 0
            for self.handle in self.handles:
                self.subscription.unsubscribe(self.handle)
                # print("Unsubscribed handle:", self.handle)
                temp += 1
            print(f"Unsubscribed {temp} handles.")
            self.handles = []
            if len(self.handles) == 0:
                print("All handles unsubscribed successfully.")
            try:
                self.subscription.delete()
            except:
                pass
            self.subscription = None

    def datachange_notification(self, node, val, data):
        print("")

    def stop(self):
        if self._is_connected:
            self.control.call_method(f"{self.nsidx}:stop")

    def read_module(self, module_name):
        if module_name not in self.module_vars:
            raise ValueError(f"Module '{module_name}' not found")
        values = {}
        for vname, vnode in self.module_vars[module_name].items():
            values[vname] = vnode.get_value()
        return values
    
    def read_all_modules(self):
        all_values = {}
        for module_name in self.modules.keys():
            all_values[module_name] = self.read_module(module_name)
        return all_values
    


    #def  Methode um einzelne Werte zu lesen

async def main():
    while True:
        sleep(10)
        print("Module list:", list(energy.modules.keys()))
        data = energy.read_all_modules()
        for module_name, module_data in data.items():
            print(f"Data for {module_name}:")
            for key, value in module_data.items():
                print(f"{key}: {value}")
        
    client.disconnect()

if __name__ == "__main__":
    energy = Energy()
    asyncio.run(main(), debug=False)
    
