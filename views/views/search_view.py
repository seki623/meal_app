# -*- coding: utf-8 -*-
"""
views/search_view.py
---------------------
🔍 検索モード（レシピの一覧・検索・編集・新規登録）の画面描画
"""

import re
import streamlit as st
import database as db

def render_search_page():
    st.title("🔍 検索モード：レシピの登録・検索・編集")

    tab_search, tab_add = st.tabs(["レシピ検索・編集", "レシピ新規登録"])

    # ---- タブ1：レシピ検索・編集 ----
    with tab_search:
        st.subheader("条件を指定して絞り込み")

        # 料理ジャンル・種別は st.pills でチップ風のタップ選択に変更
        # （st.selectbox の代わりに複数選択可能なチップとして提示する）
        cuisine_selected = st.pills(
            "料理ジャンル",
            db.CUISINE_CATEGORIES,
            selection_mode="multi",
            key="chip_cuisine",
        )
        meal_selected = st.pills(
            "種別（主菜/副菜など）",
            db.MEAL_TYPE_CATEGORIES,
            selection_mode="multi",
            key="chip_meal",
        )

        # 食材は「抽出チップ」＋「フリーワード」の併用
        st.markdown("**食材で絞り込み**")
        freeword = st.text_input(
            "食材名の一部を入力",
            placeholder="例：ねぎ",
            key="ingredient_freeword",
            label_visibility="collapsed",
        )
        all_tags = db.get_all_ingredient_tags()
        ingredient_chips = st.pills(
            "よく使う食材から選ぶ",
            all_tags,
            selection_mode="multi",
            key="chip_ingredients",
            label_visibility="collapsed",
        )

        # フリーワードとチップの両方を1つの検索条件リストにまとめる
        # （db.search_recipes の ingredient_query は部分一致のOR判定なので、
        #  そのまま両方の入力を合流させられる）
        ingredient_query = list(ingredient_chips) if ingredient_chips else []
        if freeword.strip():
            ingredient_query.append(freeword.strip())

        # st.pills は複数選択時にリストを返すため、既存の search_recipes が
        # 期待する単一カテゴリ文字列に変換する（未選択時は「すべて」扱い）
        # ジャンル・種別を複数選んだ場合はOR条件として複数回検索して結合する
        cuisine_options = cuisine_selected if cuisine_selected else ["すべて"]
        meal_options = meal_selected if meal_selected else ["すべて"]

        results_map = {}
        for c in cuisine_options:
            for m in meal_options:
                for r in db.search_recipes(
                    ingredient_query=ingredient_query if ingredient_query else None,
                    cuisine_category=c,
                    meal_category=m,
                ):
                    results_map[r["id"]] = r
        results = list(results_map.values())

        st.markdown(f"**{len(results)} 件のレシピが見つかりました**")
        for r in results:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3.5, 0.8, 0.8])
                with c1:
                    st.markdown(f"### {r['name']}")
                    st.caption(f"{r.get('cuisine_category', 'その他')} / {r.get('meal_category', 'その他')}")
                    
                    ing_list = r.get("ingredients", [])
                    if isinstance(ing_list, list):
                        st.write("材料：" + "、".join(ing_list))
                    else:
                        st.write("材料：" + str(ing_list))
                        
                    if r.get("notes"):
                        with st.expander("作り方・メモを見る"):
                            st.write(r["notes"])
                with c2:
                    if st.button("✏️ 編集", key=f"edit_recipe_{r['id']}"):
                        st.session_state.editing_recipe_id = r['id']
                        st.rerun()
                with c3:
                    if st.button("削除", key=f"del_recipe_{r['id']}"):
                        db.delete_recipe(r["id"])
                        st.rerun()

                # 編集フォーム
                if st.session_state.editing_recipe_id == r['id']:
                    st.markdown("---")
                    st.subheader(f"✏️ 「{r['name']}」の編集")
                    
                    existing_ings = "、".join(r.get("ingredients", [])) if isinstance(r.get("ingredients"), list) else ""
                    
                    with st.form(f"edit_form_{r['id']}"):
                        edit_name = st.text_input("レシピ名 *", value=r.get("name", ""))
                        edit_ings = st.text_input("材料（読点やカンマ区切り）", value=existing_ings)
                        
                        cuisine_idx = db.CUISINE_CATEGORIES.index(r["cuisine_category"]) if r.get("cuisine_category") in db.CUISINE_CATEGORIES else 0
                        meal_idx = db.MEAL_TYPE_CATEGORIES.index(r["meal_category"]) if r.get("meal_category") in db.MEAL_TYPE_CATEGORIES else 0
                        
                        edit_cuisine = st.selectbox("料理ジャンル", db.CUISINE_CATEGORIES, index=cuisine_idx)
                        edit_meal = st.selectbox("種別", db.MEAL_TYPE_CATEGORIES, index=meal_idx)
                        edit_notes = st.text_area("作り方・メモ", value=r.get("notes", ""))

                        c_save, c_cancel = st.columns([1, 1])
                        with c_save:
                            save_submitted = st.form_submit_button("更新を保存", type="primary")
                        with c_cancel:
                            cancel_submitted = st.form_submit_button("キャンセル")

                        if save_submitted:
                            if not edit_name.strip():
                                st.error("レシピ名は必須です。")
                            else:
                                ing_list = [i.strip() for i in re.split(r'[,，、\s]+', edit_ings) if i.strip()]
                                db.update_recipe(
                                    recipe_id=r['id'],
                                    name=edit_name.strip(),
                                    ingredients=ing_list,
                                    cuisine_category=edit_cuisine,
                                    meal_category=edit_meal,
                                    notes=edit_notes.strip()
                                )
                                st.session_state.editing_recipe_id = None
                                st.success("レシピを更新しました！")
                                st.rerun()
                        elif cancel_submitted:
                            st.session_state.editing_recipe_id = None
                            st.rerun()

    # ---- タブ2：レシピ新規登録 ----
    with tab_add:
        st.subheader("新しいレシピを登録")
        
        with st.form("add_recipe_form", clear_on_submit=True):
            input_name = st.text_input("レシピ名 *")
            input_ingredients = st.text_input("材料（読点やカンマで入力。例: 豚肉、キャベツ、味噌）")
            input_cuisine = st.selectbox("料理ジャンル", db.CUISINE_CATEGORIES, index=0)
            input_meal = st.selectbox("種別（主菜・副菜など）", db.MEAL_TYPE_CATEGORIES, index=0)
            input_notes = st.text_area("作り方・メモ")

            submitted = st.form_submit_button("登録する", type="primary")
            if submitted:
                if not input_name.strip():
                    st.error("レシピ名は必須です。")
                else:
                    ing_list = [i.strip() for i in re.split(r'[,，、\s]+', input_ingredients) if i.strip()]
                    db.add_recipe(
                        name=input_name.strip(),
                        ingredients=ing_list,
                        cuisine_category=input_cuisine,
                        meal_category=input_meal,
                        notes=input_notes.strip()
                    )
                    st.success(f"「{input_name}」を登録しました！")
                    st.rerun()