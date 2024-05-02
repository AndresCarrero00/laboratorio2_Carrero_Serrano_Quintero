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
    
    # Método para encontrar el camino mínimo utilizando el algoritmo de Dijkstra
    def shortest_path(self, source_code, dest_code):
        # Verificar si los códigos de origen y destino existen
        if source_code not in self.connections or dest_code not in self.connections:
            print(f"Código de aeropuerto no encontrado: {source_code} o {dest_code}")
            return []

        # Diccionario para almacenar la distancia mínima a cada nodo
        distances = {airport: float('inf') for airport in self.connections}
        distances[source_code] = 0

        # Diccionario para almacenar el nodo previo en el camino
        previous = {airport: None for airport in self.connections}

        # Cola de prioridad para seleccionar el nodo con la distancia mínima
        priority_queue = [(0, source_code)]

        while priority_queue:
            # Extraer el nodo con la menor distancia
            current_distance, current_airport = heapq.heappop(priority_queue)

            #edgar
            # Si el nodo actual es el destino, detener el algoritmo
            if current_airport == dest_code:
                break

            # Recorrer las conexiones del aeropuerto actual
            for flight in self.connections[current_airport]:
                neighbor_airport = flight.dest_airport.code
                distance_to_neighbor = current_distance + self.calculate_distance(flight.source_airport, flight.dest_airport)

                # Si se encuentra una distancia menor, actualizar la información
                if distance_to_neighbor < distances[neighbor_airport]:
                    distances[neighbor_airport] = distance_to_neighbor
                    previous[neighbor_airport] = current_airport
                    heapq.heappush(priority_queue, (distance_to_neighbor, neighbor_airport))

        # Reconstruir el camino mínimo desde el destino hasta el origen
        path = []
        current_airport = dest_code
        while current_airport:
            path.append(current_airport)
            current_airport = previous[current_airport]

        path.reverse()  # Invertir el camino para que empiece desde el origen
        return path



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

# Ejemplo de uso
airport_graph = build_airport_graph('flights.csv')
connections_from_DFW = airport_graph.get_connections('DFW')
for connection in connections_from_DFW:
    print("Vuelo desde DFW a", connection.dest_airport.name)
    distance = airport_graph.calculate_distance(connection.source_airport, connection.dest_airport)
    print("Distancia:", distance, "kilómetros")