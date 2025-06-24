# Features to add: car location info

# Import module
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Json faili jaoks
import json

import os
import re

def send_notification_email(cars_dict):
    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Uued autod!"
    msg["From"] = "kristiank139@gmail.com"
    msg["To"] = "kristiankoivastik@gmail.com"

     # Construct HTML body
    html_body = "<h2>Siin on uued lisatud autod:</h2><ul>"
    for car in cars_dict:
        html_body += f"""
        <li style="margin-bottom: 15px;">
            <strong>{car['nimi']}</strong><br>
            Aasta: {car['aasta']}<br>
            Hind: {car['hind']}<br>
            Läbisõit: {car['mileage']}<br>
            Kütus: {car['kütus']}<br>
            Käigukast: {car['kast']}<br>
            Vedu: {car['vedu']}<br>
            Keretüüp: {car['tüüp']}<br>
            <a href="{car['link']}">View listing</a><br>
            {'<img src="'+car["image_url"]+'" alt="Car image" style="width:300px;margin-top:5px;">' if 'image_url' in car else ''}
        </li>
        """

    html_body += "</ul>"

    msg.attach(MIMEText(html_body, "html"))

    # Gmail SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    your_email = os.getenv("GMAIL_USER")
    your_app_password = os.getenv("GMAIL_PASSWORD") 

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(your_email, your_app_password)
        server.send_message(msg)
    print("Email sent successfully.")

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

# Laen olemasolevad lingid
if os.path.exists("seen_links.json"):
    with open("seen_links.json", "r") as f:
        seen_links = set(json.load(f))
else:
    seen_links = set()

# Setup chrome webdriver
driver = uc.Chrome(headless=True) # If it starts crashing again, just download chromium
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
            unclean_image_url = safe_find_attr(auto_element, By.CSS_SELECTOR, "div.thumbnail span.thumb", "style")
            clean_image_url = re.search(r'url\("(.*?)"\)', unclean_image_url).group(1) # Clean up the raw attribute into an url

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
                "image_url": clean_image_url,
            }

            autod.append(auto)

    except Exception as e:
        print("Could not extract car info:", e)

# close the driver
driver.quit()

print(autod)
send_notification_email(autod)

with open("seen_links.json", "w") as f:
    json.dump(list(lingid), f)