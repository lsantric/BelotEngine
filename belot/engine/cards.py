import numpy as np

point_map = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 2,
    5: 3,
    6: 4,
    7: 10,
    8: 11
}

adut_point_map = {
    0: 0,
    1: 0,
    2: 0,
    3: 14,
    4: 20,
    5: 3,
    6: 4,
    7: 10,
    8: 11
}


def cid2p(card_types, card_suits, adut):
    """Sum points over card ids and suits"""
    return (sum([point_map[card] for i, card in enumerate(card_types) if card_suits[i] != adut]) +
            sum([adut_point_map[card] for i, card in enumerate(card_types) if card_suits[i] == adut]))


def cid2s(card_ids):
    """Card ids by suit"""
    ids = card_ids // 9
    ids[card_ids != 0] += 1
    return ids


def cid2t(card_ids):
    """Card ids by card type"""
    return card_ids % 9


def cid2r(card_ids, dominant_suit, adut):
    """Card ids by rank"""
    card_ranks = cid2t(card_ids)
    card_suits = cid2s(card_ids)
    card_types = cid2t(card_ids)
    card_ranks[card_suits == dominant_suit] += 10
    card_ranks[card_suits == adut] += 20
    card_ranks[np.logical_and(card_types == 3, card_suits == adut)] += 20
    card_ranks[np.logical_and(card_types == 4, card_suits == adut)] += 20
    return card_ranks
