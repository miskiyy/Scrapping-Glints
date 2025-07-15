from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep

class Scraper:
    def __init__(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--blink-settings=imagesEnabled=false')  # extra image disabling
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        })
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

    def get_employment_type(self):
        keywords = ["Penuh Waktu", "Paruh Waktu", "Magang", "Freelance", "Kontrak", "Harian"]
        for keyword in keywords:
            try:
                elem = self.driver.find_element(By.XPATH, f"//div[contains(text(),'{keyword}')]")
                return elem.text.strip()
            except NoSuchElementException:
                continue
        return None

    def scrape_job(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[aria-label="Job Title"]'))
            )
            sleep(3)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            posisi = soup.select_one('h1[aria-label="Job Title"]')
            company = soup.select_one('a[href*="/id/companies/"]')
            lokasi = None
            for a in soup.select('a[href*="/id/job-location/"]'):
                href = a.get('href', '')
                if href and href.count('/') == 5:
                    lokasi = a.get_text(strip=True)
                    break

            industry = soup.select_one('a[href*="/id/job-category/"]')
            employment_type = self.get_employment_type()
            description = soup.select_one('div.DraftjsReadersc__ContentContainer-sc-zm0o3p-0')
            requirements = soup.select('div.JobRequirementssc__TagsWrapper-sc-15g5po6-2 div.TagStyle__TagContentWrapper-sc-r1wv7a-1')
            skills_raw = soup.select('div.TagStyle__TagContentWrapper-sc-r1wv7a-1, label.tag-content, span.tag-content, div.tag-content')

            salary = self.driver.execute_script("""
                const spans = document.querySelectorAll('span');
                for (let s of spans) {
                    if (s.innerText.includes("IDR")) return s.innerText;
                }
                return null;
            """)

            return {
                "url": url,
                "posisi": posisi.get_text(strip=True) if posisi else None,
                "company": company.get_text(strip=True) if company else None,
                "lokasi": lokasi,
                "industry": industry.get_text(strip=True) if industry else None,
                "employment_type": employment_type,
                "salary": salary or None,
                "description": description.get_text(" ", strip=True) if description else None,
                "requirements": ", ".join([r.get_text(strip=True) for r in requirements]) if requirements else None,
                "skills": ", ".join([s.get_text(strip=True) for s in skills_raw]) if skills_raw else None,
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {"url": url, "error": str(e)}

    def close(self):
        if self.driver:
            self.driver.quit()

def worker_scrape(args):
    url, source_file = args
    scraper = Scraper()
    try:
        result = scraper.scrape_job(url)
        result["source_file"] = source_file
        return result
    except Exception as e:
        return {"url": url, "source_file": source_file, "error": str(e)}
    finally:
        scraper.close()