import getpass
import time
import json

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


def get_details(soup):
    assignment_table = soup.find("tbody", recursive=True)

    assignments = []
    for row in assignment_table.findAll('tr')[:-1]:
        cols = row.findAll('td')
        assignments.append(cols)

    return assignments


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

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainnav"]/div/a[9]')))
    grade_book_tab = driver.find_element(By.XPATH, '//*[@id="mainnav"]/div/a[9]')
    grade_book_tab.click()

    grade_book_soup = BeautifulSoup(driver.page_source, features="html.parser")
    school_class_lists = grade_book_soup.find_all("div", class_="update-panel")

    data = []
    for school in school_class_lists:
        data_rows = school.find_all("div", class_="row")

        for row in data_rows:
            classes = row["class"]
            if "gb-class-header" in classes:
                data.append([])
                class_name = row.find("button", recursive=True).text
                teacher = row.find("div", class_="teacher", recursive=True).text
                room = row.find("div", class_="teacher-room", recursive=True).text

                data[-1].append(class_name)
                data[-1].append(teacher)
                data[-1].append(room)
            else:
                score = row.find("span", class_="score").text
                data[-1].append(score)

    enrolled_classes_header = len(driver.find_elements(By.CLASS_NAME, "gb-class-header"))
    for i in range(enrolled_classes_header):
        header = driver.find_elements(By.CLASS_NAME, "gb-class-header")
        header[i].find_element(By.TAG_NAME, "button").click()

        time.sleep(.5)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ctl00_CategoryWeights")))

        raw_grade_weight = driver.find_element(By.ID, "ctl00_CategoryWeights").get_attribute("data-data-source")
        if raw_grade_weight:
            formatted_info = json.loads(str(driver.find_element(By.ID, "ctl00_CategoryWeights").get_attribute("data-data-source")))
            gathered_info = {}
            for i_2 in range(len(formatted_info)):
                assignment_category = formatted_info[i_2]["Category"]
                assignment_pct_of_grade = formatted_info[i_2]["PctOfGrade"]
                gathered_info[assignment_category] = assignment_pct_of_grade

            data[i].append(gathered_info)
        else:
            data[i].append(None)

        try:
            assignment_table = driver.find_element(By.XPATH, '//*[@id="AssignmentsGrid"]/div/div[6]/div/div/div[1]/div/table/tbody')
            data[i].append([])
            for assignment in assignment_table.find_elements(By.CLASS_NAME, "dx-data-row"):
                data[i][-1].append(assignment.text.split("\n"))

            if len(data[i][-1]) == 0:
                data[i].pop()
                data[i].append(None)
        except selenium.common.exceptions.NoSuchElementException:
            data[i].append(None)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "GradebookHeader")))
        driver.find_element(By.ID, "GradebookHeader").find_element(By.TAG_NAME, "a").click()

    driver.quit()

    return data


def format_data(grade_object):
    formatted_grade_data = []

    for i in grade_object:
        empty = {"name": i[0], "grade": i[3], "weighting": i[4]}

        if isinstance(i[5], list):
            empty["assignments"] = []

            for i_2 in i[5]:
                assignment = {"name": i_2[1], "type": i_2[2].replace("0", "").replace(" ", "")}
                score_total = i_2[3].split(" out of ")

                if score_total[0] != "Not Due" and score_total[0] != "Not Graded":
                    assignment["score"] = score_total[0]
                    assignment["total"] = score_total[1]
                else:
                    assignment["assignments"] = score_total[0]

                empty["assignments"].append(assignment)

        formatted_grade_data.append(empty)

    return formatted_grade_data


given_username = input("Username: ")
given_password = getpass.getpass("Password: ")

grade_data = begin(given_username, given_password)
formatted_data = format_data(grade_data)

file1 = open("./data.json", "w")
file1.write(json.dumps(formatted_data))
file1.close()

print("saved to data.json")
