# -*- coding: utf-8 -*-
"""
seed_data.py
------------
動作確認用のサンプルレシピを投入するスクリプト。
初回起動時にレシピが0件だと検索・決定モードを試しにくいため用意している。

実行方法:
    python seed_data.py
"""

import database as db

SAMPLE_RECIPES = [
    {
        "name": "肉じゃが",
        "ingredients": ["じゃがいも", "玉ねぎ", "豚肉", "人参"],
        "cuisine_category": "和食",
        "meal_category": "主菜",
        "notes": "じゃがいもと玉ねぎ、豚肉を炒めてから、だし・醤油・みりんで煮込む。",
    },
    {
        "name": "麻婆豆腐",
        "ingredients": ["豆腐", "豚ひき肉", "豆板醤", "長ねぎ"],
        "cuisine_category": "中華",
        "meal_category": "主菜",
        "notes": "ひき肉を炒めて豆板醤で香りを出し、豆腐と調味料を加えて煮込む。",
    },
    {
        "name": "ナポリタン",
        "ingredients": ["パスタ", "ソーセージ", "ピーマン", "玉ねぎ", "ケチャップ"],
        "cuisine_category": "洋食",
        "meal_category": "主食",
        "notes": "具材を炒めた後、茹でたパスタとケチャップを絡める。",
    },
    {
        "name": "味噌汁",
        "ingredients": ["豆腐", "わかめ", "味噌", "だし"],
        "cuisine_category": "和食",
        "meal_category": "副菜",
        "notes": "だしを取り、具材を入れて煮たあと味噌を溶く。",
    },
    {
        "name": "野菜炒め",
        "ingredients": ["キャベツ", "人参", "ピーマン", "もやし"],
        "cuisine_category": "中華",
        "meal_category": "副菜",
        "notes": "強火で手早く炒め、塩コショウと少量の醤油で味を整える。",
    },
    {
        "name": "白ご飯",
        "ingredients": ["米"],
        "cuisine_category": "和食",
        "meal_category": "主食",
        "notes": "普通に炊飯器で炊く。",
    },
    {
        "name": "ハンバーグ",
        "ingredients": ["合いびき肉", "玉ねぎ", "パン粉", "卵"],
        "cuisine_category": "洋食",
        "meal_category": "主菜",
        "notes": "材料を混ぜて成形し、両面を焼いてからソースを煮絡める。",
    },
    {
        "name": "サラダ",
        "ingredients": ["レタス", "トマト", "きゅうり"],
        "cuisine_category": "その他",
        "meal_category": "副菜",
        "notes": "野菜を切って盛り付け、好みのドレッシングをかける。",
    },
]


def main():
    db.init_db()
    existing = db.get_all_recipes()
    if existing:
        print(f"既に {len(existing)} 件のレシピが登録されています。サンプル投入をスキップします。")
        return

    for recipe in SAMPLE_RECIPES:
        db.add_recipe(
            recipe["name"],
            recipe["ingredients"],
            recipe["cuisine_category"],
            recipe["meal_category"],
            recipe["notes"],
        )
    print(f"{len(SAMPLE_RECIPES)} 件のサンプルレシピを登録しました。")


if __name__ == "__main__":
    main()
