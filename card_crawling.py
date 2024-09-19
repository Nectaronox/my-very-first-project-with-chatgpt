import base64
import csv
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import os  # 파일 경로 관리에 필요

# Selenium 웹드라이버 설정
driver = webdriver.Chrome()  # chromedriver의 경로를 지정하세요.

data_list = []
data_list1 = []
data_list2 = []
image_paths = []  # 이미지 경로를 저장할 리스트

for i in range(1, 2748):
    base_url = f"https://www.card-gorilla.com/card/detail/{i}"
    driver.get(base_url)
    driver.implicitly_wait(10)
    
    # 페이지에서 특정 요소가 있는지 확인하여 유효한 페이지인지 판단
    try:
        # 카드 이름 요소가 있는지 확인
        card_names = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "strong.card"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 카드 이름 가져오기
        card_name = card_names.text.strip()
        data_list.append(card_name)
        print(f"카드 네임을 성공적으로 수집하였습니다: {card_name}")
        
        # 카드 브랜드 가져오기
        card_brands = soup.find("p", class_="brand")
        if card_brands:
            card_brand = card_brands.get_text().strip()
            data_list1.append(card_brand)
            print("카드 브랜드를 성공적으로 수집하였습니다")
        else:
            data_list1.append(None)
            print("카드 브랜드를 수집하지 못했습니다")

        card_img = soup.find('img')
        # img 태그의 src 속성을 추출
        if card_img:
            img_src = card_img.get('src')
        else:
            print("img 태그를 찾을 수 없습니다.")
            continue  # 이미지가 없는 경우 다음으로 건너뜁니다.

        # 고유한 이미지 파일 경로 설정
        os.makedirs('images', exist_ok=True)
        save_path = os.path.join('images', f"downloaded_image_{i}.png")


        # 이미지 다운로드 및 저장
        urlretrieve(img_src, save_path)
        print(f"이미지가 {save_path}에 저장되었습니다.")
        
        # 저장된 이미지 경로를 리스트에 추가
        image_paths.append(save_path)

        # 카드 혜택 정보 가져오기
        card_all_benefits = soup.find("div", class_="lst bene_area")
        card_dl = card_all_benefits.select("dl[data-v-225eb1a5][data-v-35734774]")
        data_card_benefit = []
        for card_ind_dl in card_dl:
            card_benefit_category = card_ind_dl.find("p", class_="txt1").get_text().strip()
            card_benefit = card_ind_dl.select("i[data-v-225eb1a5][data-v-35734774]")[0].get_text(separator='\n').split('\n')
            dic_card_benefit = {card_benefit_category: card_benefit}
            data_card_benefit.append(dic_card_benefit)
        
        data_list2.append(data_card_benefit)

    except Exception as e:
        # 요소가 없거나 페이지가 로드되지 않는 경우, 해당 페이지를 건너뜁니다.
        print(f"페이지 {i}에 정보를 찾을 수 없습니다. 건너뜁니다. - {e}")
        continue

df_card_benefits = pd.DataFrame({'card_name': data_list, 'card_brand': data_list1, 'card_benefit': data_list2})

# 이미지 파일들을 base64로 인코딩하여 DataFrame에 추가
image_data = []
for image_path in image_paths:
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    image_data.append(encoded_string)

df_image = pd.DataFrame({'image_name': image_paths, 'image_base64': image_data})

# 두 개의 DataFrame 병합
card_merged_csv = pd.concat([df_card_benefits.reset_index(drop=True), df_image.reset_index(drop=True)], axis=1)

# 병합된 CSV 파일 저장
card_merged_csv.to_csv('card_gorilla_merged.csv', index=False)

print("CSV 파일이 병합되었습니다.")

driver.quit()

