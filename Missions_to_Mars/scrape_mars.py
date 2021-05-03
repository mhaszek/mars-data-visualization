import pandas as pd
import time
import datetime
from bs4 import BeautifulSoup
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager

from config import driver_path

# define function to start browser
def init_browser():
    
    executable_path = {"executable_path": driver_path}
    return Browser("chrome", **executable_path, headless=False)

# define scrape function
def scrape():
    browser = init_browser()
    
    # create mars_data dict that we can insert into mongo
    mars_data = {}
    
    # scrape Mars News
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    
    browser.is_element_present_by_css(".image_and_description_container", 2)
    
    news_html = browser.html
    news_soup = BeautifulSoup(news_html, 'html.parser')
    
    news = news_soup.find(class_="image_and_description_container")
    news_title = news.find(class_="content_title").text
    news_p = news.find(class_="article_teaser_body").get_text()
    
    
    # scrape Mars Featured Image
    mars_image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(mars_image_url)
    
    browser.is_element_present_by_text("FULL IMAGE", 2)
    
    browser.links.find_by_partial_text('FULL IMAGE').click()
    
    image_html = browser.html
    image_soup = BeautifulSoup(image_html, 'html.parser')
    
    image_url = image_soup.find("img", class_="fancybox-image")["src"]
    featured_image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/' + image_url
    
    # scrape Mars Facts
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    df = tables[0]
    df.columns = ['Description', 'Value']
    html_table = df.to_html()
    
    
    # scrape Mars Hemispheres Images
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    
    browser.is_element_present_by_css(".description", 2)
    
    number_of_clicks = len(browser.find_by_css('div[class="description"] a'))
    
    hemisphere_image_urls = []
    
    for i in range(number_of_clicks):
        links = browser.find_by_css('div[class="description"] a')
        links[i].click()
        
        time.sleep(2)
        
        hemisphere_html = browser.html
        hemisphere_soup = BeautifulSoup(hemisphere_html, 'html.parser')
        
        title = hemisphere_soup.find("h2", class_="title").get_text()
        img_url = hemisphere_soup.find("div", class_="downloads").a['href']
        
        hemisphere_dict = {}
        hemisphere_dict["title"] = title
        hemisphere_dict["img_url"] = img_url
        hemisphere_image_urls.append(hemisphere_dict)
        
        browser.visit(hemispheres_url)                  
    
    
    browser.quit()
    
    # scrape Mars Data Table
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    df = tables[0]
    df.columns = ['Name', 'Description']
    def highlight_oddRow(s):
        return ['' if s.name % 2 else 'background-color: #f9f9f9' for v in s]
    html_table = df.style.apply(highlight_oddRow,axis=1).hide_index().render()
    html_table = html_table.replace('\n', '')

    
    # add all results to mars_data dictionary
    mars_data["news_title"] = news_title
    mars_data["news_p"] = news_p
    mars_data["featured_image_url"] = featured_image_url
    mars_data["table"] = html_table
    mars_data["hemispheres"] = hemisphere_image_urls
    mars_data['date'] = datetime.datetime.utcnow()
    
    # return mars data dictionary
    return mars_data
