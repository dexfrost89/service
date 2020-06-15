from flask import Flask, request
from flask_restx import Resource, Api
import json
import bcrypt






def configure_routes(app):
    api = Api(app)

    users = {}

    uids = {}

    def read_database():
        with open('database.json') as json_file:
            data = json.load(json_file)
            return data

    users = read_database()

    def write_database():
        with open('database.json', 'w') as outfile:
            json.dump(users, outfile)

    @api.route('/hello_world')
    class hello_world(Resource):
        def get(self):
            return {"Hello": "World"}

    @api.route('/user')
    class add_user(Resource):
        def post(self):
            login_password = request.get_json(force=True)
            user = list(login_password.keys())[0]
            password = login_password[user]
            hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

            users[user] = hashed.decode('utf8')

            write_database()
            return {user: users[user]}
            #return {"ok": hashed.decode('utf8')}

    @api.route('/users')
    class get_users(Resource):
        def get(self):
            return list(users.keys())


    @api.route('/auth')
    class authenticate(Resource):
        def post(self):
            login_password = request.get_json(force=True)
            user = list(login_password.keys())[0]
            password = login_password[user]

            if not user in users.keys() or not (bcrypt.checkpw(password.encode('utf8'), users[user].encode('utf8'))):
                return {"error":"not authorized"}

            new_uid = len(list(uids.keys()))
            uids[new_uid] = user
            return {"ok": new_uid}

    @api.route('/user/<string:name>')
    class change_name(Resource):
        def post(self, name):
            login_password = request.get_json(force=True)
            uid = list(login_password.keys())[0]
            new_name = login_password[uid]
            uid = int(uid)
            if name in users.keys() and uid in uids.keys() and uids[uid] == name:
                pwd = users[name]
                users.pop(name, None)
                users[new_name] = pwd
                uids[uid] = new_name
                write_database()
                return new_name
            return {"error":"not authorized"}


def test_base_route():
    app = Flask(__name__)
    configure_routes(app)
    client = app.test_client()
    url = 'http://127.0.0.1:5000/hello_world'

    response = client.get(url)
    assert response.get_data() == b'{"Hello": "World"}\n'
    assert response.status_code == 200

if __name__ == '__main__':
    app = Flask(__name__)
    configure_routes(app)
    app.run(debug=True)
    test_base_route()