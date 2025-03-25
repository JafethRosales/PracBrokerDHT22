import machine
import dht
import ssd1306
import utime
import framebuf
import logo
import ds1307
import os
import sdcard
import network
import ubinascii
import WiFiList
from umqtt.simple import MQTTClient
from machine import PWM, Pin
#MODIFICAR HORA Y FECHA
#import ds1307, machine
#i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
#rtc = ds1307.DS1307(i2c)





#Configurar led
led = machine.Pin(2, machine.Pin.OUT) #Led integrado, está en el GPIO 2

# Definir los pines PWM con la nueva configuración
pin_rojo = PWM(Pin(12), freq=1000)  
pin_verde = PWM(Pin(14), freq=1000)  
pin_azul = PWM(Pin(27), freq=1000)  

# Configuración del sensor DHT22
dht_pin = machine.Pin(4)
sensor = dht.DHT22(dht_pin)

# Configuración de la pantalla OLED (I2C en GPIO 21 y 22)
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
# Verificar si el OLED está detectado
devices = i2c.scan()
if 0x3C not in devices:
    print("Error: Pantalla OLED no detectada en el bus I2C")
else:
    print("Pantalla OLED detectada correctamente.")
# Inicializar OLED (128x64)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Cargar imagen del archivo "logo"
fb = framebuf.FrameBuffer(logo.logo, 128, 64, framebuf.MONO_HLSB)

# Inicialización del RTC DS1307
rtc = ds1307.DS1307(i2c)

# Inicialización de la microSD con la librería corregida
spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(18), mosi=machine.Pin(23), miso=machine.Pin(19))
cs = machine.Pin(5, machine.Pin.OUT) # Chip select
#Configuración sd
sd_montada = False
sd = sdcard.SDCard(spi, cs)
try:
    sd = sdcard.SDCard(spi,cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    sd_montada = True
    print("SD montada correctamente en '/SD'")
except Exception as e:
    print("Error de SD, usando memoria interna: ", e)
    try:
        os.mkdir("/sd")
        print("Directorio '/sd' creado")
    except OSError as oe:
        if oe.args[0] == 17:
            print("Directorio '/sd' ya existe, continunando...")
        else:
            raise oe

# Configuración MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "data/temp"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode()
MQTT_PORT = 1883





# Función para controlar los colores (valores entre 0 y 1023)
def set_color(r, g, b):
    pin_rojo.duty(1023 - r)  # Invertimos para LED ánodo común
    pin_verde.duty(1023 - g)
    pin_azul.duty(1023 - b)
    
#Función para cambiar el color según %humedad    
def hum_color(hum):
    if hum < 40:
        set_color(900, 500, 200) 
    elif (hum >=40 and hum <=70):
        set_color(200, 1023, 100)
    else:
        set_color(900, 0, 1023)
        
# Función para obtener datos del sensor DHT22
def obtener_temperatura():
    sensor.measure()
    temp = sensor.temperature()  # °C
    hum = sensor.humidity()  # %
    return temp, hum
    
# Función para mostrar la temperatura, humedad y el emoji de estado
def mostrar_emoji(temp, hum):
    oled.fill(0)  # Borra la pantalla antes de escribir texto
    oled.text("Temp: {:.1f}C".format(temp), 0, 0)
    oled.text("Hum: {:.1f}%".format(hum), 0, 10)
    # Mostrar un estado en función de la temperatura
    if temp < 15:
        oled.text("FRIO [*]", 30, 30)  # Frío 
    elif temp >= 15 and temp <= 30:
        oled.text("NORMAL :)", 30, 30)  # Normal 
    else:
        oled.text("CALOR [!]", 30, 30)  # Calor
    # Mostrar un estado en función de la humedad  
    if hum < 40:
         oled.text("Seco (T-T;)", 20, 40)  
    elif (hum >=40 and hum <=70):
         oled.text("Normal (^-^')", 20, 40)  
    else:
         oled.text("Mojao ('e_e)", 20, 40)  
    #Mostrar en la pantalla
    oled.show()
        
#Función para mostrar la imagen del buffer
def mostrar_imagen():
    oled.fill(0)
    oled.blit(fb, 0, 0)
    oled.show()

# Función para registrar datos
def registrar_datos(temp, hum, fecha, hora):
    try:
        # Guardar en la microSD
        with open("/sd/datalog.csv", "a") as f:
            f.write(f"{fecha}, {hora}, {temp:.1f}, {hum:.1f}\n")
        # Leer y mostrar contenido en la consola
        print("\n--- Contenido de datalog.csv ---")
        with open("/sd/datalog.csv", "r") as f:
            lines = f.readlines()
            length = len(lines)
            if length > 12:
                for line in lines[-5:]:
                    print(line)
            else:
                for line in lines:
                    print(line)
    except Exception as e:
        print("Error al guardar datos!!", e)

# Conectar WiFi
def conectar_wifi():
    for key, value in WiFiList.lista:
        SSID = key
        PASSWORD = value
        trys = 0
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected() and trys <4:
            print("Conectando a WiFi...")
            trys += 1
            utime.sleep(1)    
        if wlan.isconnected():
            print("Conexión exitosa: ", wlan.ifconfig())
            break
    if not wlan.isconnected():
        print("No se pudo conectar a Wi-Fi")
    
# Función para publicar datos en MQTT
def publicar_mqtt(temp, hum, date, hour):
    if temp is None or hum is None:
        print("No hay datos válidos para enviar.")
        return
    try:
        mensaje = f'{{"temperatura": {temp:.1f}, "humedad": {hum:.1f}, "fecha": {date}, "hora": {hour}}}'
        mqtt_client.publish(MQTT_TOPIC, mensaje)
        print(f"Datos enviados MQTT: {mensaje}")
    except Exception as e:
        print("Error al enviar datos MQTT:", e)

#Función para conectarse como subscriptor
def mqtt_callback(topic, msg):
    mensaje = msg.decode('utf-8').strip().lower()
    print(f"Mensaje recibido: {mensaje}")   
    if mensaje == "on":
        led.value(1)
        print("Led encendido desde MQTT")
    elif mensaje =="off":
        led.value(0)
        print("Led apagado desde MQTT")
    




# Conectar a WiFi antes de iniciar MQTT
conectar_wifi()

# Inicializar cliente MQTT
mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
#Set callback
mqtt_client.set_callback(mqtt_callback)
mqtt_client.connect()
mqtt_client.subscribe("data/led")
print(f"Conectado al broker MQTT {MQTT_BROKER}")

# Bucle principal
while True:
    try:
        mostrar_imagen()
        utime.sleep(1)
        mqtt_client.check_msg() #revisa si hay mensajes
        temperatura, humedad = obtener_temperatura()
        fecha = rtc.obtener_fecha()
        hora = rtc.obtener_hora()
        hum_color(humedad)
        mostrar_emoji(temperatura, humedad)
        registrar_datos(temperatura,humedad, fecha, hora)
        utime.sleep(3)  # Espera 3 segundos antes de actualizar
        if temperatura is not None and humedad is not None:
            print(f" Temp: {temperatura:.1f}°C | Hum: {humedad:.1f}%")
            publicar_mqtt(temperatura, humedad, fecha, hora)
    except OSError as e:
        oled.fill(0)
        oled.text("Error Sensor!", 20, 20)
        oled.show()
        utime.sleep(2)
        
        
        
        
        