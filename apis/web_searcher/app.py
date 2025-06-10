from duckduckgo_search import DDGS
import textwrap
import re


def search_duckduckgo(query, max_results=10):
    
    try:
        snippets = []
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                if r.get("body"):
                    snippets.append(r["body"])
                elif r.get("snippet"):
                    snippets.append(r["snippet"])
        return snippets
    
    except Exception as e:
        print(f"Error during search: {e}")
        return []


def prettify(text, num_paragraphs=1):
    
    try:

        paragraphs = []
        chunks = textwrap.wrap(text, width=1000)[:num_paragraphs]  # limit to n chunks
        
        for chunk in chunks:
            cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', chunk)
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = cleaned.strip()
            paragraphs.append(cleaned)
        
        return paragraphs
    
    except Exception as e:
        print(f"Error during summarization: {e}")
        return ["Error summarizing the text."]


def search_topic(topic, num_paragraphs=2):
    
    try:
        print(f"🔍 Searching the web for: {topic}")
        snippets = search_duckduckgo(topic, max_results=num_paragraphs*10)
        
        if not snippets:
            return ["No relevant search results found."]
        
        combined_text = " ".join(snippets)
        print(f"📚 Found {len(snippets)} snippets. Summarizing...")
        return prettify(combined_text, num_paragraphs=num_paragraphs)
    
    except Exception as e:
        print(f"Error in agent_search_topic: {e}")
        return ["Error processing the topic."]


# Example usage
if __name__ == "__main__":
    
    topic = "Impact of AI on modern education"
    parags = search_topic(topic, num_paragraphs=20)
    
    print("\n📄 Summary:")
    for i, para in enumerate(parags, 1):
        print(f"\nParagraph {i}:\n{para}")