from concurrent.futures import ProcessPoolExecutor, as_completed
import time

def run_worker(job_keyword):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from bs4 import BeautifulSoup
    import logging
    from selenium.webdriver.remote.remote_connection import LOGGER
    LOGGER.setLevel(logging.WARNING)  # Atau ERROR biar lebih senyap
    import pandas as pd
    import os
    import re

    email = "ayamiskiyah46@gmail.com"
    password = ""
    path_to_driver = r"C:/chromedriver/chromedriver.exe"
    csv_path = f"job_links_{job_keyword.replace(' ', '_')}.csv"

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--log-level=3")  

    driver = webdriver.Chrome(service=Service(path_to_driver), options=chrome_options)

    try:
        driver.get("https://glints.com/id")
        time.sleep(5)

        driver.find_element(By.XPATH, '//button[span[text()="Masuk"]]').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//a[span[text()="Masuk dengan Email"]]').click()
        time.sleep(2)

        driver.find_element(By.ID, "login-form-email").send_keys(email)
        driver.find_element(By.ID, "login-form-password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@data-cy="submit_btn_login"]').click()
        time.sleep(5)
        print(f"[{job_keyword}] Logged in")

        try:
            driver.find_element(By.CLASS_NAME, "sKTdp").click()
            time.sleep(2)
        except:
            pass

        search_input = driver.find_element(By.XPATH, '//input[@placeholder="Cari Nama Pekerjaan, Skill, dan Perusahaan"]')
        search_input.clear()
        search_input.send_keys(job_keyword)
        search_input.send_keys(Keys.ENTER)
        time.sleep(5)

        prev_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, '//button[@data-testid="close-button"]').click()
            except:
                pass
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == prev_height:
                break
            prev_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("a", href=re.compile("^/id/opportunities/jobs/"))
        links = ["https://glints.com" + a["href"] for a in job_cards]
        links = list(dict.fromkeys(links))

        df = pd.DataFrame(links, columns=["Job Link"])
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[{job_keyword}] {len(links)} job links saved to {csv_path}")

    except Exception as e:
        print(f"[{job_keyword}] Error: {e}")
    finally:
        driver.quit()


# Pake max 3 worker
job_keywords = [
    # Tech & Data
    # "Software Engineer", "Backend Developer", "Frontend Developer", "Full Stack Developer",
    # "Mobile Developer", "Data Analyst", "Data Scientist", "Machine Learning", "Cyber Security",
    # "DevOps Engineer", "QA Engineer", "IT Support", "Database Administrator", "Product Manager",

    # # UI/UX & Creative
    # "UI Designer", "UX Designer", "Graphic Designer", "Creative Designer", "Motion Designer",
    # "Illustrator", "Video Editor", "Animator", "3D Artist", "Content Creator",

    # # Business & Management
    # "Business Analyst", "Project Manager", "Business Development", "Operations Manager",
    # "Sales Executive", 
    "Account Executive", "Partnership Manager", "Consultant",
    "Product Owner", "Scrum Master", "Strategy Analyst",

    # Marketing & Communications
    "Digital Marketing", "Content Writer", "Copywriter", "SEO Specialist", "Marketing Strategist",
    "Social Media Specialist", "PR Specialist", "Brand Manager", "Market Research",

    # Finance & Legal
    "Finance Officer", "Accounting Staff", "Tax Consultant", "Auditor", "Financial Analyst",
    "Investment Analyst", "Risk Analyst", "Legal Officer", "Corporate Secretary", "Compliance Officer",

    # HR & GA
    "HR Generalist", "HRBP", "Talent Acquisition", "Recruiter", "People Development",
    "Training Specialist", "Payroll Staff", "Office Manager", "GA Staff",

    # Education & Training
    "Teacher", "Private Tutor", "Curriculum Developer", "Instructional Designer", 
    "Education Consultant", "Trainer", "Mentor", "Counselor",

    # Healthcare & Labs
    "Nurse", "Doctor", "Pharmacist", "Nutritionist", "Medical Staff", "Lab Analyst",
    "Health Analyst", "Radiographer", "Clinical Researcher",

    # F&B & Hospitality
    "Chef", "Barista", "Cook", "Waiter", "Kitchen Staff", "Bartender",
    "Hotel Receptionist", "Housekeeping", "Event Organizer",

    # Manufacturing & Logistics
    "Production Staff", "Warehouse Staff", "Procurement", "Quality Control",
    "Logistics", "Supply Chain", "Maintenance Engineer", "Mechanical Engineer",

    # Design & Architecture
    "Interior Designer", "Architect", "Draftsman", "Civil Engineer", "Urban Planner",

    # Customer Support
    "Customer Service", "Call Center", "Telemarketing", "Client Support", "Technical Support",

    # Entry-level & Internship
    "Intern", "Magang", "Fresh Graduate", "Admin", "Office Assistant", "Staff",
    "Receptionist", "Data Entry", "Junior Staff", "Student Intern"
]

from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor, as_completed

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_worker, keyword): keyword for keyword in job_keywords}
        
        for future in as_completed(futures):
            keyword = futures[future]
            try:
                future.result(timeout=300)  # Timeout per task di executor
            except Exception as e:
                print(f"[{keyword}] ❌ Error: {e}")
