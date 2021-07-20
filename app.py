from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from tkinter import *
import xlsxwriter
import time

#start of rosfrim parser

companies_on_page = 20

description_list, info_list = [], []

def number_of_pages(soup, inp):
	navigation = soup.find("div", {"class": "navigation"})
	navigation = str(navigation)
	s = "Поиск: " + inp + " "
	start = navigation.find("(")
	end = start
	res = ""
	while navigation[end] != ")":
		if navigation[end].isnumeric():
			res += navigation[end]
		end += 1
	return int(res) // companies_on_page

def get_elems(soup):
	descriptions = soup.find_all("div", {"class": "goodsDescription"})
	infos = soup.find_all("div", {"class": "goodsInfo"})
	for i in descriptions:
		tmp = str(i)
		s = "<a href=\""
		start = tmp.find(s)
		end = start + len(s)
		while tmp[end] != "\"":
			end += 1
		link = tmp[start+len(s):end:]
		s = "<span itemprop=\"name\">"
		start = tmp.find(s)
		end = start+len(s)
		while tmp[end] != "<":
			end += 1
		name = tmp[start+len(s):end:]
		description_list.append((link, name))
	for i in infos:
		tmp = str(i)
		s = "<div class=\"goodsInfo-p\" itemprop=\"address\">"
		start = tmp.find(s)
		end = start+len(s)
		while tmp[end] != "<":
			end += 1
		address = tmp[start+len(s):end]
		start = tmp.find("+7 (")
		end = start
		while tmp[end] != "<":
			end += 1
		phone = tmp[start:end:]
		info_list.append((address, phone))

inp = "теплоизоляция"

root = Tk()
root.title("Сбербанк")
root.geometry("300x100")
e = Entry(root, width=100)
e.pack(pady=10)
e.focus_set()

def callback():
	global inp
	inp = e.get()
	root.destroy()

b = Button(root, text="Подтвердить", width=100, height=50, command=callback)
b.pack() 

root.mainloop()

print(inp)

search = "https://www.rosfirm.ru/catalog?field_keywords=" + inp + "&search=1"
driver = webdriver.Safari()
driver.get(search)

soup = BeautifulSoup(driver.page_source, 'html.parser')
get_elems(soup)

pages = int(number_of_pages(soup, inp) * 0.9)

for i in range(1, pages):
	search = "https://www.rosfirm.ru/catalog?field_keywords=" + inp + "&search=1&query_start:int=" + str(i*companies_on_page)
	driver.get(search)
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	get_elems(soup)

workbook = xlsxwriter.Workbook('результат.xlsx')
worksheet = workbook.add_worksheet()
for i in range(len(description_list)):
	worksheet.write(i, 0, description_list[i][1])
	worksheet.write(i, 1, description_list[i][0])
	worksheet.write(i, 2, info_list[i][1])
	worksheet.write(i, 3, info_list[i][0])

# end of rosfirm parser

# start of списокфирм parser

worksheet = workbook.add_worksheet()
search = "https://списокфирм.рф/"
driver.get(search)
inp_elem = driver.find_element_by_id("zapros")
inp_elem.send_keys(inp)
inp_elem.send_keys(Keys.ENTER)
inp_elem.submit()

links = []

time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'html.parser')
divs = soup.find_all("div", {"class": "orglist_full_company"})
for div in divs:
    links.append(div.find("a").get("href"))

count = 0

for link in links:
    driver.get(search + link)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    worksheet.write(count, 0, soup.find("div", {"class": "nazvanie_firmi"}).find("h1").text.strip())
    worksheet.write(count, 3, soup.find("div", {"class": "content_firmi"}).find_all("p")[1].text.strip())
    worksheet.write(count, 1, soup.find("a", {"rel": "nofollow", "target": "_blank"}).get("href").strip()[12::])
    worksheet.write(count, 2, soup.find("div", {"class": "content_firmi"}).find_all("p")[5].text.strip())
    count += 1

# end of списокфирм parser

workbook.close()
driver.quit()
