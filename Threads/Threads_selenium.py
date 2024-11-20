#https://scrapfly.io/blog/how-to-scrape-threads/
import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
from datetime import datetime

warnings.simplefilter("ignore", category=UserWarning)

def parse_thread(data: Dict) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        title: post.caption.text,
        time: post.taken_at,
        author: post.user.username,
        content: post.caption.text,
        location: post.location.name || 'N/A',
        id: post.id,
        pk: post.pk,
        code: post.code,
        username: post.user.username,
        user_pic: post.user.profile_pic_url,
        user_verified: post.user.is_verified,
        user_pk: post.user.pk,
        user_id: post.user.id,
        has_audio: post.has_audio,
        reply_count: view_replies_cta_string,
        like_count: post.like_count,
        images: post.carousel_media[].image_versions2.candidates[1].url,
        image_count: post.carousel_media_count,
        videos: post.video_versions[].url
    }""",
        data,
    )

    if result.get("time"):
        result["time"] = datetime.utcfromtimestamp(result["time"]).strftime('%Y-%m-%d %H:%M:%S')

    
    if result.get("reply_count") and type(result["reply_count"]) != int:
        result["reply_count"] = int(result["reply_count"].split(" ")[0])


    result["videos"] = list(set(result["videos"] or []))


    result["link"] = f"https://www.threads.net/@{result['username']}/post/{result['code']}"


    return result

def scrape_thread(url: str) -> dict:
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (without UI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-pressable-container=true]"))
        )

        
        page_content = driver.page_source

        selector = Selector(page_content)
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()

        for hidden_dataset in hidden_datasets:

            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            if "thread_items" not in hidden_dataset:
                continue
            data = json.loads(hidden_dataset)

            thread_items = nested_lookup("thread_items", data)
            if not thread_items:
                continue

            threads = [parse_thread(t) for thread in thread_items for t in thread]
            return {
                "thread": threads[0],  # the first parsed thread is the main post
                "replies": threads[1:],  # other threads are replies
            }
        
       
        raise ValueError("Could not find thread data in page")

    finally:
        driver.quit()

if __name__ == "__main__":

    url = "https://www.threads.net/t/C8H5FiCtESk/" 
    result = scrape_thread(url)

    print(json.dumps(result, indent=4, ensure_ascii=False))
