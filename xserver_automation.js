const { Builder, By, Key, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const fs = require('fs');

async function log(message) {
    const timestamp = new Date().toISOString();
    const msg = `${timestamp} [INFO] ${message}\n`;
    console.log(msg.trim());
    fs.appendFileSync('automation.log', msg);
}

function waitHumanly(min = 2000, max = 5000) {
    const ms = Math.floor(Math.random() * (max - min + 1) + min);
    return new Promise(resolve => setTimeout(resolve, ms));
}

(async function run() {
    const options = new chrome.Options();
    
    // 対策：自動操作フラグの隠蔽
    options.addArguments('--disable-blink-features=AutomationControlled');
    options.excludeSwitches('enable-automation');
    options.addArguments('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Actions環境用
    options.addArguments('--no-sandbox');
    options.addArguments('--disable-dev-shm-usage');

    let driver = await new Builder()
        .forBrowser('chrome')
        .setChromeOptions(options)
        .build();

    let currentStep = "開始準備";

    try {
        log("=== Node.js プロセス開始 ===");

        const id = process.env.XSERVER_ID;
        const pass = process.env.XSERVER_PASS;

        if (!id || !pass) throw new Error("環境変数が設定されていません。");

        // 1. ログイン
        currentStep = "ログインページアクセス";
        await driver.get("https://secure.xserver.ne.jp/xapanel/login/xserver/");
        await waitHumanly(3000, 6000);

        currentStep = "ログイン情報の入力";
        await driver.wait(until.elementLocated(By.id('memberid')), 20000).sendKeys(id);
        await waitHumanly(1000, 2000);
        await driver.findElement(By.id('user_password')).sendKeys(pass);
        await waitHumanly(1000, 3000);

        currentStep = "ログインボタンクリック";
        await driver.findElement(By.name('action_user_login')).click();
        log("ログイン完了。");
        await waitHumanly(5000, 8000);

        // 2. サービス管理
        currentStep = "VPSメニュー展開";
        const navToggle = await driver.wait(until.elementLocated(By.className('serviceNav__toggle')), 20000);
        await navToggle.click();
        await waitHumanly(2000, 3000);

        await driver.wait(until.elementLocated(By.id('ga-xsa-serviceNav-xvps')), 20000).click();
        await waitHumanly(5000, 7000);

        // 3. 契約詳細
        currentStep = "三点リーダーのクリック";
        await driver.wait(until.elementLocated(By.className('contract__menu')), 20000).click();
        await waitHumanly(2000, 3000);

        currentStep = "契約情報リンククリック";
        const infoLink = await driver.wait(until.elementLocated(By.xpath("//a[contains(text(), '契約情報')]")), 20000);
        await driver.executeScript("arguments[0].click();", infoLink);
        await waitHumanly(4000, 6000);

        // 4. 更新
        currentStep = "更新ボタンクリック";
        const updateBtn = await driver.wait(until.elementLocated(By.xpath("//a[contains(text(), '更新する')]")), 20000);
        await driver.executeScript("arguments[0].click();", updateBtn);
        await waitHumanly(3000, 5000);

        currentStep = "継続確定ボタンクリック";
        const continueBtn = await driver.wait(until.elementLocated(By.css('button.freeVpsBtn')), 20000);
        await driver.executeScript("arguments[0].click();", continueBtn);

        log("=== 全工程を正常に完了しました ===");

    } catch (error) {
        log(`【失敗】ステップ: ${currentStep}\nエラー: ${error.message}`);
        const url = await driver.getCurrentUrl();
        log(`エラー発生時のURL: ${url}`);
    } finally {
        log("ブラウザを終了します。");
        await waitHumanly(2000, 5000);
        await driver.quit();
    }
})();