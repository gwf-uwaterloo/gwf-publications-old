# Generate Bibtex and Metadata for Articles

This documentation shows how to generate bibtex file for a collection of articles and it also shows how to retrieve important information about an Article based on the available information on that article on semantic scholar.

## Setup

Follow the steps below to setup the code to generate bibtex collection for a set of articles

- Clone the repository::
 ```bash
 git clone https://github.com/gwf-uwaterloo/gwf-publications.git
 ```
- Create a virtual environment with conda or virualenv and install the python dependencies 

```bash
$ conda create -n yourenvname python=x.x anaconda
$ conda activate yourenvname
(yourenvname) $ pip install -r scripts/requirements.txt
```

- Follow the instructions [here](https://selenium-python.readthedocs.io/installation.html) to setup the Selenium driver for your OS and browser type.

## Fetch Semantic Scholar URL & Bibtex for Articles

To generate a semantic scholar landing page and bibtex collection for a collection of records in an excel csv/xlsx file; you can use the sample code snippets below.

- ### For a collection of articles with doi identifiers

    ```python
    from scripts.generatebibtex import GenerateBibtex

    generator = GenerateBibtex()
    input_csv = "articles_with_doi.csv"
    output_file = "articles_with_url.csv"

    # fetch semantic scholar landing page url for articles with doi
    generator.fetch_semantic_scholar_url(input_file=input_csv, output_file=output_file)

    # generate bib file with bibtex for each paper
    output_bib_file = "output.bib"
    generator.generate_bib(output_bib_file)
    ```

- ### For a collection of articles without doi identifiers

    ```python
    from scripts.generatebibtex import GenerateBibtex

    generator = GenerateBibtex()
    input_csv = "articles_with_doi.csv"
    output_file = "articles_with_url.csv"

    # fetch semantic scholar landing page url for articles with doi
    generator.no_doi_fetch_url(input_file=input_csv, output_file=output_file)

    # generate bib file with bibtex for each paper
    output_bib_file = "output.bib"
    generator.generate_bib(output_bib_file)
    ```

- ### To generate bibtex for a single article with it's semantic scholar landing page

    ```python
    from scripts.generatebibtex import GenerateBibtex

    generator = GenerateBibtex()
    landing_page_url = "https://www.semanticscholar.org/paper/e784370c56d4eef9ddd26ed08e4cb683ff00e7c9"

    bibtex = generator._fetch_bib(landing_page_url)
    ```

- ### To generate bibtex for a single article with it's doi identifier

    ```python
    from scripts.generatebibtex import GenerateBibtex

    generator = GenerateBibtex()
    doi_identifier = "10.5194/ESSD-12-629-2020"

    sem_url = generator.fetch_url_with_doi(doi_identifier)
    bibtex = generator._fetch_bib(sem_url)
    ```

## Fetch Metadata for Articles 

To fetch metadata such as <i>(Authors, Venue, Title, URL, Year, Doi, arxivId, abstract, citations)</i> for an article using the Article idenfier on semantic scholar.

- ### Fetch Citations & References & Other Metadata
    ```python
    from scripts.generatemetadata import GenerateMetadata

    metadata_generator = GenerateMetadata()
    paper_id = "e784370c56d4eef9ddd26ed08e4cb683ff00e7c9"

    citation_list = metadata_generator.fetch_citations(paper_id)
    references_list = metadata_generator.fetch_references(paper_id)

    paper_data = metadata_generator.fetch_paper_metadata(paper_id)

    print(f"Article Title: {paper_data['title']}")
    print(f"Article URL: {paper_data['url']}")
    print(f"Article DOI: {paper_data['doi']}")
    print(f"Article YEAR: {paper_data['year']}")


    ```

