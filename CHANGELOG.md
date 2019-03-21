# 日志
## 19.3.21  
* 由于Google chrome更新，导致打包后chromedriver时不时抛出异常说不支持浏览器版本（73.0.3683.86），所以用chromedriver73和chromedriver74分别打包两个程序（run_73.exe和run_74.exe），但是最后测试时两个都能用，无异常🤬  
* 打包程序已经将chromedriver.exe打包进run_\*.exe，本人测试成功，所以理论上不用下载chromedriver.exe  
* 目前正在改进代码，但是由于激进地对网页源代码进行删改（因为能简化代码，减少维护复杂），导致遇到复杂问题，现在也只是临时方法解决  
## 19.3.20  
* 成品.exe文件更名为run.exe，理论上将chromedriver.exe打包进run.exe  
## 19.3.20  
* 发现打包的程序在别的电脑不能运行，大概是没有装好环境，所以就删除了程序😅
* 用浏览器时看到了油猴插件，于是打算写一个js脚本，先开个坑吧，也不一定会写，我也不是学编程的  
## 19.3.19
* 又简化了一下代码
* code.py改为run.py，直观明了
* 更新把自己更新烦了😓，以后每天尽量只更一次
## 19.3.19  
* 简化代码
* 修改异常页面判断  
增加对不兼容页面的检测，防止进入死循环不断判断页面类型  
## 19.3.17 
* 浏览器可以无窗口运行  
YXY的“plugins.js”脚本会检测浏览器的navigator.userAgent，如果不正常会返回异常页面：https://ua.ulearning.cn/learnCourse/compatibility.html
* 修改一处逻辑错误
## 19.3.16
* 上传第一份
