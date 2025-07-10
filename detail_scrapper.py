import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm

from main_scraper import scrape_job 

# === Load file CSV ===
df = pd.read_csv("batch_01 copy.csv")
urls = df["Job Link"].tolist()
sources = df["source_file"].tolist()
inputs = list(zip(urls, sources))

# === Fungsi pembungkus ===
def scrape_with_source(args):
    url, source_file = args
    result = scrape_job(url)
    result["source_file"] = source_file
    return result

# === Parallel scraping ===
if __name__ == "__main__":
    MAX_WORKERS = 4
    with Pool(processes=MAX_WORKERS) as pool:
        results = list(tqdm(pool.imap_unordered(scrape_with_source, inputs), total=len(inputs)))

    df_result = pd.DataFrame(results)
    df_result.to_csv("scraped_batch_01.csv", index=False, encoding="utf-8-sig")
    print("Selesai, hasil disimpan di scraped_batch_01.csv")
