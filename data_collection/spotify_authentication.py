from selenium import webdriver      
import config
import time
import requests

wait_time = 1

driver = webdriver.Chrome('chromedriver.exe')
options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")

url = "https://accounts.spotify.com/authorize?client_id=%s&response_type=code&redirect_uri=%s" % (config.spotify_client_id, config.spotify_redirect_uri)
driver.get(url)
btn = driver.find_element_by_xpath(".//a[starts-with(@href, 'https://www.facebook.com/') and contains(@class,'btn')]")
btn.click()
time.sleep(wait_time)

email = driver.find_element_by_xpath(".//input[@name='email']")
email.send_keys(config.email)
time.sleep(wait_time)
pw = driver.find_element_by_xpath(".//input[@name='pass']")
pw.send_keys(config.password)
time.sleep(wait_time)
login = driver.find_element_by_xpath(".//button[@id='loginbutton']")
login.click()
time.sleep(wait_time)

accept = driver.find_element_by_xpath("//button[@id='auth-accept']")
accept.click()
time.sleep(wait_time)

auth_code = driver.current_url[(len(config.spotify_redirect_uri)+len("?code=")):]

data = requests.post('https://accounts.spotify.com/api/token', 
				  {'code': auth_code, 'redirect_uri': config.spotify_redirect_uri, 'grant_type': "authorization_code", 
				   "client_id": config.spotify_client_id, "client_secret": config.spotify_client_secret}).json()

spotify_access_token = data["access_token"]

s = ""
search_string = "spotify_access_token"
replace_string = spotify_access_token
with open("config.py", "r") as f:
	for line in f:
		if line[:min(len(search_string),len(line))] == search_string:
			s += (line.split("= ")[0] + '= "' + replace_string + '"\n')
		else:
			s += line

with open("config.py", "w") as f:
	f.write(s)

driver.quit()