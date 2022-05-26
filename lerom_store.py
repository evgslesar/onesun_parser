import json
import time
import requests
import lxml.html
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_links():
    url = 'https://lerom.store/sitemap.xml'
    response = requests.get(url)
    tree = lxml.html.fromstring(response.content)
    links = tree.cssselect('loc')
    links = [link.text for link in links]
    links = [link for link in links if len(link.split('/')) > 4]

    print(len(links))

    return links

    

def get_data(links):
    result = []
    for link in links:
        driver.get(link)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

        tree = lxml.html.fromstring(driver.page_source)
        
        if tree.xpath('//button[@data-original-title="Сетка"]') == []:
            try:
                title = tree.xpath("//h1/text()")[0]
            except:
                title = ''
            try:
                manufacturer = tree.xpath("//h1/following-sibling::ul[1]/li/a/text()")[0]
            except:
                manufacturer = ''
            try:
                sku = tree.xpath("//h1/following-sibling::ul[1]/li[2]/text()")[0].split(': ')[1].strip()
            except:
                sku = ''
            try:
                is_present = tree.xpath("//h1/following-sibling::ul[1]/li[3]/text()")[0].split(': ')[1]
            except:
                is_present = ''
            try:
                category = tree.xpath("//ul[@class='breadcrumb']/li/a/text()")[-1]
            except:
                category = ''
            try:
                old_price = tree.xpath("//span[@class='price-old-live']/text()")[0].split('р')[0].replace(' ', '')
            except:
                old_price = ''
            try:
                price = tree.xpath("//span[@class='price-new-live']/text()")[0].split('р')[0].replace(' ', '')
            except:
                price = old_price
            try:
                colors = tree.xpath("//*[@class='radio-inline theme-button']/descendant::img/@alt")
            except:
                colors = []
            try:
                pictures = tree.xpath("//a[@class='thumbnail']/@href")
            except:
                pictures = []
            try:
                description = ''.join(tree.xpath("//div[@id='tab-description']/descendant::*/text()")).strip()
            except:
                description = ''
            try:
                param_table = tree.xpath("//div[@id='tab-specification']//tbody/tr")
                param_dict = {}
                for row in param_table:
                    key = row.xpath("./td")[0].text
                    value = row.xpath("./td")[1].text
                    param_dict.update({key: value})
            except:
                param_table = []
            try:    
                modules = tree.xpath("//div[@class='image']/a/@href")
            except:
                modules = []

            result_dict = {
                "Название": title,
                "Артикул": sku,
                "Производитель": manufacturer,
                "Категория": category,
                "Ссылка": link,
                "Цена": price,
                "Старая цена": old_price,
                "Наличие": is_present,
                "Варианты": ', '.join(colors),
                "Изображения": ', '.join(pictures),
                "Описание": description,
                "Модули": ', '.join(modules)
            }
            result_dict.update(param_dict)
            result.append(result_dict)

    # with open('lerom_store.json', 'w', encoding='utf-8') as f:
    #     json.dump(result, f, indent=4, ensure_ascii=False)

    return result

def save_to_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("lerom_store.csv", index=False)


if __name__ == '__main__':
    links = get_links()
    data = get_data(links)
    save_to_csv(data)