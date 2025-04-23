# **Arquitectura Cliente-Suscriptor con Broker EMQX**

## **ESP32**

### **Este proyecto utiliza un esp32 con micropython integrando las siguientes funcionalidades:**

- Usar un sensor dht22 para medir temperatura y humedad.
- Controlar un Led RGB de ánodo común cambiando su color según la humedad del ambiente.
- Visualizar en una pantalla OLED las lecturas obtenidas del sensor.
- Recopilar la fecha y hora de las lecturas del dht22 usando un módulo rtc.
- Almacenar en una tarjeta microSD la información del sensor, junto con la fecha y hora de la lectura.
- Enviar las lecturas del sensor a un broker y a la vez estar suscrito a un tópico por el cual puede encenderse o apagarse el led integrado al esp32.

## **Sitio Web**

### **Se montó una pequeña página estática con HTML, CSS y JS para:**

- Suscribirse al tópico donde se envían las lecturas del sensor.
- Parsear las lecturas a formato JSON para poder presentar los datos de una forma más entendible para la lectura humana.
- Conectarse al **broker** como publicista para enviar señales de encendido y apagado al led integrado del esp32, habilitando su uso de forma remota.
