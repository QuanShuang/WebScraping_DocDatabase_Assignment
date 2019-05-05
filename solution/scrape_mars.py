#!/usr/bin/env python
# coding: utf-8


# Import dependencies
import os
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    
    #create a dictionary to store scraped data
    mars_data={}

    # use splinter to visit news page
    url_news = "https://mars.nasa.gov/news/"
    browser.visit(url_news)

    # create BS object to scrape from
    html_news=browser.html
    soup_news=bs(html_news,'lxml')

    #scrape the latest news title and article paragraph
    news_title=soup_news.find('div',class_="content_title").text
    news_p=soup_news.find('div',class_="article_teaser_body").text
    
    #store result into scraped_data
    mars_data["news_title"]=news_title
    mars_data["news_p"]=news_p

    # use splinter to visit JPL page
    url_jpl = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_jpl)

    # create BS object to scrape from
    html_jpl=browser.html
    soup_jpl=bs(html_jpl,'html.parser')

    # create scrape_link from Chrome inspector
    scrape_link=soup_jpl.find('div',class_="carousel_items").a["data-fancybox-href"]

    # base link is different from url_jpl (open the real link to find out)
    base_link="https://www.jpl.nasa.gov"
    featured_image_url=base_link+scrape_link
    
    #store result into scraped_data
    mars_data["featured_image_url"]=featured_image_url

    #https://dev.to/ayushsharma/
    #a-guide-to-web-scraping-in-python-using-beautifulsoup-1kgo
    # referred to above page for method
    url_mwt = "https://twitter.com/marswxreport?lang=en"
    data=requests.get(url_mwt)

    # use select to parse html into timeline
    html_mwt=bs(data.text,'html.parser')
    all_tweets=[]
    timeline=html_mwt.select('#timeline li.stream-item')

    # iterate through each tweet and convert text we want into dictionary
    for tweet in timeline:
        tweet_text=tweet.select('p.tweet-text')[0].get_text()
        all_tweets.append({'text':tweet_text})
    print(f"we have scraped: {len(all_tweets)} tweets")

    mars_weather = all_tweets[0]['text'][0:-26]
    # Remove last picture url by using [:] 
    # because it's the same len of character each time
    mars_data["weather"]=mars_weather

    # use read_html to read table from html to pandas
    url_fact = "https://space-facts.com/mars/"
    tables=pd.read_html(url_fact)
    
    # rename columns
    df_fact=tables[0]
    # df=df.columns=["Parameter","Value"]
    df_fact.columns = ['Description','Value']

    # convert table into html table ready to be used
    html_fact=df_fact.to_html(header=True,index=False,justify='center')
    html_fact=html_fact.replace('\n', '')

    #store result into scraped_data      
    mars_data["html_fact"]=html_fact


    # use splinter to visit Hemisphere page
    url_hemi = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_hemi)

    # create BS object to scrape from
    html_hemi=browser.html
    soup_hemi=bs(html_hemi,'html.parser')

    # find all "item" containing links
    scrape_hemis=soup_hemi.find_all('div', class_="item")


    # construct links using base_url_hemi and store into a list
    base_url_hemi='https://astrogeology.usgs.gov'
    link_hemis=[]
    for hemi in scrape_hemis:
        link_hemis.append(base_url_hemi+hemi.a['href'])
    print(f"There are totally {len(link_hemis)} links")


    #loop through the list of links to extract title and img links
    hemisphere_image_urls=[]
    for link in link_hemis:
        browser.visit(link)
        soup_img=bs(browser.html,'html.parser')
        img_title=soup_img.find('h2',class_="title").text
        img_url=soup_img.find('div',class_='downloads').ul.a["href"]
        hemisphere_image_urls.append({"title":img_title, "img_url":img_url})

    #store result into scraped_data      
    mars_data["hemisphere_image_urls"]=hemisphere_image_urls


    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data


if __name__ == "__main__":
	scrape()
