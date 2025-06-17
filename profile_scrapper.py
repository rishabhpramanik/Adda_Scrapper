from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
import time

# Initializing the driver
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Launching the browser and getting the course
def scrape_adda247_course(url):
    driver = setup_driver()
    driver.get(url)

    data = {
        "course_includes": [],
        "faculties": [],
        "subjects_covered": [],
        "faqs": [],
        "note": {
            "description": [],
            "form_link": None
        }
    }

    # 📦 Course Includes
    try:
        includes = driver.find_elements(By.CSS_SELECTOR, ".pdpIncludeList ul li")
        for inc in includes:
            text = inc.text.strip()
            data["course_includes"].append(text)
    except Exception as e:
        print("Error in includes:", e)

    # 👨‍🏫 Faculty Details
    try:
        faculty_cards = driver.find_elements(By.CSS_SELECTOR, "#facultyProfileContainer .pdpLi")
        for fac in faculty_cards:
            try:
                name = fac.find_element(By.CLASS_NAME, "pdpFacName").text.strip()
                subject = fac.find_element(By.CLASS_NAME, "pdpFacExpt").text.strip()
                image = fac.find_element(By.TAG_NAME, "img").get_attribute("src")
                points = fac.find_elements(By.CSS_SELECTOR, ".pdpFacList li")
                experience = points[0].text.strip() if points else ""
                description = points[1].text.strip() if len(points) > 1 else ""

                data["faculties"].append({
                    "name": name,
                    "subject": subject,
                    "experience": experience,
                    "description": description,
                    "image_url": image
                })
            except Exception as inner_e:
                print("Faculty parsing error:", inner_e)
    except Exception as e:
        print("Error in faculty section:", e)

    # 📘 Subjects Covered
    try:
        subject_section = driver.find_elements(By.CSS_SELECTOR, "#Subjects\\ Covered li")
        for sub in subject_section:
            data["subjects_covered"].append(sub.text.strip())
    except Exception as e:
        print("Error in subjects covered:", e)

    # ❓ FAQs
    faq_data = []

    try:
        faq_items = driver.find_elements(By.CSS_SELECTOR, "#pdpFaqList .pdpFaqActive li")
        for item in faq_items:
            try:
                import re
                raw_question = item.find_element(By.CLASS_NAME, "pdpFaqHeader").text.strip()
                question = re.sub(r"^\d+\.\s*", "", raw_question)  # Remove number prefix like "1. "
                answer = item.find_element(By.CLASS_NAME, "pdpFaqContent").text.strip()
                faq_data.append({
                    "question": question,
                    "answer": answer
                })
            except Exception as inner_err:
                print(f"Failed to extract an FAQ item: {inner_err}")
    except Exception as e:
        print(f"FAQ parse error: {e}")

    # Store in result object or print
    data["faq"] = faq_data

    # 📝 Note Section
    try:
        note_section = driver.find_elements(By.CSS_SELECTOR, "#Note .productInfoBody p")
        for p in note_section:
            text = p.text.strip()
            if text:
                data["note"]["description"].append(text)
            try:
                link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
                if "docs.google.com" in link:
                    data["note"]["form_link"] = link
            except:
                pass  # Not every paragraph has a link
    except Exception as e:
        print("Error in Note section:", e)

    driver.quit()
    return data


if __name__ == "__main__":
    course_url = "https://www.adda247.com/product-onlineliveclasses/3937/bank-maha-pack-ibps-sbi-rrb?productId=4204"
    result = scrape_adda247_course(course_url)

    # Print result
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Optional: Save to file
    with open("adda247_course_data.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)