# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import xml.etree.ElementTree as ET
import urllib.parse
import requests
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional
from bs4 import BeautifulSoup
import aiohttp
import asyncio

# Constants
PUB_SEARCH_MED_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
SCI_HUB_URL = "https://sci-hub.se/"


# Data Classes
@dataclass
class Author:
    last_name: str
    fore_name: str


@dataclass
class Article:
    title: str
    abstract: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    year: Optional[str] = None
    month: Optional[str] = None


@dataclass
class MedlineCitation:
    pmid: str
    article: Article


@dataclass
class ArticleId:
    id: str
    id_type: str


@dataclass
class PubmedData:
    article_ids: List[ArticleId] = field(default_factory=list)


@dataclass
class PubMedArticle:
    medline_citation: MedlineCitation
    pubmed_data: PubmedData


@dataclass
class PubMedSearchResult:
    ids: List[str] = field(default_factory=list)


@dataclass
class PubMedFetchResult:
    articles: List[PubMedArticle] = field(default_factory=list)


class PubMedService:
    """
    Service for interacting with PubMed API to search and fetch articles.
    """

    def __init__(self):
        pass

    def generate_pubmed_search_url(self, query: str, start_date: str, end_date: str, num_results: int) -> str:
        """
        Generate URL for PubMed search API with given query parameters.

        Args:
            query: Search query string
            start_date: Start date in format "YYYY.MM.DD"
            end_date: End date in format "YYYY.MM.DD"
            num_results: Maximum number of results to return

        Returns:
            Formatted URL string for PubMed search API
        """
        keywords = query.split()
        query_parts = [urllib.parse.quote(kw) for kw in keywords]

        # Format date filter
        start_date_formatted = start_date.replace('.', '/')
        end_date_formatted = end_date.replace('.', '/')
        date_filter = f"{start_date_formatted}:{end_date_formatted}[Date - Publication]"
        query_parts.append(date_filter)

        # Build query parameters
        params = {
            'db': 'pubmed',
            'term': '+AND+'.join(query_parts),
            'retmax': str(num_results),
            'retmode': 'xml'
        }

        return f"{PUB_SEARCH_MED_URL}?{urllib.parse.urlencode(params)}"

    def search_pubmed(self, query: str, start_date: str, end_date: str, num_results: int) -> PubMedSearchResult:
        """
        Search PubMed for articles matching the query.

        Args:
            query: Search query string
            start_date: Start date in format "YYYY.MM.DD"
            end_date: End date in format "YYYY.MM.DD"
            num_results: Maximum number of results to return

        Returns:
            PubMedSearchResult object containing list of article IDs
        """
        url = self.generate_pubmed_search_url(query, start_date, end_date, num_results)

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            id_list = []

            # Extract IDs from IdList element
            for id_elem in root.findall('.//Id'):
                id_list.append(id_elem.text)

            return PubMedSearchResult(ids=id_list)

        except Exception as e:
            raise Exception(f"Error searching PubMed: {str(e)}")

    def fetch_articles(self, article_ids: List[str]) -> PubMedFetchResult:
        """
        Fetch detailed information for PubMed articles by their IDs.

        Args:
            article_ids: List of PubMed article IDs

        Returns:
            PubMedFetchResult object containing list of articles
        """
        if not article_ids:
            return PubMedFetchResult()

        # Build query parameters
        params = {
            'db': 'pubmed',
            'id': ','.join(article_ids),
            'retmode': 'xml'
        }

        try:
            response = requests.get(PUBMED_FETCH_URL, params=params, timeout=30)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            articles = []

            # Process each PubmedArticle
            for article_elem in root.findall('.//PubmedArticle'):
                # Extract MedlineCitation
                medline_citation_elem = article_elem.find('.//MedlineCitation')
                pmid = medline_citation_elem.find('.//PMID').text

                # Extract Article info
                article_elem_in = medline_citation_elem.find('.//Article')
                title = article_elem_in.find('.//ArticleTitle').text if article_elem_in.find(
                    './/ArticleTitle') is not None else ''

                # Extract abstract
                abstract_elem = article_elem_in.find('.//AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None else None

                # Extract authors
                authors = []
                for author_elem in article_elem_in.findall('.//Author'):
                    last_name_elem = author_elem.find('.//LastName')
                    fore_name_elem = author_elem.find('.//ForeName')

                    if last_name_elem is not None and fore_name_elem is not None:
                        authors.append(Author(
                            last_name=last_name_elem.text,
                            fore_name=fore_name_elem.text
                        ))

                # Extract publication date
                year_elem = article_elem_in.find('.//PubDate/Year')
                month_elem = article_elem_in.find('.//PubDate/Month')

                year = year_elem.text if year_elem is not None else None
                month = month_elem.text if month_elem is not None else None

                article = Article(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    month=month
                )

                medline_citation = MedlineCitation(
                    pmid=pmid,
                    article=article
                )

                # Extract PubmedData
                pubmed_data_elem = article_elem.find('.//PubmedData')
                article_ids_list = []

                for article_id_elem in pubmed_data_elem.findall('.//ArticleId'):
                    article_id = ArticleId(
                        id=article_id_elem.text,
                        id_type=article_id_elem.get('IdType', '')
                    )
                    article_ids_list.append(article_id)

                pubmed_data = PubmedData(article_ids=article_ids_list)

                # Create PubMedArticle
                pubmed_article = PubMedArticle(
                    medline_citation=medline_citation,
                    pubmed_data=pubmed_data
                )

                articles.append(pubmed_article)

            return PubMedFetchResult(articles=articles)

        except Exception as e:
            raise Exception(f"Error fetching PubMed articles: {str(e)}")

    def download_pubmed_paper(self, doi: str, paper_id: str, parent_path: str) -> bool:
        """
        Download a paper from Sci-Hub using DOI or paper ID.

        Args:
            doi: DOI of the paper
            paper_id: Paper ID to use for saving the file
            parent_path: Directory to save the downloaded PDF

        Returns:
            True if download successful, False otherwise
        """
        # Check if file already exists
        save_path = os.path.join(parent_path, f"{paper_id}.pdf")
        if os.path.exists(save_path):
            return True

        try:
            # Ensure parent directory exists
            os.makedirs(parent_path, exist_ok=True)

            # Try to get the paper from Sci-Hub
            page_url = f"{SCI_HUB_URL}{doi}"
            response = requests.get(page_url, timeout=30)
            response.raise_for_status()

            # Parse HTML to find PDF link
            soup = BeautifulSoup(response.text, 'html.parser')
            download_url = ""

            # Try to find PDF in iframe
            iframe = soup.find('iframe')
            if iframe and 'src' in iframe.attrs and '.pdf' in iframe['src']:
                download_url = iframe['src']

            # If not found in iframe, try embed tag
            if not download_url:
                embed = soup.find('embed')
                if embed and 'src' in embed.attrs:
                    download_url = embed['src']

            # Fix URL if needed
            if download_url.startswith('//'):
                download_url = f"https:{download_url}"
            elif not download_url.startswith('http'):
                raise Exception("Could not find PDF download URL")

            # Download the PDF
            pdf_response = requests.get(download_url, timeout=60)
            pdf_response.raise_for_status()

            # Save the PDF
            with open(save_path, 'wb') as f:
                f.write(pdf_response.content)

            return True

        except Exception as e:
            print(f"Error downloading paper {doi}: {str(e)}")
            return False

    async def download_pubmed_paper_async(self, doi: str, paper_id: str, parent_path: str) -> bool:
        """
        Async version of download_pubmed_paper.
        """
        # Check if file already exists
        save_path = os.path.join(parent_path, f"{paper_id}.pdf")
        if os.path.exists(save_path):
            return True

        try:
            # Ensure parent directory exists
            os.makedirs(parent_path, exist_ok=True)

            # Try to get the paper from Sci-Hub
            page_url = f"{SCI_HUB_URL}{doi}"

            async with aiohttp.ClientSession() as session:
                async with session.get(page_url, timeout=30) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP error, status code: {response.status}")

                    # Parse HTML to find PDF link
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    download_url = ""

                    # Try to find PDF in iframe
                    iframe = soup.find('iframe')
                    if iframe and 'src' in iframe.attrs and '.pdf' in iframe['src']:
                        download_url = iframe['src']

                    # If not found in iframe, try embed tag
                    if not download_url:
                        embed = soup.find('embed')
                        if embed and 'src' in embed.attrs:
                            download_url = embed['src']

                    # Fix URL if needed
                    if download_url.startswith('//'):
                        download_url = f"https:{download_url}"
                    elif not download_url.startswith('http'):
                        raise Exception("Could not find PDF download URL")

                    # Download the PDF
                    async with session.get(download_url, timeout=60) as pdf_response:
                        if pdf_response.status != 200:
                            raise Exception(f"HTTP error downloading PDF, status code: {pdf_response.status}")

                        # Save the PDF
                        with open(save_path, 'wb') as f:
                            f.write(await pdf_response.read())

            return True

        except Exception as e:
            print(f"Error downloading paper {doi}: {str(e)}")
            return False


def path_exists(path: str) -> bool:
    """
    Check if a path exists.

    Args:
        path: Path to check

    Returns:
        True if path exists, False otherwise
    """
    return os.path.exists(path)


# Global instance
pub_med = PubMedService()