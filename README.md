# AI キャル v3

為公主連結所設計的 Discord 聊天機器人

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/discord.py?style=for-the-badge)
[![Discord](https://img.shields.io/discord/605314314768875520?style=for-the-badge)](https://discord.gg/cwFc4qh)
[![Invite bot](https://img.shields.io/badge/Invite-bot-blue?style=for-the-badge)](https://discordapp.com/oauth2/authorize?client_id=594885334232334366&permissions=8&scope=applications.commands%20bot)
[![Notion document](https://img.shields.io/badge/Notion-Docs-lightgrey?style=for-the-badge)](https://iandesuyo.notion.site/AI-v3-baec83903f764b7f95d0186f105190ee)

# 安裝方式

## 前置需求

在開始安裝前, 請先完成下列步驟

- 於[Discord Developer Portal](https://discord.com/developers/applications/)建立一個Bot
- 擁有一個[mongoDB](https://www.mongodb.com/), 並建立名為`AIKyaru`的 Database 及名為`guild`, `user`的 Collections
- 閱讀 [設定說明](#設定說明) 來完成`config.json`之設置

## Docker

要使用 Docker 運行, 你可以直接使用下列指令來建置與運行

```bash
docker build -t ai_kyaru .

docker run -d \
    --name ai_kyaru \
    -e BOT_TOKEN=YOUR_BOT_TOKEN \
    -v /path/to/config.json:/app/config.json \
    ai_kyaru
```

## 手動安裝

在開始安裝前, 建議先使用 virtualenv 創建虛擬環境, 並設置環境變數`TOKEN`

```bash
pip3 install -r requirements.txt

BOT_TOKEN=YOUR_BOT_TOKEN

python3 main.py
```

# 設定說明

除了 Discord 機器人的 Token 外, 其餘設定皆儲存於`config.json`

首次設定時, 請先參考`config.json.example`內的格式並修改設定值

```json
{
  "status": "online", // 機器人的上線狀態
  "activity": {
    // 根據下方設定, 結果為 "正在看 .help｜ヤバイわよ!!"
    "type": 3, // 機器人的狀態, playing=0, streaming=1, listening=2, watching=3
    "prefix": ".help｜", // 機器人狀態的前綴
    "default_text": "ヤバイわよ!!" // 預設狀態文字
  },
  "prefix": ".", // 指令前綴
  "cogs": [
    // 需要載入的Cogs
    "cogs.admin", // 管理員功能
    "cogs.rubiBank", // 盧幣銀行
    "cogs.character", // 角色相關資訊查詢
    "cogs.profileCard", // 個人檔案
    "cogs.common", // 基本功能, 如體力計算及抽卡模擬
    "cogs.newsForward", // 簡易設定公告轉發
    "cogs.preferences", // 偏好設定
    "cogs.clan", // 戰隊系統
    "cogs.response", // 基本回覆
    "cogs.tasks" // 排程任務
  ],
  "helpTitle": "哈囉~ 歡迎使用 AI キャル", // 使用help時的主要提示文字
  "AssetsURL": "https://randosoru.me/static/assets", // 圖片素材之網址
  "RediveJP_DB": [
    "https://redive.estertion.win/db/redive_jp.db.br", // 日版資料庫
    "https://redive.estertion.win/last_version_jp.json" // 日版資料庫版本
  ],
  "RediveTW_DB": [
    "https://randosoru.me/redive_db/redive_tw.db.br", // 台版資料庫
    "https://randosoru.me/redive_db/version.json" // 台版資料庫版本
  ],
  "keywordGSheet": {
    // 於Google Sheets上的角色關鍵字匹配表
    "key": "12QiLoCODWr4TRVGqwXROCYenh2xz-ZXqhDMgzUi7Gz4",
    "gid": "755815818"
  },
  "DEBUG_CHANNEL": null, // Discord文字頻道ID, 供傳送錯誤訊息用
  "MONGODB_URL": "mongodb://username:password@host:port", // MongoDB網址
  "GUILD_API_URL": "https://guild.randosoru.me/api", // 戰隊管理協會API
  "GUILD_API_TOKEN": "GUILD_API_TOKEN", // API Token
  "GAME_API_URL": "https://example.com", // 個人檔案API
  "GAME_API_TOKEN": "GAME_API_TOKEN", // API Token
  "PCRwiki": "https://pcredivewiki.tw/Character/Detail", // 蘭德索爾圖書館 角色資訊頁面之網址
  "EmojiServers": {
    // 抽卡模擬時所使用之emojis, emoji名稱需為4位數unit_id
    "1": [802234826413178920], // 1星角色之Discord伺服器ID
    "2": [802241470878187570], // 2星角色之Discord伺服器ID
    "3": [802241643121999883], // 3星角色之Discord伺服器ID
    "Pickup": [850065739590139957] // Pickup角色之Discord伺服器ID
  },
  "RankData": {
    // Rank推薦來源
    "emonight": {
      // 漪夢奈特emonight所提供之Google Sheets表格
      "key": "",
      "gid": "",
      "sql": "select%20*"
    },
    "nonplume": {
      // 無羽nonplume所提供之Google Sheets表格
      "key": "",
      "gid": "",
      "sql": "select%20*"
    }
  }
}
```

備註:

- 上方 Google Sheets 之`key`與`gid`可於網址內獲取, 例如` https://docs.google.com/spreadsheets/d/{key}/edit#gid={gid}`
- 4 位數 unit_id 之格式為`1xxx`, 如凱留為`1060`
- 若需使用戰隊管理協會 API, 請聯繫我申請
