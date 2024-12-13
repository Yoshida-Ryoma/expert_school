import streamlit as st
import pymongo
from pymongo import MongoClient

st.markdown('<link href="expert/style.css" rel="stylesheet"/>', unsafe_allow_html=True)

BOOTSTRAP_CSS="""<link href="expert/style.css" rel="stylesheet">"""

# MongoDBの設定
MONGO_URI = "mongodb+srv://Y_ryon:ABC@expert.biu9n.mongodb.net/?retryWrites=true&w=majority&appName=expert"
DATABASE_NAME = "job_database"
ACCOUNTS_COLLECTION = "accounts"
REQUESTS_COLLECTION = "job_requests"

# MongoDBへの接続
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
accounts_collection = db[ACCOUNTS_COLLECTION]
requests_collection = db[REQUESTS_COLLECTION]

# カスタムCSSの適用
st.markdown("""<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .main__title {
        font-size: 60px;
        font-weight: 700;
    }
    .font {
        margin:0px;
        font-size: 30px;
        font-weight: 700;
    }
    .font_sub {
        margin: 0px;
        font-size: 15px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 初期化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = ""
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = ""

def login_page():
    """ログインページのUI"""
    st.markdown('<p class="main__title">ログインページ</p>', unsafe_allow_html=True)
    st.markdown('<p class="font">IDとパスワードを入力してください</p>', unsafe_allow_html=True)
    input__id = st.text_input("ID")
    input__pass = st.text_input("Password",type="password")

    if st.button("ログイン"):
        user = accounts_collection.find_one({"user_id": input__id, "password": input__pass})
        if user:
            st.session_state.logged_in = True
            st.session_state.page = "main"
            st.session_state.current_user_name = user["name"]
            st.session_state.current_user_id = user["user_id"]
        else:
            st.error("ログインに失敗しました。IDまたはパスワードを確認してください。")

    if st.button("新規アカウント作成"):
        st.session_state.page = "create_account"

def create_account_page():
    """アカウント作成ページのUI"""
    st.markdown('<p class="main__title">新規アカウント作成</p>', unsafe_allow_html=True)

    st.markdown('<p class="font">名前,ID,Passwordを入力してください</p>', unsafe_allow_html=True)
    new_user_name = st.text_input("名前")
    new_user_id = st.text_input("ID")
    new_user_password = st.text_input("Password", type="password")

    if st.button("アカウント作成"):
        if new_user_name.strip() and new_user_id.strip() and new_user_password.strip():
            if accounts_collection.find_one({"user_id": new_user_id}):
                st.error("このIDは既に使用されています。別のIDを入力してください。")
            else:
                accounts_collection.insert_one({
                    "name": new_user_name,
                    "user_id": new_user_id,
                    "password": new_user_password
                })
                st.success("アカウントが作成されました！ログインページに戻ってログインしてください。")
                if st.button("ログインページに戻る"):
                    st.session_state.page = "login"
        else:
            st.error("全ての項目を入力してください。")

def main_page():
    """メインページのUI"""
    st.markdown('<p class="main__title">メインページ</p>', unsafe_allow_html=True)
    st.write(f"ようこそ、{st.session_state.current_user_name} さん！")

    if st.button("仕事を依頼する"):
        st.session_state.page = "job_request"
    if st.button("依頼一覧を見る"):
        st.session_state.page = "job_list"
    if st.button("受託した依頼を見る"):
        st.session_state.page = "accepted_jobs"
    if st.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

def job_request_page():
    """仕事依頼ページのUI"""
    st.markdown('<p class="main__title">仕事の依頼ページ</p>', unsafe_allow_html=True)

    # MongoDBから現在のユーザー名を取得
    current_user = accounts_collection.find_one({"user_id": st.session_state.current_user_id})
    current_user_name = current_user["name"] if current_user else "不明"
    st.markdown('<p class="font">依頼内容と必要な技術を入力してください</p>', unsafe_allow_html=True)
    st.markdown('<p class="font_sub">必要な技術がない場合なしと入力してください</p>', unsafe_allow_html=True)
    job_description = st.text_area("依頼内容")
    need_ability = st.text_input("必要な技術")
    your_name = st.text_input("依頼者名", value=current_user_name, disabled=True)

    if st.button("依頼を送信"):
        if job_description.strip() and need_ability.strip():
            requests_collection.insert_one({
                "job_description": job_description,
                "need_ability": need_ability,
                "user_id": st.session_state.current_user_id,
                "user_name": current_user_name
            })

            st.success("依頼が送信されました。")
        else:
            st.error("全ての項目を入力してください。")

    if st.button("戻る"):
        st.session_state.page = "main"

def job_list_page():
    """依頼一覧ページのUI"""
    st.markdown('<p class="main__title">依頼一覧ページ</p>', unsafe_allow_html=True)

    # すべての依頼を取得
    jobs = list(requests_collection.find({"accepted_by": None}))  # 未受託の依頼のみ表示
    if jobs:
        for idx, job in enumerate(jobs, start=1):
            st.subheader(f"依頼 {idx}")
            st.write(f"仕事内容: {job['job_description']}")
            st.write(f"必要な技術: {job['need_ability']}")
            st.write(f"依頼者: {job['user_name']} ({job['user_id']})")

            # 受託ボタン
            if st.button(f"受託する - 依頼 {idx}", key=f"accept_{idx}"):
                requests_collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"accepted_by": st.session_state.current_user_id}}
                )
                st.success(f"依頼 {idx} を受託しました。")
                # 手動でページを再描画
                st.session_state.page = "job_list"
                st.experimental_set_query_params(refresh="true")


            st.write("---")
    else:
        st.markdown('<p class="font">現在受託可能な依頼はありません</p>', unsafe_allow_html=True)

    if st.button("戻る"):
        st.session_state.page = "main"

def accepted_jobs_page():
    """受託した依頼一覧ページのUI"""
    st.markdown('<p class="main__title">受託した依頼一覧</p>', unsafe_allow_html=True)

    # 現在のログインユーザーが受託した依頼を取得
    accepted_jobs = list(requests_collection.find({"accepted_by": st.session_state.current_user_id}))
    if accepted_jobs:
        for idx, job in enumerate(accepted_jobs, start=1):
            st.subheader(f"依頼 {idx}")
            st.write(f"仕事内容: {job['job_description']}")
            st.write(f"必要な技術: {job['need_ability']}")
            st.write(f"依頼者: {job['user_name']} ({job['user_id']})")

            # 終了ボタン
        if st.button(f"終了する - 依頼 {idx}", key=f"complete_{idx}"):
            requests_collection.delete_one({"_id": job["_id"]})
            st.success(f"依頼 {idx} を終了しました。")
            # 手動でページを再描画
            st.session_state.page = "accepted_jobs"
            st.experimental_set_query_params(refresh="true")


            st.write("---")
    else:
        st.markdown('<p class="font">現在受託した依頼はありません</p>', unsafe_allow_html=True)

    if st.button("戻る"):
        st.session_state.page = "main"

# ページ分岐
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "create_account":
    create_account_page()
elif st.session_state.page == "main":
    main_page()
elif st.session_state.page == "job_request":
    job_request_page()
elif st.session_state.page == "job_list":
    job_list_page()
elif st.session_state.page == "accepted_jobs":
    accepted_jobs_page()
