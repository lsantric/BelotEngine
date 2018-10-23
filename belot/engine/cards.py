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


def print_card(cards):
    ludilo_karte = []
    for i in cards:
        num = i % 9
        boja_num = i // 9
        if boja_num == 0:
            boja = 'tref'
        elif boja_num == 1:
            boja = 'herc'
        elif boja_num == 2:
            boja = 'karo'
        else:
            boja = 'pik'

        ludilo_karte.append((symbolic_map[num], boja))

    return ludilo_karte
