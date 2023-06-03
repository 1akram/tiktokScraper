from selenium import webdriver
from webdriver_manager .chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
import os
import pyperclip
from selenium.webdriver.common.action_chains import ActionChains
import random

sleepTime=4
def findElement(chromeBrowser, by, value, click=False):
 
    while True:
       
        try:
            elem = chromeBrowser.find_element(by, value)
            if click:
                try:
                    chromeBrowser.execute_script("arguments[0].click();", elem)
                    break
                except Exception as e:
                    return None

            return elem
        except Exception as e:

            return None


def nextVideo(chromeBrowser):
    elem=findElement(chromeBrowser,'xpath','//button[@data-e2e="arrow-right"]',True)
    return elem

def copyLink(chromeBrowser,elem):
    actions = ActionChains(chromeBrowser)
    actions.context_click(elem).perform()
    sleep(sleepTime)
    findElement(chromeBrowser,'xpath',"//div[@id='app']/ul/li[3]",True)
    sleep(sleepTime)
    return pyperclip.paste()

def downloadVideo(chromeBrowser,src,dest):
    jsCode="""
    function downloadVideo(url,downloadPath) {
        fetch(url)
        .then(response => response.blob())
        .then(blob => {
        const videoUrl = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = videoUrl;
        anchor.download = downloadPath; 
        anchor.click();
        URL.revokeObjectURL(videoUrl);
        })
        .catch(error => {
        console.error('Error downloading the video:', error);
        reject(error.toString());
        });
    }
    
        downloadVideo('"""+src+"""','""" +dest+"""');
        """ 
    return chromeBrowser.execute_script(jsCode)



def extractVideoId(url):
    url_parts = url.split('/')
    url_parts= url_parts[-1]
    url_parts=url_parts.split('?')
    return url_parts[0]

def extractVideoTime(chromeBrowser):
    elem=findElement(chromeBrowser,'css selector','div.tiktok-1jb9u83-DivSeekBarTimeContainer.esk3vjb1')
    if(elem !=None):
        timeText=elem.text # time is current time : all time 
        time=timeText.split('/')
        time=time[-1]
        minutes, seconds = map(int, time.split(':'))
        totalSeconds = minutes * 60 + seconds
        return totalSeconds

    return sleepTime

def newTab(chromeBrowser):
    originalWindow = chromeBrowser.current_window_handle
    windowHandles = chromeBrowser.window_handles
    print(len(windowHandles))
    if len(windowHandles) == 1:
       chromeBrowser.execute_script("window.open();")
    chromeBrowser.switch_to.window(chromeBrowser.window_handles[-1])
    return originalWindow

def initChrome(lang='en,fr', windowSize='1280,720', userDataDir=None, chromedriver=None, userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', profile='Person 1'):
   
    option = webdriver.ChromeOptions()
    option.add_argument("--lang="+lang)
    option.add_argument("--window-size="+windowSize)
    option.add_argument('--disable-blink-features=AutomationControlled')

  #  option.add_argument("--user-data-dir="+userDataDir)
    option.add_argument("--profile-directory="+profile)
    option.add_argument("user-agent="+userAgent)
    option.add_argument("Referer=https://www.leboncoin.fr/")
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    if not chromedriver:  # if driver not set it will use driver manager
        chromeBrowser = webdriver.Chrome(
            ChromeDriverManager().install(), options=option)
    else:
        chromeBrowser = webdriver.Chrome(executable_path=str(
            os.getcwd())+'/driver/'+chromedriver, options=option)
    
    return chromeBrowser
def getUserDataDir():
    try:
        return os.getenv('APPDATA').replace('Roaming', 'Local\\Google\\Chrome\\User Data\\')
    except:
        return None
 
targetWebSite = 'https://www.tiktok.com/'
chromedriver = 'chromedriver13.exe'

chromeBrowser = initChrome(

            profile="Person 1" ,userDataDir=getUserDataDir(),chromedriver=chromedriver  )
chromeBrowser.get(targetWebSite)
sleep(sleepTime)
 
elem =findElement(chromeBrowser,'css selector','div[data-e2e="recommend-list-item-container"] video',False)
if(elem!=None):
    videoUrl = copyLink(chromeBrowser,elem)
    sleep(random.randint(3, 10))
    chromeBrowser.get(videoUrl)
    while True:

        videoUrl=chromeBrowser.current_url
        videoId=extractVideoId(videoUrl)
        print(videoId)
        videoElement=None
        while videoElement == None:
            videoElement=findElement(chromeBrowser,'css selector','div[id$="'+videoId+'"] video')
            if(videoElement !=None):
                videoSrc=videoElement.get_attribute('src')
                print('get src')

        videoTime=extractVideoTime(chromeBrowser)
        while videoTime ==0:
            sleep(1)
            videoTime=extractVideoTime(chromeBrowser)

        sleepBeforeNextVideo=random.randint(int(videoTime/2),int(videoTime*3/4))
        print(sleepBeforeNextVideo)
        videoElement.click()#pause
        sleep(sleepTime)
        originalWindow=newTab(chromeBrowser)
        
        sleep(sleepTime)
        chromeBrowser.get('https://v16-webapp-prime.tiktok.com/')
        result= downloadVideo(chromeBrowser,videoSrc,'v.mp4')
        if isinstance(result, str) and result.startswith("Error"):
            print("Error occurred:", result)
        sleep(sleepTime)
        chromeBrowser.switch_to.window(originalWindow)
        sleep(sleepTime)
        videoElement.click() # continue
        sleep(sleepBeforeNextVideo)
  
        nextVideo(chromeBrowser)
 


else:
    print('none')

    
sleep(3303)