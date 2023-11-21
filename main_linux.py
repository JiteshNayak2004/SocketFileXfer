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

            # Display a stylish password prompt
            password_prompt = """
            <div style="text-align: center; margin-top: 100px;">
                <h1>Enter Pairing Password</h1>
                <form method="POST" action="/">
                    <input type="password" name="pairing-password" style="padding: 10px; font-size: 16px;">
                    <br><br>
                    <input type="submit" value="Submit" style="padding: 10px; font-size: 16px;">
                </form>
            </div>
            """
            self.wfile.write(password_prompt.encode('utf-8'))
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
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Display a stylish directory listing
        directory_listing = """
        <div style="text-align: center; margin-top: 50px;">
            <h1>Directory Listing</h1>
            <ul style="list-style-type: none; padding: 0;">
        """

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            link = f'<li><a href="{item}">{item}</a></li>'
            directory_listing += link

        directory_listing += """
            </ul>
        </div>
        """

        self.wfile.write(directory_listing.encode('utf-8'))

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
url.png("myqr.png", scale=8)

# HTML content for displaying QR code
qr_code_html = f"""
<div style="text-align: center; margin-top: 50px;">
    <h1>Scan to Access and Browse Files</h1>
    <img src="myqr.png" alt="QR Code">
</div>
"""

# Save the QR code HTML to a file
with open("qr_code_page.html", "w") as qr_code_page:
    qr_code_page.write(qr_code_html)

# Open the default web browser with the QR code HTML page
webbrowser.open("qr_code_page.html")

# Create and start the HTTP server
with socketserver.TCPServer(("", PORT), PasswordHandler) as httpd:
    print("Serving at port", PORT)
    print("Type this in your browser:", IP)
    httpd.serve_forever()
