import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def select_all_time_option(top_songs):
    top_songs.find_element(By.XPATH, "//div[@class='SquareManySelects__Container-sc-1kktot3-1 dqbVnf']").click()
    sleep(5)
    top_songs.find_element(By.XPATH, "//div[contains(@class, 'SquareSelectOption__Container-h4rr3o-0') and contains(text(), 'All Time')]").click()
    sleep(5) # wait for page to load

def load_more_songs(top_songs):
    while True:
        try:
            button = top_songs.find_element(By.XPATH, ".//div[@class='SquareButton-sc-109lda7-0 gsoAZX']")
            button.click()
            sleep(7)
        except NoSuchElementException:
            # If no more "Load More" button found, exit the loop
            break

def scrape_top_songs(top_songs):
    df = pd.DataFrame(columns=["Song Name", "Artist", "Number of Views","lyrics link"])
    elements = top_songs.find_elements(By.XPATH, ".//a[@class='PageGriddesktop-hg04e9-0 ChartItemdesktop__Row-sc-3bmioe-0 qsIlk']")
    
    for element in elements:
        href = element.get_attribute("href")
        song_name = element.find_element(By.XPATH,".//div[@class='ChartSongdesktop__Title-sc-18658hh-3 fODYHn']").text
        artist = element.find_element(By.XPATH,".//h4[@class='ChartSongdesktop__Artist-sc-18658hh-5 kiggdb']").text
        number_of_views = element.find_element(By.XPATH, ".//div[@class='ChartSongdesktop__Metadatum-sc-18658hh-7 jfdPdw']//span[@class='TextLabel-sc-8kw9oj-0 knRXtG']").text
        
        # Append the record to the DataFrame
        df.loc[len(df)] = [song_name, artist, number_of_views, href]
        
    #return the dataframe
    return(df)

def scrap_song_lyrics(driver, url):
    driver.get(url)
    sleep(10)
    lyrics_div = driver.find_elements(By.XPATH, "//*[@id='lyrics-root']/div[@class='Lyrics__Container-sc-1ynbvzw-1 kUgSbL']")
    
    lyrics_text = "" # initialize a string to save lyrics
        
    for lyrics_container in lyrics_div: 
        lyrics_text += lyrics_container.text # append lyrics from lyrics containers
    
    return lyrics_text

if __name__ == '__main__':
    
    url = "http://genius.com/" #prepare the url
    driver = webdriver.Chrome() #set up the driver
    driver.get(url) #load the page 
    print(f"getting page {url}")
    sleep(10)
    
    # select top songs division
    top_songs = driver.find_element(By.ID, "top-songs")
    
    # select top songs for all time (there are other options)
    select_all_time_option(top_songs)
 
    # load more songs until there are no more
    load_more_songs(top_songs)

    # After clicking all "Load More" buttons, scrape the page and create the dataframe
    data = scrape_top_songs(top_songs)
    
    # After scraping top songs data, we move now to scrape lyrics individually
    data["lyrics"] = None # initialize a new column to save lyrics 
    
    for i, url in enumerate(data["lyrics link"]):
        
        lyrics_text = scrap_song_lyrics(driver, url) # scrape lyrics using from song url
        data.loc[i,"lyrics"] = lyrics_text # insert lyrics into dataframe
        
        print(i+1,"- lyrics for ",data.loc[i,'Song Name'] ," - ", data.loc[i,"Artist"] , " extracted and added to dataframe" )
    
    # finally save dataframe as CSV file
    data.to_csv("scraped_data.csv", index=False) 

