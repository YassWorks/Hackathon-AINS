import requests
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.parse import urlparse
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Extract keywords using TF-IDF
def extract_keywords(text, lang='english', top_n=20):
    text = re.sub(r'[^\w\s]', '', text.lower())
    vectorizer = TfidfVectorizer(stop_words=lang)
    tfidf = vectorizer.fit_transform([text])
    scores = zip(vectorizer.get_feature_names_out(), tfidf.todense().A1)
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return [word for word, score in sorted_scores[:top_n]]
def is_reliable_source(url):
    """
    Check if the source is reliable based on domain characteristics.
    Prioritizes .edu, .gov, .org, and reputable news outlets.
    """
    reliable_domains = [
        '.edu', '.gov', '.org',
        'bbc.com', 'nytimes.com', 'theguardian.com', 'reuters.com',
        'npr.org', 'wsj.com', 'apnews.com', 'nature.com',
        'sciencedirect.com', 'nih.gov', 'who.int'
    ]
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    return any(domain.endswith(d) for d in reliable_domains) or any(d in domain for d in reliable_domains)

def clean_text(text):
    """
    Clean extracted text by removing extra whitespace and non-printable characters.
    """
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

def extract_relevant_paragraph(url, statement_words):
    """
    Extract the most relevant paragraph(s) from a webpage that matches the statement.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles to clean up content
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract all paragraphs
        paragraphs = soup.find_all(['p', 'div', 'span'])
        relevant_text = ""
        
        # Find paragraphs containing statement keywords
        for p in paragraphs:
            text = p.get_text().strip()
            if any(word in text.lower() for word in statement_words):
                relevant_text += clean_text(text) + " "
                if len(relevant_text.split()) > 100:  # Limit to ~100 words
                    break
        
        return relevant_text.strip() if relevant_text else "SKIP"
    except Exception as e:
        return f"Error accessing {url}: {str(e)}"

def search_statement(statement, num_results=10):
    """
    Search the web for a statement and return top reliable sources with relevant paragraphs.
    """
    results = {}
    try:
        statement_words=extract_keywords(statement)
        print(statement_words)
        
        # Perform Google search
        for url in search(statement, num_results=50, lang='en'):
            if is_reliable_source(url):
                paragraph = extract_relevant_paragraph(url, statement_words)
                if "SKIP" in paragraph or "Error accessing" in paragraph:
                    continue
                if paragraph:
                    results[url] = paragraph
                if len(results) >= num_results:
                    break
    except Exception as e:
        print(f"Error during search: {str(e)}")
    return results

def main():
    sources = search_statement('the pharoah used to kill children and drink their blood in ancient egypt', 20)
    
    print("\nTop Reliable Sources:")
    for i, (url, paragraph) in enumerate(sources.items(), 1):
        print(f"\n{i}. Source: {url}")
        print(f"Excerpt: {paragraph}\n\n")

if __name__ == "__main__":
    main()