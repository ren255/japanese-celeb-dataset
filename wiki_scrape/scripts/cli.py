import subprocess
from pathlib import Path
from wiki_scrape.scripts import format as fmt
import argparse

WIKI_SCRAPE_DIR = Path(__file__).parent


def run_scrapy(spider_name, cwd, data_path):
    subprocess.run(
        ["scrapy", "crawl", spider_name, "-s", f"DATA_DIR={data_path}"],
        cwd=cwd,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--lib-path",
        default=None,
        help="wiki_scrapeパッケージのディレクトリ（scrapy.cfgがある場所）",
    )
    args = parser.parse_args()

    wiki_scrape_dir = Path(args.lib_path).resolve()
    output_dir = Path(args.output).resolve()
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    print("running wiki_sub_category")
    run_scrapy("wiki_sub_category", cwd=wiki_scrape_dir, data_path=output_dir)
    print("running wiki_category_page")
    run_scrapy("wiki_category_page", cwd=wiki_scrape_dir, data_path=output_dir)
    print("running person_page")
    run_scrapy("person_page", cwd=wiki_scrape_dir, data_path=output_dir)

    output = output_dir / "data.csv" or str(Path.cwd() / "data.csv")
    print(f"running format {output=},{wiki_scrape_dir=}")
    fmt.run(output_path=output)


if __name__ == "__main__":
    main()
