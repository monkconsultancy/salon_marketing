from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def send_whatsapp_message(contact, message):
    driver = webdriver.Chrome()
    driver.get('https://web.whatsapp.com')
    input("Scan QR and press Enter...")

    search_box = driver.find_element(By.XPATH, '//div[@title="Search input textbox"]')
    search_box.send_keys(contact)
    time.sleep(2)
    
    contact_sel = driver.find_element(By.XPATH, f'//span[@title="{contact}"]')
    contact_sel.click()
    time.sleep(2)

    msg_box = driver.find_element(By.XPATH, '//div[@title="Type a message"]')
    msg_box.send_keys(message)

    send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
    send_button.click()
    time.sleep(2)
    driver.quit()

# Example
send_whatsapp_message("+918291624732", "Hey! Thank you for visiting! 🌟 Here's a 10% discount on your next visit.")
