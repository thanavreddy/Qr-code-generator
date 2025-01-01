#made using sqlite3 
from flask import Flask, render_template, request, send_file

import qrcode
import sqlite3
from io import BytesIO
app = Flask(__name__)
# Function to generate QR code and save it to database
def generate_qr_and_save(data, size, fill_color,back_color, format):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    # Save QR code image to a BytesIO object
    img_bytes = BytesIO()
    img.save(img_bytes, format=format.upper())
    img_bytes.seek(0)
    # Save QR code data to database
    conn = sqlite3.connect('qr_codes.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS qr_codes (data TEXT, size INTEGER, fill_color TEXT,back_color TEXT, format TEXT, image BLOB)''')
    cursor.execute("INSERT INTO qr_codes (data, size, fill_color, back_color,format, image) VALUES (?, ?, ?, ?, ?,?)",(data, size, fill_color,back_color, format, img_bytes.read()))
    conn.commit()
    conn.close()
    return img_bytes
# Function to retrieve QR code from database
def retrieve_qr(data):
    conn = sqlite3.connect('qr_codes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qr_codes WHERE data = ?", (data,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[4]
    else:
        return None
# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')
# Route for generating and displaying QR code
@app.route('/generate', methods=['POST'])
def generate():
    data = request.form['data']
    size = int(request.form['size'])
    fill_color = request.form['fill_color']
    back_color = request.form['back_color']
    format = request.form['format']
    img_bytes = generate_qr_and_save(data, size, fill_color,back_color, format)
    return send_file(img_bytes, mimetype='image.png')
# Route for retrieving QR code from database
@app.route('/retrieve', methods=['POST'])
def retrieve():
    data = request.form['data']
    qr_image = retrieve_qr(data)
    if qr_image:
        return send_file(BytesIO(qr_image), mimetype='image.png')
    else:
        return 'QR code not found.', 404
if __name__ == '__main__':
    app.run(debug=True,port=9000)