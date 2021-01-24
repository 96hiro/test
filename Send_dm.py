import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import datetime
import pandas as pd
import numpy as np
from logger import set_logger
import sys
####ログイン処理で使用###############################################
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from retry import retry
import traceback
####ログイン処理で使用###############################################


logger = set_logger(__name__)


# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()
    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

# main処理


def main():
    try:
        logger.info("ドライバー起動開始")
        # driverを起動
        if os.name == 'nt': #Windows
            driver = set_driver("chromedriver.exe", False)
        elif os.name == 'posix': #Mac
            driver = set_driver("chromedriver", False)

        logger.info("ドライバー起動成功")
        
        #ログインメソッド呼び出し
        login(driver)
        logger.info("ログイン成功")
    
        #送信設定(Send_Config.csv)を一件ずつ取得する
        df = pd.read_csv('./Send_Config.csv', encoding="utf-8_sig")
        #Pandas空白/空文字列でNaNを置き換える
        df = df.replace(np.nan, '', regex=True)
   
        for i in range(len(df)):
            logger.info("{}個目のURLの送信設定ファイルの読み込み".format(i+1))
            URL = df.iloc[i,0]#指定URL
            Get＿count = df.iloc[i,1]#送信件数
            Sentence = df.iloc[i,2]#メッセージ文章
            Wording = df.iloc[i,3]#所定文言
            cnt = 0#一つのURL内でDMを送信した数をカウント
            page_count = 0#ページ数のカウント
            
            logger.info("***********************************************************************************************************************")
            logger.info("指定URL：{}".format(URL))
            logger.info("指定送信件数：{}".format(Get＿count))
            logger.info("指定送信メッセージ：{}".format(Sentence))
            logger.info("所定文言：{}".format(Wording))
            logger.info("***********************************************************************************************************************")
                
            # #送信指定情報チェック処理
            if URL == "":
                logger.info("指定URLを設定されていませんでした。")
                continue
            elif Get＿count == "":
                logger.info("指定送信件数の設定されていませんでした。")
                continue
            elif Sentence == "":
                logger.info("指定送信メッセージの設定されていませんでした。")
                continue
            Sentence_spt = []
            #メッセージ文を改行コードで分割し、リストへ格納する
            Sentence_spt = Sentence.split('\\n')
            for line in range(len(Sentence_spt)):
                Sentence_spt[line] += '\n'
                
            # print(Sentence_spt)

            #CSVで指定のURL先を開く
            driver.get(URL)
            time.sleep(2)
            #次のページが無くなるまでor指定件数まで繰り返す
            while True:
               
                name_list = []
                name = []
                history = []
                Date＿Time = []
                client_list = []
                logger.info("クライアントへのDM送信処理開始：{}ページ目".format(page_count+1))
                #クライアントプロフィールページへの要素を１ページ分取得
                name_list = driver.find_elements_by_class_name("c-media-client__title")

                #クライアント一覧からそれぞれのプロフィールページへのリンクを取得しリストに格納する
                for a in name_list:
                    # name_list[1].click()
                    #クライアントのプロフィールページへのリンクを格納
                    client_list.append(a.get_attribute("href"))
                    name.append(a.text)
                
                #各プロフィールページからメッセージを入力し、送信する
                for target,target_name in zip(client_list,name):
                    logger.info("クライアント名：{}への送信処理開始".format(target_name))
                    # TargetName = target_name
                    Send_Flg = Search_History(target_name)
                    if Send_Flg == True:
                        logger.info("送信済クライアントのためスキップ")
                        continue
                    if cnt == Get＿count:#送信件数に達したらfor文を抜ける
                        break
                    
                    #プロフィールページへのリンクを開く
                    driver.get(target)
                    logger.info("プロフィールページを開く")
                    time.sleep(3)
                    #プロフィール文章内の所定文字の有無をチェックする
                    keyword = driver.find_element_by_css_selector(".p-profile__section")
                    
                    #所定の文言が指定されている時
                    if Wording != "":
                        
                        #プロフィール文の中に所定の文言が含まれる人にのみメッセージを送信する
                        if(Wording in keyword.text):
                            logger.info("所定文言あり")
                            #メッセージボタンをクリック
                            driver.find_element_by_css_selector('.p-profile__media-action-button').click()
                            time.sleep(2)
                            #メッセージ入力欄の文字を削除
                            driver.find_element_by_css_selector(".css-1eqtq1t").clear()
                            #文章を入力
                            driver.find_element_by_css_selector(".css-1eqtq1t").send_keys(Sentence_spt)
                            time.sleep(2)
                            #送信ボタンをクリック
                            driver.find_element_by_css_selector(".css-1k6q35j").click()
                            logger.info("DM送信成功")
                            time.sleep(2)
                            cnt += 1#送信件数のカウント
                            history.append(target_name)
                            Date＿Time.append(datetime.datetime.now())
                        else:
                            logger.info("所定文言なし")
                    else:#所定の文言が指定されていない時

                        #メッセージボタンをクリック
                        driver.find_element_by_css_selector('.p-profile__media-action-button').click()
                        time.sleep(2)
                        #メッセージ入力欄の文字を削除
                        driver.find_element_by_css_selector(".css-1eqtq1t").clear()
                        #文章を入力
                        driver.find_element_by_css_selector(".css-1eqtq1t").send_keys(Sentence_spt)
                        time.sleep(2)
                        #送信ボタンをクリック
                        driver.find_element_by_css_selector(".css-1k6q35j").click()
                        logger.info("DM送信成功")
                        time.sleep(2)
                        cnt += 1#送信件数のカウント
                        history.append(target_name)
                        Date＿Time.append(datetime.datetime.now())

                #１ページ目の時
                if page_count == 0:

                    #CSVで指定のURL先を開く
                    driver.get(URL)
                else:
                    driver.get(next_page)

                
                #ページ繊維ボタンの要素を取得
                pages = driver.find_elements_by_class_name("pager__item__anchor")
                
                if cnt == Get＿count:#送信件数に達したらwhile文を抜ける
                    logger.info("指定件数に達しています。")
                    logger.info("送信したクライアント名をCSVへ書き込む")
                    #送信したクライアント名を所定ファイル(Send_History.csv)へ記録する
                    write_cvs(history,Date＿Time)
                    logger.info("書き込み成功")
                    
                    break
                elif len(pages) == 0:#次へボタンがなくなったらwhile文を抜ける
                    break
                else:
                    page_count += 1
                    #get_attribute("href")で次へボタンのリンクを取得
                    next_page = pages[page_count].get_attribute("href")
                    #取得したurl先を開く
                    driver.get(next_page)
                    logger.info("次のページへ遷移")
                    
                    #相手側のサーバーに負荷をかけなように2秒間処理を止める
                    time.sleep(2)
                logger.info("送信したクライアント名をCSVへ書き込む")
                #送信したクライアント名を所定ファイル(Send_History.csv)へ記録する
                write_cvs(history,Date＿Time)
                logger.info("書き込み成功")
            logger.info("Send_Historyのインデックス番号を振りなおし開始")
            #上記で追記したファイル(Send_History.csv)のインデックス番号を振り直す
            csv_Sorting()
            logger.info("インデックス番号を振りなおし成功")
    except Exception as e:
            # logging.info('info {} {}' .format('例外発生：',e))
        # print('例外発生'+e)
        logger.info("例外発生：{}" .format(e))
    
    driver.close()
    driver.quit()

#DM送信履歴をCSVへ保存する関数
        
def write_cvs(history,Date＿Time):

    df = pd.DataFrame({"送信済クライアント":history,
        "送信日時":Date＿Time})
    #ファイル存在チェック
    if os.path.isfile('./Send_History.csv'):
       
        df.to_csv('./Send_History.csv', encoding="utf-8_sig", mode='a', header=False, index=True)
    else:
        df.to_csv('./Send_History.csv', encoding="utf-8_sig", mode='a', header=True, index=True)


#送信履歴管理CSVのインデックス番号を0から連番で振り直す関数


def csv_Sorting():

    #Send_History.csvのindex番号を整頓する
    df = pd.read_csv('./Send_History.csv', encoding="utf-8_sig", index_col=0)
    #行数を取得
    # print(len(df))
    #Send_History.csvのインデックス番号を振り直す
    df=df.reset_index(drop=True)
    df.to_csv('./Send_History.csv', encoding="utf-8_sig")

#以前にDMを送信したクライアントかをチェックする関数
    
def Search_History(target_name):

    #ファイル存在確認
    if os.path.isfile('./Send_History.csv'):  
        #CSVの情報を一見ずつ取得する
        df = pd.read_csv('./Send_History.csv', encoding="utf-8_sig")
    
        for i in range(len(df)):

            if target_name == df.iloc[i,1]:  
                print(df.iloc[i,1])#送信したクライアント名
                return True

        return False

#ログイン処理を行う関数


# @retry(tries=3, delay=5)
def login(driver):

    
    # Webサイトを開く
    driver.get("https://www.lancers.jp/user/login")
    logger.info("ログインページの表示成功")
    logger.info("ログイン処理開始")

    #ログイン情報(Login_Info.csv)のデータを取得
    df1 = pd.read_csv('./Login_Info.csv', encoding="utf-8_sig")

    #Pandas空白/空文字列でNaNを置き換える
    df1 = df1.replace(np.nan, '', regex=True)

    user_id = df1["ログインID"]
    pass_word = df1["パスワード"]


    #ログイン情報ファイル設定値チェック
    if len(df1) == 0:
        logger.info("ログイン情報が設定されていません。")
        sys.exit()
    elif user_id[0] == "":
        logger.info("ログインIDが設定されていません。")
        sys.exit()
    elif pass_word[0] == "":
        logger.info("ログインパスワードが設定されていません。")
        sys.exit()

    #入力されたログイン情報をサイトへ書き込む
    driver.find_element_by_id(
        "UserEmail").send_keys(user_id)
    driver.find_element_by_id(
        "UserPassword").send_keys(pass_word)
    #ログインボタンをクリック
    driver.find_element_by_id("form_submit").click()
    time.sleep(1)
    try:
        # サイドバーに[マイページ]のリングが表示されたらログイン成功
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.dashboard-menu'), 'マイページ')
        )
    except:
        logger.info("ログインに失敗しました。ログイン情報を確認してください。")
        sys.exit()
#直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
