const msgerChat = document.querySelector(".msger-chat");
const scriptPath = document.currentScript.src;
const basePath = scriptPath.substring(0, scriptPath.lastIndexOf("/") + 1);

const BOT_MSGS = [
  "Hi, how are you?",
  "Ohh... I can't understand what you trying to say. Sorry!",
  "I like to play games... But I don't know how to play!",
  "Sorry if my answers are not relevant. :))",
  "I feel sleepy! :(",
];

const BOT_NAME = "Universe";
const PERSON_NAME = "You";
const BOT_IMG = `${basePath}avatar.jpeg`;
const PERSON_IMG = `${basePath}user.png`;

var form = document.getElementById("messageForm");
var messageInput = document.getElementById("messageInput");

form.addEventListener("submit", function (event) {
  event.preventDefault();
  var message = messageInput.value;
  if (!message) return;
  appendMessage(PERSON_NAME, PERSON_IMG, "right", message);
  messageInput.value = "";
  sendMessage(message);
});

function appendMessage(name, img, side, text) {
  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img}) "></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${text}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

function botResponse(msgText) {
  const delay = msgText.split(" ").length * 100;
  setTimeout(() => {
    appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
  }, delay);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}

function random(min, max) {
  return Math.floor(Math.random() * (max - min) + min);
}

// Aggiorna la funzione sendMessage per inviare messaggi solo a Dialogflow
async function sendMessage(message) {
  try {
    // Supponendo che tu abbia ottenuto sessionId in qualche modo

    const sessionId = getSessionId();
    // Invia il messaggio a Dialogflow attraverso il frontend
    const responseFromDialogflow = await sendToDialogflow(message, sessionId);
    const dialogflowResponse = responseFromDialogflow.message;
    botResponse(dialogflowResponse);
  } catch (error) {
    console.error("Errore nella gestione dei messaggi:", error);
  }


}

// Funzione per inviare il messaggio a Dialogflow attraverso il frontend
async function sendToDialogflow(message, sessionId) {
  const response = await fetch("/Chatbot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message, session: sessionId }),
  });

  if (!response.ok) {
    throw new Error(
      `Errore nella richiesta a Dialogflow: ${response.statusText}`
    );
  }

  return response.json();
}
