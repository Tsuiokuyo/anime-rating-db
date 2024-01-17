import numpy as np


def norm(scores, mean=0, std=1):
    """
    Normalize the scores, let mean and std are as given.

    @param scores: list/np.array, all scores.
    @return: np.array, normalized scores.
    """
    #mean 總平均
    #std 總標準
    
    _mean = np.mean(scores) #單平均
    _std = np.std(scores) #單標準
    #將計算混合在一起的所有分數的總體 μ（平均值）和總體 σ（標準差）。 然後，對於某個網站 i，將計算其自身的 μi 和 σi。 最後，來自網站 i 的分數將通過以下方式標準化：
    # (單標準 /總標準) * (分數 -單平均) +總平均
    # print(_mean, _std)
    #_scores = (scores - _mean) / _std * std + mean
    _scores = (_std / std) * (scores - _mean) + mean
    return _scores


def adjust_scores(all_data):
    """
    Adjust scores from different sites.

    @param all_data: dict, as defined in ../pre_process.py.
    @return: dict, with "adjusted_score" in each item.
    """

    min_votes = 10

    mapping = {
        'ANN': 'b_score',
        'MAL': 'score',
        'BGM': 'b_score',
        'AniList': 'b_score',
        'Anikore': 'b_score',
        'Gamer' : 'b_score',
        'AnimePlanetCom' : 'b_score',
        'anisearch': 'b_score',
        'kitsu': 'b_score',
        'notifyMoe' : 'b_score',
        'trakt': 'b_score',
        'livechart': 'b_score',
        'redditanimelist':'b_score',
        'anidb':'b_score',
    }

    all_scores = {
        'ANN': ([], []),
        'MAL': ([], []),
        'BGM': ([], []),
        'AniList': ([], []),
        'Anikore': ([], []),
        'Gamer': ([], []),
        'AnimePlanetCom': ([], []),
        'anisearch': ([], []),
        'kitsu': ([], []),
        'notifyMoe': ([], []),
        'trakt':([],[]),
        'livechart':([],[]),
        'redditanimelist':([],[]),
        'anidb':([],[]),
    }
    
    for uid, item in all_data.items():
        for site, attr in mapping.items():
            if site in item and item[site] is not None:
                if attr in item[site] and item[site][attr] is not None:
                    score = item[site][attr]
                    if item[site]['votes'] is not None and int(item[site]['votes']) >= min_votes:
                        all_scores[site][0].append(float(score))
                        all_scores[site][1].append(uid)

    overall_scores = []
    for site, data in all_scores.items():
        scores, uids = data
        overall_scores.extend(scores)

    overall_mean = np.mean(overall_scores)
    overall_std = np.std(overall_scores)
    # print(overall_mean, overall_std)
    
    for site, data in all_scores.items():
        scores, uids = data
        if len(scores) > 0:
            adj_scores = norm(scores, overall_mean, overall_std)
            for adj_score, uid in zip(adj_scores, uids):
                if adj_score > 10:
                    adj_score = 10.0
                all_data[uid][site]['adj_score'] = round(adj_score,2)
    return all_data


if __name__ == '__main__':
    """
    Just for testing.
    """

    # import json
    # with open('../all.json', 'r', encoding='utf-8') as f:
    #     all_data = json.load(f)
    # all_data = adjust_scores(all_data)
    # with open('../all.adjusted.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_data, f, indent=2, ensure_ascii=False)
