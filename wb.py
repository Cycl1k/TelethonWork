import requests

def get_catalog(name):
    url = 'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=no_test&TestID=no_test&appType=1&curr=rub&dest=-1257786&query='+name+'&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://www.wildberries.ru',
        'Referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=cat',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site', 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'sec-ch-ua': 'Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'sec-ch-ua-mobile' : '?0',
        'sec-ch-ua-platform': 'Windows',
        'x-queryid': 'qid311154607170629030720240127062428' 
    }

    response = requests.get(url=url, headers=headers)
    return response.json()

def parser_json(response):
    products = []
    counter = 0

    products_raw = response.get('data', {}).get('products', None)

    if products_raw != None and len(products_raw) >0:
        for product in products_raw:
            products.append({
                'id': product.get('id', None),
                'name': product.get('name', None)
            })
            counter +=1
            if counter == 10:
                break

    return products

def wb_items(name):
    response = get_catalog(name)
    products = parser_json(response)

    return products


wb_items('cat')