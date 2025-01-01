from flask import Flask, request, send_file, jsonify, render_template
import mysql.connector
import io
import qrcode

app = Flask(__name__)

def generate_qr_and_save(data, size, fill_color, back_color, format):
    try:
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=size, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        
        # Connect to the database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='', #this is kept empty enter your sql password here
            database='qrdb'
        )
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS qr_codes (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            data TEXT, 
                            size INT, 
                            fill_color VARCHAR(10),
                            back_color VARCHAR(10), 
                            format VARCHAR(10), 
                            image LONGBLOB)''')
        
        # Insert data into the table
        cursor.execute('''INSERT INTO qr_codes (data, size, fill_color, back_color, format, image) 
                          VALUES (%s, %s, %s, %s, %s, %s)''', 
                       (data, size, fill_color, back_color, format, img_bytes.getvalue()))
        conn.commit()
        cursor.close()
        conn.close()
        
        return img_bytes
    except mysql.connector.Error as e:
        return str(e), 500
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.form['data']
        size = int(request.form['size'])
        fill_color = request.form['fill_color']
        back_color = request.form['back_color']
        format = request.form['format']
        
        img_bytes = generate_qr_and_save(data, size, fill_color, back_color, format)
        
        if isinstance(img_bytes, tuple) and img_bytes[1] == 500:
            return jsonify({"error": img_bytes[0]}), 500
        
        return send_file(img_bytes, mimetype=f'image/{format}')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=7000)
