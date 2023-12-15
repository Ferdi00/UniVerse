// Aggiorna la funzione sendMessage per inviare messaggi solo a Dialogflow
async function sendMessage() {
  const userInput = document.getElementById("userInput");
  const message = userInput.value.trim();

  if (message !== "") {
    appendMessage("You", message, "you-message"); // Aggiunta classe "you-message"

    try {
      // Invia il messaggio a Dialogflow attraverso il frontend
      const responseFromDialogflow = await sendToDialogflow(message);
      const dialogflowResponse = responseFromDialogflow.message;
      appendMessage("Universe", dialogflowResponse, "dialogflow-message"); // Aggiunta classe "dialogflow-message"
    } catch (error) {
      console.error("Errore nella gestione dei messaggi:", error);
    }

    // Cancella l'input utente
    userInput.value = "";
  }
}

// Funzione per inviare il messaggio a Dialogflow attraverso il frontend
async function sendToDialogflow(message) {
  const response = await fetch("/Chatbot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message }),
  });

  if (!response.ok) {
    throw new Error(
      `Errore nella richiesta a Dialogflow: ${response.statusText}`
    );
  }

  return response.json();
}

function appendMessage(sender, text, messageClass) {
  const chatMessages = document.getElementById("chatMessages");
  const messageElement = document.createElement("div");
  messageElement.classList.add(messageClass); // Aggiunta della classe specificata
  messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatMessages.appendChild(messageElement);

  // Scrolla verso il basso per mostrare sempre l'ultimo messaggio
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
