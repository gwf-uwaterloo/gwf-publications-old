import os
import yaml
import pandas as pd
from typing import Any
from typing import Dict
from utils import extract_dois, fetch_bib, fetch_url_no_doi
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class GenerateBibtex:
    def __init__(self, config_path: str = "scripts/config/config.yaml"):
        assert os.path.exists(
            config_path
        ), f"[INFO] Config file {config_path} does not exist"
        self.config_path = config_path
        self.config_dict = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        loads yaml configuration file.
        """
        conf_file = yaml.full_load(open(self.config_path, "r"))
        return conf_file

    def generate_bib(self, output_bib_path: str, input_file: str = None):
        """
        Generate a bibtex collection file from a series of article
        The bibtex is scraped from the semantic scholar landing scholar of
        each article.

        Args:
        output_bib_path: output path of the bibtex collection file
        input_file: input excel file containing semanticscholar urls

        """
        if input_file:
            paper_df = self._read_input_file(input_file)
            self.url_list = list(paper_df["semantic_scholar_url"])

        assert len(self.url_list) != 0, "Semantic Scholar URL link is empty"
        bib_collection = [fetch_bib(url) for url in self.url_list if url is not None]
        db = BibDatabase()
        db.entries = bib_collection
        writer = BibTexWriter()
        writer.indent = "    "  # indent entries with 4 spaces instead of one
        writer.comma_first = False  # place the comma at the beginning of the line
        with open(output_bib_path, "w") as bibfile:
            bibfile.write(writer.write(db))

    def no_doi_fetch_url(self, input_file: str, output_file: str = None):
        """
        This function generates the semantic scholar landing page URL for
        Articles in a CSV/XLSX file without a doi link

        Args:
        Input: csv/xlsx file containing the publications in the first column

        e.g of publication ==>
        "Wilson, H., Elliott, J., Macrae, M. and Glenn, A. (2019).
        Near-surface soils as a source of phosphorus in snowmelt runoff from cropland.
        Journal of Environmental Quality"
        """

        paper_df = self._read_input_file(input_file)
        if "semantic_scholar_url" in list(paper_df.columns):
            url_list = paper_df["semantic_scholar_url"].tolist()
        else:
            url_list = [None] * len(paper_df)
            paper_df["semantic_scholar_url"] = url_list
            paper_df = paper_df.fillna("")

        for i in range(len(paper_df)):
            publication = paper_df.loc[i][0].lower().strip()

            if paper_df.loc[i]["semantic_scholar_url"] == "":
                sem_landing_url = fetch_url_no_doi(publication)
                url_list[i] = sem_landing_url

        paper_df["semantic_scholar_url"] = url_list

        if output_file:
            paper_df.to_csv(output_file, index=False)

        self.url_list = url_list
        return paper_df

    def fetch_semantic_scholar(self, input_file: str, output_file: str = None):
        """
        This function generates the semantic scholar landing page URL for
        Articles in a CSV/XLSX file with a doi link

        Args:
        Input: csv/xlsx file containing the publications in the first column
        The publications should contain a doi link in any of the formats
        'doi:10.2134/jeq2018.07.0280.' or 'https://doi.org/10.1016/j.jhydrol.2020.124541.'

        e.g of publication ==>
        "Wilson, H., Elliott, J., Macrae, M. and Glenn, A. (2019).
        Near-surface soils as a source of phosphorus in snowmelt runoff from cropland.
        Journal of Environmental Quality, 48(4):921-930. doi:10.2134/jeq2019.04.0155."
        """
        paper_df = self._read_input_file(input_file)

        if "semantic_scholar_url" in list(paper_df.columns):
            url_list = paper_df["semantic_scholar_url"].tolist()
        else:
            url_list = [None] * len(paper_df)
            paper_df["semantic_scholar_url"] = url_list
            paper_df = paper_df.fillna("")

        for i in range(len(paper_df)):
            publication = paper_df.loc[i][0].lower().strip()

            if paper_df.loc[i]["semantic_scholar_url"] == "":
                if publication.find("doi.org/", 0) != -1:
                    print(f"[INFO] Article {i + 2}: doi number present in string")
                    sem_landing_url = extract_dois(
                        publication, self.config_dict, "doi.org/"
                    )
                elif publication.find("doi:", 0) != -1:
                    print(f"[INFO] Article {i + 2}: doi number present in string")
                    sem_landing_url = extract_dois(
                        publication, self.config_dict, "doi:"
                    )
                else:
                    publication = paper_df.loc[i][0]
                    print(f"[INFO] Article {i + 2}: doi number absent in string")
                    sem_landing_url = None  # fetch_url_no_doi(publication)

                print(sem_landing_url)
                url_list[i] = sem_landing_url
            else:
                pass

        paper_df["semantic_scholar_url"] = url_list

        if output_file:
            paper_df.to_csv(output_file, index=False)

        self.url_list = url_list
        return paper_df

    def _read_input_file(self, input_file: str):
        """
        Read excel file
        """
        assert os.path.exists(
            input_file
        ), f"[INFO] Input file {input_file} does not exist"
        df = (
            pd.read_excel(input_file, header=0).fillna("")
            if input_file.endswith(".xlsx")
            else pd.read_csv(input_file, header=0, encoding="iso8859_16").fillna("")
        )
        return df


if __name__ == "__main__":
    excel_file = "/Users/mac/Desktop/gwf_publications.csv"
    generator = GenerateBibtex()
    # df = generator.fetch_semantic_scholar(excel_file)
    generator.generate_bib(
        output_bib_path="output.bib",
        input_file="/Users/mac/Desktop/gwf_publications_no_doi.csv",
    )
