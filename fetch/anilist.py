import requests
import traceback
import json
import os
import time
import random

def get_anime_detail(anl_id, cache=False, cache_dir='.',useCache = True,needSleep = False):
    """
    Get detail for an anime, from AniList.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param anl_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.
    """

    try:
        api_url = 'https://graphql.anilist.co'
        cache_path = os.path.join(cache_dir, '{}.json'.format(anl_id))
       
        oldCache = True
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) > 86400 * (random.getrandbits(5)):
            # if random.getrandbits(4) == 0 :
                oldCache = False
        # elif random.getrandbits(6) == 0 :
        #     oldCache = False
        if cache and os.path.exists(cache_path) and oldCache or useCache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            query = '''
            query ($id: Int) {
                Media (id: $id, type: ANIME) {
                    id
                    averageScore
                    externalLinks {
                        site
                        url
                    }
                    stats {
                        scoreDistribution {
                            score
                            amount
                        }
                    }
                }
            }
            '''
            variables = {
                'id': anl_id
            }
            resp = requests.post(api_url, json={ 'query': query, 'variables': variables }, timeout=10)
            data = resp.json()['data']
            data = data['Media']

            url = None
            twitter = None
            if 'externalLinks' in data:
                for i in data['externalLinks']:
                    if i['site'] == 'Official Site':
                        url = i['url'].replace('https://','').replace('http://','')
                    
                    if i['site'] == 'Twitter':
                        twitter = i['url'].replace('https://','').replace('http://','')
                    
            data['official'] = url
            data['twitter'] = twitter
            
            if cache and os.path.exists(cache_path):
                    os.remove(cache_path)
            if cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            if needSleep:
                time.sleep(1)
        if data is  None or data == 'null':
            return None
        data['score'] = data['averageScore']
        if 'averageScore' in data:
            del data['averageScore']
        if 'externalLinks' in data:
            del data['externalLinks']
        return data
    except Exception:
        print('anilist: {}'.format(anl_id))
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """

    # print(get_anime_detail(21860))
'''
            query ($id: Int) {
                Media (id: $id, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    coverImage {
                        large
                    }
                    averageScore
                    stats {
                        scoreDistribution {
                            score
                            amount
                        }
                    }
                }
            }

'''