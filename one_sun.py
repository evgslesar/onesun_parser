import json
import requests
import lxml.html
import pandas as pd
from fake_useragent import UserAgent


def get_links():
    url = 'https://one-sun.ru/sitemap_iblock_40.xml'
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    html = requests.get(url, headers=headers)
    tree = lxml.html.fromstring(html.content)
    links = tree.cssselect('loc')
    links = [link.text for link in links]
    print(len(links))

    return links


def get_data(links):
    result = []
    for link in links:
        if link.endswith('.html'):
            ua = UserAgent()
            headers = {'User-Agent': ua.random}
            html = requests.get(link, headers=headers)
            tree = lxml.html.fromstring(html.content)

            try:
                title = tree.xpath("//h1[@class='product-header__title']/text()")[0].strip()
            except:
                title = 'Страница не найдена'
            category_slug = link.split('/')[-2]
            category_slugs = {'kontrollery-zaryada-epsolar': 'Контроллеры заряда EPSolar (Epever)',
                              'komplektuyushchie-k-kontrolleram-zaryada': 'Комплектующие к контроллерам заряда',
                              'invertory-cotek':'Инверторы COTEK',
                              'gibridnye-pv-invertory': 'Инверторы',
                              'invertory-sunways-serii-uma': 'Инверторы Sunways UMX',
                              'invertory-serii-is': 'Инверторы СибКонтакт',
                              'invertory-epsolar-epever': 'Инверторы EPSolar (EPEVER)',
                              'krepezhnye-elementy': 'Крепежные элементы',
                              'litiy-zhelezo-fosfatnye-akb-lifepo4': 'Аккумуляторы LifePo4',
                              'gotovye-komplekty': 'Готовые комплекты',
                              'kabel-i-konnektory': 'Кабель и коннекторы',
                              'akkumulyatornye-batarei-po-tekhnologii-agm-absorbent-glass-mat': 'Аккумуляторные батареи по технологии AGM (Absorbent Glass Mat)',
                              'akkumulyatornye-batarei-po-tekhnologii-gel-gel-electrolite': 'Аккумуляторные батареи по технологии GEL (гель-электролит)',
                              'solnechnye-moduli-one-sun': 'Солнечные модули One-sun',
                              }
            if category_slug in category_slugs.keys():
                category = category_slugs[category_slug]
            else:
                category = tree.xpath("//li[@class='breadcrumb-item']/a/text()")[-1].strip()
            try:
                sku = tree.xpath("//div[@class='product-header__article']/text()")[1].strip().split(' ')[1]
            except:
                sku = ''
            try:
                warranty = tree.xpath("//span[@class='product-tag product-tag--green']/*/text()")[0].strip().replace('<br>', '')
            except:
                warranty = ''
            try:
                sale = tree.xpath("//span[@class='product-tag product-tag--orange']/text()")[0].strip()
            except:
                sale = ''
            try:
                price = tree.xpath("//div[@class='product-price__new']/text()")[0].strip().replace(' ', '')
            except:
                price = 'Скоро в продаже'
            try:
                old_price = tree.xpath("//div[@class='product-price__old']/text()")[0].strip().replace(' ', '')
            except:
                old_price = ''
            try:
                discount = tree.xpath("//div[@class='product-price__benefit']/text()")[0].strip().split(' ')[1]
            except:
                discount = ''
            try:
                description = ''.join(tree.xpath("//div[@id='description']/div[@class='row']/div[@class='col-xl-9']/descendant::*/text()")).strip().replace('\t', '')
                if not description:
                    description = tree.xpath("//div[@id='description']/div/div/text()")[0].strip()
            except:
                description = ''
            try:
                manuals = tree.xpath("//div[@id='manual']//a/@href")
                if manuals:
                    manuals = ['https://one-sun.ru' + manual for manual in manuals]
            except:
                manuals = []
            try:
                video_reviews = tree.xpath("//div[@id='review']//@data-youtube-video-id")
                if video_reviews:
                    video_reviews = ['https://www.youtube.com/watch?v=' + video_review for video_review in video_reviews]
            except:
                video_reviews = []
            try:
                images = tree.xpath("//div[@class='product-media__gallery']/descendant::a/@href")
            except:
                images = []
            if images:
                images = ['https://one-sun.ru' + image for image in images]
            try:
                param_table = tree.xpath("//div[@class='product-content']//tr")
                param_dict = {}
                for row in param_table:
                    key = row.xpath("./th")[0].text
                    value = row.xpath("./td")[0].text
                    param_dict.update({key: value})
            except:
                param_table = []

            result_dict = {
                "Название": title,
                "Артикул": sku,
                "Гарантия": warranty,
                "Категория": category,
                "Ссылка": link,
                "Цена": price,
                "Наличие распродажи": sale,
                "Старая цена": old_price,
                "Скидка": discount,
                "Изображения": ', '.join(images),
                "Инструкции": ', '.join(manuals),
                "Видеообзоры": ', '.join(video_reviews),
                "Описание": description
            }
            result_dict.update(param_dict)
            result.append(result_dict)

    # with open('one_sun.json', 'w', encoding='utf-8') as f:
    #     json.dump(result, f, indent=4, ensure_ascii=False)
    
    return result


def save_to_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("one_sun.csv", index=False)


if __name__ == '__main__':
    links = get_links()
    data = get_data(links)
    save_to_csv(data)