import socket
import json

class Client:

    def __init__(self):
        self.server_host = "localhost"
        self.server_port = 40000
        self.socket = None
        self.player_num = None

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

    def get_player_num(self):
        data = self.socket.recv(1024)
        json_data = json.loads(data.decode())
        self.player_num = json_data["player_num"]

if __name__ == "__main__":
    client = Client()
    client.connect_to_server()
    client.get_player_num()