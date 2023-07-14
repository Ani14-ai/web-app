from flask import Flask, render_template, request, jsonify,current_app
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from PIL import ImageGrab, Image
import pytesseract as tess
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)


class Transaction(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    date = db.Column(db.String(10))
    time = db.Column(db.String(8))
    minreff_id = db.Column(db.String(20))
    track_id = db.Column(db.String(20))


@app.route('/')
def home():
    return render_template('test_1.htm')


@app.route('/login', methods=['POST'])
def login():
    login_id = request.form.get('login_id')
    password = request.form.get('password')

    if login_id == 'abc' and password == '1234':
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['excel_file']
    file.save(file.filename)
    if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Create the 'uploads' directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

    file.save(file_path)

        # Process the uploaded file
    df = pd.read_excel(file,engine='openpyxl')
    process_transactions(df)

    return jsonify({'success': True})

    return jsonify({'success': False})


def process_transactions(df):
    for i in df.index:
        time.sleep(5)
        driver = webdriver.Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')
        entry = df.loc[i]
        driver.get(entry['PAYMENT LINKS'])
        card_no = driver.find_element(By.ID, 'creditCardNumber')
        card_no.send_keys(str(entry['CARDNO']))
        time.sleep(1)
        exp_mon = driver.find_element(By.ID, 'expiryMonthCreditCard')
        exp_mon.send_keys('Apr(04)')
        time.sleep(1)
        exp_yr = driver.find_element(By.ID, 'expiryYearCreditCard')
        exp_yr.send_keys('2024')
        time.sleep(1)
        cvv_no = driver.find_element(By.ID, 'CVVNumberCreditCard')
        cvv_no.send_keys(str(entry['CVV']))
        
        time.sleep(1)
        mp = driver.find_element(By.ID, 'SubmitBillShip')
        mp.click()
        ipin = driver.find_element(By.ID, 'txtipin')
        ipin.send_keys(str(entry['IPIN']))
        time.sleep(1)
        sub = driver.find_element(By.ID, 'btnverify')
        sub.click()
        time.sleep(10)
        im = ImageGrab.grab()
        im.save("ss.png")
        tess.pytesseract.tesseract_cmd = r"C:\\Users\chatt\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        text = tess.image_to_string(im)

        transaction_info = {}
        status_match = re.search(r"Status Date\n(\w+)", text)
        if status_match:
            transaction_info["status"] = status_match.group(1)
        else:
            transaction_info["status"] = None

        datetime_match = re.search(r"Failed (\d{2}-\d{2}-\d{4}) (\d{2}:\d{2}:\d{2})", text)
        if datetime_match:
            transaction_info["date"] = datetime_match.group(1)
            transaction_info["time"] = datetime_match.group(2)
        else:
            transaction_info["date"] = None
            transaction_info["time"] = None

        minreff_match = re.search(r"MINREFF_ID\n([\d]+)", text)
        if minreff_match:
            transaction_info["minreff_id"] = minreff_match.group(1)
        else:
            transaction_info["minreff_id"] = None

        track_id_match = re.search(r"Track_ID\n\n([\d]+)", text)
        if track_id_match:
            transaction_info["track_id"] = track_id_match.group(1)
        else:
            transaction_info["track_id"] = None
        
        new_df = pd.DataFrame([transaction_info])
        if transaction_info["status"] is not None:
            df = pd.concat([df, new_df], axis=1)

        df.to_excel("uploads/xyz.xlsx", index=False)
        driver.quit()

from flask import send_from_directory

@app.route("/download", methods=['GET'])
def download_file():
    #uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    uploads="C:\\Users\\chatt\\OneDrive\\Documents\\flask\\uploads"
    return send_from_directory(directory=uploads, path="xyz.xlsx", as_attachment=True)




if __name__ == '__main__':
    app.run(debug=False,port=5000,host='0.0.0.0')
