# https://github.com/mybdye 🌟

import json
import whisper
import base64
import os
import ssl
import time
import urllib
from urllib.parse import quote

import pydub
import pyscreenshot as ImageGrab
import requests
from seleniumbase import SB


def url_open(urlLogin):
    """
    打开登录页面
    :param urlLogin: 登录页面URL
    :return: 是否成功打开页面
    """
    try:
        sb.open(urlLogin)
        sb.assert_element('#email', timeout=30)
        print('[INFO] - 成功访问登录页面')
        return True
    except Exception as e:
        print(f'[ERROR] - 打开登录页面失败: {e}')
        return False


def recaptcha_checkbox():
    try:
        sb.switch_to_frame('[src*="recaptcha.net/recaptcha/api2/anchor?"]')
        print('- switch to frame checkbox')
        checkboxElement = 'span#recaptcha-anchor'
        print('- click checkboxElement')
        sb.click(checkboxElement)
        sb.sleep(4)
        return True
    except Exception as e:
        print('- 👀 def recaptcha_checkbox():', e)
        return False


def recaptcha(audioMP3):
    print('- recaptcha')

    #   预防弹了广告
    # sb.switch_to_window(0)
    # sb.switch_to_frame('[src*="recaptcha.net/recaptcha/api2/anchor?"]')
    status = checkbox_status()
    tryReCAPTCHA = 1
    while status != 'true':
        sb.switch_to_default_content()  # Exit all iframes
        sb.sleep(1)
        sb.switch_to_frame('[src*="recaptcha.net/recaptcha/api2/bframe?"]')
        print('- switch to frame image/audio')
        sb.click("button#recaptcha-audio-button")
        try:
            sb.assert_element('[href*="recaptcha.net/recaptcha/api2/payload/audio.mp3?"]')
            print('- normal')
            src = sb.find_elements('[href*="recaptcha.net/recaptcha/api2/payload/audio.mp3?"]'
                                   )[0].get_attribute("href")
            print('- audio src:', src)
            # download audio file
            urllib.request.urlretrieve(src, audioMP3)
            # mp3_to_wav(audioMP3, audioWAV)
            text = speech_to_text(audioMP3)
            sb.switch_to_window(0)
            sb.switch_to_default_content()  # Exit all iframes
            #sb.assert_element('#email', timeout=20)
            sb.sleep(1)
            sb.switch_to_frame('[src*="recaptcha.net/recaptcha/api2/bframe?"]')
            sb.type('#audio-response', text)
            sb.click('button#recaptcha-verify-button')
            sb.sleep(4)
            sb.switch_to_default_content()  # Exit all iframes
            sb.switch_to_frame('[src*="recaptcha.net/recaptcha/api2/anchor?"]')
            sb.sleep(1)
            status = checkbox_status()

        except Exception as e:
            print('- 💣 recaptcha Exception:', e)
            sb.switch_to_default_content()  # Exit all iframes
            sb.sleep(1)
            sb.switch_to_frame('[src*="recaptcha.net/recaptcha/api2/bframe?"]')
            msgBlock = '[class*="rc-doscaptcha-body-text"]'
            if sb.assert_element(msgBlock):
                print('- 💣 maybe block by google', sb.get_text(msgBlock))
                break
            elif tryReCAPTCHA > 3:
                break
            else:
                tryReCAPTCHA += 1
    if status == 'true':
        print('- reCAPTCHA solved!')
        return True


def login(username, password, loginButton):
    print('- login')
    sb.switch_to_default_content()  # Exit all iframes
    sb.sleep(1)
    sb.type('#email', username)
    sb.type('input[type="password"]', password)
    sb.click(loginButton)
    sb.sleep(6)
    assert '/user' in sb.get_current_url()
    print('- login success')
    dialogRead()
    return True


def checkbox_status():
    print('- checkbox_status')
    statuslist = sb.find_elements('#recaptcha-anchor')
    # print('- statuslist:', statuslist)
    status = statuslist[0].get_attribute('aria-checked')
    print('- status:', status)
    return status


# def mp3_to_wav(audioMP3, audioWAV):
#     print('- mp3_to_wav')
#
#     pydub.AudioSegment.from_mp3(
#         os.getcwd() + audioMP3).export(
#         os.getcwd() + audioWAV, format="wav")
#     print('- mp3_to_wav done')


def speech_to_text(audioMP3):
    print('- speech_to_text')
    model = whisper.load_model("tiny.en")
    result = model.transcribe(audioMP3)
    text = result["text"]
    print('- text:', text)
    return text


def checkin_status(checkinStatus):
    print('- checkin_status')
    status = sb.get_text(checkinStatus)
    print('- status:', status)
    if '已' in status or '再' in status or '明' in status:
        return True, status
    else:
        return False, status
    
def dialogRead():
    print('- dialog read')
    try:
        sb.click('Read')
    except Exception as e:
        print('- 👀 dialog read:', e)


def checkin(checkinButton):
    print('- checkin')
    sb.click(checkinButton)
    print('- checkin clicked')


def traffic_info(urlUser, trafficInfo):
    print('- get traffic')
    sb.open(urlUser)
    assert '/user' in sb.get_current_url()
    dialogRead()
    sb.sleep(2)
    traffic = sb.get_text(trafficInfo)
    print('- traffic:', traffic)
    return traffic


def screenshot(imgFile):
    print('- screenshot')
    # grab fullscreen
    im = ImageGrab.grab()
    # save image file
    im.save(os.getcwd() + '/' + imgFile)
    # sb.save_screenshot(imgFile, folder=os.getcwd())
    print('- screenshot done')
    sb.open_new_window()
    print('- screenshot upload')
    sb.open('http://imgur.com/upload')
    sb.choose_file('input[type="file"]', os.getcwd() + '/' + imgFile)
    sb.sleep(6)
    imgUrl = sb.get_current_url()
    i = 1
    while not '/a/' in imgUrl:
        if i > 3:
            break
        print('- waiting for url... *', i)
        sb.sleep(5)
        imgUrl = sb.get_current_url()
        i += 1
    print('- 📷 img url: %s\n- screenshot upload done' % imgUrl)
    #sb.driver.close()
    return imgUrl


def url_decode(s):
    return str(base64.b64decode(s + '=' * (4 - len(s) % 4))).split('\'')[1]


def push(body):
    print('- body: %s \n- waiting for push result' % body)
    # bark push
    if barkToken == '':
        print('*** No BARK_KEY ***')
    else:
        barkurl = 'https://api.day.app/' + barkToken
        barktitle = 'A-checkin'
        barkbody = quote(body, safe='')
        rq_bark = requests.get(url=f'{barkurl}/{barktitle}/{barkbody}?isArchive=1')
        if rq_bark.status_code == 200:
            print('- bark push Done!')
        else:
            print('*** bark push fail! ***', rq_bark.content.decode('utf-8'))
    # tg push
    if tgBotToken == '' or tgUserID == '':
        print('*** No TG_BOT_TOKEN or TG_USER_ID ***')
    else:
        body = 'A-checkin' + '\n\n' + body
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + tgBotToken + '/sendMessage'
        rq_tg = requests.post(tgurl, data={'chat_id': tgUserID, 'text': body}, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
        if rq_tg.status_code == 200:
            print('- tg push Done!')
        else:
            print('*** tg push fail! ***', rq_tg.content.decode('utf-8'))
    print('- finish!')


##
try:
    urlUserPasswd = os.environ['URL_USER_PASSWD']
except:
    # 本地调试用， without any 'https://' or '/'
    urlUserPasswd = ''
try:
    barkToken = os.environ['BARK_TOKEN']
except:
    # 本地调试用
    barkToken = ''
try:
    tgBotToken = os.environ['TG_BOT_TOKEN']
except:
    # 本地调试用
    tgBotToken = ''
try:
    tgUserID = os.environ['TG_USER_ID']
except:
    # 本地调试用
    tgUserID = ''
##
body = []
# Speech2text
urlSpeech = url_decode('aHR0cHM6Ly9yZXBsaWNhdGUuY29tL29wZW5haS93aGlzcGVy')
# 关闭证书验证
ssl._create_default_https_context = ssl._create_unverified_context

# ikuxx, qsy, xly
loginButtonList = ('button[type="submit"]', 'button[type="button"]')
checkinStatusList = ('[id*="checkin"]', '[class*="card-action"]',
                     '[class*="white font-weight-bold py-3 px-6"]')
checkinButtonList = ('#checkin', 'a[onclick*="checkin()"]')
trafficInfoList = (
    'div.col-lg-3:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)', '#remain',
    '.bg-diagonal-light-success > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')


def process_account(account, i):
    """
    处理单个账户的签到流程
    :param account: 账户信息列表
    :param i: 账户索引
    :return: 处理结果信息
    """
    try:
        urlBase = account[i * 3]
        username = account[i * 3 + 1] 
        password = account[i * 3 + 2]
        
        # 初始化URL和文件路径
        urlLogin = 'https://' + urlBase + '/auth/login'
        urlUser = 'https://' + urlBase + '/user'
        audioMP3 = f"{urlBase.split('.')[-2]}{i + 1}.mp3"
        imgFile = f"{urlBase.split('.')[-2]}{i + 1}.png"
        
        # 根据URL设置页面元素
        if 'ikuuu' in urlBase:
            loginButton, checkinStatus, checkinButton, trafficInfo = loginButtonList[0], checkinStatusList[0], checkinButtonList[1], trafficInfoList[0]
        elif 'qiushiyun' in urlBase:
            loginButton, checkinStatus, checkinButton, trafficInfo = loginButtonList[0], checkinStatusList[1], checkinButtonList[0], trafficInfoList[1]
        elif 'xiaolongyun' in urlBase:
            loginButton, checkinStatus, checkinButton, trafficInfo = loginButtonList[1], checkinStatusList[2], checkinButtonList[0], trafficInfoList[2]
        else:
            raise ValueError(f"不支持的URL: {urlBase}")

        # 执行签到流程
        if url_open(urlLogin):
            if recaptcha_checkbox():
                recaptcha(audioMP3)
            if login(username, password, loginButton):
                status = checkin_status(checkinStatus)
                if not status[0]:
                    checkin(checkinButton)
                sb.sleep(3)
                traffic = traffic_info(urlUser, trafficInfo)
                status = checkin_status(checkinStatus)
                sb.sleep(1)
                return f'账号({i + 1}/{len(account)//3}): [{urlBase.split(".")[-2]}-{username[:3]}***]\n签到状态：{status[1]}\n剩余流量：{traffic}'

    except Exception as e:
        print(f'[ERROR] - 处理账号时发生错误: {e}')
        try:
            imgUrl = screenshot(imgFile)
            return f'账号({i + 1}/{len(account)//3}): [{urlBase.split(".")[-2]}-{username[:3]}***]\n{e}\n{imgUrl}'
        except Exception as img_error:
            print(f'[ERROR] - 截图保存失败: {img_error}')
            return f'账号({i + 1}/{len(account)//3}): [{urlBase.split(".")[-2]}-{username[:3]}***]\n{e}'


with SB(uc=True, pls="none", sjw=True) as sb:
    if urlUserPasswd != '':
        account = urlUserPasswd.split(',')
        accountNumber = len(account) // 3
        print(f'[INFO] - 开始处理{accountNumber}个账号')
        
        results = []
        for i in range(accountNumber):
            print(f'[INFO] - 开始处理第{i+1}个账号')
            result = process_account(account, i)
            if result:
                results.append(result)
            time.sleep(1)
            
        # 拼接并推送结果
        push_body = '\n- - -\n'.join(results)
        push(push_body)
    else:
        print('[ERROR] - 请检查URL_USER_PASSWD环境变量')

# END
