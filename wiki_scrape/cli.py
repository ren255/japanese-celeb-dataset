import subprocess
import sys
from pathlib import Path
from wiki_scrape import format as fmt
import argparse

WIKI_SCRAPE_DIR = Path(__file__).parent


def run_scrapy(spider_name, cwd):
    subprocess.run(["scrapy", "crawl", spider_name], cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--lib-path",
        default=None,
        help="wiki_scrapeパッケージのディレクトリ（scrapy.cfgがある場所）",
    )
    args = parser.parse_args()

    if args.lib_path:
        wiki_scrape_dir = Path(args.lib_path)
    else:
        wiki_scrape_dir = Path(__file__).parent  # ローカル開発時

    run_scrapy("wiki_sub_category", cwd=wiki_scrape_dir)
    run_scrapy("wiki_category_page", cwd=wiki_scrape_dir)
    run_scrapy("person_page", cwd=wiki_scrape_dir)

    from wiki_scrape import format as fmt

    output = args.output or str(Path.cwd() / "data.csv")
    fmt.run(output_path=output)


if __name__ == "__main__":
    main()
