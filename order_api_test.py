import datetime
import threading
import time
import pika
import json
from pymongo import MongoClient
from flask import Flask, current_app, jsonify, render_template, request
import requests
#commit
#client = MongoClient('mongodb://localhost:27017/')
#db = client['test_db']
#collection = db["orders"]
app = Flask(__name__)

@app.route('/order_api')#, methods=['POST'])
def order_api():
    # połączenie z RabbitMQ i odbiór wiadomości z kolejki
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='my-rabbit'))
    channel = connection.channel()
    channel.queue_declare(queue='orderqueue')
    method_frame, header_frame, body = channel.basic_get(queue='orderqueue')#, auto_ack=True)
    if method_frame is None:
        return 'Brak zamowienie w kolejce orderqueue'
    else:
        #test=body.get('adres')
        #print(test)
        data = json.loads(body)
        address = data.get('adres')
        return address

# @app.route('/saveorder', methods=['POST'])
# def saveorder():
#     # Sprawdź, czy request zawiera JSON
#     if request.is_json:
#         # Przekonwertuj request do słownika Pythona
#         json_str = request.get_json()
#         document = json.loads(json_str)       
#         # Wstaw dokument do bazy danych
#         result = collection.insert_one(document)
#         # Zwróć komunikat o sukcesie
#         return {"message": "Document inserted with id {}".format(result.inserted_id)}, 200
#     else:
#         # Zwróć błąd, jeśli request nie zawiera JSON
#         return {"error": "Invalid JSON"}, 400
#     return response

@app.route('/check-queue', methods=['GET'])
def check_queue():
    print("Start check_queue")
    # Utwórz połączenie z serwerem RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('my-rabbit', port=5672))
    channel = connection.channel()

    # Utwórz kolejkę, jeśli jeszcze nie istnieje
    channel.queue_declare(queue='orderqueue')

    # Sprawdź liczbę wiadomości w kolejce
    method_frame, header_frame, body = channel.basic_get(queue='orderqueue',auto_ack=True)
    if method_frame:
        # Jeśli kolejka ma wiadomości, wyślij odpowiedź z informacją
        # o liczbie wiadomości
        message_count = method_frame.message_count
        response = f"Liczba wiadomości w kolejce: {message_count}"
        data = json.loads(body)
#        url_save='http://localhost:5025/saveorder'
#        response = requests.post(url_save, json=data)
        with app.app_context():
            address = jsonify(data.get('adres'))
        print(address)
        #url_address='http://trackorder:5035/get_coordinates'
        url_address='http://trackorder:8081/get_coordinates'

        response = requests.post(url_address, json=data)
        print (response)
    else:
        # W przeciwnym razie wyślij odpowiedź z informacją, że kolejka jest pusta
        response = "Kolejka jest pusta."
        print (response)

    # Zamknij połączenie z serwerem RabbitMQ
    connection.close()

    return response

def check_queue_periodically():
    #with current_app.app_context():
    print("Start check_queue_periodically")

    while True:
        # Wywołaj funkcję sprawdzającą kolejkę
        print("Start  petli check_queue_periodically")

        check_queue()
        # Poczekaj 
        print("petla po ko check_queue")
        time.sleep(5)


@app.route('/start-check-queue', methods=['GET'])
def start_check_queue():
    print("Starting check_queue thread...")
    check_queue_thread = threading.Thread(target=check_queue_periodically)
    check_queue_thread.start()
    return "Started check_queue thread."


if __name__ == '__main__':
    # Utwórz wątek, który co 5 sekund będzie sprawdzał kolejkę
    print("Start")

    #check_queue_thread = threading.Thread(target=check_queue_periodically)
    #check_queue_thread.daemon = True
    #time.sleep(2)
    #heck_queue_thread.start()
    app.run(port=5025, debug=True)
 
