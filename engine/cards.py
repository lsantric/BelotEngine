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

symbolic_map = {
    0: None,
    1: 7,
    2: 8,
    3: 9,
    4: "dečko",
    5: "dama",
    6: "kralj",
    7: 10,
    8: "AŠ"
}


def cards_to_points(cards, card_colors, adut):
    print(cards, card_colors, adut)
    return (sum([point_map[card] for i, card in enumerate(cards) if card_colors[i] != adut]) +
            sum([adut_point_map[card] for i, card in enumerate(cards) if card_colors[i] == adut]))


def cards_breakdwon(cards):
    pass


def printCard(cards):
    ludiloKarte = []
    for i in cards:
        num = i % 9
        bojaNum = i // 9
        if bojaNum == 0:
            boja = 'tref'
        elif bojaNum == 1:
            boja = 'herc'
        elif bojaNum == 2:
            boja = 'karo'
        else:
            boja = 'pik'

        ludiloKarte.append((symbolic_map[num], boja))

    return ludiloKarte
