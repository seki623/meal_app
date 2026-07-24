# -*- coding: utf-8 -*-
"""
views/decision_view.py
-----------------------
🎯 決定モード（流れ星＆金色のふわふわ光アニメーション適用版）
"""

import datetime
import random
import time
import os
import streamlit as st
import database as db

# 画像ファイルのパス
TAROT_BACK_IMAGE = "static/tarot_back.jpg"


def render_decision_page():
    # ==================================================================
    # 🌸 流れ星＆金色のふわふわアニメーションCSS
    # ==================================================================
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@700&display=swap');

        :root {
            --navy: #030d22;
            --navy-2: #081231;
            --navy-3: #0d1c42;
            --gold: #c9a94f;
            --gold-2: #e0c47a;
            --ivory: #e8d9a8;
            --danger: #d97a7a;
        }

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html, body, .stApp {
            color: var(--ivory) !important;
            font-family: 'Noto Sans JP', sans-serif !important;
            background: linear-gradient(180deg, var(--navy) 0%, var(--navy-2) 100%) !important;
            overflow-x: hidden;
        }

        /* ------------------------------------
           🌠 背景の流れ星アニメーション
        ------------------------------------ */
        .shooting-stars-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }

        .star {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 4px;
            height: 4px;
            background: #fff;
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1), 0 0 0 8px rgba(255, 255, 255, 0.1), 0 0 20px rgba(255, 255, 255, 1);
            animation: animate 3s linear infinite;
        }
        .star::before {
            content: '';
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 300px;
            height: 1px;
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), transparent);
        }

        @keyframes animate {
            0% {
                transform: rotate(315deg) translateX(0);
                opacity: 1;
            }
            70% {
                opacity: 1;
            }
            100% {
                transform: rotate(315deg) translateX(-1000px);
                opacity: 0;
            }
        }

        .star:nth-child(1) { top: 0px; right: 0px; animation-delay: 0s; animation-duration: 2.5s; }
        .star:nth-child(2) { top: 100px; right: 200px; animation-delay: 1.2s; animation-duration: 3s; }
        .star:nth-child(3) { top: 300px; right: 100px; animation-delay: 2.4s; animation-duration: 2.2s; }
        .star:nth-child(4) { top: 200px; right: 400px; animation-delay: 0.8s; animation-duration: 3.5s; }

        /* ------------------------------------
           ✨ 金色のふわふわ光アニメーション
        ------------------------------------ */
        @keyframes goldGlow {
            0% {
                box-shadow: 0 0 15px rgba(201, 169, 79, 0.3), inset 0 0 10px rgba(224, 196, 122, 0.2);
                border-color: var(--gold);
            }
            50% {
                box-shadow: 0 0 28px rgba(224, 196, 122, 0.65), inset 0 0 18px rgba(201, 169, 79, 0.4);
                border-color: var(--gold-2);
            }
            100% {
                box-shadow: 0 0 15px rgba(201, 169, 79, 0.3), inset 0 0 10px rgba(224, 196, 122, 0.2);
                border-color: var(--gold);
            }
        }

        @keyframes goldPulseBtn {
            0% {
                box-shadow: 0 10px 25px rgba(201, 169, 79, 0.35);
            }
            50% {
                box-shadow: 0 12px 35px rgba(224, 196, 122, 0.65);
            }
            100% {
                box-shadow: 0 10px 25px rgba(201, 169, 79, 0.35);
            }
        }

        .brand {
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .sub-caption {
            margin-top: 8px;
            font-size: 13px;
            color: var(--ivory);
            opacity: 0.85;
            letter-spacing: .05em;
        }

        /* Streamlitボタンにふわふわ光を適用 */
        .stButton > button {
            width: 100% !important;
            margin-top: 12px !important;
            padding: 14px 20px !important;
            border-radius: 14px !important;
            font-size: 16px !important;
            background: linear-gradient(135deg, var(--gold-2), var(--gold)) !important;
            color: #1c1408 !important;
            border: none !important;
            font-family: 'Shippori Mincho', serif !important;
            font-weight: 700 !important;
            letter-spacing: .08em !important;
            transition: .2s ease !important;
            animation: goldPulseBtn 3s infinite ease-in-out !important;
        }
        .stButton > button:active {
            transform: scale(0.98) !important;
        }

        /* 3Dカードスタイル（ふわふわ揺らめく金枠） */
        .card-container {
            perspective: 1000px;
            width: 100%;
            height: 200px;
            margin-bottom: 10px;
            cursor: pointer;
            position: relative;
            z-index: 1;
        }
        .card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            transform-style: preserve-3d;
            border-radius: 14px;
        }
        .card-flipped {
            transform: rotateY(180deg);
        }
        .card-front, .card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            border-radius: 14px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px;
            box-sizing: border-box;
            animation: goldGlow 3s infinite ease-in-out;
        }
        .card-front {
            border: 2px solid var(--gold);
        }
        .card-back {
            background: linear-gradient(145deg, var(--navy-3), var(--navy-2));
            color: var(--ivory);
            transform: rotateY(180deg);
            border: 2px solid var(--gold);
            font-family: 'Shippori Mincho', serif;
            font-weight: 700;
            font-size: 15px;
            text-shadow: 0 0 6px rgba(201, 169, 79, 0.5);
        }
    </style>

    <!-- 背景の流れ星要素 -->
    <div class="shooting-stars-container">
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
    </div>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # メインコンテンツ
    # ------------------------------------------------------------------
    st.markdown('<div class="brand"><h1 style="font-family: \'Shippori Mincho\', serif; color: var(--gold-2); text-shadow: 0 0 12px rgba(224, 196, 122, 0.5);">🎯 決定モード</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand sub-caption">条件を絞り込んでから、神秘的なカードかガチャで献立を決定しますの🌸</div>', unsafe_allow_html=True)

    st.write("")

    # ---- 条件絞り込み ----
    col1, col2, col3 = st.columns(3)
    with col1:
        cuisine_filter = st.selectbox("料理ジャンル", ["すべて"] + db.CUISINE_CATEGORIES, key="dec_cuisine")
    with col2:
        meal_filter = st.selectbox("種別", ["すべて"] + db.MEAL_TYPE_CATEGORIES, key="dec_meal")
    with col3:
        all_tags = db.get_all_ingredient_tags()
        ingredient_filter = st.multiselect("含まれる材料で絞り込み", all_tags, key="dec_ingredients")

    candidates = db.search_recipes(
        ingredient_query=ingredient_filter if ingredient_filter else None,
        cuisine_category=cuisine_filter,
        meal_category=meal_filter,
    )
    st.info(f"現在の候補：{len(candidates)} 件")

    if not candidates:
        st.warning("条件に合うレシピがありません。検索モードでレシピを登録するか、条件を緩めてくださいませ。")
        return

    with st.expander("候補レシピの一覧を見る"):
        for c in candidates:
            st.write(f"- {c['name']}（{c.get('cuisine_category', '')} / {c.get('meal_category', '')}）")

    tab_tarot, tab_gacha = st.tabs(["🔮 タロットカード", "🎰 ガチャガチャ"])

    # ==================================================================
    # 🌸 タブ1：タロットカード
    # ==================================================================
    with tab_tarot:
        st.markdown('<div class="sub-caption" style="text-align: center;">カードをタップしてめくってくださいませ✨</div>', unsafe_allow_html=True)
        st.write("")

        num_cards = min(4, len(candidates))

        # 初期化・シャッフル
        if "tarot_deck" not in st.session_state or len(st.session_state.get("tarot_deck", [])) != num_cards or st.button("🂠 カードをシャッフルする", key="shuffle_tarot"):
            st.session_state.tarot_deck = random.sample(candidates, num_cards)
            st.session_state.tarot_selected_idx = None

        st.markdown("---")

        actual_deck_size = len(st.session_state.tarot_deck)
        cols = st.columns(actual_deck_size)

        has_image = os.path.exists(TAROT_BACK_IMAGE)
        bg_style = f"background-image: url('{TAROT_BACK_IMAGE}'); background-size: cover; background-position: center;" if has_image else "background: linear-gradient(135deg, var(--navy-3), var(--navy-2));"

        for idx in range(actual_deck_size):
            with cols[idx]:
                is_selected = (st.session_state.get("tarot_selected_idx") == idx)
                recipe = st.session_state.tarot_deck[idx]

                card_container = st.container()
                with card_container:
                    card_html = f"""
                    <div class="card-container">
                        <div class="card-inner {'card-flipped' if is_selected else ''}">
                            <div class="card-front" style="{bg_style}">
                                {'<div style="color:var(--gold-2); font-size:28px; filter: drop-shadow(0 0 6px rgba(224,196,122,0.8));">🔮</div>' if not has_image else ''}
                            </div>
                            <div class="card-back">
                                <div style="font-size: 10px; color: var(--gold-2); margin-bottom: 6px; letter-spacing: .05em;">✨ 今日の献立 ✨</div>
                                <div>{recipe['name']}</div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button(f"カード{idx+1}を選択", key=f"tarot_btn_{idx}", use_container_width=True):
                        st.session_state.tarot_selected_idx = idx
                        st.rerun()

        # 結果表示
        if st.session_state.get("tarot_selected_idx") is not None and st.session_state.tarot_selected_idx < actual_deck_size:
            selected_idx = st.session_state.tarot_selected_idx
            chosen_recipe = st.session_state.tarot_deck[selected_idx]

            st.markdown("---")
            st.success(f"🔮 運命のカードは 「**{chosen_recipe['name']}**」 でしたわ！")
            st.caption(f"{chosen_recipe.get('cuisine_category', '')} / {chosen_recipe.get('meal_category', '')}")

            if chosen_recipe.get("ingredients"):
                st.write("材料：" + "、".join(chosen_recipe["ingredients"]))
            if chosen_recipe.get("notes"):
                with st.expander("作り方・メモを見る"):
                    st.write(chosen_recipe["notes"])

            meal_time_for_log = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="tarot_log_time")
            if st.button("この結果を今日の記録に追加する", key="save_tarot_log"):
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.add_meal_log(today_str, meal_time_for_log, chosen_recipe["id"], "")
                st.success("記録モードに保存いたしましたわ！")

    # ==================================================================
    # 🌸 タブ2：ガチャガチャ
    # ==================================================================
    with tab_gacha:
        st.markdown('<div class="sub-caption" style="text-align: center;">ハンドルを回して、今日の献立カプセルを取り出しましょう✨</div>', unsafe_allow_html=True)
        st.write("")

        if st.button("🎰 ガチャを回す", key="turn_gacha", type="primary", use_container_width=True):
            placeholder = st.empty()

            for i in range(3, 0, -1):
                placeholder.markdown(f"<h3 style='text-align:center; color:var(--gold-2); font-family: \"Shippori Mincho\", serif; text-shadow: 0 0 10px rgba(224,196,122,0.6);'>🌀 ガチャガチャ回転中... {i}</h3>", unsafe_allow_html=True)
                time.sleep(0.5)

            final_recipe = random.choice(candidates)
            st.session_state.gacha_result = final_recipe
            placeholder.empty()

        if st.session_state.get("gacha_result"):
            r = st.session_state.gacha_result

            st.markdown("---")
            st.success(f"🎉 カプセルの中から「**{r['name']}**」が出てまいりましたわ！")
            st.caption(f"{r.get('cuisine_category', '')} / {r.get('meal_category', '')}")

            if r.get("ingredients"):
                st.write("材料：" + "、".join(r["ingredients"]))
            if r.get("notes"):
                with st.expander("作り方・メモを見る"):
                    st.write(r["notes"])

            meal_time_for_log2 = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="gacha_log_time")
            if st.button("この結果を今日の記録に追加する", key="save_gacha_log"):
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.add_meal_log(today_str, meal_time_for_log2, r["id"], "")
                st.success("記録モードに保存いたしましたわ！")