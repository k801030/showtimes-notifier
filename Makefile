.PHONY: test run setup deploy install clean help

.DEFAULT_GOAL := help

help:
	@echo "秀泰影城售票通知系統 - 快捷指令:"
	@echo "  make install  - 安裝 Python 相關套件"
	@echo "  make run      - 在本地執行一次檢查 (未全面開放時不會發通知)"
	@echo "  make test     - 在本地強制發送一次測試通知"
	@echo "  make setup    - 初始化 GCP 基礎建設與權限 (首次部署才需要)"
	@echo "  make deploy   - 快速部署最新的程式碼與排程到 GCP"
	@echo "  make clean    - 清除本地快取與通知狀態 (重置 state.txt)"

install:
	@echo "正在安裝套件..."
	pip3 install -r requirements.txt --user --index-url https://pypi.org/simple

run:
	@echo "正在本地執行檢查..."
	python3 main.py

test:
	@echo "正在強制發送測試通知..."
	TEST_NOTIFICATION=1 python3 main.py

setup:
	@echo "正在初始化 GCP 基礎建設與權限 (此步驟只需執行一次)..."
	bash setup.sh

deploy:
	@echo "正在啟動快速部署流程..."
	bash deploy.sh

clean:
	@echo "正在清除本地快取與狀態..."
	rm -rf __pycache__
	rm -f state.txt
