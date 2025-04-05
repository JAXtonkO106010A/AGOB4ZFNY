# admin_utils.py
import streamlit as st
from db_utils import conn, get_cursor
from auth_utils import hash_password, login_form, register_form
import sqlite3

def generate_api_key(username, key, total_tokens):
    try:
        with get_cursor() as c: 
            c.execute('INSERT INTO api_keys (key, username, total_tokens) VALUES (?, ?, ?)',
                    (key, username, total_tokens))
            return key
    except sqlite3.IntegrityError:
        st.error("API密钥已存在")
        return None

def update_admin_status(user_id, is_admin):
    with get_cursor() as c: 
        c.execute('UPDATE users SET is_admin = ? WHERE id = ?', (int(is_admin), user_id))

def delete_user(user_id):
    with get_cursor() as c: 
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        c.execute('DELETE FROM api_keys WHERE username = (SELECT username FROM users WHERE id = ?)', (user_id,))

def setup_admin(admin_user, admin_pass, key):
    with get_cursor() as c: 
        c.execute('SELECT 1 FROM users WHERE username = ?', (admin_user,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, 1)
                ON CONFLICT(username) 
                DO UPDATE SET
                    password_hash = excluded.password_hash,
                    is_admin = excluded.is_admin
            ''', (admin_user, admin_pass))
            c.execute('''
                INSERT INTO api_configurations (config_name, base_url, api_key, model_name, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', ("default", 
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
                key,
                "deepseek-r1"))

def admin_panel():
    if not st.session_state.get('logged_in'):
        login_form()
        return

    if not st.session_state.is_admin:
        st.header("用户面板")
        with get_cursor() as c: 
            keys = c.execute('''SELECT id, key, username, used_tokens, total_tokens 
                            FROM api_keys WHERE is_active = 1 AND username = ?''',
                        (st.session_state.username,)).fetchall()
            for key in keys:
                with st.expander(f"密钥 {key[0]}"):
                    st.write(f"密钥: {key[1]}")
                    st.write(f"用户名: {key[2]}")
                    st.write(f"已用token: {key[3]}")
                    st.write(f"总token: {key[4]}")
                    if st.button(f"撤销密钥 {key[1]}"):
                        c.execute('DELETE FROM api_keys WHERE key = ?', (key[1],))
                        conn.commit()
                        st.rerun()
        return

    st.header("管理面板")
    tab1, tab2, tab3, tab4 = st.tabs(["用户凭证", "API Key配置", "用户", "黑名单"])

    with tab1:
        st.subheader("用户凭证管理")
        with st.form("生成凭证"):
            username = st.text_input("用户名")
            key = st.text_input("输入凭证（数字、字母组合）")
            token_total = st.number_input("总token数")
            if st.form_submit_button("生成凭证"):
                if generate_api_key(username, key, token_total):
                    st.success("凭证生成成功")

        st.subheader("活跃凭证")
        with get_cursor() as c: 
            keys = c.execute('SELECT id, key, username, used_tokens, total_tokens FROM api_keys WHERE is_active = 1').fetchall()
            for key in keys:
                with st.expander(f"密钥 {key[1]}"):
                    st.write(f"密钥: {key[1]}")
                    st.write(f"用户: {key[2]}")
                    st.write(f"已用token: {key[3]}")
                    st.write(f"总token: {key[4]}")
                    if st.button(f"删除key {key[1]}"):
                        c.execute('DELETE FROM api_keys WHERE key = ?', (key[1],))
                        st.rerun()

    with tab2:
        st.subheader("API配置管理")
        with st.form("添加配置"):
            config_name = st.text_input("配置名称")
            base_url = st.text_input("Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1")
            api_key = st.text_input("API密钥（sk-xxx格式）", type="password")
            model_name = st.text_input("模型名称（参考云服务厂商提供名称）", value="deepseek-r1")
            if st.form_submit_button("添加"):
                try:
                    with get_cursor() as c: 
                        c.execute('''
                            INSERT INTO api_configurations 
                            (config_name, base_url, api_key, model_name)
                            VALUES (?, ?, ?, ?)
                        ''', (config_name, base_url, api_key, model_name))
                    st.success("配置添加成功")
                except sqlite3.IntegrityError:
                    st.error("配置名称已存在")

        st.subheader("现有配置")
        with get_cursor() as c: 
            configs = c.execute('SELECT id, config_name, base_url, model_name, is_active FROM api_configurations').fetchall()
            for config in configs:
                with st.expander(f"{config[1]} ({'激活' if config[4] else '未激活'})"):
                    st.code(f"Base URL: {config[2]}\n模型: {config[3]}")
                    if st.button(f"{'停用' if config[4] else '激活'}", key=f"toggle_{config[0]}"):
                        c.execute('UPDATE api_configurations SET is_active = ? WHERE id = ?',
                                (not config[4], config[0]))
                        st.rerun()
                    if st.button("删除", key=f"del_{config[0]}"):
                        c.execute('DELETE FROM api_configurations WHERE id = ?', (config[0],))
                        st.rerun()

    with tab3:
        st.subheader("用户管理")
        register_form()
        with get_cursor() as c: 
            users = c.execute('SELECT id, username, is_admin FROM users').fetchall()
        for user in users:
            cols = st.columns([3,1,1])
            cols[0].write(user[1])
            is_admin = cols[1].checkbox("管理员", value=bool(user[2]), key=f"admin_{user[1]}")
            if is_admin != user[2]:
                update_admin_status(user[0], is_admin)
            if cols[2].button("删除", key=f"del_{user[1]}"):
                delete_user(user[0])
                st.rerun()

    with tab4:
        st.subheader("黑名单管理")
        with get_cursor() as c: 
            with st.form("黑名单操作"):
                username = st.text_input("用户名")
                reason = st.text_input("原因")
                col1, col2 = st.columns(2)
                if col1.form_submit_button("添加"):
                    try:
                        c.execute('INSERT INTO blacklist (username, reason) VALUES (?, ?)', (username, reason))
                        st.success("已添加至黑名单")
                    except sqlite3.IntegrityError:
                        st.error("用户已在黑名单中")
                if col2.form_submit_button("移除"):
                    c.execute('DELETE FROM blacklist WHERE username = ?', (username,))
                    st.success("已从黑名单移除")

            st.subheader("黑名单列表")
            blacklist = c.execute('SELECT username, reason FROM blacklist').fetchall()
            for entry in blacklist:
                st.write(f"{entry[0]} - {entry[1]}")
