import csv
from math import radians, sin, cos, sqrt, atan2
import heapq

class Airport:
    def __init__(self, code, name, city, country, latitude, longitude):
        self.code = code
        self.name = name
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

class Flight:
    def __init__(self, source_airport, dest_airport):
        self.source_airport = source_airport
        self.dest_airport = dest_airport

class AirportGraph:
    def __init__(self):
        self.connections = {}

    def add_flight(self, flight):
        source_code = flight.source_airport.code
        if source_code not in self.connections:
            self.connections[source_code] = []
        self.connections[source_code].append(flight)

    def get_connections(self, airport_code):
        return self.connections.get(airport_code, [])

    def calculate_distance(self, airport1, airport2):
        lat1, lon1 = airport1.latitude, airport1.longitude
        lat2, lon2 = airport2.latitude, airport2.longitude
        distance = self.haversine_distance(lat1, lon1, lat2, lon2)
        return distance

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        # Convertir grados decimales a radianes
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Diferencia de latitud y longitud
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de la haversine
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c  # Radio de la Tierra en km

        return distance
    

# Cargar los vuelos desde el archivo CSV y construir el grafo
def build_airport_graph(csv_filename):
    airport_graph = AirportGraph()

    with open(csv_filename, 'r', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)  # Saltar la fila de encabezados

        for fila in lector_csv:
            try:
                source_airport = Airport(fila[0], fila[1], fila[2], fila[3], float(fila[4]), float(fila[5]))
                dest_airport = Airport(fila[6], fila[7], fila[8], fila[9], float(fila[10]), float(fila[11]))
                flight = Flight(source_airport, dest_airport)
                airport_graph.add_flight(flight)
            except ValueError as e:
                print(f"Error al procesar la fila {fila}: {e}")

    return airport_graph


