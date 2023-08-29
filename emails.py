from flask import Flask, render_template, request
import imaplib
import email

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.htm', emails='')

@app.route('/fetch_emails', methods=['POST'])
def fetch_emails():
    user = request.form.get('email')
    password = request.form.get('password')
    target_email = request.form.get('target_email')

    try:
        my_mail = imaplib.IMAP4_SSL('imap.gmail.com')
        my_mail.login(user, password)
        my_mail.select('INBOX')  # Select the mailbox
    except imaplib.IMAP4.error:
        return render_template('index.htm', emails='Invalid email or password.')

    key = 'FROM'
    value = target_email
    _, data = my_mail.search(None, key, value)

    mail_id_list = data[0].split()
    emails = []

    for num in mail_id_list:
        typ, data = my_mail.fetch(num, '(RFC822)')
        msgs = data[0][1]
        my_msg = email.message_from_bytes(msgs)
        emails.append("_________________________________________\n")
        emails.append("subj: {}\n".format(my_msg['subject']))
        emails.append("from: {}\n".format(my_msg['from']))
        emails.append("body:\n")
        for part in my_msg.walk():
            if part.get_content_type() == 'text/plain':
                emails.append("{}\n".format(part.get_payload()))

    my_mail.logout()
    emails_text = ''.join(emails)

    return render_template('index.htm', emails=emails_text)

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
