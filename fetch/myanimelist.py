from ast import Try
from pickle import FALSE, TRUE
from turtle import update
import requests
import traceback
import time
import json
import os
import re
import datetime
import random

from tqdm import tqdm
from bs4 import BeautifulSoup
# from . import utils


"""
Since MyAnimeList (https://myanimelist.net) does not provide easy-to-use api,
this script is based on a third-party, unofficial api: Jikan (https://jikan.moe).

The Web API of Jikan is rate-limited strictly. But you can build your own Jikan
REST API since it's free and open-source.
"""

# by changing the following variables, you can choose the API you want to use.
# for an example, see ../pre_process.py

jikan_api_pool = []
jikan_api_idx = 0
use_api_pool = False
jikan_api = 'https://api.jikan.moe/v4'
req_delay = 1


def change_api_url():
    if use_api_pool:
        global jikan_api_idx
        jikan_api_idx = (jikan_api_idx + 1) % len(jikan_api_pool)
        jikan_api = jikan_api_pool[jikan_api_idx]
        print('Now using Jikan api: ' + jikan_api)
    print('Sleeping for 30s')
    time.sleep(30)

def parse_data(data,mal_id):
    """
    Parse the data (response) to extract information.
    If anything failed, return None.

    @param data: JSON object.
    @return: dict, containing extracted information.
    """

    try:
        detail = {}
        
        detail['official'] = None
        if 'official' in data:
            detail['official'] = data['official']
        
        detail['twitter'] = None
        if 'twitter' in data:
            detail['twitter'] = data['twitter']
        
        data = data['data']
        detail['id'] = data['mal_id']
        detail['type'] = data['type']
        detail['score'] = data['score'] if 'score' in data else None
        detail['votes'] = data['scored_by'] if 'scored_by' in data else None
        
        detail['season'] = data['season'] if 'season' in data else None
        #detail['rank'] = data['rank'] if 'rank' in data else None
        if 'images'in data:
            if data['images']['webp'] is not None:
                detail['image'] = data['images']['webp']['image_url'].replace("https://cdn.myanimelist.net/images/anime/","")
        # detail['image'] = data['image_url'].replace("https://cdn.myanimelist.net/images/anime/","")
        #detail['air_from'] = data['aired']['from']
        #detail['air_to'] = data['aired']['to']
        #detail['air_status'] = data['status']
        detail['title'] = data['title']
        detail['en_name'] = data['title_english']
        if detail['en_name'] is None:
            detail['en_name'] = detail['title']
        detail['jp_name'] = data['title_japanese']
        detail['premiered'] = data['aired']['prop']['from']['year']
        detail['genres'] = []
        detail['studios'] = []
        detail['official'] = None
        detail['duration'] = None
        detail['episodes'] = None
        detail['source'] = None
        if 'source'in data:
            if data['source'] is not None:
                detail['source'] = data['source']

        if 'episodes'in data:
            if data['episodes'] is not None:
                detail['episodes'] = data['episodes']
                    
        if 'duration' in data:
            if data['duration'] is not None:
                    overHr = False
                    if data['duration'].find('hr') != -1:
                        overHr = True
                    time = re.findall('\d+\.?\d*',data['duration'])
                    if time :
                        if len(time) > 1:
                            detail['duration'] = int(time[0]) * 60 + int(time[1])
                        else :
                            if overHr:
                                detail['duration'] = int(time[0]) * 60
                            else :
                                detail['duration'] = int(time[0])

        detail['trailer'] = None
        if 'external'in data:
            if data['external'] is not None:
                for item in data['external']:
                    if item['name'] == 'Official Site':
                        detail['official'] = item['url'].replace("http://","").replace("https://","")
        
        # if 'official' in data:
        #     detail['official'] = data['official']
        
        # detail['twitter'] = None
        # if 'twitter' in data:
        #     detail['twitter'] = data['twitter']

        if 'studios'in data:
            if data['studios'] is not None:
                for item in data['studios']:
                    detail['studios'].append(item['name'])
        if 'genres'in data:
            if data['genres'] is not None:
                for item in data['genres']:
                    detail['genres'].append(item['name'])
        
        if 'themes'in data:
            if data['themes'] is not None:
                for item in data['themes']:
                    detail['genres'].append(item['name'])
        
        if 'trailer' in data:
            if data['trailer'] is not None:
                detail['trailer'] = data['trailer']['youtube_id']
                # a = data['trailer']['embed_url']
                # start = a.find('embed/')
                # end = a.find('?')
                # detail['trailer'] = a[start:end].replace('embed/','')
            
        if 'score' in data :
            if data['score'] is not None:
                b_score = data['score']
                detail['b_score'] = round(b_score,2)
            else:
                detail['b_score'] = None
        else: 
            detail['b_score'] =  None
        return detail
    except Exception:
        traceback.print_exc()
        return None


def get_top_1000_id_list():
    """
    Get a list of top-1000 anime, from MyAnimeList.
    If anything failed, return None.

    @return: a list of strings (1000 items), each string is an id.

    P.S. Regretfully, I failed to find an api which provides the whole list of anime
         on MyAnimeList. But fortunately, MyAnimeList provides a list ranked by rating.
         Since this project is called "anime-rating-db", I believe it's enough to pick
         up only top-1000 anime.
    """

    try:
        api_url = jikan_api + '/top/anime/'
        # items per page: 50
        anime_list = []
        for page in tqdm(range(1, 21)):
            whole_url = api_url + str(page)
            resp = requests.get(whole_url)
            # response in json format
            data = resp.json()['top']
            anime_list.extend([item['mal_id'] for item in data])
            # api request rate-limit
            time.sleep(req_delay)
        return anime_list
    except Exception:
        traceback.print_exc()
        return None


def cache_anime_detail(mal_id, dir_path='.'):
    """
    Cache detail for an anime, from MyAnimeList.

    @param id_list: a list of strings, each string is an id.
    @param dir_path: string, path to the cache directory.
    """

    try:
        api_url = jikan_api + '/anime/' + str(mal_id) 
        resp = requests.get(api_url)
        # response in json format
        data = resp.json()
        if 'error' in data and data['status'] == 403:
            # may get 403 for requesting too fast
            change_api_url()
            cache_anime_detail(mal_id)
        fpath = os.path.join(dir_path, '{}.json'.format(mal_id))
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        traceback.print_exc()

def getVoice(voice_id,useCache = True):
    try:
        # api_url = jikan_api + '/anime/' + str(mal_id) + '/full'
        api_url = 'https://api.jikan.moe/v4/people/' + str(voice_id) + '/full'
        cache_path = os.path.join('fetch/voice/' '/{}.json'.format(voice_id))
        updateDate = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            # if random.getrandbits(4) == 0 :
                updateDate = False
        # elif random.getrandbits(6) == 0 :
        #     updateDate = False
        if os.path.exists(cache_path) and updateDate or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            newdt = {}
            newdt['voice_id'] = data['mal_id']
            family_name = str(data['family_name']) if data['family_name'] != None else ''
            given_name = str(data['given_name'])  if data['given_name'] != None else ''
            newdt['name'] = family_name + given_name
            birth = None
            if data['birthday'] is not None and 'Unknown' not in data['birthday']:
                birth = data['birthday']
                idx = birth.find('T')
                if(idx != -1):
                    birth = birth[:idx]
                    birth = datetime.datetime.strptime(birth, '%Y-%m-%d')
                    birth = '{0}-{1:02d}-{2:02d}'.format(birth.year,birth.month, birth.day)
            newdt['birth'] = birth
            newdt['isMain'] = 0
            newdt['isSup'] = 0
            if data['voices']:
                for item in data['voices']:
                    if(item['role'] == 'Main'):
                        newdt['isMain'] +=1
                    elif(item['role'] =='Supporting'):
                        newdt['isSup'] +=1


        else:
            time.sleep(1)
            resp = requests.get(api_url, timeout=5)
            time.sleep(1)
            # response in json format
            data = resp.json()
            data = data['data']

            newdt = {}
            newdt['voice_id'] = data['mal_id']
            family_name = str(data['family_name']) if data['family_name'] != None else ''
            given_name = str(data['given_name'])  if data['given_name'] != None else ''
            newdt['name'] = family_name + given_name
            birth = None
            if data['birthday'] is not None and 'Unknown' not in data['birthday']:
                birth = data['birthday']
                idx = birth.find('T')
                if(idx != -1):
                    birth = birth[:idx]
                    birth = datetime.datetime.strptime(birth, '%Y-%m-%d')
                    birth = '{0}-{1:02d}-{2:02d}'.format(birth.year,birth.month, birth.day)
            newdt['birth'] = birth
            newdt['isMain'] = 0
            newdt['isSup'] = 0
            if data['voices']:
                for item in data['voices']:
                    if(item['role'] == 'Main'):
                        newdt['isMain'] +=1
                    elif(item['role'] =='Supporting'):
                        newdt['isSup'] +=1

            if os.path.exists(cache_path):
                    os.remove(cache_path)
                # add to cache
            if not os.path.isfile(cache_path):
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        return newdt
    except Exception:
        print('mal_id_Voice: {}'.format(voice_id))
        if useCache:
            cache_path = os.path.join('fetch/voice/' '/{}.json'.format(voice_id))
            if os.path.exists(cache_path):
                    os.remove(cache_path)
        traceback.print_exc()
        return None
        
def getChar(detail ,useCache = True):
    try:
        # api_url = jikan_api + '/anime/' + str(mal_id) + '/full'
        mai_id = str(detail['id'])
        newdetail = detail
        api_url = 'https://api.jikan.moe/v4/anime/' + mai_id + '/characters'
        cache_path = os.path.join('fetch/char/' '{}.json'.format(mai_id))
        updateDate = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            # if random.getrandbits(4) == 0 :
                updateDate = False
        # elif random.getrandbits(6) == 0 :
        #     updateDate = False
        if os.path.exists(cache_path) and updateDate or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            newdetail['voices'] = []
        
            for item in data:
                if(item['role'] == 'Main'):
                    vo = {}
                    vo['chId'] = item['character']['mal_id']
                    a = item['character']['images']['webp']['image_url'].replace("https://cdn.myanimelist.net/images/characters/","")
                    end = a.find('?')
                    vo['img'] = a[:end]
                    
                    vo['role'] = item['role']
                    # vo['score'] = item['voice_actors']
                    for actor in item['voice_actors']:
                        if actor['language'] == 'Japanese':
                            vo['voice'] = actor['person']['mal_id']
                            voiceData = getVoice(vo['voice'],useCache)
                            vo['name'] = None
                            vo['birth'] = None
                            if voiceData is not None:
                                vo['name'] = voiceData['name']
                                if 'birth' in voiceData:
                                    vo['birth'] = voiceData['birth']
                                vo['isMain'] = voiceData['isMain']
                                vo['isSup'] = voiceData['isSup']
                            newdetail['voices'].append(vo)
                            break
            return newdetail
        else:
            time.sleep(1)
            resp = requests.get(api_url, timeout=5)
            time.sleep(1)
            # response in json format
            data = resp.json()
            if 'error' in data:
                return detail
            data = data['data']
            newdetail['voices'] = []
            for item in data:
                if(item['role'] == 'Main'):
                    vo = {}
                    vo['chId'] = item['character']['mal_id']
                    a = item['character']['images']['webp']['image_url'].replace("https://cdn.myanimelist.net/images/characters/","")
                    end = a.find('?')
                    vo['img'] = a[:end]
                    
                    vo['role'] = item['role']
                    # vo['score'] = item['voice_actors']
                    for actor in item['voice_actors']:
                        if actor['language'] == 'Japanese':
                            vo['voice'] = actor['person']['mal_id']
                            voiceData = getVoice(vo['voice'],useCache)
                            vo['name'] = None
                            vo['birth'] = None
                            if voiceData is not None:
                                vo['name'] = voiceData['name']
                                if 'birth' in voiceData:
                                    vo['birth'] = voiceData['birth']
                                vo['isMain'] = voiceData['isMain']
                                vo['isSup'] = voiceData['isSup']
                            newdetail['voices'].append(vo)
                            break
                    
                    # add to cache
            if os.path.exists(cache_path):
                    os.remove(cache_path)
            if not os.path.isfile(cache_path):
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        return newdetail
    except Exception:
        print('mal_id_CharVoice: {}'.format(mai_id))
        if useCache:
            cache_path = os.path.join('fetch/char/' '{}.json'.format(mai_id))
            if os.path.exists(cache_path):
                    os.remove(cache_path)
        traceback.print_exc()
        return detail
    
def get_anime_detail(mal_id, cache=False, cache_dir='.',useCache = False,needSleep = False):
    """
    Get detail for an anime, from MyAnimeList.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param mal_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.
    """

    try:
 
        # api_url = jikan_api + '/anime/' + str(mal_id) + '/full'
        api_url = 'https://api.jikan.moe/v4/anime/' + str(mal_id) + '/full'
        cache_path = os.path.join(cache_dir, '{}.json'.format(mal_id))
        
        updateDate = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            # if random.getrandbits(4) == 0 :
                updateDate = False
        # elif random.getrandbits(6) == 0 :
        #     oldCache = False
        if cache and os.path.exists(cache_path) and updateDate or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            resp = requests.get(api_url, timeout=5)
            # response in json format
            data = resp.json()
            if 'error' in data:
                if data['status'] == 403:
                    # may get 403 for requesting too fast
                    change_api_url()
                    return get_anime_detail(mal_id, cache, cache_dir)
            elif cache:
                
                eLinks = get_external_links(mal_id)
                official = None
                twitter = None
                if eLinks is not None:
                    for i in eLinks:
                        if i[0] == 'Official Site':
                            official = i[1].replace('https://','').replace('http://','')
                        elif i[1].find('twitter') > 0:
                            twitter = i[1].replace('https://','').replace('http://','')

                data['official'] = official
                data['twitter'] = twitter
                
                if cache and os.path.exists(cache_path):
                    os.remove(cache_path)
                    
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            if needSleep:
                time.sleep(1)
        data = parse_data(data,mal_id)
        data = getChar(data,useCache)
        return data
    except Exception:
        print('mal_id: {}'.format(mal_id))
        traceback.print_exc()
        return None



# 直接抓網址
# def get_anime_detail2(ani_id, cache=False, cache_dir='.'):

#     try:
#         url = 'https://myanimelist.net/anime/' + str(ani_id)
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
#             AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
#         }
#         cache_path = os.path.join(cache_dir, '{}.json'.format(ani_id))
#         if cache and os.path.exists(cache_path):
#             with open(cache_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
#         else:
#             resp = requests.get(url, headers=headers)
#             # response in json format
#             html = resp.text
#             if not html:
#                 # got empty data
#                 # retry in 30s
#                 time.sleep(30)
#                 return get_anime_detail(ani_id, cache, cache_dir)
            
#             # 藉由 BeautifulSoup 套件將網頁原始碼使用 `html.parser` 解析器來解析
#             data = {'id': ani_id}
#             soup = BeautifulSoup(html, 'html.parser')
#             # 取得各個動畫元素區塊
#             ty = soup.find_all("a", href="https://myanimelist.net/topanime.php?type=tv")
#             if not ty:
#                 ty = soup.find_all("a", href="https://myanimelist.net/topanime.php?type=movie")
#             if not ty:
#                 ty = soup.find_all("a", href="https://myanimelist.net/topanime.php?type=ova")
                
#             data['type'] = ty[0].text

#             score = soup.select('div.score-label')[0].text
#             data['score'] = float(score)
#             vote = soup.select('div.score')[0]['data-user']
#             vote = vote.replace(',','')
#             match_obj = re.match(r'(\d+)', vote)
#             if match_obj:
#                 data['votes'] = int(match_obj.group(1))
#             else:
#                 data['votes'] = 0


#             img = soup.select('div#content')[0].select('img')
#             if hasattr(img,'data-src'):
#                 data['image'] = img[0]['data-src'].replace("https://cdn.myanimelist.net/images/anime/","")
#             else:
#                 data['image'] = 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png'
#             title = soup.select('h1.title-name strong')[0].text
#             title = title.strip().replace('\r\n', '')
#             data['title'] = title
            

#             enN = soup.select('div.js-alternative-titles')
#             if enN :
#                 data['en_name'] = soup.select('div.js-alternative-titles')[0].innerText
#             else:
#                 data['en_name'] = data['title']
            
#             data['jp_name']= soup.select('td.borderClass')[0].find("span", string="Japanese:").find_parent('div').text.replace('Japanese: ','').replace('\n','')
#             premiered= soup.find("span", string="Premiered:")
#             if premiered is not None:
#                 if premiered.find('?') == -1:
#                     premiered = premiered.find_parent('div').text.replace('Premiered: ','').replace('\n','')
#                     data['premiered'] = re.findall('.*([0-9]{4})',premiered)[0]
#             else:
#                 premiered= soup.find("span", string="Aired:")
#                 if premiered.find('?') == -1:
#                     premiered=premiered.find_parent('div').text.replace('Aired: ','').replace('\n','')
#                     data['premiered'] = re.findall('.*([0-9]{4})',premiered)[0]
#                 else:
#                     data['premiered'] =  None
#             gens = soup.select('td.borderClass')[0].find_all("span", itemprop="genre")
#             gen = []
#             for txt in gens:
#                 if txt.text != 'Kids' and txt.text != 'Seinen' and txt.text != 'Shoujo' and txt.text != 'Shounen':
#                     gen.append(txt.text)
#             data['genres'] = gen
            
#             duration = soup.select('td.borderClass')[0].find("span", string="Duration:").find_parent('div').text.replace('Duration: ','').replace('\n','')

#             if duration is not None:
#                     time = re.findall('\d+\.?\d*',duration)
#                     if time :
#                             if len(time) > 1:
#                                     data['duration'] = int(time[0]) * 60 + int(time[1])
#                             else :
#                                     data['duration'] = int(time[0])
#             source = soup.select('td.borderClass')[0].find("span", string="Source:").find_parent('div').text.replace('Source:','').replace('\n','').replace(' ','')
#             data['source'] = source
#             episodes = soup.select('td.borderClass')[0].find("span", string="Episodes:").find_parent('div').text.replace('Episodes:','').replace('\n','').replace(' ','')
#             data['episodes'] = episodes

#             # data['trailer']
#             a = soup.select('a.iframe')
#             if a :
#                 a = a[0].attrs['href']
#                 start = a.find('embed/')
#                 end = a.find('?')
#                 data['trailer'] = a[start:end].replace('embed/','')
                
#             if 'score' in data :
#                 if data['score'] is not None:
#                     b_score = data['score']
#                     data['bayesian_score'] = b_score
#                 else:
#                     data['bayesian_score'] = None
#             else: 
#                 data['bayesian_score'] =  None
            
#             if cache:
#                 # add to cache
#                 with open(cache_path, 'w', encoding='utf-8') as f:
#                     json.dump(data, f, indent=2, ensure_ascii=False)
#         return data
#     except Exception:
#         print('mal: {}'.format(ani_id))
#         traceback.print_exc()
#         return None



def get_external_links(mal_id):
    """
    Get external links for an anime, from MyAnimeList.
    If anything failed, return None.

    @param mal_id: string or int, an id.
    @param cookie: string, your cookie.
    @return: a list of tuple, containing links.

    P.S. External links are not provided by Jikan API, so we have to parse it from raw HTML.
         However, you must login to see external links, so cookie is needed.
    """

    try:
        url = 'https://myanimelist.net/anime/' + str(mal_id)
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
        #     AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15',
        #     'Cookie': cookie
        # }        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            # may get 403 for requesting too fast
            time.sleep(5)
            # retry in 1 min
            return get_external_links(mal_id)
        html = resp.text
        # parse HTML-format text
        soup = BeautifulSoup(html, 'html.parser')
        # div = soup.select('div.pb16')[0]
        exlinks = None
        if(len(soup.find_all('div', {'class':'external_links'})) != 0 ):
            div = soup.select('div.external_links')[0]
            exlinks = div.select('a')
        result = []
        if exlinks is not None:
            for item in exlinks:
                result.append((item.text ,item.attrs['href']))
        return result
    except Exception:
        print('mal_id exlink: {}'.format(mal_id))
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """
    print(get_anime_detail(1))
    
    # print(get_external_links(5114))
    
    # id_list = get_top_1000_id_list()
    # detail_list = []
    # for mal_id in tqdm(id_list):
    #     detail = get_anime_detail(mal_id)
    #     detail_list.append(detail)
    #     time.sleep(4)
    # import json
    # with open('mal.json', 'w', encoding='utf-8') as f:
    #     json.dump(detail_list, f, indent=2, ensure_ascii=False)
    
    # res = search_for_anime('爆れつハンター', 'Spell Wars: Sorcerer Hunters Revenge', '1995-10-03')
    # print(res)



