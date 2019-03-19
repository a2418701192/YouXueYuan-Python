from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,re,json,pickle,sys,os,getpass
from collections import OrderedDict
from bs4 import BeautifulSoup
from pathlib import Path

#该程序灵感来源于GitHub的fuck_xuexiqiangguo 项目
#因为以前写过爬虫代码，看到GitHub的项目，于是就浮现了一个想法
#这个程序我已经重写了第三遍，加上这个学期课程满的要死
#并且为了解决网页点击问题，selenium和BeautifulSoup模块都用（主要是有的模块功能不能满足，要用其他模块）
#所以程序有问题我不一定有时间解决
#最后，禁止滥用程序，代码开源、免费

#加载cookies
def Load_cookies():
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        print('cookies加载完成。')
        return True
    except:
        return False

#检查登录状态
def Check_login():
    driver.get('https://www.ulearning.cn/umooc/learner/userInfo.do?operation=studentChangeInfo')
    if driver.page_source.find(username) != -1:
        print('登录状态正常。')
        return True
    else:
        print('登录状态失效。')
        driver.delete_all_cookies()
        return False

#登录
def Login():
    driver.get('https://www.ulearning.cn/ulearning/index.html#/index/portal')
    while True:
        if driver.page_source.find('<div class="login-btn-text" data-bind="click: login, text: publicI18nText.signin">') != -1:
            break
        else:
            try:
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//div[@class="login-btn-text"]')))
                break
            except:
                pass
    while True:
        if driver.page_source.find('<div class="form-title">登录</div>') == -1:
            try:
                driver.find_element_by_xpath('//div[@class="login-btn-text"]').click()
                break
            except:
                pass
        else:
            pass
    while True:
        try:
            driver.find_element_by_id('userLoginName').send_keys(username)
            driver.find_element_by_id('userPassword').send_keys(password)
            driver.find_element_by_xpath('//*[@id="loginForm"]/button').click()
            break
        except:
            pass
    if Check_login() == True:
        pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
        with open('data.json','w') as data:
            data.write(json.dumps({'username':username,'password':password,'headless':headless,'save':save}))
        return True
    else:
        return False

#跳转至课程
def Jump2class():
    driver.get('https://dgut.ulearning.cn/umooc/learner/study.do?operation=catalog')
    while True:
        if driver.page_source.find('<span onclick="changeYear(0);">全部</span>') != -1:
            try:
                driver.find_element_by_xpath('//span[@onclick="changeYear(0);"]').click()
                break
            except:
                pass
        else:
            break

#解析课程
def Analysis_class():
    title_rule = re.compile(r'<h3>(.*?)</h3>')
    schedule_rule = re.compile(r'<span class="progress-pre left">(.*?)</span>')
    url_rule = re.compile(r'<a class="btn-primary btn-coursein title" href="(.*?)">')
    html = driver.page_source.replace('amp;','')
    soup = BeautifulSoup(html,features = "html5lib")
    trees = soup.find_all('div',class_='course-detail left english-course-detail')
    data = OrderedDict()
    count = 0
    for tree in trees:
        title = re.search(title_rule,str(tree)).group(1)
        schedule = re.search(schedule_rule,str(tree)).group(1)
        try:
            url = re.search(url_rule,str(tree)).group(1).replace('amp;','')
        except:
            url = None
        data[str(count)] = OrderedDict()
        data[str(count)]['title'] = title
        data[str(count)]['schedule'] = schedule
        data[str(count)]['url'] = url
        count = count + 1
    return data

#选择课程
def Choose_course():
    all_class = Analysis_class()
    print('\n课程名称：')
    for data in all_class:
        print(str(data) + '.' + all_class[data]['title'])
    choose = input('请选择编号：')
    return all_class[choose]['url']

#选择名称
def Choose_name(url):
    driver.get('https://www.ulearning.cn' + url)
    html = driver.page_source.replace('&nbsp;','')
    soup = BeautifulSoup(html,features = "html5lib")
    trees = soup.find_all('tr',class_='thecuorse')
    title_rule = re.compile(r'<p>(.*?)</p>')
    data = OrderedDict()
    count = 1
    print('')
    print('或者从下面选名称')
    #print('-1.全部从头开始')
    print('0.自动')
    for tree in trees:
        title = str(tree.find('p').get_text()).replace(' ','').replace('\t','').replace('\n','').replace('\r','')
        schedule = str(tree.find('span',class_='progress-pre course-over').get_text()).replace(' ','').replace('\t','').replace('\n','').replace('\r','').replace('&nbsp;','').replace(u'\xa0', u'')
        onclick = re.search(r'<div class="btn-primary title tsize14" onclick="(.*?)">',str(tree)).group(1)
        print(str(count) + '.' + title)
        data[str(count)] = OrderedDict()
        data[str(count)]['title'] = title
        data[str(count)]['schedule'] = schedule
        data[str(count)]['onclick'] = onclick
        count = count + 1
    choose = input('请选择序号：')
    global choose_type
    choose_type = choose
    print('')
    if choose == '-1':
        return data['1']['onclick']
    elif choose == '0':
        for tree in data:
            if data[tree]['schedule'] != '100%':
                return data[tree]['onclick']
            else:
                pass
        return True
    else:
        return data[choose]['onclick']

#点击目录
def Click_name(choose):
    if choose == True:
        print('课程完成。')
        return None
    else:
        driver.find_element_by_xpath('//div[@onclick="' + choose + '"]').click()
        return True

#跳过提示框
def Close_tips():
    while True:
        try:
            driver.find_element_by_xpath("//div[@id='alertModal'][@style='display: block;']")
            try:
                driver.find_element_by_xpath('//button[@data-bind="text: $root.i18nMsgText().gotIt"]').click()
            except:
                try:
                    driver.find_element_by_xpath('//button[@data-bind="text: $root.i18nMsgText().confirmLeave"]').click()
                except:
                    pass
        except:
            try:
                driver.find_element_by_xpath("//div[@id='alertModal'][@class='modal fade in']")
                try:
                    driver.find_element_by_xpath('//button[@data-bind="text: $root.i18nMsgText().gotIt"]').click()
                except:
                    try:
                        driver.find_element_by_xpath('//button[@data-bind="text: $root.i18nMsgText().confirmLeave"]').click()
                    except:
                        pass
            except:
                break

#跳过用户引导
def Close_guid():
    Close_tips()
    while True:
        try:
            driver.find_element_by_xpath("//div[@class='user-guide main'][@style='display: block;']")
            try:
                driver.find_element_by_xpath('//div[@data-bind="click: hideGuide,text: $root.i18nMsgText().skipTips"]').click()
            except:
                try:
                    driver.find_element_by_xpath('//div[@class="close-btn"]').click()
                except:
                    Close_tips()
        except:
            break

#关闭目录
def Close_mune():
    Close_guid()
    while True:
        try:
            driver.find_element_by_xpath("//div[@data-bind='css: { \'return-url\': returnUrl }, click: $root.toggleCatalog'][@class='hide-catalog-btn control-btn cursor']")
            try:
                driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().hideCatalog"]').click()
            except:
                try:
                    driver.find_element_by_xpath('//span[@class="btn-text"]').click()
                except:
                    Close_tips()
                    Close_guid()
        except:
            try:
                driver.find_element_by_xpath("//div[@class='catalog-col full-height']")
                try:
                    driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().hideCatalog"]').click()
                except:
                    try:
                        driver.find_element_by_xpath('//span[@class="btn-text"]').click()
                    except:
                        Close_tips()
                        Close_guid()
            except:
                break

#判断是否视频
def Check_video():
    code = driver.page_source
    if code.find('file-media') != -1:
        print('视频。')
        return True
    elif code.find('doc-canvas') != -1:
        print('可能是PPT')
        return False
    elif code.find('question-view') != -1:
        print('选择题。')
        return False
    elif code.find('哎呀，这个页面没有内容，看看其它页面吧') != -1:
        print('页面不存在。')
        return False
    elif code.find('page-content') != -1:
        print('文章。')
        return False
    elif code.find('<title>浏览器兼容性提示</title>') != -1 or code.find('检测到您在使用旧版或系统不支持的浏览器') != -1:
        return 'error'
    else:
        return None

#调整播放器并播放
def Adjust_player():
    Close_tips()
    Close_guid()
    Close_mune()
    while True:
        if driver.page_source.find('title="Pause" aria-label="Pause" tabindex="0"></button>') == -1 or driver.page_source.find('title="Play" aria-label="Play" tabindex="0"></button>') != -1:
            try:
                element = driver.find_element_by_xpath('//button[@title="Mute"]')
                driver.execute_script("arguments[0].scrollIntoView();", element)
            except:
                Close_tips()
                Close_guid()
                Close_mune()
            try:
                driver.find_element_by_xpath('//button[@title="Mute"]').click()
            except:
                Close_tips()
                Close_guid()
                Close_mune()
            try:
                speed = re.search("mep_(\d+)-speed-1.50",driver.page_source).group(0)
                driver.find_element_by_xpath('//button[@title="Speed Rate"]').click()
                driver.find_element_by_xpath('//label[@for="' + speed + '"]').click()
            except:
                Close_tips()
                Close_guid()
                Close_mune()
            try:
                driver.find_element_by_xpath('//button[@title="Play"]').click()
            except:
                Close_tips()
                Close_guid()
                Close_mune()
        else:
            break
            

#判断视频是否完成
def Check_done():
    while True:
        Click_next()
        if driver.page_source.find('<span data-bind="text: $root.i18nMessageText().finished">已看完</span>') == -1:
            progress = re.search(r'<span data-bind="text: pageElement.record\(\).viewProgress\(\)">(\d+).(\d+)</span>',driver.page_source)
            if not progress:
                Adjust_player()
            else:
                print('\r',"当前视频进度：" + progress.group(1) + "." + progress.group(2) + "%",end='',flush=True)
                time.sleep(1)
        else:
            print('\r',"视频完成。              ")
            break

#下一页
def Next_page():
    Close_mune()
    while True:
        try:
            driver.find_element_by_xpath('//div[@data-bind="click: goNextPage"]').click()
            break
        except:
            pass
    return Click_next()

def Click_next():
    Close_tips()
    Close_guid()
    Close_mune()
    if driver.page_source.find('<span data-bind="text: i18nMessageText().nextChapter">继续下一章</span>') != -1:
        if choose_type == '-1' or choose_type == '0':
            print('\n下一章。\n')
            while True:
                try:
                    driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().nextChapter"]').click()
                except:
                    pass
                if driver.page_source.find('<span data-bind="text: i18nMessageText().nextChapter">继续下一章</span>') != -1:
                    continue
                else:
                    break
            return True
        else:
            print('\n本章结束。\n')
            while True:
                try:
                    driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().stayHere"]').click()
                except:
                    pass
                if driver.page_source.find('<span data-bind="text: i18nMessageText().stayHere">留在本页</span>') != -1:
                    continue
                else:
                    break
            return False
    elif driver.page_source.find('<span data-bind="text: i18nMessageText().close">关闭</span>') != -1:
        print('课程结束。')
        while True:
            try:
                driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().close"]').click()
            except:
                pass
            if driver.page_source.find('<span data-bind="text: i18nMessageText().close">关闭</span>') != -1:
                continue
            else:
                break
        return False
    elif driver.page_source.find('本页面还有题目没有完成，') != -1:
        Close_tips()
        if driver.page_source.find('<span data-bind="text: i18nMessageText().nextChapter">继续下一章</span>') != -1:
            if choose_type == '-1' or choose_type == '0':
                print('\n下一章。\n')
                while True:
                    try:
                        driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().nextChapter"]').click()
                    except:
                        pass
                    if driver.page_source.find('<span data-bind="text: i18nMessageText().nextChapter">继续下一章</span>') != -1:
                        continue
                    else:
                        break
                return True
            else:
                print('\n本章结束。\n')
                while True:
                    try:
                        driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().stayHere"]').click()
                    except:
                        pass
                    if driver.page_source.find('<span data-bind="text: i18nMessageText().stayHere">留在本页</span>') != -1:
                        continue
                    else:
                        break
                return False
        else:
            return True
    else:
        return True

#返回章节
def Exit_chapter():
    while True:
        try:
            driver.find_element_by_xpath('//span[@data-bind="text: i18nMessageText().backToCourse"]').click()
            break
        except:
            try:
                driver.find_element_by_xpath('//span[@class="back btn-text"]').click()
                break
            except:
                try:
                    driver.find_element_by_xpath('//div[@class="back-btn control-btn cursor"]').click()
                    break
                except:
                    try:
                        driver.find_element_by_xpath('//div[@data-bind="css: { \'return-url\': returnUrl }, click: $root.goBack"]').click()
                        break
                    except:
                        pass

#更新数据
def Updata():
    #是否隐藏窗口
    headless = input('是否隐藏窗口（Y/n）：')
    if headless == 'y' or headless == 'Y':
        headless = True
    else:
        headless = False
    save = input('是否保存该设置（Y/n）：')
    if save == 'y' or save == 'Y':
        save = True
    else:
        save = False
    with open('data.json','w') as data:
        data.write(json.dumps({'username':username,'password':password,'headless':headless,'save':save}))

if __name__ == '__main__':
    #准备登录信息
    try:
        with open('.\data.json','r') as data:
            data = json.loads(data.read())
            username = data['username']
            password = data['password']
            try:
                save = data['save']
                headless = data['headless']
                if save == True:
                    pass
                else:
                    Updata()
            except:
                Updata()
    except:
        username = input('账号：')
        password = getpass.getpass('密码（光标不可见）：')
        Updata()
    #准备chrome
    chrome_options = webdriver.ChromeOptions()
    if headless == True:
        chrome_options.add_argument('--headless')
    else:
        pass
    #我也不确定是啥，但是我这里要这条才能用headless模式
    chrome_options.add_argument('--disable-gpu')
    #静音
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('log-level=3')
    #我也不知道设置多少最好，只是为了所有元素都一页显示、不用滚动条，虽然程序已经可以定位到元素再点击
    chrome_options.add_argument('--window-size=4000,2000')
    chrome_options.add_argument('--window-position=800,0')
    #设置navigator.userAgent，优学院检测navigator.userAgent，如果不正常会返回异常页面：https://ua.ulearning.cn/learnCourse/compatibility.html
    #检测的js脚本是“plugins.js”
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36")
    chromedriver = Path(".\chromedriver.exe")
    if not chromedriver.is_file():
        input('chromedriver.exe文件找不到，请将chromedriver.exe放至程序同目录下。\n回车结束。')
        sys.exit()
    driver = webdriver.Chrome(chrome_options=chrome_options,executable_path = '.\chromedriver.exe')
    driver.get('https://www.ulearning.cn/ulearning/index.html#/index/portal')
    
    if Load_cookies() == True:
        if Check_login() == True:
            print('登录成功。')
        else:
            if Login() == True:
                print('登录成功。')
            else:
                input ('登录失败，回车退出。')
                driver.quit()
                sys.exit()
    else:
        if Login() == True:
            print('登录成功。')
        else:
            input('登录失败，回车退出。')
            driver.quit()
            sys.exit()
    while True:
        Jump2class()
        url = Choose_course()
        choose_name = Choose_name(url)
        click_name = Click_name(choose_name)
        if click_name == True:
            while True:
                Close_tips()
                Close_guid()
                Close_mune()
                check_video = Check_video()
                if check_video == True:
                    Adjust_player()
                    Check_done()
                elif check_video == False:
                    if Next_page() == True:
                        Click_next()
                        continue
                    else:
                        break
                elif check_video == 'error':
                    print('不兼容，可能检测到异常\n请尝试有界面浏览器（打开data.json文件将“"headless": true”改为“"headless": false”）')
                    input('回车退出')
                    sys.exit()
                else:
                    print('未知类型。')
                if Next_page() == True:
                    continue
                else:
                    break
            Exit_chapter()
        else:
            pass
        carry = input('是否继续（Y/n）：')
        if carry == 'y' or carry == 'Y':
            pass
        else:
            driver.quit()
            break

