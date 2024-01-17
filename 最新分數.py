import json
from pickle import FALSE, TRUE
import time
import os
import shutil
import argparse
import numpy as np
import random
import gzip
import re


from json_minify  import json_minify
import json
from tqdm import tqdm
from fetch import anime_news_network, myanimelist, bangumi, anilist, anikore, gamer, anime_planet, anisearch, kitsu, notify_moe , anidb , trakt, sakuhindb,redditanimelist,annict,livechart,fanart,traktapi
from analyze import adjust, bayesian


MAL_DIR = 'fetch/mal'
BGM_DIR = 'fetch/bgm'
ANN_DIR = 'fetch/ann'
ANL_DIR = 'fetch/anilist'
AKR_DIR = 'fetch/anikore'
GAMER_DIR = 'fetch/gamer'
ANIMEPLANECOM_DIR = 'fetch/anime_planet'
ANISEARCH_DIR = 'fetch/anisearch'
KITSU_DIR = 'fetch/kitsu'
NOTIFYMOE_DIR = 'fetch/notify_moe'
ANIDB_DIR = 'fetch/anidb'
TRAKT_DIR = 'fetch/trakt'
SAKUHINDB_DIR = 'fetch/sakuhindb'
REDDITANIMELIST_DIR = 'fetch/redditanimelist'
ANNICT_DIR = 'fetch/annict'
LIVECHART_DIR = 'fetch/livechart'
VOICE_DIR = 'fetch/voice'
CHAR_DIR = 'fetch/char'
FANART_DIR = 'fetch/fanart'
TRAKTAPI_DIR = 'fetch/traktAPI'



def clear_cache():
    """
    Clear local cache files.
    """

    if os.path.exists(MAL_DIR):
        shutil.rmtree(MAL_DIR)
    if os.path.exists(BGM_DIR):
        shutil.rmtree(BGM_DIR)
    if os.path.exists(ANN_DIR):
        shutil.rmtree(ANN_DIR)
    if os.path.exists(ANL_DIR):
        shutil.rmtree(ANL_DIR)
    if os.path.exists(AKR_DIR):
        shutil.rmtree(AKR_DIR)
    if os.path.exists(GAMER_DIR):
        shutil.rmtree(GAMER_DIR)
    if os.path.exists(ANIMEPLANECOM_DIR):
        shutil.rmtree(ANIMEPLANECOM_DIR)
    if os.path.exists(ANISEARCH_DIR):
        shutil.rmtree(ANISEARCH_DIR)
    if os.path.exists(KITSU_DIR):
        shutil.rmtree(KITSU_DIR)
    if os.path.exists(NOTIFYMOE_DIR):
        shutil.rmtree(NOTIFYMOE_DIR)
    if os.path.exists(ANIDB_DIR):
        shutil.rmtree(ANIDB_DIR)
    if os.path.exists(TRAKT_DIR):
        shutil.rmtree(TRAKT_DIR)
    if os.path.exists(SAKUHINDB_DIR):
        shutil.rmtree(SAKUHINDB_DIR)
    if os.path.exists(REDDITANIMELIST_DIR):
        shutil.rmtree(REDDITANIMELIST_DIR)
    if os.path.exists(ANNICT_DIR):
        shutil.rmtree(ANNICT_DIR)
    if os.path.exists(LIVECHART_DIR):
        shutil.rmtree(LIVECHART_DIR)
    if os.path.exists(VOICE_DIR):
        shutil.rmtree(VOICE_DIR)
    if os.path.exists(CHAR_DIR):
        shutil.rmtree(CHAR_DIR)
        
    os.mkdir(MAL_DIR)
    os.mkdir(BGM_DIR)
    os.mkdir(ANN_DIR)
    os.mkdir(ANL_DIR)
    os.mkdir(AKR_DIR)
    os.mkdir(GAMER_DIR)
    os.mkdir(ANIMEPLANECOM_DIR)
    os.mkdir(ANISEARCH_DIR)
    os.mkdir(KITSU_DIR)
    os.mkdir(NOTIFYMOE_DIR)
    os.mkdir(ANIDB_DIR)
    os.mkdir(TRAKT_DIR)
    os.mkdir(SAKUHINDB_DIR)
    os.mkdir(REDDITANIMELIST_DIR)
    os.mkdir(ANNICT_DIR)
    os.mkdir(LIVECHART_DIR)
    os.mkdir(VOICE_DIR)
    os.mkdir(CHAR_DIR)

def update_once(args, save_method, pre_data={}):
    """
    Update the data once.

    @param args: some args to be passed, as defined in arg_parser.
    @param save_method: a function, used for saving data to file/sql/oss.
    @param pre_data: a dict, loaded from tmp file.
    """
    
    with open('all_id.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    allow_types = set(('TV', 'Movie', 'OVA'))
    mapping = dict(list(mapping.items()))
    # fetch data
    all_data = pre_data
    traktErr = []
    # traktErrElse = []
    for uid, item in tqdm(mapping.items()):
        start = time.time()
        if uid in all_data:
            continue
        if item['mal'] is None:
            continue
        assert item['mal'] is not None
        # print('目前處理：MALid = ' + str(item['mal']))
        allCount = 0
        if item['livechart'] is not None:
            allCount +=1
        if item['ann'] is not None:
            allCount +=1
        if item['bgm'] is not None:
            allCount +=1
        if item['anilist'] is not None:
            allCount +=1
        if item['anikore'] is not None:
            allCount +=1
        if item['animePlanetCom'] is not None:
            allCount +=1
        if item['anisearch'] is not None:
            allCount +=1
        if item['kitsu'] is not None:
            allCount +=1
        if item['notifyMoe'] is not None:
            allCount +=1
        # 9個
        if  allCount >= 4 or item['isHentai']:  
            
            # if item['mal'] > 10:
            #     continue
            try:
                mal_res = myanimelist.get_anime_detail(item['mal'], True, MAL_DIR,True)
            except Exception:
                print('mal_res: {}'.format(item['mal']))
            if mal_res is None or mal_res['type'] not in allow_types:
                time.sleep(args.delay)
                continue
            else:
                # print('redditanimelist start...')
                try:
                    redditanimelist_res = redditanimelist.get_anime_detail(item['mal'],True,REDDITANIMELIST_DIR,True)
                except Exception:
                    print('mal_res: {}'.format(item['mal']))
                # redditanimelist_res = None
            if item['livechart'] is not None:
                    # print('livechart start...')
                    # livechart_res = None
                    try:
                        livechart_res = livechart.get_anime_detail(item['livechart'], True, LIVECHART_DIR,True)
                    except Exception:
                        print('livechart: {}'.format(item['livechart']))
            else:   
                    livechart_res = None  
            if item['ann'] is not None:
                    # print('anime_news_network start...')
                    try:
                        ann_res = anime_news_network.get_anime_detail(item['ann'], True, ANN_DIR,True)
                    except Exception:
                        print('ann: {}'.format(item['ann']))
            else:
                    ann_res = None
            if item['bgm'] is not None:
                    # print('bangumi start...')
                    try:
                        bgm_res = bangumi.get_anime_detail(item['bgm'], True, BGM_DIR,True)
                        if bgm_res is None: #里番
                            bgm_res = bangumi.get_anime_detail2(item['bgm'], True, BGM_DIR,True)
                    except Exception:
                        print('bgm: {}'.format(item['bgm']))
            else:
                    bgm_res = None
            if item['anilist'] is not None:
                    # print('anilist start...')
                    try:
                        anl_res = anilist.get_anime_detail(item['anilist'], True, ANL_DIR,True)
                    except Exception:
                        print('anilist: {}'.format(item['anilist']))
            else:
                    anl_res = None
            if item['anikore'] is not None and not item['isHentai']:
                    # print('anikore start...')
                    try:
                        akr_res = anikore.get_anime_detail(item['anikore'], True, AKR_DIR,True)
                    except Exception:
                        print('anikore: {}'.format(item['anikore']))
            else:
                    akr_res = None    
            if item['gamer'] is not None:
                    # print('gamer start...')
                    try:
                        gamer_res = gamer.get_anime_detail(item['gamer'], True, GAMER_DIR,True)
                    except Exception:
                        print('gamer: {}'.format(item['gamer']))
            else:
                    gamer_res = None   
            if item['animePlanetCom'] is not None:
                    # print('animePlanetCom start...')
                    try:
                        animePlanetCom_res = anime_planet.get_anime_detail(item['animePlanetCom'], True, ANIMEPLANECOM_DIR,True)
                    except Exception:
                        print('animePlanetCom: {}'.format(item['animePlanetCom']))
            else:
                    animePlanetCom_res = None           
            if item['anisearch'] is not None:
                    # print('anisearch start...')
                    try:
                        anisearch_res = anisearch.get_anime_detail(item['anisearch'], True, ANISEARCH_DIR,True)
                    except Exception:
                        print('anisearch: {}'.format(item['anisearch']))
            else:
                    anisearch_res = None      
            if item['kitsu'] is not None:
                    # print('kitsu start...')
                    try:
                        kitsu_res = kitsu.get_anime_detail(item['kitsu'], True, KITSU_DIR,True)
                    except Exception:
                        print('kitsu: {}'.format(item['kitsu']))
            else:
                    kitsu_res = None    
            
            if item['notifyMoe'] is not None:
                    # print('notifyMoe start...')
                    try:
                        notifyMoe_res = notify_moe.get_anime_detail(item['notifyMoe'], True, NOTIFYMOE_DIR,True)
                    # notifyMoe_res = None
                    except Exception:
                        print('notifyMoe: {}'.format(item['notifyMoe']))
            else:
                    notifyMoe_res = None     
            if notifyMoe_res is not None and 'traktId' in notifyMoe_res :
                    # print('trakt start...')
                    # trakt_res = None
                    try:
                        trakt_res = trakt.get_anime_detail(notifyMoe_res['traktId'], True, TRAKT_DIR,True)
                    except Exception:
                        print('traktId: {}'.format(item['traktId']))
                    # if trakt_res is None:
                        # traktErr.append(notifyMoe_res['traktId'])
                        # with open('traktErr.json', 'w', encoding='utf-8') as f:
                        #     json.dump(traktErr, f, indent=2, ensure_ascii=False)
            else:
                        trakt_res = None
            if item['sakuhindb'] is not None:
                    # print('sakuhindb start...')
                    try:
                        sakuhindb_res = sakuhindb.get_anime_detail(item['sakuhindb'], True, SAKUHINDB_DIR,True)
                    except Exception:
                        print('sakuhindb: {}'.format(item['sakuhindb']))
            else:
                    sakuhindb_res = None    
            if 'annict' in item: #必要
                    if item['annict'] is not None:
                            # print('annict start...')
                            try:
                                annict_res = annict.get_anime_detail(item['annict'], True, ANNICT_DIR,True)
                            # annict_res = None  
                            except Exception:
                                print('annict: {}'.format(item['annict']))
                    else:
                            annict_res = None    
            else:
                annict_res    = None
            if item['anidb'] is not None:
                    try:
                    # anidb_res = None
                    # print('anidb start...')
                        anidb_res = anidb.get_anime_detail2(item['anidb'], True, ANIDB_DIR,True)
                    except Exception:
                        print('anidb: {}'.format(item['anidb']))
            else:
                    anidb_res = None   
                    
            voiranime = None 
            s1vote = None 
            kinopoisk = None 
            animeflv = None 
            animeaddicts = None 
            csfd = None 
            
            if 'voiranime' in item and item['voiranime']:
                voiranime = item['voiranime'] 
            if item['s1vote']:
                s1vote =  item['s1vote'] 
            if item['kinopoisk']:
                kinopoisk = item['kinopoisk'] 
            if item['animeflv']:
                animeflv = item['animeflv'] 
            if item['animeaddicts']:
                animeaddicts = item['animeaddicts'] 
            if item['csfd']:
                csfd = item['csfd']  
                    
            banner = None
            tvdb_res = None
            imdb_res = None 
            tmdb_res = None    
            if item['tvdb'] is not None:
                    tvdb_res = item['tvdb']
            if item['imdb'] is not None:
                    imdb_res = item['imdb']
            if item['tmdb'] is not None:
                    tmdb_res = item['tmdb']
                    
            if trakt_res is not None:
                xxdb = traktapi.get_anime_detail(trakt_res['id'],True,TRAKTAPI_DIR,True)
                if xxdb['tvdb'] is not None:
                    tvdb_res = xxdb['tvdb']
                if xxdb['imdb'] is not None:
                    imdb_res = xxdb['imdb']
                if xxdb['tmdb'] is not None:
                    tmdb_res = xxdb['tmdb']
                
                banner = 'traktQWQ' + trakt_res['coverS']
                del trakt_res['coverS']
            
            if anisearch_res is not None :
                if anisearch_res['coverS'] is not None:
                    banner = 'anisearchQWQ'+anisearch_res['coverS']
                del anisearch_res['coverS']
            
            if kitsu_res is not None:
                if kitsu_res['coverT'] is not None:
                    banner = 'kitsuQWQ'+kitsu_res['coverT']
                del kitsu_res['coverT']
            
            if tvdb_res is not None:
                fan_res = fanart.get_anime_detail(tvdb_res,True,FANART_DIR,True,mal_res['type'])
                if fan_res is not None:
                    banner = fan_res

            onl = {}
            if trakt_res is not None:
                # if trakt_res['online']:
                #     for uid, item in trakt_res['online'].items():
                #         onl[uid] = item  
                if  trakt_res['online']:
                    for oid, item in trakt_res['online'].items():
                        oName = None
                        if oid.lower().find('amazon') != -1:
                            oName = 'Amazon Prime Video'
                        elif oid.lower().find('ani-one asia') != -1:
                            oName = '羚邦(Ani-One) YouTube'
                        elif oid.lower().find('animelog') != -1:
                            oName = 'AnimeLog Youtube'
                        elif oid.lower().find('bahamut') != -1:
                            oName = '動畫瘋'
                        elif oid.lower().find('cht mod') != -1:
                            oName = '中華電信MOD'
                        elif oid.lower().find('catchplay') != -1:
                            oName = 'CatchPlay+ TW'
                        elif oid.lower().find('disney') != -1:
                            oName = 'Disney+'
                        elif oid.lower().find('gundam.info') != -1:
                            oName = 'GUNDAM.INFO Youtube'
                        elif oid.lower().find('hoogle play') != -1:
                            oName = 'Google Play'
                        elif oid.lower().find('hamivideo') != -1:
                            oName = 'HamiVideo'
                        elif oid.lower().find('kktv') != -1:
                            oName = 'KKTV'
                        elif oid.lower().find('line tv') != -1:
                            oName = 'LINE TV Taiwan'
                        elif oid.lower().find('litv') != -1:
                            oName = 'LiTV立視'
                        elif oid.lower().find('muse tw') != -1:
                            oName = '木棉花(Muse) Youtube'
                        elif oid.lower().find('netflix') != -1:
                            oName = 'Netflix'
                        elif oid.lower().find('yahoo') != -1:
                            oName = 'Yahoo! TV Taiwan'
                        elif oid.lower().find('bilibili') != -1:
                            oName = 'bilibili'
                        elif oid.lower().find('哔哩') != -1:
                            oName = 'bilibili'
                        elif oid.lower().find('friday') != -1:
                            oName = 'friDay影音'
                        elif oid.lower().find('hmvod') != -1:
                            oName = 'hmvod'
                        elif oid.lower().find('iqiyi') != -1:
                            oName = 'iQIYI愛奇藝'
                        elif oid.lower().find('itunes') != -1:
                            oName = 'iTunes'
                        elif oid.lower().find('myvideo') != -1:
                            oName = 'MyVideo'
                        elif oid.lower().find('line_tv') != -1:
                            oName = 'LINE TV Taiwan'
                        else :
                            # traktErrElse.append(oid)
                            oName = None
                        if oName is not None:
                            onl[oName] = item
                        # onl[oid] = item  

            if gamer_res is not None :
                if gamer_res['online']:
                    onl['動畫瘋'] = gamer_res['online']
                del gamer_res['online']
            if livechart_res is not None :
                if livechart_res['online']:
                    for onlineId, item in livechart_res['online'].items():
                        if onlineId.find('Crunchyroll') == -1 and onlineId.find('GagaOOLala') == -1 and onlineId.find('NHK WORLD') == -1 and onlineId.find('Pokémon') == -1\
                        and onlineId.find('Rooster Teeth') == -1 and onlineId.find('YouTube') == -1 \
                        and onlineId.find('iTunes') == -1 and onlineId.find('Twitter') == -1 and onlineId.find('Instagram') == -1 and onlineId.find('Plex') == -1 and onlineId.find('Steam') == -1\
                        and onlineId.find('Tencent Video') == -1 and onlineId.find('AnimeLog') == -1 and onlineId.find('i-Fun') == -1:
                            onlineIdName = ''
                            if onlineId.find('Amazon') != -1:
                                onlineIdName = 'Amazon Prime Video'
                            elif onlineId.find('Ani-One') != -1:
                                onlineIdName = '羚邦(Ani-One) YouTube'
                            # elif onlineId.find('AnimeLog') != -1:
                            #     onlineIdName = 'AnimeLog Youtube'
                            elif onlineId.find('Bahamut') != -1:
                                onlineIdName = '動畫瘋'
                            elif onlineId.find('CHT MOD') != -1:
                                onlineIdName = '中華電信MOD'
                            elif onlineId.find('CatchPlay') != -1:
                                onlineIdName = 'CatchPlay+ TW'
                            elif onlineId.find('Disney') != -1:
                                onlineIdName = 'Disney+'
                            # elif onlineId.find('GUNDAM.INFO') != -1:
                            #     onlineIdName = 'GUNDAM.INFO Youtube'
                            elif onlineId.find('Google') != -1:
                                onlineIdName = 'Google Play'
                            elif onlineId.find('HamiVideo') != -1:
                                onlineIdName = 'HamiVideo'
                            elif onlineId.find('KKTV') != -1:
                                onlineIdName = 'KKTV'
                            elif onlineId.find('LINE TV') != -1:
                                onlineIdName = 'LINE TV Taiwan'
                            elif onlineId.find('LiTV') != -1:
                                onlineIdName = 'LiTV立視'
                            elif onlineId.find('Muse TW') != -1:
                                onlineIdName = '木棉花(Muse) Youtube'
                            elif onlineId.find('Netflix') != -1:
                                onlineIdName = 'Netflix'
                            elif onlineId.find('Yahoo') != -1:
                                onlineIdName = 'Yahoo! TV Taiwan'
                            elif onlineId.find('bilibili') != -1:
                                onlineIdName = 'bilibili'
                            elif onlineId.find('哔哩') != -1:
                                onlineIdName = 'bilibili'
                            elif onlineId.find('friDay') != -1:
                                onlineIdName = 'friDay影音'
                            elif onlineId.find('hmvod') != -1:
                                onlineIdName = 'hmvod'
                            elif onlineId.find('iQIYI') != -1:
                                onlineIdName = '愛奇藝'
                            # elif onlineId.find('iTunes') != -1:
                            #     onlineIdName = 'iTunes'
                            elif onlineId.find('myVideo') != -1:
                                onlineIdName = 'MyVideo'
                            # else :
                            #     onlineIdName = onlineId
                            if onlineIdName != '':
                                onl[onlineIdName] = item
                del livechart_res['online']
                
            official = None                    
            if  anisearch_res is not None and 'official' in anisearch_res :
                if anisearch_res['official'] is not None and anisearch_res['official'] != '':
                    official = anisearch_res['official']
                del anisearch_res['official']   
            if  anl_res is not None and 'official' in anl_res:
                if anl_res['official'] is not None and anl_res['official'] != '':
                    official = anl_res['official']
                del anl_res['official']
                
            if mal_res is not None and 'official' in mal_res:
                if mal_res['official'] is not None and mal_res['official']!= '' :
                    official = mal_res['official']
                del mal_res['official']
                
            twitter = None                    
            if  anisearch_res is not None and 'twitter' in anisearch_res :
                if anisearch_res['twitter'] is not None and anisearch_res['twitter'] != '':
                    twitter = anisearch_res['twitter']
                del anisearch_res['twitter']   
            if  anl_res is not None and 'twitter' in anl_res :
                if anl_res['twitter'] is not None and anl_res['twitter'] != '':
                    twitter = anl_res['twitter']
                del anl_res['twitter']

            if mal_res is not None and 'twitter' in mal_res:
                if mal_res['twitter'] is not None and mal_res['twitter'] != '' :
                    twitter = mal_res['twitter']
                del mal_res['twitter']
                                        
            
            all_data[uid] = {
                'MAL': mal_res,
                'ANN': ann_res,
                'BGM': bgm_res,
                'AniList': anl_res,
                'Anikore': akr_res,
                'Gamer' : gamer_res,
                'AnimePlanetCom' : animePlanetCom_res,
                'anisearch': anisearch_res,
                'kitsu': kitsu_res,
                'notifyMoe' : notifyMoe_res,
                'anidb': anidb_res,
                'trakt': trakt_res,
                'sakuhindb': sakuhindb_res,
                'redditanimelist': redditanimelist_res,
                'annict':annict_res,
                'livechart':livechart_res,
                'online':onl,
                'tvdb':tvdb_res,
                'imdb':imdb_res,
                'tmdb':tmdb_res,
                'official' : official,
                'twitter' : twitter,
                'banner': banner,
                'voiranime': voiranime,
                's1vote': s1vote,
                'kinopoisk':kinopoisk,
                'animeflv':animeflv,
                'animeaddicts':animeaddicts,
                'csfd':csfd
            }
            # save to tmp file
            # with open('all.tmp.json', 'w', encoding='utf-8') as f:
            #     json.dump(all_data, f, indent=2, ensure_ascii=False)
            # request delay
            # end = time.time()
            # if end - start < args.delay:
            #     time.sleep(args.delay - (end - start))
    
    # print(traktErrElse)
    # re-calculate the scores
    
    # for anilist
    print('15:anilist start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        anl = item['AniList']
        if anl is not None and anl['stats']['scoreDistribution']:
            ids.append(uid)
            rating_detail = [0 for _ in range(10)]
            for stat in anl['stats']['scoreDistribution']:
                rating_detail[int(stat['score'] / 10) - 1] = stat['amount']
            all_data[uid]['AniList']['votes'] = int(np.sum(rating_detail))
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if score is not None:
                    all_data[uid]['AniList']['b_score'] = round(score,2)
                else:
                    all_data[uid]['AniList']['b_score'] = 0
        if anl is not None and anl['stats']['scoreDistribution'] is None:
            all_data[uid]['AniList']['b_score'] = 0
            
    # for kitsu
    print('14:kitsu start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        kit = item['kitsu']
        if kit is not None and kit['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(kit['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            
            
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['kitsu']['b_score'] = round(score/2,2)
                else:
                    all_data[uid]['kitsu']['b_score'] = 0
        if kit is not None and kit['score'] is None:
            all_data[uid]['kitsu']['b_score'] = 0
            
    # for redditanimelist
    print('13:redditanimelist start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        reddit = item['redditanimelist']
        if reddit is not None and reddit['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(reddit['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['redditanimelist']['b_score'] = round(score,2)
                else:
                    all_data[uid]['redditanimelist']['b_score'] = 0
        if reddit is not None and reddit['rating_detail'] is None:
            all_data[uid]['redditanimelist']['b_score'] = 0 

    # for anisearch
    print('12:anisearch start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        anis = item['anisearch']
        if anis is not None and anis['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(anis['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    score = score * 2
                    all_data[uid]['anisearch']['b_score'] = round(score,2)
                else:
                    all_data[uid]['anisearch']['b_score'] = 0
        if anis is not None and anis['rating_detail'] is  None:
            all_data[uid]['anisearch']['b_score'] = 0
            
    # for ap
    print('11:AnimePlanetCom start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in tqdm(all_data.items()):
        ap = item['AnimePlanetCom']
        if ap is not None and ap['score'] is not None:
            ids.append(uid)
            ratings[0].append(ap['score'] * 2)
            ratings[1].append(ap['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['AnimePlanetCom']['b_score'] = round(score,2)
                else:
                    all_data[uid]['AnimePlanetCom']['b_score'] = 0
        if ap is not None and ap['score'] is None:
            all_data[uid]['AnimePlanetCom']['b_score'] = 0
            
    # for bangumi
    print('10:bgm start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        bgm = item['BGM']
        if bgm is not None and bgm['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(bgm['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if score is not None:
                    all_data[uid]['BGM']['b_score'] = round(score,2)
                else:
                    all_data[uid]['BGM']['b_score'] = 0
        if bgm is not None and bgm['rating_detail'] is  None:
            all_data[uid]['BGM']['b_score'] = 0

        # for anidb
    print('9:anidb start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in tqdm(all_data.items()):
        ani = item['anidb']
        if ani is not None and ani['score'] is not None:
            ids.append(uid)
            ratings[0].append(ani['score'])
            ratings[1].append(ani['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['anidb']['b_score'] = round(score,2)
                else:
                    all_data[uid]['anidb']['b_score'] = 0
        if ani is not None and ani['score'] is  None:
            all_data[uid]['anidb']['b_score'] = 0

    # for notifyMoe
    print('8:notifyMoe start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in tqdm(all_data.items()):
        notifyMoe = item['notifyMoe']
        if notifyMoe is not None and notifyMoe['score'] is not None:
            ids.append(uid)
            ratings[0].append(notifyMoe['score'])
            ratings[1].append(notifyMoe['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['notifyMoe']['b_score'] = round(score,2)
                else:
                    all_data[uid]['notifyMoe']['b_score'] = 0
        if notifyMoe is not None and notifyMoe['score'] is  None:
            all_data[uid]['notifyMoe']['b_score'] = 0
    # for anikore
    print('7:Anikore start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in tqdm(all_data.items()):
        akr = item['Anikore']
        if akr is not None and akr['score'] is not None:
            ids.append(uid)
            ratings[0].append(akr['score'] * 2)
            ratings[1].append(akr['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if score is not None:
                    all_data[uid]['Anikore']['b_score'] = round(score,2)
                else:
                    all_data[uid]['Anikore']['b_score'] = 0
        if akr is not None and akr['score'] is  None:
            all_data[uid]['Anikore']['b_score'] = 0
        
    # for livechart
    print('6:livechart start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in tqdm(all_data.items()):
        lc = item['livechart']
        if lc is not None and lc['score'] is not None:
            ids.append(uid)
            ratings[0].append(lc['score'])
            ratings[1].append(lc['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['livechart']['b_score'] = round(score,2)
                else:
                    all_data[uid]['livechart']['b_score'] = 0
        if lc is not None and lc['score'] is  None:
            all_data[uid]['livechart']['b_score'] = 0

    # for annict
    print('5:annict start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        anni = item['annict']
        if anni is not None and anni['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(anni['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['annict']['b_score'] = round(score*2.5,2)
                else:
                    all_data[uid]['annict']['b_score'] = 0
        if anni is not None and anni['rating_detail'] is None:
            all_data[uid]['annict']['b_score'] = 0
    # for gamer
    print('4:Gamer start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        gam = item['Gamer']
        if gam is not None and gam['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(gam['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    score = score * 2
                    all_data[uid]['Gamer']['b_score'] = round(score,2)
                else:
                    all_data[uid]['Gamer']['b_score'] = 0
        if gam is not None and gam['rating_detail'] is None:
            all_data[uid]['Gamer']['b_score'] = 0

    # for sakuhindb
    print('3:sakuhindb start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        sakuhin = item['sakuhindb']
        if sakuhin is not None and sakuhin['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(sakuhin['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['sakuhindb']['b_score'] = round(score,2)
                else:
                    all_data[uid]['sakuhindb']['b_score'] = 0
        if sakuhin is not None and sakuhin['rating_detail'] is None:
            all_data[uid]['sakuhindb']['b_score'] = 0 
            
    # for trakt
    print('2:trakt start bayesian')
    ids, ratings = [], []
    for uid, item in tqdm(all_data.items()):
        tr = item['trakt']
        if tr is not None and tr['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(tr['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['trakt']['b_score'] = round(score,2)
                else:
                    all_data[uid]['trakt']['b_score'] = 0
        if tr is not None and tr['rating_detail'] is None:
            all_data[uid]['trakt']['b_score'] = 0

    # bayesian_score => b_score
    # normalize and average
    print('1:normalize and average')
    all_data = adjust.adjust_scores(all_data)
    min_count = 4
    all_list = []
    
    for uid, item in tqdm(all_data.items()):
        count = 0
        score_sum = 0
        # adj_score_sum = 0
        # adj_count = 0
        for site in item:
            if site == 'tmdb' or site == 'imdb' or site == 'tvdb' or site == 'official' or site == 'twitter' or site == 'banner':
                break
            site_data = item[site]
            #if site_data is not None and 'adjusted_score' in site_data: 
            
            # 改過為這條，不過標準化分數覺得有問題 改成貝氏分數
            # if site_data is not None and 'adj_score' in site_data:
            #     if site_data['adj_score'] is not None: 
            #         adj_score_sum += site_data['adj_score']
            #         if site_data['adj_score'] > 0:
            #             adj_count += 1
            
            if site_data is not None and 'b_score' in site_data:
                if site_data['b_score'] is not None: 
                    score_sum += site_data['b_score']
                    if site_data['b_score'] > 0:
                        count += 1
        
        if count >= min_count or  item['MAL']['genres'] and count >= 2 and 'Hentai' in item['MAL']['genres']:
            score_org = score_sum / count
            item['score'] = round(score_org,2)
            # adj_score_org = adj_score_sum / count
            # item['adj_score'] = round(adj_score_org,2)
            all_list.append(item)
        else: 
            item['score'] = 0
            item['adj_score'] = 0
            all_list.append(item)
            
            
        if item['BGM']:
            del item['BGM']['rating_detail']
        if  item['AniList']:
            del item['AniList']['stats']
        if item['Gamer']:
            del item['Gamer']['rating_detail']
        if item['anisearch']:
            del item['anisearch']['rating_detail']
        if item['kitsu']:
            del item['kitsu']['rating_detail']
        if  item['trakt']:
            del item['trakt']['rating_detail']
        if item['sakuhindb']:
            del item['sakuhindb']['rating_detail']
        if item['annict']:
            del item['annict']['rating_detail']
        if item['redditanimelist']:
            del item['redditanimelist']['rating_detail']
            
        
    # save
    print('0:rank and save')
    all_list.sort(key=lambda x: x['score'], reverse=True)
    rankIndex = 0
    scoreZero = False
    for i in tqdm(all_list):
        if not scoreZero:
            rankIndex += 1
        if i['score'] == 0:
            scoreZero = True
        i['rank']=rankIndex
        # i['seen']=False
    save_method(all_list)


def always_update(args, save_method):
    """
    Keep udating the data.

    @param args: some args to be passed, as defined in arg_parser.
    @param save_method: a function, used for saving data to file/sql/oss.
    """

    myanimelist.jikan_api = args.jikan
    myanimelist.req_delay = args.delay
    myanimelist.use_api_pool = args.jikan_use_api_pool
    if args.jikan_use_api_pool:
        if args.jikan_api_pool == '':
            raise RuntimeError('You should provide the api pool if you enable Jikan api pool.')
        myanimelist.jikan_api_pool = [url for url in args.jikan_api_pool.split(' ') if url != '']
        myanimelist.jikan_api = myanimelist.jikan_api_pool[0]
        myanimelist.jikan_api_idx = 0

    if args.checkpoint != '':
        with open(args.checkpoint, 'r', encoding='utf-8') as f:
            pre_data = json.load(f)
    else:
        pre_data = {}
    
    while True:
        start_time = time.time()
        # clear_cache()
        update_once(args, save_method, pre_data)
        end_time = time.time()
        time_spent = int(end_time - start_time)
        time_to_sleep = max(args.interval - time_spent, 0)
        print('\n\n\nSleeping for {} seconds\n\n\n'.format(time_to_sleep))
        time.sleep(time_to_sleep)
        del pre_data
        pre_data = {}



if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--jikan', default='https://api.jikan.moe/v4',
        help='The URL of Jikan api')
    arg_parser.add_argument('--jikan_use_api_pool', action='store_true', default=False,
        help='Enable Jikan api pool')
    arg_parser.add_argument('--jikan_api_pool', default='',
        help='Jikan api url pool, use space to divide urls')
    arg_parser.add_argument('--delay', type=float, default=0.1,
        help='Delay seconds for requests')
    arg_parser.add_argument('--interval', type=int, default=86400,#86400
        help='Update interval (seconds)')
    arg_parser.add_argument('--checkpoint', default='',
    # arg_parser.add_argument('--checkpoint', default='all.tmp.json',
        help='File path to checkpoint (all.tmp.json).')
    args = arg_parser.parse_args()

    def save_json(data):
        # 將數據轉換為 JSON 字符串
        json_string = json.dumps(data, indent=2, ensure_ascii=False)

        # 保存原始 JSON 到文件
        with open('all.save.json', 'w', encoding='utf-8') as f:
            f.write(json_string)
            
        # 使用 gzip 保存原始 JSON 到文件
        with gzip.open('test2.gzip', 'wt', encoding='utf-8') as zipfile:
            json.dump(data, zipfile)

        # 保存最小化的 JSON 到文件
        minified_json_string = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        with open('all.save.min.json', 'w', encoding='utf-8') as f:
            f.write(minified_json_string)

        # 使用 gzip 保存最小化的 JSON 到文件
        with gzip.open('test2min.gzip', 'wt', encoding='utf-8') as zipfile:
            json.dump(data, zipfile, separators=(',', ':'))

    always_update(args, save_json)
    
