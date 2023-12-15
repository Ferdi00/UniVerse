import os
from google.cloud import dialogflow_v2
from google.oauth2 import service_account

LANGUAGE_CODE = "it-IT"

class DialogFlow:
    def __init__(self):
        # Crea le credenziali dal percorso del file JSON (auth/auth.json)
        credentials_path = os.path.join(os.path.dirname(__file__), "../auth", "auth.json")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )

        # Estrai il campo project_id dal file JSON delle credenziali
        self.project_id = credentials.project_id

        self.session_client = dialogflow_v2.SessionsClient(credentials=credentials)

    def send_text_message_to_dialogflow(self, text_message, session_id):
        # Define session path
        session_path = self.session_client.session_path(self.project_id, session_id)

        # The text query request.
        request = {
            "session": session_path,
            "query_input": {
                "text": {
                    "text": text_message,
                    "language_code": LANGUAGE_CODE,
                }
            },
        }

        try:
            responses = self.session_client.detect_intent(request=request)
            return responses
        except Exception as err:
            print("DialogFlow.send_text_message_to_dialogflow ERROR:", err)
            raise err


def main():
    # Inizializza il tuo oggetto DialogFlow
    dialogflow_agent = DialogFlow()

    print("Chatbot: Ciao! Chatta con me o scrivi 'exit' per uscire.")

    # Avvia una simulazione di chat
    while True:
        # Richiedi all'utente di inserire il messaggio da inviare a Dialogflow
        user_input = input("Tu: ")

        # Esci dal loop se l'utente inserisce 'exit'
        if user_input.lower() == "exit":
            print("Chatbot: Arrivederci!")
            break

        # Invia il messaggio a Dialogflow e ottieni la risposta
        response = dialogflow_agent.send_text_message_to_dialogflow(
            user_input, "un_id_di_sessione_unico"
        )

        # Stampa la risposta di Dialogflow
        fulfillment_text = response.query_result.fulfillment_text
        print(f"Chatbot: {fulfillment_text}")


if __name__ == "__main__":
    main()
