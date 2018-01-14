import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import argparse
import random


def get_courses_urls_list(courses_xml_feed, courses_amount, keyword=None):
    soup = BeautifulSoup(courses_xml_feed, "xml")
    urls = soup.find_all("loc")
    if keyword is None:
        courses_urls_ist = [random.choice(urls).text
                        for range_index in range(courses_amount)]
    else:
        courses_urls_ist = [url.text for url in urls
                        if keyword in url.text]
    return courses_urls_ist


def get_course_info(course_page, course_url):
    soup = BeautifulSoup(course_page, "html.parser")
    course_name = soup.find("h1", {"class": "title display-3-text"}).text
    print_progress_status(course_name)
    lang = soup.find("div", class_="rc-Language").text
    start_date = soup.find(
        "div", class_="startdate rc-StartDateString caption-text").text
    duration = len(soup.find_all("div", class_="week"))
    if soup.find(
            "div", class_="ratings-text bt3-visible-xs"):
        raiting = soup.find(
            "div", class_="ratings-text bt3-visible-xs").text
    else:
        raiting = None
    return {"Course name": course_name,
            "Language": lang,
            "Start date": start_date,
            "Average raiting": raiting,
            "Duration": duration,
            "URL": course_url}


def send_get_request(url):
    response = requests.get(url).content.decode('utf-8')
    return response


def print_progress_status(course_name):
    print("gathering info about course: {}".format(course_name))


def get_courses_data_to_write(courses_info):
    table_title = ['Course name', 'Language', 'Start date',
                   'Rating', 'Duration (week)', "URL"]
    courses_data = [table_title]
    for course in courses_info:
        courses_data.append([
            course["Course name"],
            course["Language"],
            course["Start date"],
            course["Average raiting"],
            course["Duration"],
            course["URL"],
        ])
    return courses_data


def write_data_to_xlsx(filepath, courses_list):
    wb = Workbook()
    ws = wb.active
    for course_row in courses_list:
        ws.append(course_row)
    wb.save(filename=filepath)


def get_input_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=False,
                        help='Path to output Excel .xlsx file')
    parser.add_argument('-k', '--keyword', required=False,
                        help='find courses with a particular keyword')
    return parser


if __name__ == "__main__":
    courses_amount = 20
    parser = get_input_argument_parser()
    args = parser.parse_args()
    filepath = args.file
    if filepath is None:
        filepath = "courses.xlsx"
    keyword = args.keyword

    courses_xml_feed = send_get_request("https://www.coursera.org/sitemap~www~courses.xml")
    courses_urls_list = get_courses_urls_list(courses_xml_feed, courses_amount, keyword)
    courses_info = []
    for url in courses_urls_list:
        course_page = send_get_request(url)
        courses_info.append(get_course_info(course_page, url))
    courses_data = get_courses_data_to_write(courses_info)
    write_data_to_xlsx(filepath, courses_data)


