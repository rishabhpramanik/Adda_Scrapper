import json
import logging
import time

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Initialize the Webdriver
try:
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)
    logging.info("Webdriver initialized successfully")
except Exception as e:
    logging.error(f"Webdriver initialization failed: {e}")
    exit(1)

# Navigating to the target webpage
url = "https://www.adda247.com/live-classes"
try:
    driver.get(url)
    logging.info(f"Navigated to {url}")
# Store main window handle
    main_window = driver.current_window_handle
    logging.info("Main window handle stored")
except Exception as e:
    logging.error(f"Failed to load page: {e}")
    driver.quit()
    exit(1)

# Scrolling and wait for the element to be loaded
def load_all_courses_full_scroll():
    logging.info("Starting full page scroll to load all courses")
    last_height = driver.execute_script("return document.body.scrollHeight")
    retries = 0
    max_retries = 3

    while retries < max_retries:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Wait for content to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            retries += 1
            logging.info(f"No new content detected. Retry {retries}/{max_retries}")
        else:
            retries = 0
            last_height = new_height
            logging.info("New content loaded, scrolling again...")

    logging.info("Finished scrolling. All content should now be loaded.")

# Scrolling and loading elements
load_all_courses_full_scroll()

# Getting the total pages and storing them into list
courses = driver.find_elements(By.XPATH, "//a[@class='listingCardBoxCard ']")
# total = len(courses) Uncomment to scrape all the courses
total = 20

batch_size = 20

course_title = ""
highlight_text = []
exam_cover_text = []
inclusions = []
courses_data = []

# Clicking on each course and navigating to new window
for i in range(0, total, batch_size):
    batch = courses[i:i + batch_size]
    logging.info("Opening 4 tabs for scrapping")

    # Open tabs
    for element in batch:
        ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        time.sleep(1)

    # Get all tabs
    all_tabs = driver.window_handles

    # Only keep the newly opened ones
    new_tabs = [tab for tab in all_tabs if tab != main_window]

    logging.info("Scrapping each tab and closing")
    # =======================Scrape and close each new tab=======================
    for tab in new_tabs:
        driver.switch_to.window(tab)
        time.sleep(2)  # wait for content to load
        print("Title:", driver.title)
        course_title = driver.title

        # =======================Scrapping Course Highlight=======================
        logging.info("Scrapping product highlight")
        highlights = driver.find_elements(By.XPATH, "//div[@class='pdpHighlightFullBox']/ul/li")
        for highlight in highlights:
            highlight_text.append(highlight.text)
        print(highlight_text)


        # =======================Scrapping the Exam Covers=======================
        logging.info("Scrapping product exam_coverage")

        # Finding the Show More button
        # If not found the list will be empty, Exception will not be thrown
        show_more = driver.find_elements(By.XPATH, "//span[contains(text(),'Show more')]")

        if show_more:
            element = driver.find_element(By.XPATH, "//span[contains(text(),'Show more')]")
            driver.execute_script("arguments[0].click();", element)
        else:
            logging.info("No Show more button found, continuing")

        exam_coverage = driver.find_elements(By.XPATH, "//div[@class='ExamCoverName']")
        for exam_cover in exam_coverage:
            exam_cover_text.append(exam_cover.text)
        print(exam_cover_text)


        # =======================Scrapping Course Inclusions=======================
        inclusions_elements = driver.find_elements(By.XPATH, "//div[@class='pdpIncludeList']/ul/li")
        for inclusion_element in inclusions_elements:
            inclusions.append(inclusion_element.text)
        print(inclusions)

        # =======================Saving the data in JSON format=======================
        course_info = {
            "title": course_title,
            "product_highlights": highlight_text,
            "exam_covers": exam_cover_text,
            "this_course_includes": inclusions
        }
        courses_data.append(course_info)

        driver.close()  # close this tab

    # Switch back to main tab
    driver.switch_to.window(main_window)
    time.sleep(1)
driver.quit()

try:
    with open("adda247_courses_info.json", "w", encoding="utf-8") as f:
        json.dump(courses_data, f, indent=4, ensure_ascii=False)
    logging.info("Courses exported to 'adda247_courses.json'")
except Exception as e:
    logging.error(f"Error saving JSON: {e}")





