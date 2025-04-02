from flask import Flask, request, redirect, url_for, render_template, jsonify, flash, session, json
import os
import re
from werkzeug.utils import secure_filename
import datetime
import email, ssl, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from pathlib import Path
from requests import Response

app = Flask(__name__,
            static_url_path='', 
            static_folder='static')


app.config.from_object(os.environ['APP_SETTINGS'])

def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = app.config['SECRET_SITE_KEY']
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/certificates')
def certificates():
    return render_template('certificates.html')

@app.route('/briefing')
def briefing():
    return render_template('briefing.html')

@app.route('/pdf') #the url you'll send the user to when he wants the pdf
def pdfviewer():
    return redirect("../static/cv/cv.pdf") #the pdf itself


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    sitekey = app.config['RECAPTCHA_SITE_KEY']
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        captcha_response = request.form['g-recaptcha-response']
    
        if not is_human(captcha_response):
            # Log invalid attempts
            status = "Sorry ! Please Check Im not a robot."
            flash(status, "warning")
            return render_template('contact.html', sitekey=sitekey)
        else:    
            #send contact mail
            html = "<html><head></head><body>"
            html += "<p>Name: " + name + "</p>"
            html += "<p>Email: " + email + "</p>"
            html += "<p>Subject: " + subject + "</p>"
            message = "<br />".join(message.split("\n"))
            html += "<p>Message: <br /><br />" + message + "</p>"
            html += "</body></html>"
        
            body = html
            email_username = app.config['MAIL_USERNAME']
            sender_email = app.config['MAIL_DEFAULT_SENDER']
            receiver_email = app.config['MAIL_RECEIVER']
            password = app.config['MAIL_PASSWORD']

            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = "IOL Invoice " + '<' + sender_email + '>'
            message["To"] = receiver_email
            message["Subject"] = subject
            #message["Bcc"] = receiver_email  # Recommended for mass emails

            # Add body to email
            message.attach(MIMEText(body, "html"))

            #text = message.as_string()
            """"connection = smtplib.SMTP(host='smtp.office365.com', port=587)
            connection.starttls()
            connection.login(email_username,password)
            connection.send_message(message)
            connection.quit()"""

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(email_username, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
        
            return render_template('contact-form-sent.html')
    
    return render_template('contact.html', sitekey=sitekey)

if __name__ == "__main__":
    app.run()





