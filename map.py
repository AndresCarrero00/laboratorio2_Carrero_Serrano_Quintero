import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from math import pi, log, tan
import csv
from Lab2 import Airport, Flight, AirportGraph, build_airport_graph

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

# Función para dibujar los adyacentes y los adyacentes más lejanos desde un aeropuerto de origen
def dibujar_adyacentes_y_lejanos():
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

    # Asegurarnos de obtener los 10 vuelos más lejanos disponibles
    top_10_flights = distances[:10]

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

    # Resaltar los 10 vuelos más lejanos en rojo
    for distancia, vuelo in top_10_flights:
        # Obtener coordenadas de origen y destino
        source_coords = (vuelo.source_airport.latitude, vuelo.source_airport.longitude)
        dest_coords = (vuelo.dest_airport.latitude, vuelo.dest_airport.longitude)

        # Convertir coordenadas a píxeles
        x1, y1 = mercator_projection(*source_coords, image_width, image_height)
        x2, y2 = mercator_projection(*dest_coords, image_width, image_height)

        # Dibujar la línea de vuelo más lejano en rojo
        draw.line([(x1, y1), (x2, y2)], fill="red", width=2)

    # Actualizar la imagen mostrada en el mapa
    actualizar_imagen_con_dibujos(imagen_con_lineas)



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

# Función para calcular y dibujar el camino mínimo
def calcular_camino_minimo():
    # Obtener los códigos de origen y destino
    source_code = entry_source.get().strip().upper()
    dest_code = entry_destino.get().strip().upper()

    # Calcular el camino mínimo
    path = airport_graph.shortest_path(source_code, dest_code)

    # Copiar la imagen original para dibujar el camino mínimo
    imagen_con_camino = imagen_original.copy()
    draw = ImageDraw.Draw(imagen_con_camino)

    # Obtener dimensiones de la imagen
    image_width, image_height = imagen_con_camino.size

    # Dibujar el camino mínimo en la imagen
    for i in range(len(path) - 1):
        # Obtener los aeropuertos en el camino
        source_airport = aeropuertos[path[i]]
        dest_airport = aeropuertos[path[i + 1]]

        # Convertir las coordenadas a píxeles
        x1, y1 = mercator_projection(source_airport.latitude, source_airport.longitude, image_width, image_height)
        x2, y2 = mercator_projection(dest_airport.latitude, dest_airport.longitude, image_width, image_height)

        # Dibujar la línea del camino mínimo en verde
        draw.line([(x1, y1), (x2, y2)], fill="green", width=2)

    # Actualizar la imagen mostrada en el mapa
    actualizar_imagen_con_dibujos(imagen_con_camino)

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
boton_dibujar_adyacentes = tk.Button(frame_botones, text="Dibujar adyacentes y lejanos", command=dibujar_adyacentes_y_lejanos)
boton_dibujar_adyacentes.pack(pady=5)

# Botón para hacer zoom in en la imagen
boton_zoom_in = tk.Button(frame_botones, text="Zoom In", command=zoom_in)
boton_zoom_in.pack(pady=5)

# Botón para hacer zoom out en la imagen
boton_zoom_out = tk.Button(frame_botones, text="Zoom Out", command=zoom_out)
boton_zoom_out.pack(pady=5)

# Botón para dibujar los aeropuertos en la imagen
boton_dibujar = tk.Button(frame_botones, text="Dibujar Aeropuertos", command=dibujar_aeropuertos)
boton_dibujar.pack(pady=5)

# Botón para cerrar la ventana
boton_cerrar = tk.Button(frame_botones, text="Cerrar", command=cerrar_ventana)
boton_cerrar.pack(pady=5)

# Ejecutar la aplicación
raiz.mainloop()
