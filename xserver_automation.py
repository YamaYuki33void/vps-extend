import os
import time
import logging
import traceback
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# 1. 設定情報 (GitHub Actions用)
# ==========================================
LOGIN_URL = "https://secure.xserver.ne.jp/xapanel/login/xserver/"
# GitHub ActionsのSecretsから取得するように変更
MEMBER_ID = os.environ.get("XSERVER_ID")
PASSWORD = os.environ.get("XSERVER_PASS")

log_file = os.path.join(os.path.dirname(__file__), "automation.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
)

def log(message):
    logging.info(message)

def wait_humanly(min_sec=2, max_sec=5):
    """人間らしいランダムな待ち時間を挟む"""
    sec = random.uniform(min_sec, max_sec)
    time.sleep(sec)

# ==========================================
# 2. ブラウザの設定
# ==========================================
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# サーバー（GitHub Actions）環境で動かすための必須設定
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# 録画を行う場合は --headless を付けない（仮想ディスプレイ上で描画させるため）

driver = webdriver.Chrome(options=options)

# navigator.webdriver の隠蔽
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
    """
})

wait = WebDriverWait(driver, 20)
current_step = "開始準備"

try:
    if not MEMBER_ID or not PASSWORD:
        raise ValueError("環境変数 XSERVER_ID または XSERVER_PASS が設定されていません。")

    log("=== 対策版プロセス開始 ===")

    # --- 1. ログイン ---
    current_step = "ログインページアクセス"
    driver.get(LOGIN_URL)
    wait_humanly(3, 6)

    current_step = "ログイン情報の入力"
    wait.until(EC.visibility_of_element_located((By.ID, "memberid"))).send_keys(MEMBER_ID)
    wait_humanly(1, 2)
    driver.find_element(By.ID, "user_password").send_keys(PASSWORD)
    wait_humanly(1, 3)
    
    current_step = "ログインボタンのクリック"
    driver.find_element(By.NAME, "action_user_login").click()
    log("ログイン完了。")
    wait_humanly(5, 8)

    # --- 2. サービス管理 ---
    current_step = "サービス管理メニューの展開"
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "serviceNav__toggle"))).click()
    wait_humanly(2, 3)

    current_step = "VPSリンクのクリック"
    wait.until(EC.element_to_be_clickable((By.ID, "ga-xsa-serviceNav-xvps"))).click()
    wait_humanly(5, 7)

    # --- 3. 契約詳細への移動 ---
    current_step = "三点リーダーのクリック"
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "contract__menu"))).click()
    wait_humanly(2, 3)

    current_step = "「契約情報」リンクのクリック"
    info_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '契約情報')]")))
    driver.execute_script("arguments[0].click();", info_link)
    wait_humanly(4, 6)

    # --- 4. 更新手続き ---
    current_step = "「更新する」ボタンのクリック"
    update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '更新する')]")))
    driver.execute_script("arguments[0].click();", update_btn)
    wait_humanly(3, 5)

    current_step = "継続利用確定ボタンのクリック"
    continue_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.freeVpsBtn")))
    driver.execute_script("arguments[0].click();", continue_btn)
    
    log("=== 全工程を正常に完了しました ===")

except Exception:
    error_msg = traceback.format_exc()
    logging.error(f"【失敗】ステップ: {current_step}\n内容: {error_msg}")
    log(f"エラー発生時のURL: {driver.current_url}")

finally:
    log("ブラウザを終了します。")
    wait_humanly(2, 5)
    driver.quit()