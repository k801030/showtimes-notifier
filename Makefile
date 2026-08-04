.PHONY: test test-showtimes test-vieshow run run-showtimes run-vieshow setup deploy install clean help

.DEFAULT_GOAL := help

help:
	@echo "電影場次開放通知系統 - 快捷指令:"
	@echo "  make install         - 安裝 Python 相關套件"
	@echo "  make run             - 在本地執行所有影城檢查"
	@echo "  make run-showtimes   - 在本地執行 [秀泰] 檢查"
	@echo "  make run-vieshow     - 在本地執行 [威秀] 檢查"
	@echo "  make test            - 在本地發送所有影城測試通知"
	@echo "  make test-showtimes  - 在本地發送 [秀泰] 測試通知"
	@echo "  make test-vieshow    - 在本地發送 [威秀] 測試通知"
	@echo "  make setup           - 初始化 GCP 基礎建設與權限 (首次部署才需要)"
	@echo "  make deploy          - 快速部署最新的程式碼與排程到 GCP"
	@echo "  make clean           - 清除本地快取與通知狀態 (重置 state.txt)"

install:
	@echo "正在安裝套件..."
	pip3 install -r requirements.txt --user --index-url https://pypi.org/simple

run-showtimes:
	@echo "正在本地執行 [秀泰] 檢查..."
	CHAIN=showtimes python3 main.py

run-vieshow:
	@echo "正在本地執行 [威秀] 檢查..."
	CHAIN=vieshow python3 main.py

run: run-showtimes run-vieshow

test-showtimes:
	@echo "正在強制發送 [秀泰] 測試通知..."
	CHAIN=showtimes TEST_NOTIFICATION=1 python3 main.py

test-vieshow:
	@echo "正在強制發送 [威秀] 測試通知..."
	CHAIN=vieshow TEST_NOTIFICATION=1 python3 main.py

test: test-showtimes test-vieshow

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
