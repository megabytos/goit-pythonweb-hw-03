import json
import mimetypes
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from json import JSONDecodeError
from jinja2 import Environment, FileSystemLoader
import os

TEMPLATES_DIR = Path(__file__).parent.absolute() / "templates"
STORAGE_DIR = Path(__file__).parent.absolute() / "storage"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        self.write_json_to_file(data_dict, 'data.json')
        self.send_response(302)
        self.send_header('Location', '/read')
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == '/':
            self.send_html_file('index.html')
        elif parsed_url.path == '/message':
            self.send_html_file('message.html')
        elif parsed_url.path == '/read':
            self.send_template('data.json', "read.jinja")
        else:
            if Path().joinpath(parsed_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_template(self, datafile, template_file, status=200):
        template = env.get_template(template_file)
        self.check_storage_file(datafile)
        with open(STORAGE_DIR / datafile, "r+", encoding='utf-8') as file:
            try:
                file_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                file_data = {}
        output = template.render(data=file_data)
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(output.encode())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(TEMPLATES_DIR / filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def write_json_to_file(self, data, filename='data.json'):
        self.check_storage_file(filename)
        with open(STORAGE_DIR / filename, "r+", encoding='utf-8') as file:
            try:
                file_data = json.load(file)
            except JSONDecodeError:
                file_data = {}
            file_data[str(datetime.now())] = data
            file.seek(0)
            json.dump(file_data, file, indent=4, ensure_ascii=False)

    def check_storage_file(self, filename):
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
        if not os.path.exists(STORAGE_DIR / filename):
            open(STORAGE_DIR / filename, 'x')


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)  # noqa
    try:
        print("Starting http server on ", server_address)
        print("Press Ctrl+C to stop")
        http.serve_forever()
    except KeyboardInterrupt:
        print("Server is shutting down...")
        http.server_close()


if __name__ == '__main__':
    run()
