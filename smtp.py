import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviarEmail(conexao_smtp, email):

    smtp_host = conexao_smtp.get('host')
    smtp_port = conexao_smtp.get('port')
    smtp_user = conexao_smtp.get('user')
    smtp_password = conexao_smtp.get('password')

    email_to = email.get('to')
    email_subject = email.get('subject')
    email_message = email.get('message')
    email_message_html = email.get('message_html')

    message = MIMEMultipart("alternative")
    message['Subject'] = email_subject
    message['From'] = smtp_user
    message['To'] = email_to

    if email_message_html == True:
        message.attach(MIMEText(email_message, 'html', 'utf-8'))
    else:
        message.attach(MIMEText(email_message, 'plain', 'utf-8'))


    context = ssl.create_default_context()
    sucesso = False
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as smtp_server:
        login = smtp_server.login(smtp_user, smtp_password)
        if login[0] != 235:
            sucesso = False
            smtp_server.close()
            return sucesso
        send = smtp_server.sendmail(smtp_user, email_to, message.as_string())
        if send == {}:
            sucesso = True
    smtp_server.close()
    return sucesso