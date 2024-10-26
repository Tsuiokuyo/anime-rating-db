import requests
import traceback
import time
import json
import os
import dateutil.parser
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from tqdm import tqdm
from bs4 import BeautifulSoup
from . import utils


def parse_data(data):
    """
    Parse the data (response) to extract information.
    If anything failed, return None.

    @param data: JSON object.
    @return: dict, containing extracted information.
    """

    try:
        detail = {}
        if 'id' not in data :
            return None
        detail['id'] = data['id']
        if 'rating' in data:
            rating = data['rating']
            detail['votes'] = rating['total']
            detail['score'] = rating['score']
            detail['rating_detail'] = rating['count']
        else:
            detail['votes'] = None
            detail['score'] = None
            detail['rating_detail'] = None
        #detail['rank'] = data['rank'] if 'rank' in data else None
        if len(data) == 4:
            detail['votes'] = data['votes']
            detail['score'] = data['score']
            detail['rating_detail'] = data['rating_detail']
            return detail
        #detail['air_from'] = data['air_date']
        detail['cn_name'] = data['name_cn']
        #detail['jp_name'] = data['name']
        
        if data['images'] is not None:
            detail['image'] = data['images']['large'].replace("http://lain.bgm.tv/pic/cover/l/","").replace(".jpg","")
        else:
            detail['image'] = None
        #detail['Thumbnail'] = data['images']['common']
        #detail['grid'] = data['images']['grid']
        
        #detail['summary'] = data['summary']
        
        if detail['cn_name'] == '':
            detail['cn_name'] = data['name']
        #if detail['air_from'] == '0000-00-00':
            #return None
        return detail
    except Exception:
        print('bgm_id: {}'.format(data['id']))
        traceback.print_exc()
        return None


def get_top_1000_id_list():
    """
    Get a list of top-1000 anime, from Bangumi.
    If anything failed, return None.

    @return: a list of strings (1000 items), each string is an id.

    P.S. Regretfully, I failed to find any official or unofficial api which
         provides the whole list of anime on Bangumi. In that case, I have no
         choice but to parse raw HTML myself.
    """

    try:
        prefix_url = 'https://bgm.tv/anime/browser?sort=rank&page='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        id_list = []
        # items per page: 24
        for page in tqdm(range(1, 43)):
            web_url = prefix_url + str(page)
            resp = requests.get(web_url, headers=headers)
            html = resp.text
            # parse HTML-format text
            soup = BeautifulSoup(html, 'html.parser')
            ul = soup.find_all('ul', id='browserItemList')[0]
            items = ul.contents
            for item in items:
                bgm_id = item.a.attrs['href'].split('/')[-1]
                id_list.append(bgm_id)
            # avoid making requests too fast
            time.sleep(0.5)
        # 42 pages * 24 items/page = 1008
        # however, we'll only keep top-1000
        id_list = id_list[:1000]
        return id_list
    except Exception:
        traceback.print_exc()
        return None


def cache_anime_detail(bgm_id, dir_path='.'):
    """
    Cache detail for an anime, from Bangumi.

    @param id_list: a list of strings, each string is an id.
    @param dir_path: string, path to the cache directory.
    """

    try:
        api_url = 'http://api.bgm.tv/subject/' + str(bgm_id) + '?responseGroup=large'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(api_url, headers=headers)
        # response in json format
        data = resp.json()
        fpath = os.path.join(dir_path, '{}.json'.format(bgm_id))
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        traceback.print_exc()


def get_anime_detail(bgm_id, cache=False, cache_dir='.',useCache = True,needSleep = False):
    """
    Get detail for an anime, from Bangumi.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param bgm_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.

    P.S. Fortunately, Bangumi has official api to fetch detailed info of
         a certain anime. This api also provides rating details, so we can
         record it for further use.
    """
    
    try:
        api_url = 'http://api.bgm.tv/subject/' + str(bgm_id) + '?responseGroup=large'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        cache_path = os.path.join(cache_dir, '{}.json'.format(bgm_id))

        oldCache = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            # if random.getrandbits(4) == 0 :
                oldCache = False
        # elif random.getrandbits(6) == 0 :
        #     oldCache = False
        if cache and os.path.exists(cache_path) and oldCache or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'error' in data:
                    return None
        else:
            resp = requests.get(api_url, headers=headers, timeout=10)
            # response in json format
            data = resp.json()
            
            if 'error' in data:
                return None
            if 'error' not in data:
                if cache and os.path.exists(cache_path):
                        os.remove(cache_path)
                if cache:
                    # add to cache
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
            if needSleep:
                time.sleep(1)
        return parse_data(data)
    except Exception:
        print('bgm_id: {}'.format(bgm_id))
        traceback.print_exc()
        return None

def get_anime_detail2(ani_id, cache=False, cache_dir='.',useCache = True,needSleep = False):
    
    try:
        url = 'https://bangumi.tv/subject/' + str(ani_id)
        cache_path = os.path.join(cache_dir, '{}.json'.format(ani_id))

        oldCache = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400*10:
            if random.getrandbits(4) == 0 :
                oldCache = False
        elif random.getrandbits(6) == 0 :
            oldCache = False
        if cache and os.path.exists(cache_path) and oldCache or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'error' in data:
                    f.close()
                    os.remove(cache_path)
                    data = get_anime_detail2(ani_id, cache=True, cache_dir='fetch/bgm',useCache = False,needSleep = False)
                    
        else:
            options = uc.ChromeOptions()
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--password-store=basic')

            browser = uc.Chrome(use_subprocess=True,suppress_welcome=False,options=options)

            browser.get(url)
            browser.add_cookie({"name": "chii_auth", "value": "9vXisJGKJz7UZPWMaReKO%2FWub5tZApraQIIFV28kT0syngzdv6FN3NVfYp31xVBmnPY%2BtGwKm3jrCDJOYZ2mzDRb8HVhStXJ%2F2pd"})
            browser.add_cookie( {"name": "chii_cookietime", "value": "259200000"})
            browser.add_cookie( {"name": "chii_searchDateLine", "value": "0"})
            browser.add_cookie( {"name": "chii_sec_id", "value": "MxFYYDJna5MAXerXvrxCQUsFtR0LLuXWiaoMkA"})
            browser.add_cookie( {"name": "chii_sid", "value": "Maisxa"})
            browser.add_cookie( {"name": "__utmc", "value": "1"})
            browser.add_cookie( {"name": "ticketing_country", "value": "tw"})
            browser.add_cookie( {"name": "chii_theme", "value": "light"})
            browser.refresh()
            time.sleep(1)
            browser.refresh()
            time.sleep(2)
            

            html = browser.page_source

            # # 藉由 BeautifulSoup 套件將網頁原始碼使用 `html.parser` 解析器來解析
            data = {'id': ani_id}
            soup = BeautifulSoup(html, 'html.parser')
            score = soup.select('div.global_score')[0].select('span.number')[0].text
            data['score'] = float(score)

            votes = soup.select('div#ChartWarpper')[0].select('div.chart_desc')[0].select('span')[0].text
            data['votes'] = int(votes)

            v10 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[0].select('span')[1].text.replace('(','').replace(')','')
            v9 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[1].select('span')[1].text.replace('(','').replace(')','')
            v8 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[2].select('span')[1].text.replace('(','').replace(')','')
            v7 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[3].select('span')[1].text.replace('(','').replace(')','')
            v6 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[4].select('span')[1].text.replace('(','').replace(')','')
            v5 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[5].select('span')[1].text.replace('(','').replace(')','')
            v4 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[6].select('span')[1].text.replace('(','').replace(')','')
            v3 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[7].select('span')[1].text.replace('(','').replace(')','')
            v2 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[8].select('span')[1].text.replace('(','').replace(')','')
            v1 = soup.select('div#ChartWarpper')[0].select('ul.horizontalChart')[0].select('li')[9].select('span')[1].text.replace('(','').replace(')','')

            v = {'10': int(v10), '9': int(v9), '8': int(v8), '7': int(v7), '6': int(v6), '5': int(v5)
                                , '4': int(v4), '3': int(v3), '2': int(v2), '1': int(v1)}
            data['rating_detail'] = v
            browser.close()
            
            if cache and os.path.exists(cache_path):
                os.remove(cache_path)
                    
            if cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception:
        print('bgm_id: {}'.format(ani_id))
        traceback.print_exc()
        return None


def search_for_anime(jp_name, en_name, start_date, cache=False, cache_dir='.'):
    """
    Search a certain anime on MyAnimeList, through 3 main parameter.
    If anything failed, return None.

    @param jp_name: string, the anime name in Japanese.
    @param en_name: string, the anime name in English.
    @param start_date: string, the date when the anime started airing.
           Should be in 'yyyy-mm-dd' format.
    @param cache: boolean, used in get_anime_detail.
    @param cache_dir, string, used in get_anime_detail.
    @return: a dict, containing detailed data for best-matched search result.
             If no result, return None.

    P.S. Bangumi does not provide official English name for anime. However,
         we can still search in English.
    """

    max_keep = 10
    try:
        air_date = dateutil.parser.parse(start_date)
        air_date = air_date.replace(tzinfo=None)
        # first, search by jp_name
        if jp_name is not None:
            jp_name = jp_name.lower()
            api_url = 'http://api.bgm.tv/search/subject/' + jp_name + '?type=2&max_results=' + str(max_keep)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
                AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
            }
            resp = requests.get(api_url, headers=headers)
            # response in json format
            try:
                data = resp.json()['list']
                if data is None:
                    data = []
            except Exception:
                # traceback.print_exc()
                data = []
            best_match_jp = None
            best_match_jp_lcs = 0
            for item in data:
                bgm_id = item['id']
                tar_jp_name = item['name']
                tar_jp_name = tar_jp_name.lower()
                match_lcs = utils.lcs(jp_name, tar_jp_name) / min(len(jp_name), len(tar_jp_name))
                if match_lcs > best_match_jp_lcs:
                    best_match_jp_lcs = match_lcs
                    best_match_jp = bgm_id
                elif abs(match_lcs - best_match_jp_lcs) < 1e-6:
                    detail_last = get_anime_detail(best_match_jp, cache, cache_dir) if best_match_jp is not None else None
                    detail_curr = get_anime_detail(bgm_id, cache, cache_dir)
                    if detail_last is None:
                        best_match_jp = bgm_id
                        continue
                    elif detail_curr is None:
                        continue
                    air_date_last = dateutil.parser.parse(detail_last['air_from'])
                    air_date_curr = dateutil.parser.parse(detail_curr['air_from'])
                    air_date_last = air_date_last.replace(tzinfo=None)
                    air_date_curr = air_date_curr.replace(tzinfo=None)
                    delta_last = abs((air_date - air_date_last).days)
                    delta_curr = abs((air_date - air_date_curr).days)
                    best_match_jp = best_match_jp if delta_last <= delta_curr else bgm_id
            if best_match_jp is not None:
                best_match_jp = get_anime_detail(best_match_jp, cache, cache_dir)
        else:
            best_match_jp = None
        # then, search by en_name
        if en_name is not None:
            en_name = en_name.lower()
            api_url = 'http://api.bgm.tv/search/subject/' + en_name + '?type=2&max_results=' + str(max_keep)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
                AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
            }
            resp = requests.get(api_url, headers=headers)
            # response in json format
            try:
                data = resp.json()['list']
                if data is None:
                    data = []
            except Exception:
                # traceback.print_exc()
                data = []
            best_match_en = None
            best_match_en_lcs = 0
            for item in data:
                bgm_id = item['id']
                tar_jp_name = item['name']
                tar_jp_name = tar_jp_name.lower()
                match_lcs = utils.lcs(en_name, tar_jp_name) / min(len(en_name), len(tar_jp_name))
                if match_lcs > best_match_en_lcs:
                    best_match_en_lcs = match_lcs
                    best_match_en = bgm_id
                elif abs(match_lcs - best_match_en_lcs) < 1e-6:
                    detail_last = get_anime_detail(best_match_en, cache, cache_dir) if best_match_en is not None else None
                    detail_curr = get_anime_detail(bgm_id, cache, cache_dir)
                    if detail_last is None or detail_curr is None:
                        continue
                    air_date_last = dateutil.parser.parse(detail_last['air_from'])
                    air_date_curr = dateutil.parser.parse(detail_curr['air_from'])
                    air_date_last = air_date_last.replace(tzinfo=None)
                    air_date_curr = air_date_curr.replace(tzinfo=None)
                    delta_last = abs((air_date - air_date_last).days)
                    delta_curr = abs((air_date - air_date_curr).days)
                    best_match_en = best_match_en if delta_last <= delta_curr else bgm_id
            if best_match_en is not None:
                best_match_en = get_anime_detail(best_match_en, cache, cache_dir)
        else:
            best_match_en = None
        
        if best_match_jp is None or best_match_en is None:
            if best_match_en is not None:
                return best_match_en
            if best_match_jp is not None:
                return best_match_jp
            return None
        
        if best_match_jp['id'] == best_match_en['id']:
            return best_match_jp
        else:
            # compare 2 results, choose the best one
            air_date_jp = dateutil.parser.parse(best_match_jp['air_from'])
            air_date_en = dateutil.parser.parse(best_match_en['air_from'])
            air_date_jp = air_date_jp.replace(tzinfo=None)
            air_date_en = air_date_en.replace(tzinfo=None)
            delta_jp = abs((air_date - air_date_jp).days)
            delta_en = abs((air_date - air_date_en).days)
            return best_match_jp if delta_jp <= delta_en else best_match_en
    except Exception:
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """

    # id_list = get_top_1000_id_list()
    # detail_list = []
    # for bgm_id in tqdm(id_list):
    #     detail = get_anime_detail(bgm_id)
    #     detail_list.append(detail)
    #     time.sleep(0.5)
    # import json
    # with open('bgm.json', 'w', encoding='utf-8') as f:
    #     json.dump(detail_list, f, indent=2, ensure_ascii=False)

    # res = search_for_anime('科学忍者隊ガッチャマン', 'Science Ninja Team Gatchaman', '1972-10-01')
    res= get_anime_detail2(338672)
    print(res)