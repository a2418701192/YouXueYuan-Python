from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,re,json,pickle,sys,os,getpass
from collections import OrderedDict
from bs4 import BeautifulSoup
from pathlib import Path

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
        try:
            driver.find_element_by_xpath('//div[@class="btn-login"]').click()
            break
        except:
            pass
    while True:
        try:
            driver.find_element_by_id('userLoginName').send_keys(username)
            driver.find_element_by_id('userPassword').send_keys(password)
            driver.find_element_by_xpath('//button[@class="button button-red-solid btn-confirm"]').click()
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
                #改用调用js代码，以免无法点击
                driver.execute_script("changeYear(0);")
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
        onclick = re.search(r'<div class="btn-primary title tsize14" onclick="javascript:(.*?)">',str(tree)).group(1)
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
        #改用调用js代码，以免无法点击
        driver.execute_script(choose)
        return True

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
        input()
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
    while True:
        if driver.page_source.find('title="Pause" aria-label="Pause" tabindex="0"></button>') == -1 or driver.page_source.find('title="Play" aria-label="Play" tabindex="0"></button>') != -1:
            try:
                driver.find_element_by_xpath('//button[@title="Play"]').click()
            except:
                pass
        else:
            break
            

#判断视频是否完成
def Check_done():
    while True:
        html = driver.page_source
        if html.find('<span data-bind="text: $root.i18nMessageText().finished">已看完</span>') == -1:
            progress = re.search(r'<span data-bind="text: pageElement.record\(\).viewProgress\(\)">(\d+).(\d+)</span>',html)
            if not progress:
                Adjust_player()
            else:
                print("\r当前视频进度：" + progress.group(1) + "." + progress.group(2) + "%",end='',flush=True)
                time.sleep(1)
        else:
            print('\r',"视频完成。              ")
            break

#下一页
def Next_page():
    global title
    try:
        element = driver.find_element_by_xpath("//div[@class='user-guide']")
        driver.execute_script("""
var element = arguments[0];
element.parentNode.removeChild(element);
""", element)
    except:
        pass

    try:
        element = driver.find_element_by_xpath("//div[@id='statModal']")
        driver.execute_script("""
var element = arguments[0];
element.parentNode.removeChild(element);
""", element)
    except:
        pass

    if driver.page_source.find('<div class="mobile-next-page-btn" data-bind="click: goNextPage">') == -1:
        print ('课程完成。')
        return None
    else:
        while True:
            try:
                driver.find_element_by_xpath('//div[@class="mobile-next-page-btn"]').click()
                break
            except:
                pass
        while True:
            try:
                soup = BeautifulSoup(driver.page_source,features = "html5lib")
                if title == soup.find('div',class_ = 'course-title small pack-up').string and driver.page_source.find('<div class="mobile-next-page-btn" data-bind="click: goNextPage">') != -1:
                    driver.find_element_by_xpath('//button[@class="btn-hollow"]').click()
                    break
                else:
                    break
            except:
                try:
                    driver.find_element_by_xpath('//div[@class="mobile-next-page-btn"]').click()
                except:
                    pass
        title = soup.find('div',class_ = 'course-title small pack-up').string
        return True

#返回章节
def Exit_chapter():
    driver.find_element_by_xpath('//div[@class="back-btn control-btn cursor"]').click()

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
        pass
    else:
        pass
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=360,740')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
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
                while True:
                    soup = BeautifulSoup(driver.page_source,features = "html5lib")
                    title = soup.find('div',class_ = 'course-title small pack-up').string
                    if not title:
                        pass
                    else:
                        break
                print ("标题：" + title)
                check_video = Check_video()
                if check_video == True:
                    Adjust_player()
                    Check_done()
                elif check_video == False:
                    pass
                elif check_video == 'error':
                    print('不兼容，可能检测到异常\n请尝试有界面浏览器（打开data.json文件将“"headless": true”改为“"headless": false”）')
                    input('回车退出')
                    driver.quit()
                    sys.exit()
                else:
                    #print('未知类型。')
                    pass
                next_page = Next_page()
                if next_page == True:
                    continue
                elif next_page == None:
                    break
                else:
                    #input('未知情况。回车退出。')
                    #sys.exit()
                    pass
            Exit_chapter()
        else:
            pass
        carry = input('是否继续（Y/n）：')
        if carry == 'y' or carry == 'Y':
            pass
        else:
            driver.quit()
            break
