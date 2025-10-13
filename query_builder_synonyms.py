from synonyms import Synonyms
from keybert import KeyBERT

class SynonymQueryBuilder:
    def __init__(self, sentence, max_keywords=5, model_name="en_core_web_md",
                 top_n_syns=3, threshold=0.1, max_syns_per_kw=2):
        self.sentence = sentence
        self.model_name = model_name
        self.top_n_syns = top_n_syns
        self.threshold = threshold
        self.max_syns_per_kw = max_syns_per_kw
        self.keywords = self.extract_keywords(max_keywords)
        self.synonyms = {}
        

    def extract_keywords(self, max_keywords=5):
        """Extract keywords from text using KeyBERT"""
        kw_model = KeyBERT(model="AIDA-UPM/mstsb-paraphrase-multilingual-mpnet-base-v2")
        keywords = kw_model.extract_keywords(self.sentence, top_n=max_keywords)
        keywords = [k[0] for k in keywords]
        print(f"\nExtracted keywords: {keywords}")
        return keywords
    

    def get_contextual_synonyms(self, top_n_syns=3, threshold=0.1):
        synonym_finder = Synonyms(model_name=self.model_name)
        for kw in self.keywords:
            self.synonyms[kw] = synonym_finder.find_contextual(
                word=kw, 
                sentence=self.sentence, 
                top_n=top_n_syns, 
                threshold=threshold
            )


    def interactive_selection(self, max_syns_per_kw=2):
        """Allow user to select preferred synonyms interactively"""
        user_choices = {}
        print("\nSelect your preferred synonyms (or add new ones):\n")

        for kw, syns in self.synonyms.items():
            choice = input(f"Choose up to {max_syns_per_kw} synonyms for '{kw}' (comma-separated), add custom synonyms, or press Enter to skip: ").strip()
            chosen = [c.strip() for c in choice.split(",") if c.strip()] if choice else []

            user_choices[kw] = [kw] + chosen[:max_syns_per_kw]

        return user_choices

  
    @staticmethod
    def build_boolean_query(user_choices):
        groups = []
        for kw, syns in user_choices.items():
            if len(syns) == 1:
                groups.append(f"({syns[0]})")
            else:
                joined = " OR ".join(syns)
                groups.append(f"({joined})")
        return " AND ".join(groups)
    
    def run(self):
        self.get_contextual_synonyms(top_n_syns=self.top_n_syns, threshold=self.threshold)
        print("\nSuggested synonyms for each keyword:")
        for kw, syns in self.synonyms.items():
            print(f"{kw}: {syns}")

        user_choices = self.interactive_selection(max_syns_per_kw=self.max_syns_per_kw)
        query = self.build_boolean_query(user_choices)

        return query
        



if __name__ == "__main__":
    claim = "Climate change is just a natural cycle - the Earth has always warmed and cooled"
    max_keywords = 5
    top_n_syns = 5
    threshold = 0.1
    model_name = "en_core_web_md"
    max_syns_per_kw = 2

    query_builder = SynonymQueryBuilder(
        sentence=claim, 
        max_keywords=max_keywords, 
        model_name=model_name,
        top_n_syns=top_n_syns, 
        threshold=threshold, 
        max_syns_per_kw=max_syns_per_kw
    )
    query = query_builder.run()