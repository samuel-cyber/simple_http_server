import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_FILE = "users.json"




def load_users():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE,"r") as user_file:
        return json.load(user_file)

def write_users(users):
    with open(DB_FILE,"w") as user_file:
        json.dump(users,user_file)


class RequestHandler(BaseHTTPRequestHandler):
    def _send(self,status_code,body):
        self.send_response(status_code)
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
    def do_GET(self):
        if self.path == "/":
            self._send(200,"Welcome to Samuel's Server")
        elif self.path == "/users":
            users = load_users()
            self._send(200,users)
        elif self.path.startswith("/users/"):
            path = self.path.split("/")
            id_num = int(path[2])
            try:
                users = load_users()
                self._send(200,users[id_num-1])
            except IndexError:
                self._send(404,{"message": "User Not Found"})
        else:
            self._send(404,{"message": "Wrong Path"})
    def do_POST(self):
        if self.path == "/create":
            length = int(self.headers.get("Content-Length"))
            body = json.loads(self.rfile.read(length))
            existing_users = load_users()
            id = len(existing_users) + 1

            existing_users.append({"id": id, "name": body.get("name"), "email": body.get("email")})
            write_users(existing_users)

            self._send(201,{"message" : f"user with ID: {id} has been added"})

        else:
            self._send(400,{"message": "This path is not supported"})


    def do_PUT(self):
        if self.path.startswith("/users/"):
            try:
                path = self.path.split("/")
                id_num = int(path[2])
                length = int(self.headers.get("Content-Length"))
                body = json.loads(self.rfile.read(length))
                existing_users = load_users()
                existing_users[id_num-1] = {"id": id_num, "name": body.get("name"),"email": body.get("email")}
                write_users(existing_users)
                self._send(200, {"message": f"User at ID: {id_num} replaced"})
            except IndexError:
                self._send(404,{"message": "ID not found"})
        else:
            self._send(400,{"message": "Wrong Path"})
    def do_DELETE(self):
        if self.path.startswith("/users/"):
            try:
                path = self.path.split("/")
                id_num = int(path[2])
                existing_users = load_users()

                del existing_users[id_num-1]
                write_users(existing_users)
                self._send(200, {"message": f"User at ID: {id_num} has been deleted"})
            except IndexError:
                self._send(400, {"message": f"Incorrect ID Given"})
        else:
            self._send(400, {"message": "Wrong Path Given"})


if __name__ == "__main__":
    print("Server is running at Port: 3500")
    HTTPServer(("",3500),RequestHandler).serve_forever()