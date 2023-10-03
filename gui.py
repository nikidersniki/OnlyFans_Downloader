import eel
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
import os
eel.init('web')

@eel.expose
def search(name, site):
    eel.removeold()
    print(site)
    site = int(site)*50
    print (site)
    if site>0:   
        url = "https://coomer.su/onlyfans/user/"+name+"?o=" + str(site)
    else:
        url = "https://coomer.su/onlyfans/user/"+name
    print(url)
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Failed to retrieve Page")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    posts = soup.find('div', class_='card-list__items')
    post = posts.find_all('article')
    for num in post:
        text = num.find('header', class_='post-card__header')
        img_element = num.find('img', class_='post-card__image')
        date = num.find('time', class_='timestamp')
        if text is not None and img_element is not None:
            text = text.text
            img_url = img_element.get('src')
            postid = num.get('data-id')
            datetime = date.get('datetime')
            eel.createPost(text, img_url, postid, datetime)
@eel.expose 
def download(pid, usr, date):
    mdate = "-".join(date.split())
    mdate = mdate.replace(":", "")
    mdate = mdate.replace("-", "")
    print(pid, usr, mdate)
    url = "https://coomer.su/onlyfans/user/" + usr + "/post/" + pid + "/"
    if not os.path.exists("files/" + usr):
        os.makedirs("files/" + usr)
    if not os.path.exists("files/" + usr + "/"+mdate):
        os.makedirs("files/" + usr+"/"+mdate)
    for _ in range(3):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                break 
        except RequestException as e:
            print(f"Request failed: {e}")
    
    if response.status_code != 200:
        print("Failed to retrieve the image.")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    post = soup.find_all('div', class_='post__thumbnail')
    
    for files in post:
        img_tag = files.find('img')

        if img_tag is not None:
            img_url = img_tag.get('data-src')
            img_url = img_url[2:]
            img_url = "https://"+img_url
            img_file_name = os.path.basename(img_url)
            
            file_name = os.path.join("files/" + usr + "/" + mdate + "/", img_file_name)
            
            with open(file_name, 'wb') as file:
                file.write(requests.get(img_url).content)
            
            print(f"Downloaded: {img_file_name}")
        else:
            print("Image not found in post")
    print("Download Finished")
@eel.expose
def downloadAll(usr):
    url = "https://coomer.su/onlyfans/user/"+usr
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Failed to retrieve Page")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    posts = soup.find('div', class_='card-list__items')
    post = posts.find_all('article')
    for num in post:
        text = num.find('header', class_='post-card__header')
        img_element = num.find('img', class_='post-card__image')
        date = num.find('time', class_='timestamp')
        if text is not None and img_element is not None:
            text = text.text
            postid = num.get('data-id')
            datetime = date.get('datetime')
            download(postid, usr, datetime)
    print("Downloaded Finished")
eel.start('index.html')