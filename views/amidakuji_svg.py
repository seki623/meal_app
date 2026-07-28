# -*- coding: utf-8 -*-
"""
amidakuji_svg.py
----------------
あみだくじの構造をSVGとして描画するためのモジュール。
Streamlitのst.markdown(unsafe_allow_html=True)でそのまま表示できる形式を返す。
"""


def render_amidakuji_svg(amidakuji, labels, highlight_path=None):
    """
    あみだくじをSVGで描画する。

    Parameters
    ----------
    amidakuji : dict
        build_amidakuji() で生成した構造
    labels : list[str]
        各縦線の下部に表示するラベル（＝割り当てられたレシピ名など）
    highlight_path : list[tuple] or None
        (row, x座標) のリストで、選ばれた経路をハイライト表示する場合に指定
    """
    num_players = amidakuji["num_players"]
    num_rungs = amidakuji["num_rungs"]

    col_width = 80
    row_height = 30
    top_margin = 40
    bottom_margin = 60
    width = col_width * num_players + 40
    height = top_margin + row_height * num_rungs + bottom_margin

    lines_svg = []
    # 縦線を描画
    for i in range(num_players):
        x = 20 + i * col_width + col_width // 2
        lines_svg.append(
            f'<line x1="{x}" y1="{top_margin}" x2="{x}" y2="{top_margin + row_height * num_rungs}" '
            f'stroke="#888" stroke-width="3" />'
        )
        # 上部にプレイヤー番号
        lines_svg.append(
            f'<text x="{x}" y="{top_margin - 15}" text-anchor="middle" font-size="14" fill="#333">'
            f'{i + 1}</text>'
        )
        # 下部にラベル（レシピ名）
        label = labels[i] if i < len(labels) else ""
        lines_svg.append(
            f'<text x="{x}" y="{top_margin + row_height * num_rungs + 25}" text-anchor="middle" '
            f'font-size="13" fill="#e05" font-weight="bold">{label}</text>'
        )

    # 横線を描画
    for row, left in amidakuji["rungs"]:
        x1 = 20 + left * col_width + col_width // 2
        x2 = 20 + (left + 1) * col_width + col_width // 2
        y = top_margin + row * row_height + row_height // 2
        lines_svg.append(
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#4a90d9" stroke-width="3" />'
        )

    svg = f"""
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{width}" height="{height}" fill="white" />
        {''.join(lines_svg)}
    </svg>
    """
    return svg
