'''
Module to extract the keywords of a claim, for which we use KeyBERT LLM, 
and build a query suitable for advance search.
'''

from keybert import KeyBERT
from itertools import combinations

class QueryGenerator:
    def __init__(self, claim):
            self.claim = claim

    def _extract_keywords(self, top_n):
            """Extract keywords from text using KeyBERT"""
            kw_model = KeyBERT(model="AIDA-UPM/mstsb-paraphrase-multilingual-mpnet-base-v2")
            keywords = kw_model.extract_keywords(self.claim, top_n=top_n)
            keywords = [k[0] for k in keywords]
            print(f"Extracted keywords: {keywords}\n")
            return keywords


    def build_query(self, top_n, n=2, verbose=False, keywords=None):
        """Generate OR-combinations of keywords with AND inside each group"""

        if keywords is None:
            keywords = self._extract_keywords(top_n)

        if verbose:
             print(keywords)

        if n == 0:
             return " ".join(keywords)
               
        queries = []
        for i in range(len(keywords) - n, len(keywords)):
            for combo in combinations(keywords, i):
                queries.append("(" + " AND ".join(combo) + ")")

        return " OR ".join(queries)