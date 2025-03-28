// Configuración del broker MQTT con WebSockets
const broker = "ws://broker.emqx.io:8083/mqtt"; // EMQX gratuito
const topicLed = "data/led"; // Tópico para enviar mensajes
const topicSub = "data/temp/#"; // Tópico para recibir mensajes
const clientId = "web_client_" + Math.random().toString(16).substr(2, 8);

// Conectar al broker MQTT
const client = mqtt.connect(broker, { clientId });

client.on("connect", () => {
    document.getElementById("status").innerText = "Conectado a MQTT";
    console.log("Conectado al broker MQTT");

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
        console.log(`Mensaje recibido en '${topicSub}': ${msgText}`);

        // Mostrar el mensaje en la página
        const msgDiv = document.getElementById("messages");
        const newMsg = document.createElement("p");
        newMsg.innerText = `${msgText}`;
        msgDiv.appendChild(newMsg);
    }
});

