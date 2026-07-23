# -*- coding: utf-8 -*-
"""
recommend.py
------------
献立の「ルーレット」「あみだくじ」抽選ロジックをまとめたモジュール。

【設計方針】
- ロジック（抽選アルゴリズム）と描画（Streamlit UI）を分離する。
- ここでは純粋な Python 関数として実装し、streamlit に依存しない。
- app.py 側で結果を可視化する（SVGアニメーション風の表示など）。
"""

import random


def pick_roulette(recipes):
    """
    ルーレット抽選：候補レシピの中からランダムに1つを選ぶ。
    重み付け（例えば最近食べていないものを優先する）は将来拡張として
    weight を追加できるようにシンプルな一様分布にしている。
    """
    if not recipes:
        return None
    return random.choice(recipes)


def build_amidakuji(num_players, num_rungs=None):
    """
    あみだくじ（ghost leg lottery）の構造を生成する。

    【あみだくじの仕組み】
    - num_players 本の縦線を用意する。
    - 隣り合う縦線の間に「横線（rung）」をランダムに配置する。
    - 横線がある箇所を通過するとき、経路は隣の縦線に移動する。
    - 上から下まで辿ることで、各開始位置がどの結果にたどり着くかが決まる。

    戻り値:
        rungs: List[(row_index, left_line_index)] の形式で、
               どの段のどの位置に横線があるかを表す。
    """
    if num_rungs is None:
        # 縦線の本数に応じて適度な段数を自動設定
        num_rungs = max(num_players * 3, 6)

    rungs = []
    for row in range(num_rungs):
        # 各行で、隣接ペアのうちランダムに1つ（重ならないように）横線を引く
        # シンプルにするため「同じ行に複数の横線を許すが隣接ペアは重複させない」方式
        used_left_indices = set()
        # ランダムに0〜2本程度の横線を配置
        possible_positions = list(range(num_players - 1))
        random.shuffle(possible_positions)
        num_lines_this_row = random.choice([0, 1, 1, 2])  # 横線が引かれすぎないよう調整
        for pos in possible_positions[:num_lines_this_row]:
            # 隣接する横線同士が競合しないようにチェック
            if pos - 1 in used_left_indices or pos + 1 in used_left_indices or pos in used_left_indices:
                continue
            used_left_indices.add(pos)
            rungs.append((row, pos))

    return {"num_players": num_players, "num_rungs": num_rungs, "rungs": rungs}


def trace_amidakuji(amidakuji, start_index):
    """
    指定した開始位置（縦線のインデックス）から、あみだくじを辿って
    最終的にどの縦線（＝結果）にたどり着くかを計算する。

    戻り値: 最終的な縦線インデックス（0始まり）
    """
    current = start_index
    rungs_by_row = {}
    for row, left in amidakuji["rungs"]:
        rungs_by_row.setdefault(row, []).append(left)

    for row in range(amidakuji["num_rungs"]):
        lefts_in_row = rungs_by_row.get(row, [])
        # 現在位置の左側に横線があれば左へ移動、右側にあれば右へ移動
        if current in lefts_in_row:
            current += 1
        elif (current - 1) in lefts_in_row:
            current -= 1
    return current


def assign_amidakuji_results(amidakuji, recipes):
    """
    あみだくじの各縦線（プレイヤー）に、候補レシピからランダムに割り当てた
    結果を対応付け、開始位置ごとの最終結果をまとめて返す。

    戻り値: {start_index: recipe_dict} の辞書
    """
    num_players = amidakuji["num_players"]
    # 候補が足りない場合は重複を許して埋める
    if len(recipes) >= num_players:
        chosen = random.sample(recipes, num_players)
    else:
        chosen = [random.choice(recipes) for _ in range(num_players)]

    result_map = {}
    for start in range(num_players):
        end_index = trace_amidakuji(amidakuji, start)
        result_map[start] = chosen[end_index]
    return result_map
