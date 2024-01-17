import json
from pickle import FALSE, TRUE
import time
import os
import shutil
import argparse
import numpy as np
import random
import gzip

from tqdm import tqdm
from fetch import anime_news_network, myanimelist, bangumi, anilist, anikore, gamer, anime_planet, anisearch, kitsu, notify_moe , anidb , trakt, sakuhindb,redditanimelist,annict,livechart
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
    error_trakt = [
    "20100",
    "65933",
    "62038",
    "63601",
    "64566",
    "65902",
    "36510",
    "64734",
    "61029",
    "63130",
    "64765",
    "65071",
    "10775",
    "65353",
    "21078",
    "65781",
    "60992",
    "63748",
    "8916",
    "37684",
    "62371",
    "37684",
    "37684",
    "37684",
    "61452",
    "73016",
    "43276",
    "37684",
    "63262",
    "73997",
    "26116",
    "65020",
    "63600",
    "64028",
    "55852",
    "36463",
    "70902",
    "78252",
    "97608",
    "97608",
    "97608",
    "44072",
    "64737",
    "68738",
    "77886",
    "96359",
    "36463",
    "77177",
    "79729",
    "100199",
    "101614",
    "101257",
    "122059",
    "106589",
    "105484",
    "100199",
    "106167",
    "109108",
    "141438",
    "158476",
    "205923",
    "206633",
    "209283",
    "212712",
    "205785",
    "204230",
    "210558",
    "201681",
    "213555",
    "219262",
    "206938",
    "212932",
    "215463"
    ]
    allow_types = set(('TV', 'Movie', 'OVA'))

    # fetch data
    all_data = pre_data
    # traktErr = []
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
        # if item['sakuhindb'] is not None:
        #     allCount +=1
        if item['gamer'] is not None or  allCount >= 4 or item['isHentai']:  
            # if item['mal'] > 50:
            #     continue
            mal_res = myanimelist.get_anime_detail(item['mal'], True, MAL_DIR,True)
            if mal_res is None or mal_res['type'] not in allow_types:
                time.sleep(args.delay)
                continue
            else:
                # print('redditanimelist start...')
                redditanimelist_res = redditanimelist.get_anime_detail(item['mal'],True,REDDITANIMELIST_DIR,True)
                # redditanimelist_res = None
            if item['livechart'] is not None:
                    # print('livechart start...')
                    # livechart_res = None
                    livechart_res = livechart.get_anime_detail(item['livechart'], True, LIVECHART_DIR,True)
            else:   
                    livechart_res = None  
            if item['ann'] is not None:
                    # print('anime_news_network start...')
                    ann_res = anime_news_network.get_anime_detail(item['ann'], True, ANN_DIR,True)
            else:
                    ann_res = None
            if item['bgm'] is not None:
                    # print('bangumi start...')
                    bgm_res = bangumi.get_anime_detail(item['bgm'], True, BGM_DIR,True)
            else:
                    bgm_res = None
            if item['anilist'] is not None:
                    # print('anilist start...')
                    anl_res = anilist.get_anime_detail(item['anilist'], True, ANL_DIR,True)
            else:
                    anl_res = None
            if item['anikore'] is not None:
                    # print('anikore start...')
                    akr_res = anikore.get_anime_detail(item['anikore'], True, AKR_DIR,True)
            else:
                    akr_res = None    
            if item['gamer'] is not None:
                    # print('gamer start...')
                    gamer_res = gamer.get_anime_detail(item['gamer'], True, GAMER_DIR,True)
            else:
                    gamer_res = None   
            if item['animePlanetCom'] is not None:
                    # print('animePlanetCom start...')
                    animePlanetCom_res = anime_planet.get_anime_detail(item['animePlanetCom'], True, ANIMEPLANECOM_DIR,True)
            else:
                    animePlanetCom_res = None           
            if item['anisearch'] is not None:
                    # print('anisearch start...')
                    anisearch_res = anisearch.get_anime_detail(item['anisearch'], True, ANISEARCH_DIR,True)
            else:
                    anisearch_res = None      
            if item['kitsu'] is not None:
                    # print('kitsu start...')
                    kitsu_res = kitsu.get_anime_detail(item['kitsu'], True, KITSU_DIR,True)
            else:
                    kitsu_res = None    
            
            if item['notifyMoe'] is not None:
                    # print('notifyMoe start...')
                    notifyMoe_res = notify_moe.get_anime_detail(item['notifyMoe'], True, NOTIFYMOE_DIR,True)
                    # notifyMoe_res = None
            else:
                    notifyMoe_res = None     
            if notifyMoe_res is not None and 'traktId' in notifyMoe_res and notifyMoe_res['traktId'] not in error_trakt:
                    # print('trakt start...')
                    # trakt_res = None
                    trakt_res = trakt.get_anime_detail(notifyMoe_res['traktId'], True, TRAKT_DIR,True)
                    # if trakt_res is None:
                        # traktErr.append(notifyMoe_res['traktId'])
                        # with open('traktErr.json', 'w', encoding='utf-8') as f:
                        #     json.dump(traktErr, f, indent=2, ensure_ascii=False)
            else:
                        trakt_res = None
            if item['sakuhindb'] is not None:
                    # print('sakuhindb start...')
                    sakuhindb_res = sakuhindb.get_anime_detail(item['sakuhindb'], True, SAKUHINDB_DIR,True)
            else:
                    sakuhindb_res = None    
            if 'annict' in item: #必要
                    if item['annict'] is not None:
                            # print('annict start...')
                            annict_res = annict.get_anime_detail(item['annict'], True, ANNICT_DIR,True)
                            # annict_res = None  
                    else:
                            annict_res = None    
            else:
                annict_res    = None
            if item['anidb'] is not None:
                    # anidb_res = None
                    # print('anidb start...')
                    anidb_res = anidb.get_anime_detail2(item['anidb'], True, ANIDB_DIR,True)
            else:
                    anidb_res = None    
                
                
            onl = {}
            if trakt_res is not None:
                # if trakt_res['online']:
                #     for uid, item in trakt_res['online'].items():
                #         onl[uid] = item  
                if  trakt_res['online']:
                    for oid, item in trakt_res['online'].items():
                        oName = None
                        if oid.find('Amazon') != -1:
                            oName = 'Amazon Prime Video'
                        elif oid.find('Ani-One Asia') != -1:
                            oName = '羚邦(Ani-One) YouTube'
                        elif oid.find('AnimeLog') != -1:
                            oName = 'AnimeLog Youtube'
                        elif oid.find('Bahamut') != -1:
                            oName = '動畫瘋'
                        elif oid.find('CHT MOD') != -1:
                            oName = '中華電信MOD'
                        elif oid.find('CatchPlay') != -1:
                            oName = 'CatchPlay+ TW'
                        elif oid.find('Disney') != -1:
                            oName = 'Disney+'
                        elif oid.find('GUNDAM.INFO') != -1:
                            oName = 'GUNDAM.INFO Youtube'
                        elif oid.find('Google Play') != -1:
                            oName = 'Google Play'
                        elif oid.find('HamiVideo') != -1:
                            oName = 'HamiVideo'
                        elif oid.find('KKTV') != -1:
                            oName = 'KKTV'
                        elif oid.find('LINE TV') != -1:
                            oName = 'LINE TV Taiwan'
                        elif oid.find('LiTV') != -1:
                            oName = 'LiTV立視'
                        elif oid.find('Muse TW') != -1:
                            oName = '木棉花(Muse) Youtube'
                        elif oid.find('Netflix') != -1:
                            oName = 'Netflix'
                        elif oid.find('Yahoo') != -1:
                            oName = 'Yahoo! TV Taiwan'
                        elif oid.find('bilibili') != -1:
                            oName = 'bilibili'
                        elif oid.find('哔哩') != -1:
                            oName = 'bilibili'
                        elif oid.find('friDay') != -1:
                            oName = 'friDay影音'
                        elif oid.find('hmvod') != -1:
                            oName = 'hmvod'
                        elif oid.find('iQIYI') != -1:
                            oName = '愛奇藝'
                        elif oid.find('iTunes') != -1:
                            oName = 'iTunes'
                        elif oid.find('myVideo') != -1:
                            oName = 'MyVideo'
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
    
        # for anidb
    print('anidb start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in all_data.items():
        ani = item['anidb']
        if ani is not None and ani['score'] is not None:
            ids.append(uid)
            ratings[0].append(ani['score'])
            ratings[1].append(ani['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['anidb']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['anidb']['bayesian_score'] = 0
        if ani is not None and ani['score'] is  None:
            all_data[uid]['anidb']['bayesian_score'] = 0
            
    # for bangumi
    print('bgm start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
        bgm = item['BGM']
        if bgm is not None and bgm['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(bgm['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if score is not None:
                    all_data[uid]['BGM']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['BGM']['bayesian_score'] = 0
        if bgm is not None and bgm['rating_detail'] is  None:
            all_data[uid]['BGM']['bayesian_score'] = 0
    # for anilist
    print('anilist start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
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
                    all_data[uid]['AniList']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['AniList']['bayesian_score'] = 0
        if anl is not None and anl['stats']['scoreDistribution'] is None:
            all_data[uid]['AniList']['bayesian_score'] = 0
    # for anikore
    print('Anikore start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in all_data.items():
        akr = item['Anikore']
        if akr is not None and akr['score'] is not None:
            ids.append(uid)
            ratings[0].append(akr['score'] * 2)
            ratings[1].append(akr['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if score is not None:
                    all_data[uid]['Anikore']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['Anikore']['bayesian_score'] = 0
        if akr is not None and akr['score'] is  None:
            all_data[uid]['Anikore']['bayesian_score'] = 0
        
    # for gamer
    print('Gamer start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
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
                    all_data[uid]['Gamer']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['Gamer']['bayesian_score'] = 0
        if gam is not None and gam['rating_detail'] is None:
            all_data[uid]['Gamer']['bayesian_score'] = 0
    
    # for annict
    print('annict start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
        anni = item['annict']
        if anni is not None and anni['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(anni['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['annict']['bayesian_score'] = round(score*2.5,2)
                else:
                    all_data[uid]['annict']['bayesian_score'] = 0
        if anni is not None and anni['rating_detail'] is None:
            all_data[uid]['annict']['bayesian_score'] = 0
            
    # for trakt
    print('trakt start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
        tr = item['trakt']
        if tr is not None and tr['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(tr['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['trakt']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['trakt']['bayesian_score'] = 0
        if tr is not None and tr['rating_detail'] is None:
            all_data[uid]['trakt']['bayesian_score'] = 0
            
    # for sakuhindb
    print('sakuhindb start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
        sakuhin = item['sakuhindb']
        if sakuhin is not None and sakuhin['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(sakuhin['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['sakuhindb']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['sakuhindb']['bayesian_score'] = 0
        if sakuhin is not None and sakuhin['rating_detail'] is None:
            all_data[uid]['sakuhindb']['bayesian_score'] = 0 
            
    # for redditanimelist
    print('redditanimelist start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
        reddit = item['redditanimelist']
        if reddit is not None and reddit['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(reddit['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['redditanimelist']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['redditanimelist']['bayesian_score'] = 0
        if reddit is not None and reddit['rating_detail'] is None:
            all_data[uid]['redditanimelist']['bayesian_score'] = 0 
            
    # for ap
    print('AnimePlanetCom start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in all_data.items():
        ap = item['AnimePlanetCom']
        if ap is not None and ap['score'] is not None:
            ids.append(uid)
            ratings[0].append(ap['score'] * 2)
            ratings[1].append(ap['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['AnimePlanetCom']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['AnimePlanetCom']['bayesian_score'] = 0
        if ap is not None and ap['score'] is None:
            all_data[uid]['AnimePlanetCom']['bayesian_score'] = 0
    # for anisearch
    print('anisearch start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
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
                    all_data[uid]['anisearch']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['anisearch']['bayesian_score'] = 0
        if anis is not None and anis['rating_detail'] is  None:
            all_data[uid]['anisearch']['bayesian_score'] = 0
    # for kitsu
    print('kitsu start bayesian')
    ids, ratings = [], []
    for uid, item in all_data.items():
        kit = item['kitsu']
        '''
        if kit is not None and kit['score'] is not None:
            ids.append(uid)
            ratings[0].append(kit['score'] / 10)
            ratings[1].append(kit['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
        '''
        if kit is not None and kit['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(kit['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
            scores = bayesian.calc_bayesian_score(ratings, 10)
            
            
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['kitsu']['bayesian_score'] = round(score/2,2)
                else:
                    all_data[uid]['kitsu']['bayesian_score'] = 0
        if kit is not None and kit['score'] is None:
            all_data[uid]['kitsu']['bayesian_score'] = 0
    # for notifyMoe
    print('notifyMoe start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in all_data.items():
        notifyMoe = item['notifyMoe']
        if notifyMoe is not None and notifyMoe['score'] is not None:
            ids.append(uid)
            ratings[0].append(notifyMoe['score'])
            ratings[1].append(notifyMoe['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['notifyMoe']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['notifyMoe']['bayesian_score'] = 0
        if notifyMoe is not None and notifyMoe['score'] is  None:
            all_data[uid]['notifyMoe']['bayesian_score'] = 0
            
    # for livechart
    print('livechart start bayesian')
    ids, ratings = [], [[], []]
    for uid, item in all_data.items():
        lc = item['livechart']
        if lc is not None and lc['score'] is not None:
            ids.append(uid)
            ratings[0].append(lc['score'])
            ratings[1].append(lc['votes'])
            scores = bayesian.calc_bayesian_score_by_average(ratings, 10)
            for uid, score in zip(ids, scores):
                if  score is not None:
                    all_data[uid]['livechart']['bayesian_score'] = round(score,2)
                else:
                    all_data[uid]['livechart']['bayesian_score'] = 0
        if lc is not None and lc['score'] is  None:
            all_data[uid]['livechart']['bayesian_score'] = 0

    
    # normalize and average
    print('normalize and average')
    all_data = adjust.adjust_scores(all_data)
    min_count = 4
    all_list = []
    
    for uid, item in all_data.items():
        count = 0
        score_sum = 0
        for site in item:
            site_data = item[site]
            #if site_data is not None and 'adjusted_score' in site_data:
            if site_data is not None and 'adjusted_score' in site_data:
                if site_data['adjusted_score'] is not None: 
                    score_sum += site_data['adjusted_score']
                    if site_data['adjusted_score'] > 0:
                        count += 1
        
        if count >= min_count or  item['MAL']['genres'] and count >= 2 and 'Hentai' in item['MAL']['genres']:
            score_org = score_sum / count
            item['score'] = round(score_org,2)
            all_list.append(item)
        else: 
            item['score'] = 0
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
    print('rank and save')
    all_list.sort(key=lambda x: x['score'], reverse=True)
    rankIndex = 0
    for i in all_list:
        rankIndex += 1
        i['rank']=rankIndex
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
    arg_parser.add_argument('--interval', type=int, default=86400,
        help='Update interval (seconds)')
    arg_parser.add_argument('--checkpoint', default='',
    # arg_parser.add_argument('--checkpoint', default='all.tmp.json',
        help='File path to checkpoint (all.tmp.json).')
    args = arg_parser.parse_args()

    def save_json(data):
        with open('all.save.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        with gzip.open('test2.gzip', 'wt', encoding="ascii") as zipfile:
            json.dump(data, zipfile)       

    always_update(args, save_json)
