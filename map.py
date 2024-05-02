import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from math import pi, log, tan
import csv
from Lab2 import Airport, Flight, AirportGraph, build_airport_graph
import heapq

# Cargar la imagen del mapa del mundo con proyección de Mercator
imagen_original = Image.open("Mercator.jpg")

# Escala inicial de la imagen (sin zoom)
zoom_scale = 1.0

# Posición inicial de la imagen
image_x, image_y = 0, 0

# Cargar los aeropuertos y vuelos desde el archivo CSV
ruta_csv = "flights.csv"
airport_graph = build_airport_graph(ruta_csv)

# Obtener los diccionarios de aeropuertos y vuelos desde el grafo de aeropuertos
aeropuertos = {}
vuelos = []

for airport_code, connections in airport_graph.connections.items():
    for flight in connections:
        # Obtener los aeropuertos de origen y destino
        aeropuertos[flight.source_airport.code] = flight.source_airport
        aeropuertos[flight.dest_airport.code] = flight.dest_airport
        # Agregar vuelo a la lista de vuelos
        vuelos.append(flight)

# Función para cerrar la ventana
def cerrar_ventana():
    raiz.destroy()

# Función para hacer zoom in en la imagen
def zoom_in():
    global zoom_scale
    zoom_scale *= 1.2  # Aumentar la escala un 20%
    actualizar_imagen()

# Función para hacer zoom out en la imagen
def zoom_out():
    global zoom_scale
    zoom_scale /= 1.2  # Disminuir la escala un 20%
    actualizar_imagen()

# Función para actualizar la imagen mostrada en el mapa
def actualizar_imagen():
    # Redimensionar la imagen según la escala actual
    new_width = int(imagen_original.width * zoom_scale)
    new_height = int(imagen_original.height * zoom_scale)
    
    # Usar Image.Resampling.LANCZOS para el redimensionamiento de alta calidad
    imagen_redimensionada = imagen_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Convertir la imagen a formato PhotoImage
    imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
    
    # Actualizar el widget Label con la nueva imagen
    label_imagen.configure(image=imagen_tk)
    # Ajustar la posición de la imagen
    label_imagen.place(x=image_x, y=image_y, width=new_width, height=new_height)
    # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura
    label_imagen.image = imagen_tk

# Función para dibujar los aeropuertos en la imagen
def dibujar_aeropuertos():
    # Copiar la imagen original para dibujar los puntos de los aeropuertos
    imagen_con_aeropuertos = imagen_original.copy()
    draw = ImageDraw.Draw(imagen_con_aeropuertos)

    # Obtener dimensiones de la imagen
    image_width, image_height = imagen_con_aeropuertos.size

    # Dibujar cada aeropuerto como un punto rojo en la imagen
    for airport_code, airport in aeropuertos.items():
        # Convertir latitud y longitud a coordenadas de píxeles
        latitud, longitud = airport.latitude, airport.longitude
        x, y = mercator_projection(latitud, longitud, image_width, image_height)
        # Ajustar el tamaño del punto en función del tamaño de la imagen
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="red")

    # Actualizar la imagen mostrada en el mapa
    actualizar_imagen_con_dibujos(imagen_con_aeropuertos)

# Función de proyección de Mercator
def mercator_projection(latitude, longitude, image_width, image_height):
    # Convertir latitud y longitud a radianes
    lat_rad = latitude * (pi / 180)
    lon_rad = longitude * (pi / 180)

    # Escalar las coordenadas de latitud y longitud en función del tamaño de la imagen
    x = (image_width / 2) + (image_width / (2 * pi)) * lon_rad
    y = (image_height / 2) - (image_width / (2 * pi)) * log(tan((pi / 4) + (lat_rad / 2)))

    return int(x), int(y)

def mostrar_10_caminos_minimos_mas_lejanos():
    # Obtener el código de aeropuerto de origen ingresado por el usuario
    source_code = entry_source.get().strip().upper()
    
    # Verificar si el código de aeropuerto de origen es válido
    if source_code not in aeropuertos:
        print(f"El código de aeropuerto {source_code} no existe.")
        return

    # Inicializar diccionarios para almacenar distancias y predecesores
    distancias = {airport: float('inf') for airport in aeropuertos}
    predecesores = {airport: None for airport in aeropuertos}
    
    # Inicializar la distancia del aeropuerto de origen como 0
    distancias[source_code] = 0
    
    # Crear una cola de prioridad para almacenar las distancias y los aeropuertos
    pq = [(0, source_code)]
    
    # Ejecutar el algoritmo de Dijkstra para calcular las distancias mínimas
    while pq:
        # Obtener el aeropuerto con la menor distancia
        distancia_actual, aeropuerto_actual = heapq.heappop(pq)
        
        # Recorrer los vuelos desde el aeropuerto actual
        for flight in airport_graph.get_connections(aeropuerto_actual):
            # Calcular la nueva distancia al aeropuerto de destino
            nueva_distancia = distancia_actual + airport_graph.calculate_distance(flight.source_airport, flight.dest_airport)
            
            # Si la nueva distancia es menor, actualiza la distancia y el predecesor
            if nueva_distancia < distancias[flight.dest_airport.code]:
                distancias[flight.dest_airport.code] = nueva_distancia
                predecesores[flight.dest_airport.code] = aeropuerto_actual
                # Añadir la nueva distancia y aeropuerto de destino a la cola de prioridad
                heapq.heappush(pq, (nueva_distancia, flight.dest_airport.code))
    
    # Crear una lista de distancias junto con los códigos de aeropuerto
    distancias_con_codigo = [(distancia, codigo) for codigo, distancia in distancias.items()]
    
    # Ordenar la lista por distancia descendente para obtener los caminos más lejanos
    distancias_con_codigo.sort(reverse=True, key=lambda x: x[0])
    
    # Seleccionar los 10 caminos más lejanos
    caminos_mas_lejanos = distancias_con_codigo[:10]
    
    # Mostrar los caminos más lejanos en la consola
    print(f"Los 10 caminos mínimos más lejanos desde {source_code} son:")
    for i, (distancia, codigo_destino) in enumerate(caminos_mas_lejanos, start=1):
        # Reconstruir el camino mínimo desde el origen hasta el destino
        camino_minimo = []
        aeropuerto_actual = codigo_destino
        while aeropuerto_actual:
            camino_minimo.append(aeropuerto_actual)
            aeropuerto_actual = predecesores[aeropuerto_actual]
        
        # Invertir el camino mínimo para obtener el camino de origen a destino
        camino_minimo.reverse()
        
        # Mostrar el camino mínimo y la distancia
        print(f"{i}. Camino a {codigo_destino} (distancia: {distancia:.2f} km): {camino_minimo}")
        
        # Dibujar el camino mínimo en el mapa
        dibujar_camino_minimo(camino_minimo)


# Función para dibujar los adyacentes y los adyacentes más lejanos desde un aeropuerto de origen
def dibujar_adyacentes():
    # Obtener el código de origen ingresado por el usuario
    source_code = entry_source.get().strip().upper()

    # Limpiar la lista de aeropuertos adyacentes
    lista_adyacentes.delete(0, tk.END)

    # Verificar si el código de aeropuerto existe en el diccionario
    if source_code not in aeropuertos:
        print(f"El código de aeropuerto {source_code} no existe.")
        return

    # Copiar la imagen original para dibujar las líneas de vuelo
    imagen_con_lineas = imagen_original.copy()
    draw = ImageDraw.Draw(imagen_con_lineas)

    # Obtener dimensiones de la imagen
    image_width, image_height = imagen_con_lineas.size

    # Obtener los vuelos que salen desde el aeropuerto de origen
    flights_from_source = airport_graph.get_connections(source_code)

    # Crear un conjunto para almacenar los destinos únicos y una lista para distancias
    destinos_unicos = set()
    distances = []

    # Iterar sobre los vuelos que salen desde el aeropuerto de origen
    for flight in flights_from_source:
        # Calcular la distancia entre los aeropuertos de origen y destino
        distancia = airport_graph.calculate_distance(flight.source_airport, flight.dest_airport)
        
        # Si el destino no está en el conjunto de destinos únicos, añádelo
        if flight.dest_airport.code not in destinos_unicos:
            destinos_unicos.add(flight.dest_airport.code)
            # Almacenar la distancia junto con el vuelo correspondiente
            distances.append((distancia, flight))

    # Ordenar los vuelos por distancia descendente
    distances.sort(reverse=True, key=lambda x: x[0])

    # Dibujar todos los vuelos adyacentes en azul
    for distancia, vuelo in distances:
        # Obtener coordenadas de origen y destino
        source_coords = (vuelo.source_airport.latitude, vuelo.source_airport.longitude)
        dest_coords = (vuelo.dest_airport.latitude, vuelo.dest_airport.longitude)

        # Convertir coordenadas a píxeles
        x1, y1 = mercator_projection(*source_coords, image_width, image_height)
        x2, y2 = mercator_projection(*dest_coords, image_width, image_height)

        # Dibujar la línea de vuelo en azul
        draw.line([(x1, y1), (x2, y2)], fill="blue", width=1)

        # Añadir el aeropuerto adyacente a la lista
        lista_adyacentes.insert(tk.END, f"Destino: {vuelo.dest_airport.code} Distancia: {distancia:.2f} km")

    # Actualizar la imagen mostrada en el mapa
    actualizar_imagen_con_dibujos(imagen_con_lineas)

def dibujar_camino_minimo(camino_minimo):
    # Copiar la imagen original para dibujar el camino mínimo
    imagen_con_camino = imagen_original.copy()
    draw = ImageDraw.Draw(imagen_con_camino)

    # Obtener dimensiones de la imagen
    image_width, image_height = imagen_con_camino.size

    # Iterar sobre los aeropuertos en el camino mínimo
    for i in range(len(camino_minimo) - 1):
        # Obtener el código de los aeropuertos actual y siguiente
        airport_code_actual = camino_minimo[i]
        airport_code_siguiente = camino_minimo[i + 1]
        
        # Obtener los aeropuertos a partir de los códigos
        aeropuerto_actual = aeropuertos[airport_code_actual]
        aeropuerto_siguiente = aeropuertos[airport_code_siguiente]
        
        # Convertir coordenadas a píxeles
        x1, y1 = mercator_projection(aeropuerto_actual.latitude, aeropuerto_actual.longitude, image_width, image_height)
        x2, y2 = mercator_projection(aeropuerto_siguiente.latitude, aeropuerto_siguiente.longitude, image_width, image_height)

        # Dibujar la línea verde que conecta los aeropuertos
        draw.line([(x1, y1), (x2, y2)], fill="purple", width=2)

    # Actualizar la imagen mostrada en el mapa con los dibujos del camino mínimo
    actualizar_imagen_con_dibujos(imagen_con_camino)


# Función para actualizar la imagen mostrada en el mapa con dibujos adicionales
def actualizar_imagen_con_dibujos(imagen_con_dibujos):
    # Redimensionar la imagen según la escala actual
    new_width = int(imagen_con_dibujos.width * zoom_scale)
    new_height = int(imagen_con_dibujos.height * zoom_scale)
    # Usar Image.Resampling.LANCZOS para el redimensionamiento de alta calidad
    imagen_redimensionada = imagen_con_dibujos.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convertir la imagen a formato PhotoImage
    imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)

    # Actualizar el widget Label con la nueva imagen
    label_imagen.configure(image=imagen_tk)
    # Ajustar la posición de la imagen
    label_imagen.place(x=image_x, y=image_y, width=new_width, height=new_height)
    # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura
    label_imagen.image = imagen_tk

# Funciones para manejar el desplazamiento del mouse
def start_pan(event):
    global prev_x, prev_y
    prev_x, prev_y = event.x, event.y

def pan_image(event):
    global image_x, image_y, prev_x, prev_y
    # Calcular el desplazamiento del mouse
    delta_x = event.x - prev_x
    delta_y = event.y - prev_y
    # Actualizar la posición de la imagen
    image_x += delta_x
    image_y += delta_y
    # Actualizar la imagen mostrada
    actualizar_imagen()
    # Actualizar la posición del mouse
    prev_x, prev_y = event.x, event.y

def calcular_camino_minimo():
    # Obtener los códigos de aeropuerto de origen y destino ingresados por el usuario
    source_code = entry_source.get().strip().upper()
    dest_code = entry_destino.get().strip().upper()
    
    # Verificar si los códigos de los aeropuertos son válidos
    if source_code not in aeropuertos or dest_code not in aeropuertos:
        print("Los códigos de aeropuerto ingresados no son válidos.")
        return
    
    # Inicializar diccionarios para almacenar distancias y predecesores
    distancias = {airport: float('inf') for airport in aeropuertos}
    predecesores = {airport: None for airport in aeropuertos}
    
    # Inicializar la distancia del aeropuerto de origen como 0
    distancias[source_code] = 0
    
    # Crear una cola de prioridad para almacenar las distancias y los aeropuertos
    pq = [(0, source_code)]
    
    # Ejecutar el algoritmo de Dijkstra
    while pq:
        # Obtener el aeropuerto con la menor distancia
        distancia_actual, aeropuerto_actual = heapq.heappop(pq)
        
        # Verificar si el aeropuerto actual es el destino
        if aeropuerto_actual == dest_code:
            break
        
        # Recorrer los vuelos desde el aeropuerto actual
        for flight in airport_graph.get_connections(aeropuerto_actual):
            # Calcular la nueva distancia al aeropuerto de destino
            nueva_distancia = distancia_actual + airport_graph.calculate_distance(flight.source_airport, flight.dest_airport)
            
            # Si la nueva distancia es menor, actualiza la distancia y el predecesor
            if nueva_distancia < distancias[flight.dest_airport.code]:
                distancias[flight.dest_airport.code] = nueva_distancia
                predecesores[flight.dest_airport.code] = aeropuerto_actual
                # Añadir la nueva distancia y aeropuerto de destino a la cola de prioridad
                heapq.heappush(pq, (nueva_distancia, flight.dest_airport.code))
    
    # Reconstruir el camino mínimo desde el destino hasta el origen
    camino_minimo = []
    aeropuerto_actual = dest_code
    while aeropuerto_actual:
        camino_minimo.append(aeropuerto_actual)
        aeropuerto_actual = predecesores[aeropuerto_actual]
    
    # Invertir el camino mínimo para obtener el camino de origen a destino
    camino_minimo.reverse()
    
    print(f"Camino mínimo desde {source_code} hasta {dest_code}:")
    for i, airport in enumerate(camino_minimo):
        print(f"{i + 1}. {airport}")
    
    # Llamar a dibujar_camino_minimo para dibujar el camino en el mapa
    dibujar_camino_minimo(camino_minimo)


# Crear la ventana de Tkinter
raiz = tk.Tk()
raiz.title("Flights map")

# Mostrar la imagen en un widget Label
label_imagen = tk.Label(raiz)
label_imagen.grid(row=0, column=0, sticky="nsew")

# Configurar las filas y columnas para que se expandan adecuadamente
raiz.columnconfigure(0, weight=1)
raiz.rowconfigure(0, weight=1)

# Asignar funciones de manejo de eventos de mouse a la imagen
label_imagen.bind("<ButtonPress-1>", start_pan)
label_imagen.bind("<B1-Motion>", pan_image)

# Crear un marco para los botones y colocarlo en el lado derecho
frame_botones = tk.Frame(raiz)
frame_botones.grid(row=0, column=1, sticky="ns")

# Crear campos de texto para los códigos de aeropuerto de origen
label_source = tk.Label(frame_botones, text="Source Code:")
label_source.pack(pady=5)
entry_source = tk.Entry(frame_botones)
entry_source.pack(pady=5)

label_destino = tk.Label(frame_botones, text="Destination Code:")
label_destino.pack(pady=5)
entry_destino = tk.Entry(frame_botones)
entry_destino.pack(pady=5)

# Crear un botón para calcular el camino mínimo desde el origen hasta el destino
boton_camino_minimo = tk.Button(frame_botones, text="Calcular Camino Mínimo", command=calcular_camino_minimo)
boton_camino_minimo.pack(pady=5)


# Crear una lista para mostrar los aeropuertos adyacentes
label_adyacentes = tk.Label(frame_botones, text="Aeropuertos adyacentes:")
label_adyacentes.pack(pady=5)
lista_adyacentes = tk.Listbox(frame_botones, width=40)
lista_adyacentes.pack(pady=5)

# Botón para dibujar los vuelos adyacentes y resaltar los 10 más lejanos
boton_dibujar_adyacentes = tk.Button(frame_botones, text="Dibujar adyacentes", command=dibujar_adyacentes)
boton_dibujar_adyacentes.pack(pady=5)

# Botón para dibujar los aeropuertos en la imagen
boton_dibujar = tk.Button(frame_botones, text="Dibujar Aeropuertos", command=dibujar_aeropuertos)
boton_dibujar.pack(pady=5)

# Botón para mostrar los 10 caminos mínimos más lejanos
boton_10_caminos_minimos_mas_lejanos = tk.Button(frame_botones, text="Mostrar 10 caminos más lejanos", command=mostrar_10_caminos_minimos_mas_lejanos)
boton_10_caminos_minimos_mas_lejanos.pack(pady=5)

# Botón para hacer zoom in en la imagen
boton_zoom_in = tk.Button(frame_botones, text="Zoom In", command=zoom_in)
boton_zoom_in.pack(pady=5)

# Botón para hacer zoom out en la imagen
boton_zoom_out = tk.Button(frame_botones, text="Zoom Out", command=zoom_out)
boton_zoom_out.pack(pady=5)

# Botón para cerrar la ventana
boton_cerrar = tk.Button(frame_botones, text="Cerrar", command=cerrar_ventana)
boton_cerrar.pack(pady=5)

# Ejecutar la aplicación
raiz.mainloop()
