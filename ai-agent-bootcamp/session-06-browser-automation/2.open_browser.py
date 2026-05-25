#pip install selenium

# Selenium doesn't talk to browser directly, you need to use specific browser drivers
from selenium import webdriver
import time

#driver = webdriver.Firefox()
driver = webdriver.Chrome()
# wait of 10 seconds
time.sleep(10)
driver.close()
