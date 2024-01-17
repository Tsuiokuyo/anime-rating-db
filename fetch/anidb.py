import requests
import traceback
import gzip
import xml.dom.minidom
import re
from bs4 import BeautifulSoup
import json
import os
import time
import random


"""
* No more than one active request at any point in time
* No more than 5 requests within a 1 minute time frame (i.e. the first 5 requests are very fast, one after another, but the 6th request will have to wait for ~60 seconds, heavily slowing down processing)
* No more than 200 request per 24 hour time frame (i.e. the first 200 requests will be relatively fast at 5 requests per 60 seconds, but if we hit the limit, then FileBot will deadlock and suspend processing for up to 24 hours)
* All information is cached for 6 days (i.e. FileBot will not request the same information twice, unless the information we have is more than 6 days old already)
* If our 200 request per 24 hour limit is 50% exhausted, then FileBot will prefer previously cached information regardless of age to conserve requests if possible (i.e. you may end up with episode data that is 2-3 months old that was cached in a previous run long ago)
* A single banned response will switch the AniDB client into offline mode for the remaining process life-time and all subsequent requests that cannot be served by the cache will fail immediately
"""
"""
Notice that using AniDB API requires a registered client.
You can set variables here, or pass by console arguments. (see ../pre_process.py)
"""

client = 'tsuiokuyo'  # change this to your own client here
clientver = 1  # change this to your own client version
protover = 1  # change this to your own protocol version


def download_all_anime_list(fpath='anime-titles.xml'):
    """
    Download a list of all anime, from AniDB.

    @param fpath: a string, the path to save the dumped file.
    @return: True for success and False for failure.

    P.S. AniDB provides a daily dumped file for this kind of request.
         But remember not to request the file "MORE THAN ONCE PER DAY".
         (https://wiki.anidb.net/API#Anime_Titles)
    """

    try:
        dumped_file_url = 'http://anidb.net/api/anime-titles.xml.gz'
        gzpath = fpath + '.gz'
        # downloading
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(dumped_file_url, headers=headers, timeout=10)
        with open(gzpath, 'wb') as f:
            f.write(resp.content)
        # unzipping
        gfile = gzip.GzipFile(gzpath)
        with open(fpath, 'wb') as f:
            f.write(gfile.read())
        gfile.close()
        return True
    except Exception:
        traceback.print_exc()
        return False


def get_all_anime_id_list(fpath='anime-titles.xml'):
    """
    Get a id (also called "aid") list of all anime, from local-dumped file.
    If anything failed, return None. (A typical error: file not exist)

    @param fpath: a string, the path of the local-dump file.
    @return: a list of strings, each string is an id.

    P.S. Make sure the file exists. This function won't check it for you,
         it will simply return None.
    """

    try:
        dom = xml.dom.minidom.parse(fpath)
        root = dom.documentElement
        items = root.getElementsByTagName('anime')
        id_list = [item.getAttribute('aid') for item in items]
        return id_list
    except Exception:
        traceback.print_exc()
        return None

def get_anime_detail(aid, cache=False, cache_dir='.'):
# def get_anime_detail(aid):
    """
    Get detail for an anime, from AniDB.
    If anything failed, return None.

    @param aid: string or int, an id.
    @return: a dict, containing detailed data.

    P.S. It's a very good news that AniDB provides "resource" attribute for
         an anime, which links to Anime News Network. We can only keep very
         few info and we have no need for searching!
    """

    try:
        api_url = 'http://api.anidb.net:9001/httpapi?request=anime&client=' + client \
            + '&clientver=' + str(clientver) + '&protover=' + str(protover) + '&aid=' + str(aid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        cache_path = os.path.join(cache_dir, '{}.json'.format(aid))
        if cache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            resp = requests.get(api_url, headers=headers)
            # response in XML format, parsing needed
            dom = xml.dom.minidom.parseString(resp.text)
            root = dom.documentElement
            detail = {}
            detail['id'] = aid
            rating = root.getElementsByTagName('ratings')[0]
            rating = rating.getElementsByTagName('permanent')[0]
            detail['score'] = float(rating.childNodes[0].data)
            detail['votes'] = int(rating.getAttribute('count'))
            air = root.getElementsByTagName('startdate')[0]
            detail['air'] = air.childNodes[0].data
            resources = root.getElementsByTagName('resources')[0]
            resources = resources.getElementsByTagName('resource')
            detail['ann_id'] = []
            detail['mal_id'] = []
            # for resource in resources: 
            #     if resource.getAttribute('type') == '1':
            #         externalentity = resource.getElementsByTagName('externalentity')[0]
            #         identifier = externalentity.getElementsByTagName('identifier')[0]
            #         detail['ann_id'].append(identifier.childNodes[0].data)
            #     if resource.getAttribute('type') == '2':
            #         externalentity = resource.getElementsByTagName('externalentity')[0]
            #         identifier = externalentity.getElementsByTagName('identifier')[0]
            #         detail['mal_id'].append(identifier.childNodes[0].data)
            # add to cache
            if cache:
                with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(detail, f, indent=2, ensure_ascii=False)
        return detail
    except Exception:
        print('anidb: {}'.format(aid))
        traceback.print_exc()
        return None

'''
def get_anime_detail(ani_id, cache=False, cache_dir='.'):

    try:
        url = 'https://anidb.net/anime/' + str(ani_id)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        cache_path = os.path.join(cache_dir, '{}.json'.format(ani_id))
        if cache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            resp = requests.get(url, headers=headers)
            # response in json format
            html = resp.text
            if not html:
                # got empty data
                # retry in 30s
                time.sleep(30)
                return get_anime_detail(ani_id, cache, cache_dir)
            
            # 藉由 BeautifulSoup 套件將網頁原始碼使用 `html.parser` 解析器來解析
            data = {'id': ani_id}
            soup = BeautifulSoup(html, 'html.parser')
            # 取得各個動畫元素區塊
            title = soup.select('h1.anime')[0].text
            title = title.strip().replace('\r\n', '')
            data['title'] = re.match(r'Anime: (.*)', title).group(1)
            rating = soup.select('div.links span.value')[0].text
            data['score'] = rating
            score = soup.select('div.links span.count')[0].text
            match_obj = re.match(r'\((.*)\)', score)
            if match_obj:
                data['votes'] = match_obj.group(1)
            
            if cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception:
        print('anikore: {}'.format(ani_id))
        traceback.print_exc()
        return None
'''
if __name__ == '__main__':
    """
    Just for testing.
    """

    # download_all_anime_list()
    # id_list = get_all_anime_id_list()
    # print(len(id_list))
    # detail = get_anime_detail(5101)
    # print(detail)

def get_anime_detail2(ani_id, cache=False, cache_dir='.',useCache = True):

    try:
        # with open('anidbErr.json', 'r', encoding='utf-8') as f:
        #     err = json.load(f)
        
        # if ani_id in err:
        #     return None
        
        url = 'https://anidb.net/anime/' + str(ani_id)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        cache_path = os.path.join(cache_dir, '{}.json'.format(ani_id))
        oldCache = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            if random.getrandbits(3) == 0 :
                oldCache = False
        # elif random.getrandbits(9) == 0 :
        #     oldCache = False
        if cache and os.path.exists(cache_path) and oldCache or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif not useCache:
            resp = requests.get(url, headers=headers)
            # slp = random.randint(430, 432)
            # print(str(ani_id) +'，sleep:'+ str(slp) +'sec')
            # time.sleep(slp)
            # response in json format
            html = resp.text
            if not html:
                # got empty data
                # retry in 30s
                time.sleep(2)
                return get_anime_detail(ani_id, cache, cache_dir)
            
            # 藉由 BeautifulSoup 套件將網頁原始碼使用 `html.parser` 解析器來解析
            data = {'id': ani_id}
            soup = BeautifulSoup(html, 'html.parser')
            # 取得各個動畫元素區塊
            # title = soup.select('h1.anime')[0].text
            # title = title.strip().replace('\r\n', '')
            # data['title'] = re.match(r'Anime: (.*)', title).group(1)
            
            # rating = soup.select('div.links span.value')[0].text
            # data['score'] = float(rating)
            # score = soup.select('div.links span.count')[0].text
            # match_obj = re.match(r'\((.*)\)', score)
            # if match_obj:
            #     data['votes'] = int(match_obj.group(1))
            # else :
            #     data['votes'] = 0
            if(len(soup.find_all('div', {'class':'g-recaptcha'})) != 0 ):
                print('anidb 需要驗證~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~，ID:'+ str(ani_id))
                return None
                # time.sleep(1)
                # return get_anime_detail(ani_id, cache, cache_dir)
                # return None
            score =  soup.select('div#tab_1_pane')[0].select('tr.rating')[0].select('span.value')[0].text
            if  score == 'N/A':
                    score = 0
            data['score'] = float(score)
            votes =  soup.select('div#tab_1_pane')[0].select('tr.rating')[0].select('span.count')[0].text.replace('(','').replace(')','')
            data['votes'] = int(votes)
                
            if cache and os.path.exists(cache_path):
                    os.remove(cache_path)
            if cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        else :
            data = None
            
        if data is not None and'vote' in data: #一開始抓錯10/03
            data['votes'] = int(data['vote'])
            del data['vote']
        if data is not None and 'score' in data:
            data['score'] = float(data['score'])
        return data
    except Exception:
        print('anidb: {}'.format(ani_id))
        traceback.print_exc()
        return None
    
if __name__ == '__main__':
    """
    Just for testing.
    """

    print(get_anime_detail2(21860,False,useCache=False))
