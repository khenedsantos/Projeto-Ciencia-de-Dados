from pathlib import Path
from src.ctps_pipeline import download_sources

if __name__ == "__main__":
    print(download_sources(Path("data/raw")))
