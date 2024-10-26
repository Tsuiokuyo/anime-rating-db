import requests
import xml.dom.minidom
import traceback
import time
import os
import random

from tqdm import tqdm


def parse_data(data):
    """
    Parse the data (response) to extract information.
    If anything failed, return None.

    @param data: string/xml.dom.minidom.Element, string should be in XML format.
    @return: dict, containing extracted information.
    """

    try:
        if type(data) == str:
            data = xml.dom.minidom.parseString(data)
            data = data.documentElement
        
        detail = {}
        # detail['id'] = int(data.getAttribute('id'))
        id_value = data.getAttribute('id').strip()        
        if not id_value:
            return None  # 如果 id_value 是空字串，直接返回 None
        
        detail['id'] = int(id_value)
        #detail['type'] = data.getAttribute('type')
        ratings = data.getElementsByTagName('ratings')
        if not ratings:
            detail['votes'] = None
            detail['b_score'] = None
            # detail['weighted_score'] = None
        else:
            ratings = ratings[0]
            detail['votes'] = int(ratings.getAttribute('nb_votes'))
            detail['b_score'] = float(ratings.getAttribute('bayesian_score')) if ratings.hasAttribute('bayesian_score') else None
            if detail['b_score'] is not None:
                detail['b_score'] = round(detail['b_score'], 2)
                
            detail['score'] = float(ratings.getAttribute('weighted_score')) if ratings.hasAttribute('weighted_score') else None
            if detail['score'] is not None:
                detail['score'] = round(detail['score'], 2)
        infos = data.getElementsByTagName('info')
        '''
        detail['titles'] = []
        for info in infos:
            info_type = info.getAttribute('type')
            info_lang = info.getAttribute('lang')
            if (info_type == 'Main title' or info_type == 'Alternative title') and (info_lang == 'EN' or info_lang == 'JA'):
                detail['titles'].append(info.childNodes[0].data)
            elif info_type == 'Vintage':
                vintage = info.childNodes[0].data
                if '(' not in vintage:
                    detail['air'] = vintage
        '''
        return detail
    except Exception:
        traceback.print_exc()
        return None


def get_all_anime_id_list():
    """
    Get id list of all anime, from Anime News Network.
    If anything failed, return None.

    @return: a list of strings, each string is an id.
    """
    
    try:
        api_url = 'https://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=anime&nlist=all'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(api_url, headers=headers)
        # response in XML format, parsing needed
        dom = xml.dom.minidom.parseString(resp.text)
        root = dom.documentElement
        items = root.getElementsByTagName('item')
        id_list = [item.getElementsByTagName('id')[0].childNodes[0].data for item in items]
        return id_list
    except Exception:
        traceback.print_exc()
        return None


def get_anime_detail_list(id_list):
    """
    Get details for anime in list, from Anime News Network.
    If anything failed, return None.

    @param id_list: a list of strings, each string is an id.
    @return: a list of dicts, each dict contains some detailed data.

    P.S. Requests will be batched. However, it'll still take a long time
         since you can only batch up to 50 titles at once, and the API is
         rate-limited to 1 request per second per IP address. A progress
         bar will be printed to screen.
    """

    try:
        api_url = 'https://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        max_batch = 50
        list_len = len(id_list)
        detail_list = []
        for l_end in tqdm(range(0, list_len, max_batch)):
            r_end = min(l_end + max_batch, list_len)
            whole_url = api_url + '/'.join(id_list[l_end: r_end])
            resp = requests.get(whole_url, headers=headers)
            # response in XML format, parsing needed
            try:
                dom = xml.dom.minidom.parseString(resp.text)
            except Exception:
                # if fail to parse, just skip it
                continue
            root = dom.documentElement
            items = root.getElementsByTagName('anime')
            for item in items:
                detail = parse_data(item)
                detail_list.append(detail) 
            # api request rate limit
            time.sleep(1)    
        return detail_list
    except Exception:
        traceback.print_exc()
        return None


def cache_anime_detail_list(id_list, dir_path='.'):
    """
    Cache details for anime in list, from Anime News Network.

    @param id_list: a list of strings, each string is an id.
    @param dir_path: string, path to the cache directory.

    P.S. Requests will be batched. However, it'll still take a long time
         since you can only batch up to 50 titles at once, and the API is
         rate-limited to 1 request per second per IP address. A progress
         bar will be printed to screen.
    """

    try:
        api_url = 'https://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        max_batch = 50
        list_len = len(id_list)
        detail_list = []
        for l_end in tqdm(range(0, list_len, max_batch)):
            r_end = min(l_end + max_batch, list_len)
            whole_url = api_url + '/'.join(id_list[l_end: r_end])
            resp = requests.get(whole_url, headers=headers)
            try:
                dom = xml.dom.minidom.parseString(resp.text)
            except Exception:
                # if fail to parse, just skip it
                continue
            root = dom.documentElement
            items = root.getElementsByTagName('anime')
            for item in items:
                ann_id = item.getAttribute('id')
                fpath = os.path.join(dir_path, '{}.xml'.format(ann_id))
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(item.toprettyxml())
            # api request rate limit
            time.sleep(1)    
    except Exception:
        traceback.print_exc()


def get_anime_detail(ann_id, cache=False, cache_dir='.',useCache = True,needSleep = False):
    """
    Get detail for an anime, from Anime News Network.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param ann_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.
    """

    try:
        api_url = 'https://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=' + str(ann_id)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        cache_path = os.path.join(cache_dir, '{}.xml'.format(ann_id))
        oldCache = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            # if random.getrandbits(4) == 0 :
                oldCache = False
        # elif random.getrandbits(6) == 0 :
        #     oldCache = False
        if cache and os.path.exists(cache_path) and oldCache or useCache and os.path.exists(cache_path):
            try:
                dom = xml.dom.minidom.parse(cache_path)
                data = dom.documentElement
            except Exception:
                    detail = {}
                    detail['id'] = int(ann_id)
                    detail['votes'] = None
                    detail['b_score'] = None
                    detail['weighted_score'] = None
                    return detail
        else:
            resp = requests.get(api_url, headers=headers, timeout=10)
            # response in xml format
            dom = xml.dom.minidom.parseString(resp.text)
            root = dom.documentElement
            # print(root.getElementsByTagName('anime')[0])
            # if root.getElementsByTagName('warning') is not None:
            #     if cache:
            #         with open(cache_path, 'w', encoding='utf-8') as f:
            #             f.write('no result')
            #     detail = {}
            #     detail['id'] = int(ann_id)
            #     detail['votes'] = None
            #     detail['b_score'] = None
            #     detail['weighted_score'] = None
            #     return detail
            
            # item = root.getElementsByTagName('anime')[0]
            
            anime_elements = root.getElementsByTagName('anime')
            if not anime_elements:
                # <anime> 元素不存在
                # print("No 'anime' element found.")
                return None
            item = anime_elements[0]
            if cache and os.path.exists(cache_path):
                    os.remove(cache_path)
            if cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(item.toprettyxml())
            data = item
            if needSleep:
                time.sleep(1)
        return parse_data(data)
    except Exception:
        print('ann: {}'.format(ann_id))
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """

    # id_list = get_all_anime_id_list()
    # cache_anime_detail_list(id_list, 'ann')
    # detail_list = get_anime_detail_list("10216")
    # import json
    # with open('ann.json', 'w', encoding='utf-8') as f:
    #     json.dump(detail_list, f, indent=2, ensure_ascii=False)
    # print(get_anime_detail(13, True, '.'))
    
    detail = get_anime_detail(10216)
    print(detail)