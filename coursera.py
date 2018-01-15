import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import argparse
import random


def get_courses_urls_list(courses_xml_feed, courses_amount, keyword=None):
    soup = BeautifulSoup(courses_xml_feed, "xml")
    urls = soup.find_all("loc")
    if keyword is None:
        courses_urls_ist = [
            random.choice(urls).text for range_index in range(courses_amount)
        ]
    else:
        courses_urls_ist = [
            url.text for url in urls if keyword in url.text
        ]
    return courses_urls_ist


def get_course_info(course_page, course_url):
    soup = BeautifulSoup(course_page, "html.parser")
    course_name = soup.find("h1", class_="title display-3-text").text
    print_progress_status(course_name)
    lang = soup.find("div", class_="rc-Language").text
    start_date = soup.find(
        "div", class_="startdate rc-StartDateString caption-text").text
    duration = len(soup.find_all("div", class_="week"))
    rating_div = soup.find("div", class_="ratings-text bt3-visible-xs")
    if rating_div:
        rating_value = rating_div.text
    else:
        rating_value = None
    return {
        "Course name": course_name,
        "Language": lang,
        "Start date": start_date,
        "Average raiting": rating_value,
        "Duration": duration,
        "URL": course_url
    }


def fetch_page_data(url):
    page_data = requests.get(url).text
    return page_data


def print_progress_status(course_name):
    print("gathering info about course: {}".format(course_name))


def get_xlsx_document_container(courses_info):
    workbook = Workbook()
    ws = workbook.active
    table_title = [
        'Course name', 'Language', 'Start date',
        'Rating', 'Duration (week)', "URL"
    ]
    ws.append(table_title)
    for course in courses_info:
        course_raw = [
            course["Course name"],
            course["Language"],
            course["Start date"],
            course["Average raiting"],
            course["Duration"],
            course["URL"]
        ]
        ws.append(course_raw)
    return workbook


def save_xlsx_file(filepath, wb):
    wb.save(filename=filepath)


def get_input_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        required=False,
        default="courses.xlsx",
        help="Path to output Excel .xlsx file"
    )
    parser.add_argument(
        "-k",
        "--keyword",
        required=False,
        help="find courses with a particular keyword"
    )
    return parser


if __name__ == "__main__":
    courses_amount = 20
    parser = get_input_argument_parser()
    args = parser.parse_args()
    filepath = args.file
    keyword = args.keyword

    courses_xml_feed = fetch_page_data(
        "https://www.coursera.org/sitemap~www~courses.xml"
    )
    courses_urls_list = get_courses_urls_list(
        courses_xml_feed,
        courses_amount,
        keyword
    )
    courses_info = []
    for url in courses_urls_list:
        course_page = fetch_page_data(url)
        courses_info.append(
            get_course_info(course_page, url)
        )
    workbook = get_xlsx_document_container(courses_info)
    save_xlsx_file(filepath, workbook)
