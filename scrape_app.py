from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
from selenium import webdriver
import os

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/channel" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            youtube_channel_link = "https://www.youtube.com/@" + searchString +"/videos"
            browser = webdriver.Chrome()
            browser.get(youtube_channel_link)
            soup = bs(browser.page_source, 'html.parser')
            finder_1 = soup.find_all('a', {'class':'yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media'})
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Video Description, Number of Views, Number of likes, Number of Comments\n"
            fw.write(headers)
            reviews = []
            for i in finder_1:
                try:
                    video_link = 'https://www.youtube.com/' + i.get('href')
                    browser.get(video_link)
                    soup1 = bs(browser.page_source, 'html.parser')
                    title = soup1.find('yt-formatted-string', {'class': 'style-scope ytd-watch-metadata'}).text
    
                except:
                    logging.info("title")
        
                try:
                    view_count = int(soup1.find('span', {'class':'view-count style-scope ytd-video-view-count-renderer'}).text.split()[0].replace(',',''))
                
                except:
                    logging.info("view_count")

                try:
                    likes_count = int(soup1.find('div', {'class':'factoid style-scope ytd-factoid-renderer'}).text.replace('\n','')[:-6])*1000
                    
                except:
                    logging.info("likes_count")

                try:
                    comments_count = int(soup1.find('span', {'class':'style-scope yt-formatted-string'}).text.replace(',',''))

                except:
                    logging.info("comments_count")
            

                mydict = {"Title": title, "Views": view_count, "Likes": likes_count, "Comments": comments_count,
                          }
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            
            client = pymongo.MongoClient("mongodb+srv://ss-shivam097:pwskills123@cluster0.nr95fps.mongodb.net/?retryWrites=true&w=majority")
            db =client['youtube_scrape']
            coll_pw_eng = db['scrape_youtube_channel']
            coll_pw_eng.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")