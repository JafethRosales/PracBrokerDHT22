// Configuración del broker MQTT con WebSockets
const broker = "wss://broker.emqx.io:8084/mqtt"; // EMQX gratuito
const topicLed = "data/led"; // Tópico para enviar mensajes
const topicSub = "data/temp/#"; // Tópico para recibir mensajes
const clientId = "web_client_" + Math.random().toString(16).substr(2, 8);
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

let totalLecturas = 0;
const supabaseUrl = 'https://erazcqsubbucfrvlyyad.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyYXpjcXN1YmJ1Y2Zydmx5eWFkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0MjM4MzcsImV4cCI6MjA2Mjk5OTgzN30.MCOkVXNL6p8AE7saKdE-HYPZZXNqtdg2Ut0n3qe-jWE'
const supabase = createClient(supabaseUrl, supabaseKey)


//función para insertar datos
async function supabaseInsert(jsonDHT) {
  const { data, error } = await supabase.from('mediciones').insert([jsonDHT]);
  if (error) {
    console.error('Error insertando:', error)
  } else {
    console.log('Tarea agregada:', data)
  }
}



// Conectar al broker MQTT
const client = mqtt.connect(broker, { clientId });
client.on("connect", () => {
    document.getElementById("status").innerText = "- Conectado con MQTT";
    console.log("Conectado al broker MQTT");
    document.getElementById("statusCircle").setAttribute('fill', '#61a063');
    // Suscribirse al tópico de recepción
    client.subscribe(topicSub, (err) => {
        if (!err) {
            console.log(`Suscrito al tópico: ${topicSub}`);
        }
    });
});

// Función para publicar un mensaje en un tópico diferente
function publishMessage(state) {
    let onButton = document.getElementById("onButton");
    let offButton = document.getElementById("offButton");

    if (state === "on") {
        onButton.classList.add("active");
        offButton.classList.remove("deactive");
    } 
    if (state === "off") {
        offButton.classList.add("deactive");
        onButton.classList.remove("active");
    }

    client.publish(topicLed, state);
    console.log(`Mensaje enviado al tópico '${topicLed}': ${state}`);   
}

// Escuchar mensajes del tópico de suscripción
client.on("message", (receivedTopic, message) => {
    if (receivedTopic) {
        const msgText = message.toString();
        const data = JSON.parse(msgText);
        console.log(`Mensaje recibido en '${topicSub}': ${msgText}`);

        //Enviar datos a Supabase
        supabaseInsert(data);

        // Crear el recipiente del mensaje
        const msgDiv = document.getElementById("messages");
        const newDiv = document.createElement("div");
        newDiv.classList.add('lecturas-container');
        const title = document.createElement("h3");
        title.innerText = "Has recibido un mensaje!!";
        newDiv.appendChild(title);

        // Formato del mensajes
        for (let key in data){
            const newMsg = document.createElement("p");
            if (key == "temperatura" || key == "humedad"){
                newMsg.innerText =`${key.toUpperCase()}: ${data[key]}`;
                newMsg.classList.add('lecturas');
            } else {
                newMsg.classList.add('dateTime');
                if (key == "timestamp"){
                    const newDate = new Date(data[key]) 
                    newMsg.innerText =`Fecha: ${newDate.toLocaleString()}`;
                } else {
                    newMsg.innerText =`${key.toUpperCase()}: ${data[key]}`;
                }
            }
            newDiv.appendChild(newMsg);
        }
        if(document.getElementById("vacio")){
            document.getElementById("vacio").classList.add("hidden");
        }
        msgDiv.appendChild(newDiv);

        totalLecturas += 1;
        if (totalLecturas > 4) {
            msgDiv.removeChild(msgDiv.firstElementChild);
        }
    }
});

