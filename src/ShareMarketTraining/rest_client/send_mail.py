import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from kubernetes import client, config
import base64
import time

def sendMail(text):
 config.load_incluster_config()
 v1 = client.CoreV1Api()
 secret = v1.read_namespaced_secret('gmail-secret','saikrishnaa97')
 now = time.localtime()
 curTime = str(now.tm_mday)+"-"+str(now.tm_mon)+"-"+str(now.tm_year)+" "+str(now.tm_hour)+":"+str(now.tm_min)+":"+str(now.tm_sec)
 mail_content = 'Test Case Execution done at '+str(curTime)+'. Results:- '+str(text)

 sender_address = base64.b64decode(secret.data['emailId']).decode('utf-8')
 sender_pass = base64.b64decode(secret.data['password']).decode('utf-8')
 receiver_address = "saikrishnaa.97@gmail.com"
 message = MIMEMultipart()
 message['From'] = sender_address
 message['To'] = receiver_address
 message['Subject'] = 'Test Case Execution Done'
 message.attach(MIMEText(mail_content, 'plain'))
 session = smtplib.SMTP('smtp.gmail.com', 587)
 session.starttls()
 session.login(sender_address, sender_pass)
 text = message.as_string()
 session.sendmail(sender_address, receiver_address, text)
 session.quit()
 print('Mail Sent')
 return True
