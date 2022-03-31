# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "http://www.insa-strasbourg.fr/fr/programmes-des-etudes/{}/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}insa_strasbourg_programs_{YEAR}.json')


class InsaStrasbourgCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Université Catholique de Louvain
    """

    name = "INSAStrasbourg-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}insa_strasbourg_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        df = pd.read_json(open(PROG_DATA_PATH, "r"))

        for row in df.itertuples():
            for course_id, url_course in row.courses:
                yield scrapy.Request(url=url_course,
                                     callback=self.parse_course,
                                     cb_kwargs={"course_id": course_id})

    @staticmethod
    def parse_course(response, course_id):

        course_name = cleanup(response.xpath("//h1").get())

        teachers = cleanup(response.xpath('//div[@class="formations-2"]//li').getall())

        # Course description
        response.xpath("//text()[preceding-sibling::h2[1][normalize-space()='SecondHeader']]").getall()

        def get_sections_text(section_name):
            return cleanup(response.xpath(f"//p[preceding-sibling::h2[text()='{section_name}']]").get())
        objectif = get_sections_text('Objectif')
        programme = get_sections_text('Programme')
        competences = get_sections_text('Compétences attendues')

        yield {
            'id': course_id,
            'name': course_name,
            #'year': year,
            'teachers': teachers,
            'url': response.url,
            'content': programme,
            'goal': objectif,
            'other': competences,
            'activity' : "",
            'languages' : "fr"
        }
