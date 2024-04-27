import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from math import pi, log, tan

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
    for aeropuerto, (latitud, longitud) in aeropuertos.items():
        # Convertir latitud y longitud a coordenadas de píxeles
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

# Cargar la imagen del mapa del mundo con proyección de Mercator
imagen_original = Image.open("Mercator.jpg")

# Coordenadas de los aeropuertos (ejemplo)
aeropuertos = {
    "DFW": (32.8975, -97.0378),  # Aeropuerto Internacional de Dallas-Fort Worth (EE. UU.)
    "IKT": (52.26800156, 104.3889999),  # Aeropuerto de Irkutsk (Rusia)
    "KHV": (48.52799988, 135.1880035)  # Aeropuerto de Khabarovsk-Novy (Rusia)
}

# Crear la ventana de Tkinter
raiz = tk.Tk()
raiz.title("Flights map")

# Mostrar la imagen en un widget Label
label_imagen = tk.Label(raiz)
label_imagen.pack(fill=tk.BOTH, expand=True)

# Botón para dibujar los aeropuertos en la imagen
boton_dibujar = tk.Button(raiz, text="Dibujar Aeropuertos", command=dibujar_aeropuertos)
boton_dibujar.pack()

# Botón para cerrar la ventana
boton_cerrar = tk.Button(raiz, text="Cerrar", command=cerrar_ventana)
boton_cerrar.pack()

# Ejecutar la aplicación
raiz.mainloop()