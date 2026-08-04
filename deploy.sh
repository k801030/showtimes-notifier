#!/bin/bash
set -e

# 載入 .env 檔案中的環境變數
if [ -f .env ]; then
  source .env
else
  echo "❌ 錯誤：找不到 .env 檔案！"
  exit 1
fi

if [ -z "$WEBHOOK_URL" ] || [ -z "$PROJECT_ID" ] || [ -z "$PROJECT_NUMBER" ] || [ -z "$REGION" ]; then
  echo "❌ 錯誤：.env 中未設定必要的環境變數 (WEBHOOK_URL, PROJECT_ID, PROJECT_NUMBER, REGION)！"
  exit 1
fi

SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "=== 1. 更新 Secret 版本 ==="
echo -n "$WEBHOOK_URL" | gcloud secrets versions add WEBHOOK_URL --data-file=- --project=$PROJECT_ID

echo "=== 2. 部署 Cloud Functions ==="
gcloud functions deploy showtimes-notifier \
  --gen2 \
  --runtime=python312 \
  --region=$REGION \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars THEATER_ID=91,NOTIFICATION_CHANNEL=discord \
  --set-secrets 'WEBHOOK_URL=WEBHOOK_URL:latest' \
  --project=$PROJECT_ID

echo "=== 3. 建立 Cloud Scheduler 定時排程 ==="
CRON_SCHEDULE="*/3 12-22 * * WED"
FUNCTION_URL=$(gcloud functions describe showtimes-notifier --gen2 --region=$REGION --format="value(serviceConfig.uri)" --project=$PROJECT_ID)

# 如果排程已存在，先刪除再建立，確保更新
gcloud scheduler jobs delete showtimes-notifier-trigger --quiet --location=$REGION --project=$PROJECT_ID || true

gcloud scheduler jobs create http showtimes-notifier-trigger \
  --schedule="$CRON_SCHEDULE" \
  --uri="$FUNCTION_URL" \
  --http-method=POST \
  --time-zone="Asia/Taipei" \
  --location=$REGION \
  --project=$PROJECT_ID

echo "=== ✅ 快速部署完成！ ==="
