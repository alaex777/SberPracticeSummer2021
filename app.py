from selenium import webdriver
from bs4 import BeautifulSoup
#from PyQt5.QtWidgets import QInputDialog, QApplication, QLabel
from tkinter import *
import xlsxwriter

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
e = Entry(root)
e.pack()
e.focus_set()

def callback():
	inp = e.get()

b = Button(root, text="Submit", width=10, command=callback)
b.pack() 


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
for i in range(companies_on_page*pages):
	worksheet.write(i, 0, description_list[i][1])
	worksheet.write(i, 1, description_list[i][0])
	worksheet.write(i, 2, info_list[i][1])
	worksheet.write(i, 3, info_list[i][0])

workbook.close()
driver.quit()
