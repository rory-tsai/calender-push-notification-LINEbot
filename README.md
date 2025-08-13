# Google Calendar to LINE Bot 行程提醒

這是一個用 Python 撰寫的工具，可以每天自動從 Google 行事曆抓取行程，並透過 LINE Bot 推播提醒。

## 功能特色
- 支援 **今日行程提醒**
- 支援 **明日行程提醒**
- 支援 **週五提醒下週一行程**
- 可結合 Linux `crontab` 自動發送
- 支援 Google Calendar **重複事件**（如每週固定行程）

---

## 安裝與設定

### 1. 安裝 Python 套件
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```
> 建議使用 [虛擬環境 venv](https://docs.python.org/zh-tw/3/library/venv.html) 避免環境衝突。

---

### 2. 建立 Google Calendar API 憑證
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 啟用 **Google Calendar API**
3. 到「API 和服務 → 認證」建立 **OAuth 2.0 用戶端 ID**（應用程式類型選「桌面應用程式」）
4. 下載 JSON 憑證，並將檔名改為：
   ```
   credentials.json
   ```
   放到程式根目錄（`calenderread.py` 同資料夾）

---

### 3. 設定 LINE Bot
1. 前往 [LINE Developers](https://developers.line.biz/) 建立 **Messaging API channel**
2. 取得：
   - **Channel access token**
   - **User ID**（個人推播）或 **Group ID**（群組推播）
3. 在 `calenderread.py` 內填入：
   ```python
   ACCESS_TOKEN = "你的長效 Channel Access Token"
   GROUP_ID = "你的 UserId 或 GroupId"
   ```

---

### 4. 首次授權
第一次執行程式會自動開啟瀏覽器，請登入 Google 帳號並允許存取行事曆。  
授權完成後會自動產生 `token.json`，之後就不用再登入。

---

## 使用方式

### 明日行程提醒（預設）
```bash
python calenderread.py
```

### 今日行程提醒
```bash
python calenderread.py --today
```

### 下週一行程提醒
```bash
python calenderread.py --monday
```

---

## 自動排程（Linux crontab 範例）

假設你使用虛擬環境 `/path/to/venv` 並將程式放在 `/opt/calender-push-note`：

```bash
SHELL=/bin/bash
TZ=Asia/Taipei

# 週一到週四 08:00 發「今日行程」
0 8 * * 1-4  /path/to/venv/bin/python /opt/calender-push-note/calenderread.py --today

# 週一到週四 16:30 發「明日行程」
30 16 * * 1-4 /path/to/venv/bin/python /opt/calender-push-note/calenderread.py

# 週五 16:30 發「下週一行程」
30 16 * * 5   /path/to/venv/bin/python /opt/calender-push-note/calenderread.py --monday
```

---

## 授權
本專案依 [MIT License](LICENSE) 授權，歡迎自由使用與修改。
