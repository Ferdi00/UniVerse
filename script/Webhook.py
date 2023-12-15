import json
import locale
from datetime import datetime
from google.cloud import dialogflow_v2
from google.oauth2 import service_account
from flask import Flask, jsonify, request, render_template
import os

app = Flask(__name__, static_folder="../static", template_folder="../templates")


# Route per il server Flask
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


# Route per il server Flask
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    # Estrai l'array di outputContexts dal corpo della richiesta

    # contesti di output della chiamata (per ora non utilizzati)
    output_contexts = body["queryResult"]["outputContexts"]

    # print(output_contexts)

    parameters = get_parameters(body)
    # stampa parametri
    # print("Parametri:")
    # for key, value in parameters.items():
    # print(f"{key}: {value}")

    # nome intent richiesta corrente
    intent_display_name = body["queryResult"]["intent"]["displayName"]

    print(intent_display_name)
    Intent_corsi = {
        "Lezioni_cfu",
        "Lezioni_codice_corso",
        "Lezioni_nome_corso",
        "Lezioni_orario",
        "Lezioni_prof",
        "Curriculum",
    }
    Intent_mensa = {"mensa"}

    if intent_display_name in Intent_corsi:
        print("ho trovato l'intent corsi")
        corso = get_course_info(parameters)
        if corso:
            parameters.update(corso)
        else:
            print("corso non trovato")
            return jsonify(
                {
                    "fulfillmentMessages": [
                        {"text": {"text": ["Errore corso non trovato"]}}
                    ]
                }
            )

    elif intent_display_name in Intent_mensa:
        print("ho trovato l'intent mensa")
        menu = get_canteen_info(parameters)
        if menu:
            parameters.update(menu)
        else:
            print("menu non trovato")
            return jsonify(
                {
                    "fulfillmentMessages": [
                        {"text": {"text": ["Errore menu non trovato"]}}
                    ]
                }
            )

    return jsonify(
        {
            "outputContexts": [
                {
                    "name": f"projects/{body['session'].split('/')[1]}/agent/sessions/{body['session'].split('/')[-1]}/contexts/session-vars",
                    "lifespanCount": 5,
                    "parameters": parameters,
                }
            ],
            "followupEventInput": {
                "name": "followup_intent_contesto_aggiornato",
                "languageCode": "it",
                "parameters": parameters,
            },
        }
    )


LANGUAGE_CODE = "it-IT"


@app.route("/Chatbot", methods=["POST"])
def send_text_message_to_dialogflow():
    print("ho chiamato correttamente l'api")
    try:
        body = request.get_json()
        text_message = body["message"]

        # Crea le credenziali dal percorso del file JSON (auth/auth.json)
        credentials_path = os.path.join(
            os.path.dirname(__file__), "../auth", "auth.json"
        )
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        # Estrai il campo project_id dal file JSON delle credenziali
        project_id = credentials.project_id

        session_client = dialogflow_v2.SessionsClient(credentials=credentials)
        session_id = "un_id_di_sessione_unico"
        session_path = session_client.session_path(project_id, session_id)

        # The text query request.
        request_dialogflow = {
            "session": session_path,
            "query_input": {
                "text": {
                    "text": text_message,
                    "language_code": LANGUAGE_CODE,
                }
            },
        }

        responses = session_client.detect_intent(request=request_dialogflow)
        # Estrai il testo di fulfillment dalla risposta
        fulfillment_text = responses.query_result.fulfillment_text

        # Restituisci solo il testo di fulfillment come risposta JSON
        return jsonify({"message": fulfillment_text})
    except Exception as err:
        print("DialogFlow.send_text_message_to_dialogflow ERROR:", err)
        return jsonify({"error": str(err)}), 500


# Funzione per estrarre i parametri dalla richiesta JSON
def get_parameters(body):
    return body.get("queryResult", {}).get("parameters", {})


# Funzione per ottenere informazioni sul corso in base ai parametri forniti
def get_course_info(parameters):
    nome_corso = parameters.get("nome_corso", "")
    codice_corso = parameters.get("codice_corso", "")

    # Carica i dati dei corsi dal file JSON
    corsi = load_json("corsi.json")

    if nome_corso:
        corso = next((c for c in corsi if c.get("nome_corso", "") == nome_corso), None)
    elif codice_corso:
        corso = next(
            (c for c in corsi if c.get("codice_corso", "") == int(codice_corso)), None
        )
    else:
        corso = None

    return corso


# Funzione per ottenere informazioni sulla mensa in base al giorno della settimana
def get_canteen_info(parameters):
    day_of_week = get_day_of_week(parameters.get("date", ""))
    menu_data = load_json("menu.json")

    if day_of_week:
        menu_of_the_day = next(
            (
                day_menu
                for day_menu in menu_data
                if day_menu.get("giorno", "") == day_of_week
            ),
            None,
        )
    else:
        menu_of_the_day = None

    return menu_of_the_day


# Funzione per caricare i dati dei corsi dal file JSON
def load_json(file_name):
    with open(f"json/{file_name}", "r") as json_file:
        return json.load(json_file)


# Funzione per ottenere il nome del giorno della settimana da una stringa di data
def get_day_of_week(date_string):
    # Imposta la localizzazione su italiano
    locale.setlocale(locale.LC_TIME, "it_IT")

    # Converte la stringa in un oggetto datetime
    dt = datetime.fromisoformat(
        date_string[:-6]
    )  # Rimuovi la parte del fuso orario (+01:00)

    # Ottieni il nome del giorno della settimana
    day_of_week = dt.strftime(
        "%A"
    )  # Utilizza il formato '%A' per ottenere il nome del giorno completo

    return day_of_week


# Avvia il server Flask
if __name__ == "__main__":
    app.run(debug=True)
