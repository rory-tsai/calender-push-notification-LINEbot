from __future__ import print_function
import datetime
import os
import sys
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# === LINE 機器人資訊 ===
ACCESS_TOKEN = 'LINE_ACCESS_TOKEN' # LINE 存取權杖
GROUP_ID = 'LINE_GROUP_ID' # LINE 群組 ID

# Google Calendar 權限範圍
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def load_creds():
    """讀取或建立 Google Calendar API 憑證"""
    creds = None
    token_path = 'token.json'
    cred_path = 'credentials.json'

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"[警告] 讀取 token.json 失敗：{e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"找不到 {cred_path}")
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
            print("[資訊] 已更新 token.json")

    return creds

def get_events_for_day(target_date):
    """取得指定日期的行程清單"""
    creds = load_creds()
    service = build('calendar', 'v3', credentials=creds)

    tz_offset = datetime.timedelta(hours=8)  # 台灣時區 +8
    start_of_day = datetime.datetime(target_date.year, target_date.month, target_date.day, 0, 0) - tz_offset
    end_of_day = start_of_day + datetime.timedelta(days=1)

    events_result = service.events().list(
        calendarId='primary', # 可改為所需日曆ID
        timeMin=start_of_day.isoformat() + 'Z',
        timeMax=end_of_day.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

def format_events_msg(date_obj, events, label):
    """格式化 LINE 推送訊息"""
    weekday_map = ['一', '二', '三', '四', '五', '六', '日']
    header = f"{label}（{date_obj.strftime('%Y/%m/%d')}（{weekday_map[date_obj.weekday()]}））\n—"
    if not events:
        return header + f"\n{label}沒有行程 🎉"

    lines = []
    for e in events:
        start = e['start'].get('dateTime', e['start'].get('date'))
        end = e['end'].get('dateTime', e['end'].get('date'))
        try:
            start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%H:%M')
            end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%H:%M')
            time_str = f"{start_time}–{end_time}"
        except:
            time_str = "全天"
        summary = e.get('summary', '(無標題)')
        lines.append(f"• {time_str} ｜ {summary}")

    return header + "\n" + "\n".join(lines)

def send_line_message(text):
    """推送訊息到 LINE"""
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "to": GROUP_ID,
        "messages": [{"type": "text", "text": text}]
    }
    r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print("[LINE] 狀態碼：", r.status_code, r.text)

def main():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)  # 台灣時區

    if "--today" in sys.argv:
        target_date = now.date()
        label = "今日行程"
    elif "--monday" in sys.argv:
        # 找下週一
        days_until_monday = (7 - now.weekday()) % 7  # 星期一是 0
        if days_until_monday == 0:
            days_until_monday = 7
        target_date = (now + datetime.timedelta(days=days_until_monday)).date()
        label = "下週一行程"
    else:
        # 預設是明天
        target_date = (now + datetime.timedelta(days=1)).date()
        label = "明日行程"

    events = get_events_for_day(target_date)
    msg = format_events_msg(target_date, events, label)
    print("=== 將發送到 LINE 的訊息 ===")
    print(msg)
    send_line_message(msg)

if __name__ == '__main__':
    main()
