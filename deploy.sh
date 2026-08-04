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
if [ -n "$WEBHOOK_URL" ]; then
  echo -n "$WEBHOOK_URL" | gcloud secrets versions add WEBHOOK_URL --data-file=- --project=$PROJECT_ID
fi
if [ -n "$VIESHOW_WEBHOOK_URL" ]; then
  echo -n "$VIESHOW_WEBHOOK_URL" | gcloud secrets versions add VIESHOW_WEBHOOK_URL --data-file=- --project=$PROJECT_ID
fi

echo "=== 2. 部署 Cloud Functions ==="
gcloud functions deploy showtimes-notifier \
  --gen2 \
  --runtime=python312 \
  --region=$REGION \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars THEATER_ID=91,VIESHOW_CINEMA_CODE=BQ,NOTIFICATION_CHANNEL=discord,CHAIN=showtimes \
  --set-secrets 'WEBHOOK_URL=WEBHOOK_URL:latest,VIESHOW_WEBHOOK_URL=VIESHOW_WEBHOOK_URL:latest' \
  --project=$PROJECT_ID

echo "=== 3. 建立 Cloud Scheduler 定時排程 (Scheme A) ==="
FUNCTION_URL=$(gcloud functions describe showtimes-notifier --gen2 --region=$REGION --format="value(serviceConfig.uri)" --project=$PROJECT_ID)

# 秀泰排程 (每週三 12-22 點，每 3 分鐘一次)
SHOWTIMES_CRON="*/3 12-22 * * WED"
gcloud scheduler jobs delete showtimes-notifier-trigger --quiet --location=$REGION --project=$PROJECT_ID || true

gcloud scheduler jobs create http showtimes-notifier-trigger \
  --schedule="$SHOWTIMES_CRON" \
  --uri="$FUNCTION_URL" \
  --http-method=POST \
  --headers=Content-Type=application/json \
  --message-body='{"chain": "showtimes"}' \
  --time-zone="Asia/Taipei" \
  --location=$REGION \
  --project=$PROJECT_ID

# 威秀排程 (預設每週三 12 點開始)
VIESHOW_CRON="0 12-18 * * WED"
gcloud scheduler jobs delete vieshow-notifier-trigger --quiet --location=$REGION --project=$PROJECT_ID || true

gcloud scheduler jobs create http vieshow-notifier-trigger \
  --schedule="$VIESHOW_CRON" \
  --uri="$FUNCTION_URL" \
  --http-method=POST \
  --headers=Content-Type=application/json \
  --message-body='{"chain": "vieshow"}' \
  --time-zone="Asia/Taipei" \
  --location=$REGION \
  --project=$PROJECT_ID

echo "=== ✅ 快速部署完成！ ==="
