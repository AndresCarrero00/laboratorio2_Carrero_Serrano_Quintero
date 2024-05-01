import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from math import pi, log, tan
import time
import csv
from Lab2 import Airport, Flight, AirportGraph, build_airport_graph

# Cargar la imagen del mapa del mundo con proyección de Mercator
imagen_original = Image.open("Mercator.jpg")

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

# Función para dibujar los aeropuertos en la imagen
def dibujar_aeropuertos():
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
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="red")  # Ajustar tamaño del punto

    # Redimensionar la imagen para adaptarla al tamaño de la ventana
    imagen_con_aeropuertos_resized = imagen_con_aeropuertos.resize((raiz.winfo_width(), raiz.winfo_height()))

    imagen_tk = ImageTk.PhotoImage(imagen_con_aeropuertos_resized)
    label_imagen.configure(image=imagen_tk)
    label_imagen.image = imagen_tk  # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura

# Función de proyección de Mercator
def mercator_projection(latitude, longitude, image_width, image_height):
    # Convertir latitud y longitud a radianes
    lat_rad = latitude * (pi / 180)
    lon_rad = longitude * (pi / 180)

    # Escalar las coordenadas de latitud y longitud en función del tamaño de la imagen
    x = (image_width / 2) + (image_width / (2 * pi)) * lon_rad
    y = (image_height / 2) - (image_width / (2 * pi)) * log(tan((pi / 4) + (lat_rad / 2)))

    return int(x), int(y)

# Función para dibujar los vuelos que salen del aeropuerto de origen ingresado
def dibujar_vuelos_desde_origen():
    # Obtener el código de origen ingresado por el usuario
    source_code = entry_source.get().strip().upper()

    # Verificar si el código de aeropuerto existe en el diccionario
    if source_code not in aeropuertos:
        print(f"El código de aeropuerto {source_code} no existe.")
        return

    # Copiar la imagen original para dibujar las líneas de vuelo
    imagen_con_lineas = imagen_original.copy()
    draw = ImageDraw.Draw(imagen_con_lineas)

    # Obtener el aeropuerto de origen
    source_airport = aeropuertos[source_code]

    # Inicializar variables para el vuelo más lejano
    vuelo_mas_lejano = None
    max_distancia = 0

    # Obtener dimensiones de la imagen
    image_width, image_height = imagen_con_lineas.size

    # Iterar sobre los vuelos que salen del aeropuerto de origen
    for vuelo in vuelos:
        if vuelo.source_airport.code == source_code:
            # Obtener coordenadas de destino
            dest_coords = (vuelo.dest_airport.latitude, vuelo.dest_airport.longitude)
            dest_airport = vuelo.dest_airport

            # Convertir coordenadas de origen y destino a píxeles
            x1, y1 = mercator_projection(source_airport.latitude, source_airport.longitude, image_width, image_height)
            x2, y2 = mercator_projection(dest_coords[0], dest_coords[1], image_width, image_height)

            # Calcular la distancia entre los aeropuertos
            distancia = airport_graph.calculate_distance(source_airport, dest_airport)

            # Dibujar la línea de vuelo
            if distancia > max_distancia:
                # Si este es el vuelo más lejano, resáltalo y actualiza max_distancia
                vuelo_mas_lejano = vuelo
                max_distancia = distancia
                # Dibuja el vuelo más lejano en rojo
                draw.line([(x1, y1), (x2, y2)], fill="red", width=2)
            else:
                # Dibuja los otros vuelos en azul
                draw.line([(x1, y1), (x2, y2)], fill="blue", width=1)

    # Redimensionar la imagen para adaptarla al tamaño de la ventana
    imagen_con_lineas_resized = imagen_con_lineas.resize((raiz.winfo_width(), raiz.winfo_height()))
    imagen_tk = ImageTk.PhotoImage(imagen_con_lineas_resized)
    label_imagen.configure(image=imagen_tk)
    label_imagen.image = imagen_tk  # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura

# Crear la ventana de Tkinter
raiz = tk.Tk()
raiz.title("Flights map")

# Mostrar la imagen en un widget Label
label_imagen = tk.Label(raiz)
label_imagen.grid(row=0, column=0, sticky="nsew")

# Crear un marco para los botones y colocarlo en el lado derecho
frame_botones = tk.Frame(raiz)
frame_botones.grid(row=0, column=1, sticky="ns")

# Configurar las filas y columnas para que se expandan adecuadamente
raiz.columnconfigure(0, weight=1)
raiz.rowconfigure(0, weight=1)

# Crear campos de texto para los códigos de aeropuerto de origen
label_source = tk.Label(frame_botones, text="Source Code:")
label_source.pack(pady=5)
entry_source = tk.Entry(frame_botones)
entry_source.pack(pady=5)

# Botón para dibujar los vuelos que salen del aeropuerto de origen ingresado
boton_dibujar_vuelos = tk.Button(frame_botones, text="Dibujar vuelos desde origen", command=dibujar_vuelos_desde_origen)
boton_dibujar_vuelos.pack(pady=5)

# Botón para dibujar los aeropuertos en la imagen
boton_dibujar = tk.Button(frame_botones, text="Dibujar Aeropuertos", command=dibujar_aeropuertos)
boton_dibujar.pack(pady=5)


# Botón para cerrar la ventana
boton_cerrar = tk.Button(frame_botones, text="Cerrar", command=cerrar_ventana)
boton_cerrar.pack(pady=5)

# Ejecutar la aplicación
raiz.mainloop()
