from http.server import BaseHTTPRequestHandler
import socketserver
from email.parser import BytesParser
from email.policy import default
from PIL import Image, ImageOps, ImageFilter
import mimetypes

PORT = 8081

class ImageFilerServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('templates/index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path.startswith('/static/'):
            file_path = self.path.lstrip('/')
            mimetype = mimetypes.guess_type(file_path)
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        file_content = self.rfile.read(content_length)
        boundary = self.headers['Content-Type'].split('boundary=')[1]
        parts = file_content.split(b'--' + boundary.encode())

        parts_dict = dict()

        for part in parts:
            if part.strip():
                msg = BytesParser(policy=default).parsebytes(part.strip())
                name = msg.get_param('name', header='content-disposition')
                # filename = msg.get_param('filename')
                filename = msg.get_filename()
                payload = msg.get_payload(decode=True)

                parts_dict[name] = (filename, payload)
            # if part.strip():
        
        filename, payload = parts_dict['image']
        with open(filename, 'wb') as file:
            file.write(payload)

        filter = parts_dict['filter'][1].decode().strip()
        print(filter)

        pillow_image = Image.open(filename)
        if filter == 'greyscale':
            pillow_image = ImageOps.grayscale(pillow_image) 
        elif filter == 'inversion':
            pillow_image = ImageOps.invert(pillow_image)
        elif filter == 'blur':
            pillow_image = pillow_image.filter(ImageFilter.BLUR)
        
        pillow_image.save('static/filtered_image.png')

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<img src="static/filtered_image.png"/>'.encode())
        
        
        

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), ImageFilerServer) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()