import streamlit as st

st.set_page_config(page_title="Browser Automation & Scraping", page_icon="🤖", layout="wide")

st.title("🤖 Browser Automation & Scraping with Selenium")
st.caption("AI-powered web automation with LangSmith observability — scraping, screenshots, and login flows. Interactive explainer below.")

st.info(
    "**Note:** Browser automation (Selenium) requires a local Chrome/Firefox driver and cannot run in a cloud sandbox. "
    "This demo explains the architecture, shows real code from the project, and lets you explore what the agent does step-by-step. "
    "Clone the repo to run it locally with full automation.",
    icon="ℹ️"
)

tab1, tab2, tab3 = st.tabs(["Architecture", "Live Code Walkthrough", "What It Does"])

with tab1:
    st.markdown("### Automation Architecture")
    st.markdown("""
```
User Request
     ↓
 LangSmith Tracer  ←─────────────────────────────────┐
     ↓                                                 │
 Selenium WebDriver                                    │ observability
     ├─ Chrome browser (headless)                      │ trace every step
     ├─ Navigate to target URL                         │
     ├─ Wait for elements (explicit waits)             │
     ├─ Extract data (BeautifulSoup)                   │
     └─ Screenshot at each step                        │
          ↓                                            │
     Structured output (JSON / DataFrame) ────────────┘
          ↓
     LangSmith dashboard — full trace with latency, errors, screenshots
```
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Core Components")
        st.markdown("""
- **Selenium 4.x** — browser control (click, scroll, fill forms, screenshot)
- **BeautifulSoup 4** — HTML parsing and structured extraction
- **webdriver-manager** — auto-installs matching ChromeDriver
- **LangSmith** — end-to-end trace observability for agent decisions
- **yfinance** — live financial data (no browser scraping needed for structured APIs)
        """)
    with col2:
        st.markdown("#### Use Cases Automated")
        st.markdown("""
1. **Web scraping** — RSS feed extraction, article metadata
2. **Screenshot capture** — visual verification at each step
3. **Login flows** — form fill, submit, session persistence
4. **Data extraction** — table parsing, pagination handling
5. **Financial data** — yfinance integration for live market data
        """)

with tab2:
    st.markdown("### Real Code from the Project")

    script = st.selectbox("Select a script to view:", [
        "Browser setup & navigation",
        "BeautifulSoup extraction",
        "LangSmith tracing",
        "Screenshot capture",
    ])

    code_map = {
        "Browser setup & navigation": """from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def navigate_and_wait(driver, url: str, wait_selector: str):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
    )
    return driver.page_source""",

        "BeautifulSoup extraction": """from bs4 import BeautifulSoup
import feedparser

def scrape_rss_feed(url: str) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:10]:
        articles.append({
            "title":     entry.get("title", ""),
            "link":      entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary":   BeautifulSoup(
                             entry.get("summary", ""), "html.parser"
                         ).get_text()[:300]
        })
    return articles

def extract_table(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return []
    headers = [th.text.strip() for th in table.find_all("th")]
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.text.strip() for td in tr.find_all("td")]
        if cells:
            rows.append(dict(zip(headers, cells)))
    return rows""",

        "LangSmith tracing": """from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI())  # auto-traces all API calls

@traceable(name="scrape_and_analyze")
def scrape_and_analyze(url: str, question: str) -> str:
    # LangSmith records: inputs, outputs, latency, errors
    articles = scrape_rss_feed(url)
    context = "\\n".join([f"{a['title']}: {a['summary']}" for a in articles])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Analyze the scraped content."},
            {"role": "user",   "content": f"{question}\\n\\nContent:\\n{context}"}
        ]
    )
    return response.choices[0].message.content

# View traces at: https://smith.langchain.com""",

        "Screenshot capture": """from selenium.webdriver.common.by import By
from PIL import Image
import io, base64

def capture_screenshot(driver, filename: str = "step.png") -> bytes:
    png = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(png))
    img.save(filename)
    return png

def capture_element_screenshot(driver, selector: str) -> bytes:
    element = driver.find_element(By.CSS_SELECTOR, selector)
    return element.screenshot_as_png

def full_page_screenshot(driver) -> bytes:
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1920, total_height)
    return driver.get_screenshot_as_png()""",
    }

    st.code(code_map[script], language="python")

with tab3:
    st.markdown("### Step-by-Step Automation Flow")

    steps = [
        ("1. Initialize", "ChromeDriver launched in headless mode. LangSmith tracer attached to capture every step.", "✅"),
        ("2. Navigate",   "Browser opens the target URL. Explicit wait until key element appears (avoids flaky timing).", "✅"),
        ("3. Extract",    "BeautifulSoup parses the page HTML. Tables, lists, and article blocks are pulled into structured dicts.", "✅"),
        ("4. Screenshot", "Screenshot captured after each major action. Stored locally and referenced in LangSmith trace.", "✅"),
        ("5. Analyze",    "Scraped content passed to GPT-4o-mini with a user question. Response grounded in extracted data.", "✅"),
        ("6. Observe",    "LangSmith dashboard shows full execution trace: inputs, outputs, latency per step, any errors.", "✅"),
    ]

    for title, detail, status in steps:
        with st.expander(f"{status} {title}"):
            st.write(detail)

    st.markdown("---")
    st.markdown("#### Run It Locally")
    st.code("""git clone https://github.com/ashishk-yadav/AI-portfolio.git
cd ai-agent-bootcamp/session-06-browser-automation
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../../.env.example .env   # add LANGSMITH_API_KEY
python scraper.py            # runs full automation""", language="bash")
