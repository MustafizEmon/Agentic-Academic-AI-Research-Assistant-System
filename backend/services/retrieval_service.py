import urllib.parse
import xml.etree.ElementTree as ET
import concurrent.futures
import requests

class RetrievalService:
    def __init__(self):
        # A valid descriptive User-Agent prevents free APIs from applying zero-rate blocks
        self.headers = {"User-Agent": "AcademicAgentAssistant/1.0 (mailto:assistant@local.ai)"}

    def _search_arxiv(self, query: str, max_results: int = 3) -> list:
        papers = []
        # Clean phrase for atom feed queries
        clean_query = query.replace('"', '').strip()
        encoded_query = urllib.parse.quote(f'all:"{clean_query}"')
        url = f"https://export.arxiv.org/api/query?search_query={encoded_query}&max_results={max_results}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title_el = entry.find('atom:title', ns)
                    summary_el = entry.find('atom:summary', ns)
                    id_el = entry.find('atom:id', ns)
                    pub_el = entry.find('atom:published', ns)
                    
                    title = title_el.text.strip().replace('\n', ' ') if title_el is not None else "Untitled"
                    summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else "No abstract."
                    year = pub_el.text[:4] if pub_el is not None else "N/A"
                    paper_id = id_el.text if id_el is not None else ""
                    
                    authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns) if a.find('atom:name', ns) is not None]
                    
                    pdf_url = ""
                    for link in entry.findall('atom:link', ns):
                        if link.attrib.get('title') == 'pdf' or link.attrib.get('type') == 'application/pdf':
                            pdf_url = link.attrib.get('href')
                    
                    papers.append({
                        "title": title,
                        "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
                        "year": year,
                        "abstract": summary,
                        "url": paper_id,
                        "pdf_link": pdf_url or (paper_id.replace('abs', 'pdf') + ".pdf" if paper_id else ""),
                        "source": "arXiv"
                    })
        except Exception as e:
            print(f"[DEBUG] arXiv extraction error: {e}")
        return papers

    def _search_semantic_scholar(self, query: str, max_results: int = 3) -> list:
        papers = []
        clean_query = query.replace('"', '').strip()
        encoded_query = urllib.parse.quote(clean_query)
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&limit={max_results}&fields=title,authors,year,abstract,url,openAccessPdf"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', [])
                for item in data:
                    authors_list = [a.get('name') for a in item.get('authors', []) if a.get('name')]
                    pdf_link = item.get('openAccessPdf')
                    pdf_url = pdf_link.get('url') if pdf_link else ""
                    
                    papers.append({
                        "title": item.get('title', 'Untitled'),
                        "authors": ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else ""),
                        "year": str(item.get('year', 'N/A')),
                        "abstract": item.get('abstract') or "No abstract provided.",
                        "url": item.get('url', ''),
                        "pdf_link": pdf_url,
                        "source": "Semantic Scholar"
                    })
        except Exception as e:
            print(f"[DEBUG] Semantic Scholar error: {e}")
        return papers

    def _search_openalex(self, query: str, max_results: int = 3) -> list:
        papers = []
        clean_query = query.replace('"', '').strip()
        encoded_query = urllib.parse.quote(clean_query)
        url = f"https://api.openalex.org/works?search={encoded_query}&per_page={max_results}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for item in results:
                    title = item.get('title') or "Untitled"
                    year = str(item.get('publication_year', 'N/A'))
                    
                    authors_list = []
                    for authorship in item.get('authorships', []):
                        author_meta = authorship.get('author', {})
                        if author_meta.get('display_name'):
                            authors_list.append(author_meta.get('display_name'))
                    
                    pdf_url = item.get('open_access', {}).get('oa_url') or ""
                    
                    papers.append({
                        "title": title,
                        "authors": ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else ""),
                        "year": year,
                        "abstract": "Abstract data aggregated inside secondary indexing engines.",
                        "url": item.get('id', ''),
                        "pdf_link": pdf_url,
                        "source": "OpenAlex"
                    })
        except Exception as e:
            print(f"[DEBUG] OpenAlex error: {e}")
        return papers

    def execute_parallel_search(self, queries: list) -> list:
        all_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for q in queries:
                futures.append(executor.submit(self._search_arxiv, q))
                futures.append(executor.submit(self._search_semantic_scholar, q))
                futures.append(executor.submit(self._search_openalex, q))
            
            for f in concurrent.futures.as_completed(futures):
                all_results.extend(f.result())
        
        seen_titles = set()
        deduplicated = []
        for paper in all_results:
            norm_title = paper['title'].lower().strip() if paper.get('title') else ""
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                deduplicated.append(paper)
                
        return deduplicated