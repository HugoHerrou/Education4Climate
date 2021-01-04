import re

import src.crawl.unicrawl.spiders.config.settings as s
import utils as u


# Read PDF file
page_content = u.read_pdf()



from abc import ABC

import scrapy

BASE_URL = f"https://studiegids.ugent.be/{s.YEAR}/EN/FACULTY/faculteiten.html"


class UgentCourseSpider(scrapy.Spider, ABC):
    name = 'ugent-programs'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ugent_programs_{s.YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        for href in response.xpath("//aside//li[a[@target='_top']]/a"):
            yield response.follow(href, self.parse_program_group, cb_kwargs={"base_dict": base_dict})

    def parse_program_group(self, response, base_dict):

        links = response.xpath("//div[@id='oase_heading_programmas']//li[@class='active']/a/@href").getall()
        codes = [link.split('.')[0] for link in links]

        for code, link in zip(codes, links):
            cur_dict = {"code": code}
            yield response.follow(link, self.parse_program, cb_kwargs={"base_dict": {**cur_dict, **base_dict}})

    @staticmethod
    def parse_program(response, base_dict):
        program_name = response.xpath("//h1/text()").get()
        campus = ''
        if '(' in program_name:
            campus = program_name.split('(')[-1].split(')')[0]
        cycle = ''
        if 'bachelor' in program_name or 'Bachelor' in program_name:
            cycle = 'bac'
        elif 'graduaat' in program_name or 'Graduaat' in program_name:
            cycle = 'grad'
        courses = response.xpath("//tr[contains(@class, 'opo_row')]//td[@class='code']/text()").getall()
        courses_url = response.xpath("//td[@class='opleidingsonderdeel']/a/@href").getall()
        courses_url = [c.split("/syllabi/")[1].split('.htm')[0] for c in courses_url]
        ects = response.xpath("//tr[contains(@class, 'opo_row')]//td[@class='sp']/text()").getall()
        ects = [int(e.split(" ")[0]) for e in ects]
        # Get list of unique courses and ects
        courses, courses_url, ects = zip(*set(zip(courses, courses_url, ects)))

        cur_dict = {'name': program_name,
                    'cycle': cycle,
                    'campus': campus,
                    'courses': courses,
                    'ects': ects,
                    'courses_urls': courses_url}

        yield {**base_dict, **cur_dict}



