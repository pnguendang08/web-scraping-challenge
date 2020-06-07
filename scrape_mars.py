{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "from splinter import Browser\n",
    "from bs4 import BeautifulSoup\n",
    "import pandas as pd\n",
    "import datetime as dt\n",
    "import time\n",
    "import re\n",
    "\n",
    "\n",
    "def scrape_all():\n",
    "\n",
    "    # Initiate headless driver for deployment\n",
    "    #executable_path = {'executable_path': 'chromedriver.exe'}\n",
    "    #browser = Browser('chrome', **executable_path, headless=False)\n",
    "\n",
    "    browser = Browser(\"chrome\", executable_path=\"chromedriver\", headless=True)\n",
    "    news_title, news_paragraph = mars_news(browser)\n",
    "\n",
    "    # Run all scraping functions and store in dictionary.\n",
    "    data = {\n",
    "        \"news_title\": news_title,\n",
    "        \"news_paragraph\": news_paragraph,\n",
    "        \"featured_image\": featured_image(browser),\n",
    "        \"hemispheres\": hemispheres(browser),\n",
    "        \"weather\": twitter_weather(browser),\n",
    "        \"facts\": mars_facts(),\n",
    "        \"last_modified\": dt.datetime.now()\n",
    "    }\n",
    "\n",
    "    # Stop webdriver and return data\n",
    "    browser.quit()\n",
    "    return data\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def mars_news(browser):\n",
    "    url = \"https://mars.nasa.gov/news/\"\n",
    "    browser.visit(url)\n",
    "\n",
    "    # Get first list item and wait half a second if not immediately present\n",
    "    browser.is_element_present_by_css(\"ul.item_list li.slide\", wait_time=0.5)\n",
    "\n",
    "    html = browser.html\n",
    "    news_soup = BeautifulSoup(html, \"html.parser\")\n",
    "\n",
    "    try:\n",
    "        slide_elem = news_soup.select_one(\"ul.item_list li.slide\")\n",
    "        news_title = slide_elem.find(\"div\", class_=\"content_title\").get_text()\n",
    "        news_p = slide_elem.find(\n",
    "            \"div\", class_=\"article_teaser_body\").get_text()\n",
    "\n",
    "    except AttributeError:\n",
    "        return None, None\n",
    "\n",
    "    return news_title, news_p\n",
    "\n",
    "\n",
    "\n",
    "\n",
    "def hemispheres(browser):\n",
    "\n",
    "    # A way to break up long strings\n",
    "    url = (\n",
    "        \"https://astrogeology.usgs.gov/search/\"\n",
    "        \"results?q=hemisphere+enhanced&k1=target&v1=Mars\"\n",
    "    )\n",
    "\n",
    "    browser.visit(url)\n",
    "\n",
    "    # Click the link, find the sample anchor, return the href\n",
    "    hemisphere_image_urls = []\n",
    "    for i in range(4):\n",
    "\n",
    "        # Find the elements on each loop to avoid a stale element exception\n",
    "        browser.find_by_css(\"a.product-item h3\")[i].click()\n",
    "\n",
    "        hemi_data = scrape_hemisphere(browser.html)\n",
    "\n",
    "        # Append hemisphere object to list\n",
    "        hemisphere_image_urls.append(hemi_data)\n",
    "\n",
    "        # Finally, we navigate backwards\n",
    "        browser.back()\n",
    "\n",
    "    return hemisphere_image_urls\n",
    "def featured_image(browser):\n",
    "    url = \"https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars\"\n",
    "    browser.visit(url)\n",
    "\n",
    "    # Find and click the full image button\n",
    "    full_image_elem = browser.find_by_id(\"full_image\")\n",
    "    full_image_elem.click()\n",
    "\n",
    "    # Find the more info button and click that\n",
    "    browser.is_element_present_by_text(\"more info\", wait_time=0.5)\n",
    "    more_info_elem = browser.links.find_by_partial_text(\"more info\")\n",
    "    more_info_elem.click()\n",
    "\n",
    "    # Parse the resulting html with soup\n",
    "    html = browser.html\n",
    "    img_soup = BeautifulSoup(html, \"html.parser\")\n",
    "\n",
    "    # Find the relative image url\n",
    "    img = img_soup.select_one(\"figure.lede a img\")\n",
    "\n",
    "    try:\n",
    "        img_url_rel = img.get(\"src\")\n",
    "\n",
    "    except AttributeError:\n",
    "        return None\n",
    "\n",
    "    # Use the base url to create an absolute url\n",
    "    img_url = f\"https://www.jpl.nasa.gov{img_url_rel}\"\n",
    "\n",
    "    return img_url\n",
    "\n",
    "\n",
    "\n",
    "def twitter_weather(browser):\n",
    "    url = \"https://twitter.com/marswxreport?lang=en\"\n",
    "    browser.visit(url)\n",
    "\n",
    "    # Pause for 5 seconds to let the Twitter page load before extracting the html\n",
    "    time.sleep(5)\n",
    "\n",
    "    html = browser.html\n",
    "    weather_soup = BeautifulSoup(html, \"html.parser\")\n",
    "\n",
    "    # First, find a tweet with the data-name `Mars Weather`\n",
    "    tweet_attrs = {\"class\": \"tweet\", \"data-name\": \"Mars Weather\"}\n",
    "    mars_weather_tweet = weather_soup.find(\"div\", attrs=tweet_attrs)\n",
    "\n",
    "    # Next, search within the tweet for the p tag or span tag containing the tweet text\n",
    "    # As Twitter is frequently making changes the try/except will identify the tweet\n",
    "    # text using a regular expression pattern that includes the string 'sol' if there\n",
    "    # is no p tag with a class of 'tweet-text'\n",
    "    try:\n",
    "        mars_weather = mars_weather_tweet.find(\"p\", \"tweet-text\").get_text()\n",
    "\n",
    "    except AttributeError:\n",
    "\n",
    "        pattern = re.compile(r'sol')\n",
    "        mars_weather = weather_soup.find('span', text=pattern).text\n",
    "\n",
    "    return mars_weather\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "def scrape_hemisphere(html_text):\n",
    "    # Soupify the html text\n",
    "    hemi_soup = BeautifulSoup(html_text, \"html.parser\")\n",
    "\n",
    "    # Try to get href and text except if error.\n",
    "    try:\n",
    "        title_elem = hemi_soup.find(\"h2\", class_=\"title\").get_text()\n",
    "        sample_elem = hemi_soup.find(\"a\", text=\"Sample\").get(\"href\")\n",
    "\n",
    "    except AttributeError:\n",
    "\n",
    "        # Image error returns None for better front-end handling\n",
    "        title_elem = None\n",
    "        sample_elem = None\n",
    "\n",
    "    hemisphere = {\n",
    "        \"title\": title_elem,\n",
    "        \"img_url\": sample_elem\n",
    "    }\n",
    "\n",
    "    return hemisphere\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "{'news_title': \"The Extraordinary Sample-Gathering System of NASA's Perseverance Mars Rover\", 'news_paragraph': 'Two astronauts collected Moon rocks on Apollo 11. It will take three robotic systems working together to gather up the first Mars rock samples for return to Earth.', 'featured_image': 'https://www.jpl.nasa.gov/spaceimages/images/largesize/PIA19977_hires.jpg', 'hemispheres': [{'title': 'Cerberus Hemisphere Enhanced', 'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/cerberus_enhanced.tif/full.jpg'}, {'title': 'Schiaparelli Hemisphere Enhanced', 'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/schiaparelli_enhanced.tif/full.jpg'}, {'title': 'Syrtis Major Hemisphere Enhanced', 'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/syrtis_major_enhanced.tif/full.jpg'}, {'title': 'Valles Marineris Hemisphere Enhanced', 'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg'}], 'weather': 'InSight sol 542 (2020-06-05) low -92.2ºC (-134.0ºF) high 0.0ºC (32.0ºF)\\nwinds from the SW at 5.2 m/s (11.6 mph) gusting to 18.3 m/s (41.0 mph)\\npressure at 7.30 hPa', 'facts': '<table border=\"1\" class=\"dataframe table table-striped\">\\n  <thead>\\n    <tr style=\"text-align: right;\">\\n      <th></th>\\n      <th>value</th>\\n    </tr>\\n    <tr>\\n      <th>description</th>\\n      <th></th>\\n    </tr>\\n  </thead>\\n  <tbody>\\n    <tr>\\n      <th>Equatorial Diameter:</th>\\n      <td>6,792 km</td>\\n    </tr>\\n    <tr>\\n      <th>Polar Diameter:</th>\\n      <td>6,752 km</td>\\n    </tr>\\n    <tr>\\n      <th>Mass:</th>\\n      <td>6.39 × 10^23 kg (0.11 Earths)</td>\\n    </tr>\\n    <tr>\\n      <th>Moons:</th>\\n      <td>2 (Phobos &amp; Deimos)</td>\\n    </tr>\\n    <tr>\\n      <th>Orbit Distance:</th>\\n      <td>227,943,824 km (1.38 AU)</td>\\n    </tr>\\n    <tr>\\n      <th>Orbit Period:</th>\\n      <td>687 days (1.9 years)</td>\\n    </tr>\\n    <tr>\\n      <th>Surface Temperature:</th>\\n      <td>-87 to -5 °C</td>\\n    </tr>\\n    <tr>\\n      <th>First Record:</th>\\n      <td>2nd millennium BC</td>\\n    </tr>\\n    <tr>\\n      <th>Recorded By:</th>\\n      <td>Egyptian astronomers</td>\\n    </tr>\\n  </tbody>\\n</table>', 'last_modified': datetime.datetime(2020, 6, 6, 6, 41, 50, 566859)}\n"
     ]
    }
   ],
   "source": [
    "def mars_facts():\n",
    "    try:\n",
    "        df = pd.read_html(\"http://space-facts.com/mars/\")[0]\n",
    "    except BaseException:\n",
    "        return None\n",
    "\n",
    "    df.columns = [\"description\", \"value\"]\n",
    "    df.set_index(\"description\", inplace=True)\n",
    "\n",
    "    # Add some bootstrap styling to <table>\n",
    "    return df.to_html(classes=\"table table-striped\")\n",
    "\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "\n",
    "    # If running as script, print scraped data\n",
    "    print(scrape_all())\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
