import time

from selenium import webdriver
from selenium.webdriver.common.by import By

def selenium_automation():
    #Set up WebDriver (Make sure you have the correct WebDriver installed)
    driver = webdriver.Chrome()
    driver.get("https://www.saucedemo.com/")

    # Fill the login form
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    time.sleep(4)
    driver.find_element(By.ID, "password").send_keys("secret_sauce1")
    time.sleep(4)
    driver.find_element(By.ID, "login-button").click()
    time.sleep(1)  # Wait for page to load

    # Take a screenshot
    driver.save_screenshot("login_error.png")
    print(f"Screenshot saved")

    #Extract product names
    products = driver.find_elements(By.CLASS_NAME, "inventory_item_name")
    for product in products:
        print("Product:", product.text)

if __name__ == "__main__":
    selenium_automation()
