import os
import re
import requests
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------- Configuration ----------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

IMAGE_DIR = "course_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

options = Options()
options.add_argument("--headless")  # comment this line to see the browser
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# ---------------------- Initialize Driver ----------------------

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    logging.info("WebDriver initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize WebDriver: {e}")
    exit(1)

# ---------------------- Navigate ----------------------

url = "https://www.adda247.com/live-classes"
try:
    driver.get(url)
    logging.info(f"Navigated to {url}")
except Exception as e:
    logging.error(f"Failed to navigate: {e}")
    driver.quit()
    exit(1)

# ---------------------- Scroll Logic ----------------------

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

# ---------------------- Run Scroll ----------------------

load_all_courses_full_scroll()

# ---------------------- Wait for Courses ----------------------

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'listingCardBox')]"))
    )
    logging.info("Course cards detected")
except Exception as e:
    logging.error(f"Course cards not detected: {e}")
    driver.quit()
    exit(1)

# ---------------------- Extract Data ----------------------

courses = driver.find_elements(By.XPATH, "//div[contains(@class, 'listingCardBox')]")
logging.info(f"Total courses found: {len(courses)}")

courses_data = []

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

for index, course in enumerate(courses, 1):
    try:
        name = course.find_element(By.XPATH,".//h3[contains(@class, 'listingCardTitle')] | .//div[contains(@class, 'title')] | .//p[contains(@class, 'title')] | .//span[contains(@class, 'title')]"
        ).text.strip()
    except:
        name = "N/A"

    try:
        price = course.find_element(By.XPATH,".//div[contains(@class, 'listCardMainPrice')] | .//span[contains(@class, 'price')]"
        ).text.strip()
    except:
        price = "N/A"

    try:
        original_price = course.find_element(By.XPATH,".//div[contains(@class, 'listCardCutPrice')] | .//span[contains(@class, 'original-price')]"
        ).text.strip()
    except:
        original_price = ""

    try:
        discount = course.find_element(By.XPATH,".//div[contains(@class, 'listCardTotalOff')] | .//span[contains(@class, 'discount')]"
        ).text.strip()
    except:
        discount = "No Discount"

    try:
        language = course.find_element(By.XPATH,".//div[contains(@class, 'listingCardLangTag')] | .//span[contains(@class, 'language')]"
        ).text.strip()
    except:
        language = "N/A"

    try:
        image = course.find_element(By.XPATH,".//img")
        image_url = image.get_attribute("src")
    except:
        image_url = "N/A"

    # Download image
    image_filename = sanitize_filename(name) + ".jpg"
    image_path = os.path.join(IMAGE_DIR, image_filename)
    if image_url:
        try:
            response = requests.get(image_url, timeout=10)
            with open(image_path, "wb") as img_file:
                img_file.write(response.content)
            logging.info(f"Downloaded image: {image_filename}")
        except Exception as e:
            logging.warning(f"Failed to download image for {name}: {e}")

    course_info = {
        "course_name": name,
        "language": language,
        "price": price,
        "original_price": original_price,
        "discount": discount,
        "image_url": image_url
    }

    courses_data.append(course_info)

    # Optional: Print to console
    print(f"Course No.: {index}")
    print(f"Name: {name}")
    print(f"Language: {language}")
    print(f"Price: {price}")
    print(f"Original Price: {original_price}")
    print(f"Discount: {discount}")
    print(f"Image URL: {image_url}")

# ---------------------- Export to JSON ----------------------

try:
    with open("adda247_courses.json", "w", encoding="utf-8") as f:
        json.dump(courses_data, f, indent=4, ensure_ascii=False)
    logging.info("Courses exported to 'adda247_courses.json'")
except Exception as e:
    logging.error(f"Error saving JSON: {e}")

# ---------------------- Clean Up ----------------------

driver.quit()
logging.info("Browser closed.")
