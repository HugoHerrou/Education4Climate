# -*- coding: utf-8 -*-
from pathlib import Path

import scrapy
from abc import ABC

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.insa-centrevaldeloire.fr/fr/formation/{0}"


CURSUS_CODE = {
    "sciences-et-technologies-pour-l-ingenieur": "Sciences et Technologies Pour l'Ingénieur",
    "maitrise-des-risques-industriels": "Maîtrise des risques industriels",
    "securite-et-technologies-informatique": "Sécurité et Technologies Informatiques",
    "securite-et-technologies-informatiques-apprentissage": "SÉCURITÉ ET TECHNOLOGIES INFORMATIQUES (STI) PAR APPRENTISSAGE",
    "genie-des-systemes-industriels": "Génie des Systèmes Industriels (GSI)",
    "genie-des-systemes-industriels-apprentissage": "Génie des Systèmes Industriels (GSI) par Apprentissage",
    "énergie-risques-et-environnement": "Énergie, risques et environnement (ERE)",
    "ecole-de-la-nature-et-du-paysage": "École de la nature et du paysage",
    "master": "Masters"
}


class InsaCentreProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Centre Val de Loire
    """

    name = "insa-centre-programs"
    custom_settings = {
        "FEED_URI": Path(__file__)
        .parent.absolute()
        .joinpath(f"../../../../{CRAWLING_OUTPUT_FOLDER}insa_centre_programs_{YEAR}.json")
        .as_uri()
    }

    def start_requests(self):
        for cursus_id, cursus_name in CURSUS_CODE.items():
            url = BASE_URL.format(cursus_id)
            yield scrapy.Request(
                url,
                self.parse_main,
                cb_kwargs={"cursus_id": cursus_id, "cursus_name": cursus_name},
            )

    @staticmethod
    def parse_main(response, cursus_id, cursus_name):
        # liens pdf trouvés sur la page de la formation
        pdf_links = response.xpath('//a[contains(@href, "pdf")]/@href').getall()
        pdf_links = ['https://www.insa-centrevaldeloire.fr' + pdf_link if 'https://www.insa-centrevaldeloire.fr' not in pdf_link
                     else pdf_link for pdf_link in pdf_links]

        # on associe chaque lien pdf à un cours du programme
        courses = [cursus_id + '_' + str(idx_pdf_link) for idx_pdf_link in range(len(pdf_links))]

        # contact pour la formation
        try:
            sel = response.xpath('//div[@class="bloc"]')  # selecteur pour la class "bloc" = encadré avec infos de contact (sauf masters)
            courriel = sel.xpath(".//a/@href").getall()[0]
            telephone = [x for x in response.xpath('//div[@class="bloc"]').xpath(".//p/text()").getall() if '+33' in x][0].strip()
            teachers = response.xpath('//div[@class="bloc"]').xpath(".//span[contains(@class, 'rouge')]").xpath(".//strong/text()").getall()
        except:
            # TODO prevoir extraction pour page des masters
            teachers = []

        yield {
            "id": cursus_id,
            "name": cursus_name,
            "courses":courses,
            "url": response.url,
            "pdf_links": pdf_links,
            "teachers": teachers
        }