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

echo "=== 1. 啟用必要的 GCP API ==="
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project=$PROJECT_ID

echo "⏳ 等待 API 啟用同步 (60 秒)..."
sleep 60

echo "=== 2. 建立 Firestore 資料庫 ==="
# 允許已存在錯誤
gcloud firestore databases create --location=$REGION --type=firestore-native --project=$PROJECT_ID || true

echo "=== 3. 建立 Secret Manager Secret ==="
# 允許已存在錯誤
gcloud secrets create WEBHOOK_URL --replication-policy="automatic" --project=$PROJECT_ID || true

echo "=== 4. 設定 IAM 權限 ==="
gcloud secrets add-iam-policy-binding WEBHOOK_URL \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user" \
  --condition=None

echo "⏳ 等待 IAM 權限同步 (90 秒)..."
sleep 90

echo "=== ✅ GCP 基礎建設與權限初始化完成！ ==="
echo "現在您可以執行 make deploy 來快速部署程式碼與排程。"
