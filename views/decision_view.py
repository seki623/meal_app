# -*- coding: utf-8 -*-
"""
views/decision_view.py
-----------------------
🎯 決定モード（タロットカード＆ガチャガチャ）の画面描画
"""

import datetime
import random
import time
import streamlit as st
import database as db

def render_decision_page():
    st.title("🎯 決定モード：今日の献立を決めよう")

    st.markdown("条件を絞り込んでから、タロットカードかガチャガチャで楽しく決定しますの🌸")

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
    # 🌸 タブ1：タロットカード選択
    # ==================================================================
    with tab_tarot:
        st.markdown("裏返しのカードから直感で1枚選んでみてくださいませ✨")

        # カード枚数設定（最大6枚）
        num_cards = min(6, len(candidates))
        
        # シャッフルボタン または 初期化
        if "tarot_shuffled" not in st.session_state or st.button("🂠 カードをシャッフルする", key="shuffle_tarot"):
            st.session_state.tarot_deck = random.sample(candidates, num_cards)
            st.session_state.tarot_selected_idx = None
            st.session_state.tarot_shuffled = True

        st.markdown("---")
        
        # カードを並べて表示
        cols = st.columns(num_cards)
        card_back_emoji = ["🎴", "🃏", "🂠", "✨", "🔮", "🌙"]

        for idx, col in enumerate(cols):
            with col:
                emoji = card_back_emoji[idx % len(card_back_emoji)]
                st.markdown(f"### {emoji}")
                st.caption(f"Card {idx + 1}")
                if st.button(f"めくる", key=f"tarot_btn_{idx}"):
                    st.session_state.tarot_selected_idx = idx

        # カード選択後の結果表示
        if st.session_state.get("tarot_selected_idx") is not None:
            selected_idx = st.session_state.tarot_selected_idx
            chosen_recipe = st.session_state.tarot_deck[selected_idx]

            st.markdown("---")
            st.balloons()
            st.success(f"🔮 運命の1枚： Card {selected_idx + 1} は 「**{chosen_recipe['name']}**」 でしたわ！")
            st.caption(f"{chosen_recipe.get('cuisine_category', '')} / {chosen_recipe.get('meal_category', '')}")
            
            if chosen_recipe.get("ingredients"):
                st.write("材料：" + "、".join(chosen_recipe["ingredients"]))
            if chosen_recipe.get("notes"):
                with st.expander("作り方・メモを見る"):
                    st.write(chosen_recipe["notes"])

            # 記録モードへの保存
            meal_time_for_log = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="tarot_log_time")
            if st.button("この結果を今日の記録に追加する", key="save_tarot_log"):
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.add_meal_log(today_str, meal_time_for_log, chosen_recipe["id"], "")
                st.success("記録モードに保存しましたわ！")

    # ==================================================================
    # 🌸 タブ2：ガチャガチャ
    # ==================================================================
    with tab_gacha:
        st.markdown("ハンドルを回して、カプセルをポンっと取り出しましょう✨")

        if st.button("🎰 ガチャを回す！（100pt）", key="turn_gacha", type="primary"):
            # 🌸 ガチャポンアニメーション演出
            placeholder = st.empty()
            capsule_emojis = ["🔴", "🔵", "🟡", "🟢", "🟣", "⚪"]
            
            for i in range(8):
                cap = random.choice(capsule_emojis)
                placeholder.markdown(f"### 🌀 ガチャガチャ... ガラガラ... {cap}")
                time.sleep(0.12)

            # ガチャ結果の決定
            final_recipe = random.choice(candidates)
            final_capsule = random.choice(capsule_emojis)
            
            placeholder.markdown(f"### 🫳 ポンッ！ {final_capsule} カプセルが出てきましたの！")
            time.sleep(0.4)
            
            st.session_state.gacha_result = final_recipe
            st.session_state.gacha_capsule = final_capsule
            placeholder.empty()

        if st.session_state.get("gacha_result"):
            r = st.session_state.gacha_result
            cap = st.session_state.get("gacha_capsule", "🔮")
            
            st.snow()
            st.success(f"🎉 {cap} カプセルの中から「**{r['name']}**」が出てきましたわ！")
            st.caption(f"{r.get('cuisine_category', '')} / {r.get('meal_category', '')}")
            
            if r.get("ingredients"):
                st.write("材料：" + "、".join(r["ingredients"]))
            if r.get("notes"):
                with st.expander("作り方・メモを見る"):
                    st.write(r["notes"])

            # 記録モードへの保存
            meal_time_for_log2 = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="gacha_log_time")
            if st.button("この結果を今日の記録に追加する", key="save_gacha_log"):
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.add_meal_log(today_str, meal_time_for_log2, r["id"], "")
                st.success("記録モードに保存しましたわ！")