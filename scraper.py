import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv # Env keys
from notifier_telegram import main as send_telegram_message
import json
import os
import re

load_dotenv(dotenv_path="/Users/krist/Documents/proge/Serious-projects/Autolisting/.env") # Load variables from .env

# For emails
#def create_html_body_email(cars_dict):
#    html_body = "<h2>Siin on uued lisatud autod:</h2><ul>"
#    for car in cars_dict:
#        html_body += f"""
#        <li style="margin-bottom: 15px;">
#            <strong>{car['nimi']}</strong><br>
#            Aasta: {car['aasta']}<br>
#            Hind: {car['hind']}<br>
#            Läbisõit: {car['mileage']}<br>
#            Kütus: {car['kütus']}<br>
#            Käigukast: {car['kast']}<br>
#            Vedu: {car['vedu']}<br>
#            Keretüüp: {car['tüüp']}<br>
#            <a href="{car['link']}">View listing</a><br>
#            {'<img src="'+car["image_url"]+'" alt="Car image" style="width:300px;margin-top:5px;">' if 'image_url' in car else ''}
#        </li>
#        """
#
#    html_body += "</ul>"
#
#    return html_body

def create_html_body_telegram(car):
    html_body = (
        f"<b>{car['nimi']}</b>\n"
        f"Aasta: {car['aasta']}\n"
        f"Hind: {car['hind']}\n"
        f"Läbisõit: {car['mileage']}\n"
        f"Kütus: {car['kütus']}\n"
        f"Käigukast: {car['kast']}\n"
        f"Vedu: {car['vedu']}\n"
        f"Keretüüp: {car['tüüp']}\n"
        f"<a href=\"{car['link']}\">Vaata kuulutust</a>\n\n"
    )

    return html_body

def send_telegram_messages(cars_dict):
    for car in cars_dict:
        send_telegram_message(create_html_body_telegram(car))

# For emails
#def send_notification_email(cars_dict):
#    # Create the email
#    msg = MIMEMultipart("alternative")
#    msg["Subject"] = "Uued autod!"
#    msg["From"] = os.getenv("GMAIL_USER")
#    msg["To"] = os.getenv("GMAIL_RECIEVER")
#
#    msg.attach(MIMEText(create_html_body_email(cars_dict), "html"))
#
#    # Gmail SMTP settings
#    smtp_server = "smtp.gmail.com"
#    smtp_port = 587
#    your_email = os.getenv("GMAIL_USER")
#    your_app_password = os.getenv("GMAIL_PASSWORD")
#
#    # Send the email
#    with smtplib.SMTP(smtp_server, smtp_port) as server:
#        server.starttls()  # Secure the connection
#        server.login(your_email, your_app_password)
#        server.send_message(msg)
#    print("Email sent successfully.")

def safe_find_text(parent, by, value, default = ""):
    try:
        return parent.find_element(by, value).text.strip()
    except:
        return default
    
def safe_find_attr(parent, by, value, attr, default = ""):
    try:
        return parent.find_element(by, value).get_attribute(attr)
    except:
        return default
    
def clean_image_url(raw_text):
    return re.search(r'url\("(.*?)"\)', raw_text).group(1)

# Laen olemasolevad lingid
if os.path.exists("seen_links.json"):
    with open("seen_links.json", "r") as f:
        seen_links = set(json.load(f))
else:
    seen_links = set()

options = uc.ChromeOptions()
options.headless = False
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Setup chrome webdriver
driver = uc.Chrome(options=options)
print("Driver initialized")

driver.get('https://www.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&f1=2014&g1=10000&g2=23000&l2=130000&ab%5B%5D=-1&ae=1&af=50&otsi=otsi')

# Web page max loading time, to make sure all elements are loaded
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-row")))
print("Cars loaded")

autod_elements = driver.find_elements(By.CLASS_NAME, "result-row")

lingid = []
autod = []

for auto_element in autod_elements:
    try:
        link = safe_find_attr(auto_element, By.CLASS_NAME, "row-link", "href")
        lingid.append(link)
        if link not in seen_links:
            nimi = safe_find_text(auto_element, By.CLASS_NAME, "main")
            aasta = safe_find_text(auto_element, By.CSS_SELECTOR, "div.extra > span.year")
            hind = safe_find_text(auto_element, By.CSS_SELECTOR, "div.finance span.price")  
            mileage = safe_find_text(auto_element, By.CLASS_NAME, "mileage")
            kütus = safe_find_text(auto_element, By.CLASS_NAME, "fuel")
            kast = safe_find_text(auto_element, By.CLASS_NAME, "transmission")
            tüüp = safe_find_text(auto_element, By.CLASS_NAME, "bodytype")
            vedu = safe_find_text(auto_element, By.CLASS_NAME, "drive")
            image_url = clean_image_url(safe_find_attr(auto_element, By.CSS_SELECTOR, "div.thumbnail span.thumb", "style"))

            auto = {
                "nimi": nimi,
                "aasta": aasta,
                "hind": hind,
                "mileage": mileage,
                "kütus": kütus,
                "kast": kast,
                "tüüp": tüüp,
                "vedu": vedu,
                "link": link,
                "image_url": image_url,
            }

            autod.append(auto)

    except Exception as e:
        print("Could not extract car info:", e)

# close the driver
driver.quit()

if autod:
    # send_notification_email(autod) removed for now
    send_telegram_message("Uued autod!")
    send_telegram_messages(autod)
else:
    print("Uusi autosi pole")

with open("seen_links.json", "w") as f:
    json.dump(list(lingid), f)