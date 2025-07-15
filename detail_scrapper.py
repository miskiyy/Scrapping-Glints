import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
from scraper_worker import worker_scrape

if __name__ == "__main__":
    file_name = "batch_01_02.csv"
    df = pd.read_csv(file_name)

    urls = df["Job Link"].tolist()
    sources = df["source_file"].tolist()
    inputs = list(zip(urls, sources))

    MAX_WORKERS = 3

    with Pool(processes=MAX_WORKERS, maxtasksperchild=1) as pool:
        results = list(tqdm(pool.imap_unordered(worker_scrape, inputs), total=len(inputs)))

    df_result = pd.DataFrame(results)
    df_result.to_csv(f"/res/scraped_{file_name}", index=False, encoding="utf-8-sig", sep=";")
    print(f"[info] Selesai, hasil disimpan di scraped_{file_name}")