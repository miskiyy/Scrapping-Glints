from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from selenium.common.exceptions import NoSuchElementException

def get_employment_type(driver):
    keywords = ["Penuh Waktu", "Paruh Waktu", "Magang", "Freelance", "Kontrak"]
    for keyword in keywords:
        try:
            elem = driver.find_element(By.XPATH, f"//div[contains(text(),'{keyword}')]")
            return elem.text.strip()
        except NoSuchElementException:
            continue
    return None

def scrape_job(url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[aria-label="Job Title"]'))
        )
        time.sleep(3)  # nunggu render JS

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        posisi = soup.select_one('h1[aria-label="Job Title"]')
        company = soup.select_one('a[href*="/id/companies/"]')
        lokasi = None
        for a in soup.select('a[href*="/id/job-location/"]'):
            href = a.get('href', '')
            if href.count('/') == 5:  # struktur: /id/job-location/indonesia/dki-jakarta
                lokasi = a.get_text(strip=True)
                break

        industry = soup.select_one('a[href*="/id/job-category/"]')
        # employment_type = driver.find_element(By.XPATH, "//div[contains(text(),'Penuh Waktu')]").text
        employment_type = get_employment_type(driver)
        description = soup.select_one('div.DraftjsReadersc__ContentContainer-sc-zm0o3p-0')
        requirements = soup.select('div.JobRequirementssc__TagsWrapper-sc-15g5po6-2 div.TagStyle__TagContentWrapper-sc-r1wv7a-1')
        skills_raw = soup.select('div.TagStyle__TagContentWrapper-sc-r1wv7a-1, label.tag-content, span.tag-content, div.tag-content')

        # === JavaScript injection utk salary & tanggal posting ===
        salary = driver.execute_script("""
            const spans = document.querySelectorAll('span');
            for (let s of spans) {
                if (s.innerText.includes("IDR")) return s.innerText;
            }
            return null;
        """)
        # tanggal_posting = driver.execute_script("""
        #     const spans = document.querySelectorAll('span');
        #     for (let s of spans) {
        #         if (s.innerText.includes("Lowongan ini")) return s.innerText;
        #     }
        #     return null;
        # """)
        return {
            "url": url,
            "posisi": posisi.get_text(strip=True) if posisi else None,
            "company": company.get_text(strip=True) if company else None,
            "lokasi": lokasi,
            "industry": industry.get_text(strip=True) if industry else None,
            "employment_type": employment_type,
            # "tanggal_posting": tanggal_posting or None,
            "salary": salary or None,
            "description": description.get_text(" ", strip=True) if description else None,
            "requirements": ", ".join([r.get_text(strip=True) for r in requirements]) if requirements else None,
            "skills": ", ".join([s.get_text(strip=True) for s in skills_raw]) if skills_raw else None,
        }

    except Exception as e:
        return {"url": url, "error": str(e)}
    finally:
        driver.quit()
        time.sleep(random.uniform(1.5, 3.0))
