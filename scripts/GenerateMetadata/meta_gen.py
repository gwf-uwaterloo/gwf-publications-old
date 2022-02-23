import os
from typing import List
from helper import fetch_citations, fetch_references, fetch_paper_metadata


class GenerateMetadata:
    def __init__(self) -> None:
        pass

    def fetch_citations(self, paper_id: str) -> List:
        citation_list = fetch_citations(paper_id)
        if citation_list is None:
            print("[INFO] Paper with paper id {paper_id} not found")
        else:
            return citation_list

    def fetch_references(self, paper_id: str) -> List:
        ref_list = fetch_references(paper_id)
        if ref_list is None:
            print("[INFO] Paper with paper id {paper_id} not found")
        else:
            return ref_list

    def fetch_paper_metadata(self, paper_id: str) -> List:
        metadata = fetch_paper_metadata(paper_id)
        if metadata is None:
            print("[INFO] Paper with paper id {paper_id} not found")
        else:
            return metadata


if __name__ == "__main__":
    met_gen = GenerateMetadata()
    print(met_gen.fetch_paper_metadata("bac31808aa741e0cf11b6de088a30a30196caa"))
