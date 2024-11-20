
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from datetime import datetime, timedelta
import re
import json


service = Service(ChromeDriverManager().install())
chrome_options = Options()
driver = webdriver.Chrome(service=service, options=chrome_options)


url = "https://www.threads.net/"
driver.get(url)

print(f"Đã truy cập trang: {url}")


sleep(5)


last_height = driver.execute_script("return document.body.scrollHeight")  

scroll_count = 0


posts_data = []

while scroll_count < 4: 

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    

    sleep(3)
    

    new_height = driver.execute_script("return document.body.scrollHeight")
    

    if new_height == last_height:
        break
    
    last_height = new_height 
    scroll_count += 1  


try:
    posts = driver.find_elements(By.CSS_SELECTOR, ".x1ypdohk.x1n2onr6.xvuun6i.x3qs2gp.x1w8tkb5.x8xoigl.xz9dl7a.x6bh95i.x13fuv20.xt8cgyo.xsag5q8")

    if posts:
        for i, post in enumerate(posts, 1):
            post_data = {} 


            try:

                author = post.find_element(By.CSS_SELECTOR, ".x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xp07o12.xzmqwrg.x1citr7e.x1kdxza.xt0b8zv").text  # Điều chỉnh lại class nếu cần
            except Exception as e:
                author = "Không tìm thấy tác giả"
            post_data["author"] = author

            try:

                time_str = post.find_element(By.CSS_SELECTOR, ".x9f619.x1ja2u2z.xzpqnlu.x1hyvwdk.x14bfe9o.xjm9jq1.x6ikm8r.x10wlt62.x10l6tqk.x1i1rx1s").text  # Điều chỉnh lại class nếu cần
                

                now = datetime.now()


                time_match = re.match(r"(\d+)\s*(hour|day|minute)s?\s*ago", time_str)

                if time_match:
                    value, unit = int(time_match.group(1)), time_match.group(2)
                    
                    if unit == "hour":
                        post_time = now - timedelta(hours=value)
                    elif unit == "day":
                        post_time = now - timedelta(days=value)
                    elif unit == "minute":
                        post_time = now - timedelta(minutes=value)
                    
   
                    time = post_time.strftime("%d/%m/%Y %H:%M")
                else:
                    time = time_str 
            except Exception as e:
                time = "Không tìm thấy giờ"
            post_data["time"] = time

            try:

                content = post.find_element(By.CSS_SELECTOR, ".x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x1ji0vk5.x18bv5gf.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xjohtrz.xo1l8bm.xp07o12.x1yc453h.xat24cr.xdj266r").text  # Điều chỉnh lại class nếu cần
            except Exception as e:
                content = "Không tìm thấy nội dung"
            post_data["content"] = content

            try:

                images = post.find_elements(By.TAG_NAME, 'img')  
                image_urls = [img.get_attribute('src') for img in images]  
            except Exception as e:
                image_urls = None  

            post_data["images"] = image_urls 

            try:
                video = post.find_element(By.TAG_NAME, 'video')  
                video_url = video.get_attribute('src')  
            except Exception as e:
                video_url = None  

            post_data["video"] = video_url 


            posts_data.append(post_data)

            # In thông tin bài viết
            print(f"Bài viết {i}:")
            print(f"Tác giả: {author}")
            print(f"Thời gian: {time}")
            print(f"Nội dung: {content}")
            print(f"Ảnh URLs: {image_urls if image_urls else 'Không có ảnh'}")
            print(f"Video URL: {video_url if video_url else 'Không có video'}") 
            print("-" * 40)

    else:
        print("Không tìm thấy bài viết nào.")
    
except Exception as e:
    print("Lỗi khi tìm kiếm bài viết:", e)


with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=4)

print("Dữ liệu đã được lưu vào file data.json.")


driver.quit()

