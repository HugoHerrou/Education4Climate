# -*- coding: utf-8 -*-
from abc import ABC
import io
from pathlib import Path

import pandas as pd
import scrapy
from borb.pdf.pdf import PDF
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction

from settings import YEAR, CRAWLING_OUTPUT_FOLDER


# traitement des fichiers pdf
import pdf2image
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import tempfile
tessdata_dir_config = r'--tessdata-dir "/usr/share/tesseract-ocr/4.00/tessdata"'


BASE_URL = "https://www.insa-centrevaldeloire.fr"
PROG_DATA_PATH = (
    Path(__file__)
    .parent.absolute()
    .joinpath(f"../../../../{CRAWLING_OUTPUT_FOLDER}insa_centre_programs_{YEAR}.json")
)

LANGUAGES_DICT = {
    "Français": ["fr"],
}


class InsaCentreCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Insa Centre Val de Loire
    """

    name = "insa-centre-courses"
    custom_settings = {
        "FEED_URI": Path(__file__)
        .parent.absolute()
        .joinpath(f"../../../../{CRAWLING_OUTPUT_FOLDER}insa_centre_courses_{YEAR}.json")
        .as_uri()
    }

    def start_requests(self):
        # lecture du fichier json insa_centre_programs_2021.json
        programs = pd.read_json(open(PROG_DATA_PATH, "r"))
        # pour chaque lien pdf trouvé extraction du contenu
        for index, program in programs.iterrows():
            courses_ids = program['courses']
            courses_pdf_links = program['pdf_links']
            for (course_id, course_pdf_link) in zip(courses_ids, courses_pdf_links):
                print(course_id, course_pdf_link)
                yield scrapy.Request(
                    course_pdf_link,
                    self.parse_course,
                    cb_kwargs={"course_id": course_id},
                )

    @staticmethod
    def parse_course(response, course_id):
        # conversion en texte du fichier pdf
        with tempfile.TemporaryDirectory() as path:
            images_from_bytes = pdf2image.convert_from_bytes(response.body, output_folder=path, last_page=None)
        lst_texts = [pytesseract.image_to_string(image, lang='fra', config=tessdata_dir_config)
                     for image in images_from_bytes]
        content = ' '.join(lst_texts)
        yield {
            "id": course_id,
            "name": "",
            "year": f"{YEAR}",
            'languages': ["fr"],
            "teachers": "",
            "url": response.url,
            "content": content,
            "goal": "",
            "activity": "",
            "other": "",
        }