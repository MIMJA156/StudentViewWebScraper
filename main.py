import getpass

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


def begin(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Firefox()

    driver.get("https://pvue.psdschools.org/PXP2_Login_Student.aspx?regenerateSessionId=True")
    assert "StudentVUE" in driver.title
    username_text_field = driver.find_element(By.ID, "ctl00_MainContent_username")
    username_text_field.clear()
    username_text_field.send_keys(username)

    password_text_field = driver.find_element(By.ID, "ctl00_MainContent_password")
    password_text_field.clear()
    password_text_field.send_keys(password)
    password_text_field.send_keys(Keys.RETURN)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainnav"]/div/a[9]')))
    grade_book_tab = driver.find_element(By.XPATH, '//*[@id="mainnav"]/div/a[9]')
    grade_book_tab.click()

    schools = driver.find_element(By.XPATH, '//*[@id="gb-classes"]').find_elements(By.CLASS_NAME, "update-panel")

    for school in schools:
        school_classes = school.find_elements(By.CLASS_NAME, 'row')

        for school_class in school_classes:
            print(school_class.text.strip())
            print("-" * 50)

    driver.quit()


given_username = input("Username: ")
given_password = getpass.getpass("Password: ")
print("-" * 50)
begin(given_username, given_password)
