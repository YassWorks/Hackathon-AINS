#import re
#from sklearn.feature_extraction.text import TfidfVectorizer

# Extract keywords using TF-IDF
#def extract_keywords(text, lang='english', top_n=20):
 #   text = re.sub(r'[^\w\s]', '', text.lower())
  #  vectorizer = TfidfVectorizer(stop_words=lang)
   # tfidf = vectorizer.fit_transform([text])
    #scores = zip(vectorizer.get_feature_names_out(), tfidf.todense().A1)
   # sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
   # return [word for word, score in sorted_scores[:top_n]]#