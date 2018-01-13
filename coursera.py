import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import argparse
import random


def get_courses_list(courses_amount, keyword=None):
    response = requests.get(
        "https://www.coursera.org/sitemap~www~courses.xml")
    soup = BeautifulSoup(response.content, "xml")
    urls = soup.find_all("loc")
    if keyword is None:
        courses_list = [
            random.choice(urls).text for range_index in range(courses_amount)
        ]
    else:
        courses_list = [
            url.text for url in urls if keyword in url.text
        ]
    return courses_list


def get_course_info(course_url):
    response = requests.get(course_url)

    soup = BeautifulSoup(response.text, "html.parser")
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


def print_progress_status(course_name):
    print("gathering info about course: {}".format(course_name))


def output_courses_info_to_xlsx(filepath, courses_info):
    wb = Workbook()
    ws = wb.active
    table_title = [
        'Course name', 'Language', 'Start date', 'Rating', 'Duration (week)',
    ]
    ws.append(table_title)
    for course in courses_info:
        course_row = [
            course["Course name"],
            course["Language"],
            course["Start date"],
            course["Average raiting"],
            course["Duration"],
            course["URL"],
        ]
        ws.append(course_row)
    if filepath is None:
        filepath = "courses.xlsx"
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
    keyword = args.keyword
    courses_list = get_courses_list(courses_amount, keyword)
    courses_info = []
    for course in courses_list:
        courses_info.append(get_course_info(course))
    output_courses_info_to_xlsx(filepath, courses_info)


