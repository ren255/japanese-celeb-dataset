# Scrapy settings for wiki_scrape project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "wiki_scrape"

SPIDER_MODULES = ["wiki_scrape.spiders"]
NEWSPIDER_MODULE = "wiki_scrape.spiders"

ADDONS = {}


USER_AGENT = "NameCrawler/1.0 (+https://rentoda.com)"

ROBOTSTXT_OBEY = False

# 200 req/min = 3.33 req/s に収める
# 並列4 × delay0.3s = 約3.3 req/s
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 4

DOWNLOAD_DELAY = 0.3

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.3
AUTOTHROTTLE_MAX_DELAY = 10  # 429来たら最大10s待つ
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

RETRY_HTTP_CODES = [429, 500, 502, 503, 504]
RETRY_TIMES = 5


# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "wiki_scrape.middlewares.WikiScrapeSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "wiki_scrape.middlewares.WikiScrapeDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "wiki_scrape.pipelines.ItemProcess": 800,
    "wiki_scrape.pipelines.CsvExportPipeline": 900,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"


LOG_ENABLED = True
LOG_LEVEL = "INFO"
LOG_FILE = "log/scrapy.log"  # ログファイル名（Noneならコンソール）
LOG_FILE_APPEND = False  # Trueなら追記、Falseなら上書き
LOG_ENCODING = "utf-8"
