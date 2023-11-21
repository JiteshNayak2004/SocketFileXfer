# Import necessary modules
import http.server
import socket
import socketserver
import webbrowser
import pyqrcode
from pyqrcode import QRCode
import png
import os

# Assign the appropriate port value
PORT = 6540

user_passcode = 'hello'

# Get the user's desktop directory
desktop = os.path.join(os.environ.get('XDG_DESKTOP_DIR', '/home/jitesh/Desktop'))
os.chdir(desktop)

# Create an HTTP request handler
class PasswordHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Display a form to enter the pairing password
            self.wfile.write(b'<h1>Enter Pairing Password</h1>')
            self.wfile.write(b'<form method="POST" action="/"><input type="password" name="pairing-password"><input type="submit" value="Submit"></form>')
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['content-length'])
        post_body = self.rfile.read(content_length)

        pairing_password = post_body.decode('utf-8').split('=')[1]
        print(pairing_password)

        # Validate the pairing password
        if pairing_password == user_passcode:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Serve files from the specified directory or Desktop directory
            desktop_dir = os.path.join(os.environ.get('XDG_DESKTOP_DIR', '/home/jitesh/Desktop'))
            requested_path = self.path.lstrip('/')

            full_path = os.path.join(desktop_dir, requested_path)

            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    self.serve_directory(full_path)
                else:
                    self.send_file(full_path)
            else:
                self.send_error(404, 'File not found')
        else:
            self.send_error(400, 'Incorrect pairing password')

    def serve_directory(self, directory_path):
        self.wfile.write(b'<h1>Directory Listing</h1>')
        self.wfile.write(b'<ul>')

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            link = f'<a href="{item}">{item}</a>'
            self.wfile.write(f'<li>{link}</li>'.encode('utf-8'))

        self.wfile.write(b'</ul>')

    def send_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_contents = f.read()

        self.send_response(200)
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-disposition', f'attachment; filename="{os.path.basename(file_path)}"')
        self.end_headers()

        self.wfile.write(file_contents)


# Get the hostname and IP address
hostname = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP = "http://" + s.getsockname()[0] + ":" + str(PORT)
link = IP

# Generate the QR code
url = pyqrcode.create(link)
url.svg("myqr.svg", scale=8)
webbrowser.open('myqr.svg')

# Create and start the HTTP server
with socketserver.TCPServer(("", PORT), PasswordHandler) as httpd:
    print("Serving at port", PORT)
    print("Type this in your browser:", IP)
    print("or use the QR code")
    httpd.serve_forever()