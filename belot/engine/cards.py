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
    return card_ids // 9


def cid2t(card_ids):
    """Card ids by card type"""
    return card_ids % 9


def cid2r(card_ids, dominant_color, adut):
    """Card ids by rank"""
    card_ranks = card_ids.copy()
    card_suits = cid2s(card_ranks)
    card_ranks[card_suits == dominant_color] += 10
    card_ranks[card_suits == adut] += 20
    card_ranks[card_ranks == 2] += 20
    card_ranks[card_ranks == 3] += 20
    return card_ranks
