import json
import locale
import os
from datetime import datetime
import uuid
from flask import Flask, jsonify, render_template, request
from google.cloud import dialogflow_v2
from google.oauth2 import service_account

app = Flask(__name__, static_folder="../static", template_folder="../templates")

# Dizionario per memorizzare i parametri della sessione per ciascun utente
session_parameters_dict = {}


# Route per il server Flask
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


# Route per il server Flask
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    output_contexts = body["queryResult"]["outputContexts"]
    request_parameters = get_parameters(body)
    session_id = body["session"]

    # Recupera o crea il dizionario dei parametri della sessione per l'utente corrente
    session_parameters = session_parameters_dict.get(session_id, {})

    intent_display_name = body["queryResult"]["intent"]["displayName"]
    Intent_corsi = {
        "Lezioni_cfu",
        "Lezioni_codice_corso",
        "Lezioni_nome_corso",
        "Lezioni_orario",
        "Lezioni_prof",
        "Curriculum",
    }
    Intent_mensa = {"mensa"}

    if intent_display_name == "prova":
        return jsonify(
            {
                "fulfillmentMessages": [
                    {"text": {"text": ["questa è una risposta di prova"]}}
                ]
            }
        )

    if intent_display_name in Intent_corsi:
        corso = get_course_info(request_parameters)
        if not corso:
            # Se il corso non è stato trovato nei parametri della richiesta, prova con quelli della sessione
            corso = get_course_info(session_parameters)

        if corso:
            request_parameters.update(corso)
        else:
            print("corso non trovato")
            filtered_request_parameters = filter_non_empty_parameters(
                request_parameters
            )
            # Aggiorna solo se ci sono nuovi parametri non vuoti
            if filtered_request_parameters:
                session_parameters.update(filtered_request_parameters)
            return jsonify(
                {
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "Mi dispiace sembra che non sia riuscito a trovare il corso desiderato, potresti essere più preciso? :) "
                                ]
                            }
                        }
                    ]
                }
            )

    elif intent_display_name in Intent_mensa:
        menu = get_canteen_info(request_parameters)
        if menu:
            request_parameters.update(menu)
        else:
            print("menu non trovato")
            return jsonify(
                {"query_text": [{"text": {"text": ["Errore menu non trovato"]}}]}
            )

    filtered_request_parameters = filter_non_empty_parameters(request_parameters)
    if filtered_request_parameters:
        # Aggiorna il dizionario dei parametri della sessione per l'utente corrente
        session_parameters.update(filtered_request_parameters)
        session_parameters_dict[session_id] = session_parameters

    return jsonify(
        {
            "outputContexts": [
                {
                    "name": f"projects/{body['session'].split('/')[1]}/agent/sessions/{body['session'].split('/')[-1]}/contexts/sessione",
                    "lifespanCount": 5,
                    "parameters": session_parameters,
                }
            ],
            "followupEventInput": {
                "name": "followup_intent_contesto_aggiornato",
                "languageCode": "it",
                "parameters": session_parameters,
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

        # Utilizza l'ID di sessione fornito o genera uno nuovo
        session_id = body.get("session", str(uuid.uuid4()))

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
        if responses:
            print(responses)
            fulfillment_text = responses.query_result.fulfillment_messages[0].text.text[
                0
            ]
            print("testo risposta: ", fulfillment_text)
            print("sessione : ", session_id)
            # Restituisci il testo di fulfillment e l'ID di sessione come risposta JSON
            return jsonify({"message": fulfillment_text, "session": session_id})
        else:
            print("risposta non valida")
    except Exception as err:
        print("DialogFlow.send_text_message_to_dialogflow ERROR:", err)
        return jsonify({"error": str(err)}), 500


# Funzione per estrarre i parametri dalla richiesta JSON
def get_parameters(body):
    return body.get("queryResult", {}).get("parameters", {})


def filter_non_empty_parameters(parameters):
    # Filtra solo i parametri non vuoti
    return {key: value for key, value in parameters.items() if value}


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
