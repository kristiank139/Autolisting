# import module
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

import re # Vajalik eriliste tähemärkide asendamiseks

def send_notification_email(cars_dict):
    # Create the email
    msg = MIMEMultipart("alternatice")
    msg["Subject"] = "Uued autod!"
    msg["From"] = "kristiank139@gmail.com"
    msg["To"] = "kristiankoivastik@gmail.com"

     # Construct HTML body
    html_body = "<h2>Siin on uued lisatud autod:</h2><ul>"
    for car in cars_dict:
        html_body += f"""
        <li style="margin-bottom: 15px;">
            <strong>{car['nimi']}</strong><br>
            Year: {car['aasta']}<br>
            Price: €{car['hind']}<br>
            Mileage: {car['mileage']} km<br>
            Fuel: {car['kütus']}<br>
            Transmission: {car['kast']}<br>
            Drive: {car['vedu']}<br>
            Type: {car['tüüp']}<br>
            <a href="{car['link']}">View listing</a><br>
            {'<img src="'+car["image_url"]+'" alt="Car image" style="width:300px;margin-top:5px;">' if 'image_url' in car else ''}
        </li>
        """
    html_body += "</ul>"

    msg.attach(MIMEText(html_body, "html"))

    # Gmail SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    your_email = "kristiank139@gmail.com"
    your_app_password = "cmaf yfso vfpq qnnh"  # Not your normal Gmail password

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(your_email, your_app_password)
        server.send_message(msg)
    print("Email sent successfully.")

# Laen olemasolevad lingid
if os.path.exists("seen_links.json"):
    with open("seen_links.json", "r") as f:
        seen_links = set(json.load(f))
else:
    seen_links = set()

#setup chrome webdriver
driver = uc.Chrome(version_main=116, headless=False) # If it starts crashing again, just download chromium
print("Driver initialized")

driver.get('https://www.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&f1=2014&g1=10000&g2=23000&l2=130000&ab%5B%5D=-1&ae=1&af=50&otsi=otsi')

# web page max loading time, to make sure all elements are loaded
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-row")))
print("Cars loaded")

autod_elements = driver.find_elements(By.CLASS_NAME, "result-row")

lingid = []
autod = []

for auto_element in autod_elements:
    try:
        nimi = auto_element.find_element(By.CLASS_NAME, "main").text.strip()
        aasta = auto_element.find_element(By.CLASS_NAME, "year").text.strip()
        
        hind = auto_element.find_element(By.CLASS_NAME, "price").text.strip()
        uus_hind = re.sub(r"[^\d]", "", hind)
        try:
            mileage = auto_element.find_element(By.CLASS_NAME, "mileage").text.strip()
        except:
            mileage = "Teadmata"

        uus_mileage = re.sub(r"[^\d]", "", mileage)

        try:
            kütus = auto_element.find_element(By.CLASS_NAME, "fuel").text.strip()
        except:
            kütus = "Määramata"

        kast = auto_element.find_element(By.CLASS_NAME, "transmission").text.strip()
        tüüp = auto_element.find_element(By.CLASS_NAME, "bodytype").text.strip()
        vedu = auto_element.find_element(By.CLASS_NAME, "drive").text.strip()   
        link = auto_element.find_element(By.CLASS_NAME, "row-link").get_attribute("href")  
        
        lingid.append(link)
        auto = {
            "nimi": nimi,
            "aasta": aasta,
            "hind": uus_hind,
            "mileage": uus_mileage,
            "kütus": kütus,
            "kast": kast,
            "tüüp": tüüp,
            "vedu": vedu,
            "link": link
        }

        autod.append(auto)

    except Exception as e:
        print("Could not extract detail:", e)

# close the driver
driver.quit()

# Siia tulevad uute listingute lingid
uued_lingid = []

for link in lingid:
    if link not in seen_links:
        uued_lingid.append(link)
    else:
        break

send_notification_email(" ".join(uued_lingid))

with open("seen_links.json", "w") as f:
    json.dump(list(lingid), f)


print(lingid)