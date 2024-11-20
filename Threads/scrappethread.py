#https://scrapfly.io/blog/how-to-scrape-threads/
import json
from typing import Dict
import jmespath
from parsel import Selector
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup


def parse_thread(thread):

    return {
        "thread_id": thread.get('id', 'N/A'),
        "thread_content": thread.get('content', 'No content available'),
        "likes": thread.get('like_count', 0),
        "comments": thread.get('comment_count', 0),
        "shares": thread.get('share_count', 0)
    }

def parse_profile(data: Dict) -> Dict:
    result = jmespath.search(
        """{
        is_private: text_post_app_is_private,
        is_verified: is_verified,
        profile_pic: hd_profile_pic_versions[-1].url,
        username: username,
        full_name: full_name,
        bio: biography,
        bio_links: bio_links[].url,
        followers: follower_count
    }""",
        data,
    )
    result["url"] = f"https://www.threads.net/@{result['username']}"
    return result


def scrape_profile(url: str) -> dict:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page.goto(url)
        page.wait_for_selector("[data-pressable-container=true]")
        selector = Selector(page.content())

    parsed = {
        "user": {},
        "threads": [],
    }

    hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()

    for hidden_dataset in hidden_datasets:
        if '"ScheduledServerJS"' not in hidden_dataset:
            continue
        is_profile = 'follower_count' in hidden_dataset
        is_threads = 'thread_items' in hidden_dataset
        if not is_profile and not is_threads:
            continue
        
        try:
            data = json.loads(hidden_dataset)
            if is_profile:
                user_data = nested_lookup('user', data)
                parsed['user'] = parse_profile(user_data[0])
            if is_threads:
                thread_items = nested_lookup('thread_items', data)
                threads = [parse_thread(t) for thread in thread_items for t in thread]
                parsed['threads'].extend(threads)
        except json.JSONDecodeError:
            print("Failed to decode JSON from hidden dataset")
    
    return parsed


if __name__ == "__main__":
    try:
        data = scrape_profile("https://www.threads.net/@natgeo")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"An error occurred: {e}")
