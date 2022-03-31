from abc import ABC
from pathlib import Path

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "http://www.insa-strasbourg.fr/fr/programme-des-etudes/"
PROGRAM_URL = "http://www.insa-strasbourg.fr/fr/programmes-des-etudes/{}/{}"


class InsaStrasbourgSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Strasbourg
    """

    name = 'INSAStrasbourg-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}insa_strasbourg_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(
            url=BASE_URL,
            callback=self.parse_main
        )

    def parse_main(self, response):

        links = response.xpath("//article//li").getall()
        program_ids = [link[link.find('–')+2:link.find(':')-1] if '–' in link else link[4:link.find(':')-1]
                       for link in links if 'contenu' in link]
        links = response.xpath("//article//li//a[contains(text(), 'contenu')]").getall()
        links = [link[9:link[9:].find('"')+9] for link in links]
        for program_id, link in zip(program_ids, links):
            yield scrapy.Request(url=link,
                                 callback=self.parse_program,
                                 cb_kwargs={'program_id': program_id})

    @staticmethod
    def parse_program(response, program_id):

        program_name = response.xpath("//h1/text()").get()
        if program_name is None:
            return

        courses = [(course.attrib['title'], PROGRAM_URL.format(program_id, course.attrib['href'])) for course in response.xpath("//a[@title]")]

        yield {
            "id": program_id,
            "name": program_name,
            "url": response.url,
            "courses": courses,
        }
