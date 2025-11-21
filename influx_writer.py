from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.domain.write_precision import WritePrecision
#from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime

class InfluxWriter:
    def __init__(self, url, token, org, bucket, device_id):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_precision=WritePrecision.NS)
        self.bucket = bucket
        self.device_id = device_id

    def _extract_phase(self,key):
        #Gibt A/B/C zurück oder None.
        key = key.lower()
        if key.startswith("phase_a"):
            return "A"
        elif key.startswith("phase_b"):
            return "B"
        elif key.startswith("phase_c"):
            return "C"
        return None
    
    def _extract_metric(self,key):
        #Entfernt phase-prefix und gibt metrischen Kern zurück
        clean = (
            key.lower()
                .replace("phase_a_", "")
                .replace("phase_b_", "")
                .replace("phase_c_", "")
        )
        return clean
    
    def write_measurements(self, measurements):
        """
        measurements: Liste von dicts:
          {"name": "...", "value": ..., "type": "..."}
        """
        points = []
        now = datetime.utcnow()

        for m in measurements:
            name = m["name"]
            value = m["value"]
            type = m["type"]
            phase = self._extract_phase(name)
            # print(phase)
            metric = self._extract_metric(name)

            p = (
                Point("shelly3em")                 # Measurement
                .tag("device_id",self.device_id)
                .tag("metric",metric)          # Tag damit man alle Werte gruppiert
                .time(now, WritePrecision.NS)
                .field("value", float(value)) # Feld
            )
            '''
            if type == "float":
                p = p.field("value", float(value))
            elif type == "bool":
                p = p.field("value", bool(value))
            elif type == "uint32":
                p = p.field("value", int(value))
            else:
                # Fallback: alles als float
                p = p.field("value", float(value))
            '''
            if phase:
                p = p.tag("phase", phase)
            # print(p)
            points.append(p)

        self.write_api.write(bucket=self.bucket, record=points)
