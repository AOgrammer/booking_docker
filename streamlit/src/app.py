import streamlit as st
import requests
import json
import pandas as pd
import datetime
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 設定ファイルの読み込み
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# 認証オブジェクトの作成
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# ログイン
authenticator.login()

# 認証されている場合
if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout("ログアウト")
        user_name = st.session_state['name']
        user_roles = config['credentials']['roles'][user_name]  # ユーザーのロールを取得

        page = st.selectbox('ページを選択',
                           ['予約登録'] if 'user' in user_roles else  # 予約はユーザーのみ許可
                           ['ユーザー登録', '会議室登録', '予約登録', 'ユーザー更新・削除', '会議室更新・削除', '予約更新・削除'])

    

    if page == 'ユーザー登録':
        st.title('ユーザー登録画面')
        with st.form(key='user'):
            username = st.text_input('ユーザー名', max_chars=12)
            data = {
                'username': username
            }
            submit_button = st.form_submit_button(label='ユーザー登録')

        if submit_button:
            url = 'http://fastapi:8000/users'
            res = requests.post(url, data=json.dumps(data))
            if res.status_code == 200:
                st.success('ユーザー登録完了')



    elif page == '会議室登録':
        st.title('会議室登録画面')
        with st.form(key='room'):
            room_name = st.text_input('会議室名', max_chars=12)
            capacity = st.number_input('定員', step=1)
            data = {
                'room_name': room_name,
                'capacity': capacity
            }
            submit_button = st.form_submit_button(label='会議室登録')

        if submit_button:
            url = 'http://fastapi:8000/rooms'
            res = requests.post(url, data=json.dumps(data))
            if res.status_code == 200:
                st.success('会議室登録完了')
            

    elif page == '予約登録':
        st.title('会議室予約画面')
        url_users = 'http://fastapi:8000/users'
        res = requests.get(url_users)
        users = res.json()
        users_name = {user['username']: user['user_id'] for user in users}

        url_rooms = 'http://fastapi:8000/rooms'
        res = requests.get(url_rooms)
        rooms = res.json()
        rooms_name = {room['room_name']: {'room_id': room['room_id'], 'capacity': room['capacity']} for room in rooms}

        st.write('### 会議室一覧')
        df_rooms = pd.DataFrame(rooms)
        df_rooms.columns = ['会議室名', '定員', '会議室ID']
        st.table(df_rooms)

        url_bookings = 'http://fastapi:8000/bookings'
        res = requests.get(url_bookings)
        bookings = res.json()
        df_bookings = pd.DataFrame(bookings)

        users_id = {user['user_id']: user['username'] for user in users}
        rooms_id = {room['room_id']: {'room_name': room['room_name'], 'capacity': room['capacity']} for room in rooms}

        to_username = lambda x: users_id[x]
        to_room_name = lambda x: rooms_id[x]['room_name']
        to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime('%Y/%m/%d %H:%M')

        df_bookings['user_id'] = df_bookings['user_id'].map(to_username)
        df_bookings['room_id'] = df_bookings['room_id'].map(to_room_name)
        df_bookings['start_datetime'] = df_bookings['start_datetime'].map(to_datetime)
        df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

        df_bookings = df_bookings.rename(columns={
            'user_id': '予約者名',
            'room_id': '会議室名',
            'booked_num': '予約人数',
            'start_datetime': '開始時刻',
            'end_datetime': '終了時刻',
            'booking_id': '予約番号'
        })
        st.write('### 予約一覧')
        st.table(df_bookings)

        with st.form(key='booking'):
            username = st.selectbox('予約者名', users_name.keys())
            room_name = st.selectbox('会議室名', rooms_name.keys())
            booked_num = st.number_input('予約人数', step=1, min_value=1)
            date = st.date_input('日付: ', min_value=datetime.date.today())
            start_time = st.time_input('開始時刻: ', value=datetime.time(hour=9, minute=0))
            end_time = st.time_input('終了時刻: ', value=datetime.time(hour=20, minute=0))
            submit_button = st.form_submit_button(label='予約登録')

        if submit_button:
            user_id = users_name[username]
            room_id = rooms_name[room_name]['room_id']
            capacity = rooms_name[room_name]['capacity']

            data = {
                'user_id': user_id,
                'room_id': room_id,
                'booked_num': booked_num,
                'start_datetime': datetime.datetime(
                    year=date.year, month=date.month, day=date.day,
                    hour=start_time.hour, minute=start_time.minute
                ).isoformat(),
                'end_datetime': datetime.datetime(
                    year=date.year, month=date.month, day=date.day,
                    hour=end_time.hour, minute=end_time.minute
                ).isoformat()
            }
            if booked_num > capacity:
                st.error(f'{room_name}の定員は、{capacity}名です。{capacity}名以下の予約人数のみ受け付けております。')
            elif start_time >= end_time:
                st.error('開始時刻が終了時刻を越えています')
            elif start_time < datetime.time(hour=9, minute=0, second=0) or end_time > datetime.time(hour=20, minute=0, second=0):
                st.error('利用時間は9:00~20:00になります。')
            else:
                url = 'http://fastapi:8000/bookings'
                res = requests.post(url, data=json.dumps(data))
                if res.status_code == 200:
                    st.success('予約完了しました')
                elif res.status_code == 404 and res.json()['detail'] == 'Already booked':
                    st.error('指定の時間にはすでに予約が入っています。')

    elif page == 'ユーザー更新・削除':
        st.title('ユーザー更新・削除画面')
        url_users = 'http://fastapi:8000/users'
        res = requests.get(url_users)
        users = res.json()
        users_name = {user['username']: user['user_id'] for user in users}

        selected_user = st.selectbox('ユーザーを選択', users_name.keys())
        user_id = users_name[selected_user]

        with st.form(key='update_user'):
            new_username = st.text_input("新しいユーザー名", key='new_username')
            update_button = st.form_submit_button(label='ユーザー更新')

        if update_button:
            url = f'http://fastapi:8000/users/{user_id}'
            res = requests.put(url, data=json.dumps({'username': new_username}))
            if res.status_code == 200:
                st.success('ユーザー情報が更新されました')
            

        with st.form(key='delete_user'):
            delete_button = st.form_submit_button(label='ユーザー削除')

        if delete_button:
            url = f'http://fastapi:8000/users/{user_id}'
            res = requests.delete(url)
            if res.status_code == 200:
                st.success('ユーザーが削除されました')
            

    elif page == '会議室更新・削除':
        st.title('会議室更新・削除画面')
        url_rooms = 'http://fastapi:8000/rooms'
        res = requests.get(url_rooms)
        rooms = res.json()
        rooms_name = {room['room_name']: room['room_id'] for room in rooms}

        selected_room = st.selectbox('会議室を選択', rooms_name.keys())
        room_id = rooms_name[selected_room]

        with st.form(key='update_room'):
            new_room_name = st.text_input("新しい会議室名", key='new_room_name')
            new_capacity = st.number_input("新しい定員", step=1, min_value=1, key='new_capacity')
            update_button = st.form_submit_button(label='会議室更新')

        if update_button:
            url = f'http://fastapi:8000/rooms/{room_id}'
            res = requests.put(url, data=json.dumps({'room_name': new_room_name, 'capacity': new_capacity}))
            if res.status_code == 200:
                st.success('会議室情報が更新されました')
            

        with st.form(key='delete_room'):
            delete_button = st.form_submit_button(label='会議室削除')

        if delete_button:
            url = f'http://fastapi:8000/rooms/{room_id}'
            res = requests.delete(url)
            if res.status_code == 200:
                st.success('会議室が削除されました')
            

    elif page == '予約更新・削除':
        st.title('予約更新・削除画面')
        url_bookings = 'http://fastapi:8000/bookings'
        res = requests.get(url_bookings)
        bookings = res.json()
        bookings_id = {f"{booking['booking_id']} - {booking['start_datetime']} to {booking['end_datetime']}": booking['booking_id'] for booking in bookings}

        selected_booking = st.selectbox('予約を選択', bookings_id.keys())
        booking_id = bookings_id[selected_booking]

        url_users = 'http://fastapi:8000/users'
        res = requests.get(url_users)
        users = res.json()
        users_name = {user['username']: user['user_id'] for user in users}

        url_rooms = 'http://fastapi:8000/rooms'
        res = requests.get(url_rooms)
        rooms = res.json()
        rooms_name = {room['room_name']: {'room_id': room['room_id'], 'capacity': room['capacity']} for room in rooms}

        with st.form(key='update_booking'):
            username = st.selectbox('予約者名', users_name.keys(), key='update_username')
            room_name = st.selectbox('会議室名', rooms_name.keys(), key='update_room_name')
            booked_num = st.number_input('予約人数', step=1, min_value=1, key='update_booked_num')
            date = st.date_input('日付: ', min_value=datetime.date.today(), key='update_date')
            start_time = st.time_input('開始時刻: ', value=datetime.time(hour=9, minute=0), key='update_start_time')
            end_time = st.time_input('終了時刻: ', value=datetime.time(hour=20, minute=0), key='update_end_time')
            update_button = st.form_submit_button(label='予約更新')

        if update_button:
            user_id = users_name[username]
            room_id = rooms_name[room_name]['room_id']
            capacity = rooms_name[room_name]['capacity']

            data = {
                'user_id': user_id,
                'room_id': room_id,
                'booked_num': booked_num,
                'start_datetime': datetime.datetime(
                    year=date.year, month=date.month, day=date.day,
                    hour=start_time.hour, minute=start_time.minute
                ).isoformat(),
                'end_datetime': datetime.datetime(
                    year=date.year, month=date.month, day=date.day,
                    hour=end_time.hour, minute=end_time.minute
                ).isoformat()
            }
            if booked_num > capacity:
                st.error(f'{room_name}の定員は、{capacity}名です。{capacity}名以下の予約人数のみ受け付けております。')
            elif start_time >= end_time:
                st.error('開始時刻が終了時刻を越えています')
            elif start_time < datetime.time(hour=9, minute=0, second=0) or end_time > datetime.time(hour=20, minute=0, second=0):
                st.error('利用時間は9:00~20:00になります。')
            else:
                url = f'http://fastapi:8000/bookings/{booking_id}'
                res = requests.put(url, data=json.dumps(data))
                if res.status_code == 200:
                    st.success('予約が更新されました')
                

        with st.form(key='delete_booking'):
            delete_button = st.form_submit_button(label='予約削除')

        if delete_button:
            url = f'http://fastapi:8000/bookings/{booking_id}'
            res = requests.delete(url)
            if res.status_code == 200:
                st.success('予約が削除されました')

# 認証されていない場合
elif st.session_state["authentication_status"] is False:
    st.error('ユーザー名/パスワードが不正です')

# ログイン情報がない場合
elif st.session_state["authentication_status"] is None:
    st.warning('ユーザー名とパスワードを入力してください')
