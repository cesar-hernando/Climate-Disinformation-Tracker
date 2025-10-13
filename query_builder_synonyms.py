from synonyms import Synonyms
from keybert import KeyBERT
from itertools import combinations, product

class SynonymQueryBuilder:
    def __init__(self, sentence, max_keywords=5, n_keywords_dropped=1, model_name="en_core_web_md",
                 top_n_syns=3, threshold=0.1, max_syns_per_kw=2):
        self.sentence = sentence
        self.n_keywords_dropped = n_keywords_dropped
        self.model_name = model_name
        self.top_n_syns = top_n_syns
        self.threshold = threshold
        self.max_syns_per_kw = max_syns_per_kw
        self.keywords = self.extract_keywords(max_keywords)
        self.synonyms = {}
        

    def extract_keywords(self, max_keywords=5):
        """Extract keywords from text using KeyBERT."""
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
        """Allow user to select preferred synonyms interactively."""
        user_choices = {}
        print("\nSelect your preferred synonyms (or add new ones):\n")

        for kw, syns in self.synonyms.items():
            choice = input(f"Choose up to {max_syns_per_kw} synonyms for '{kw}' (comma-separated), add custom synonyms, or press Enter to skip: ").strip()
            chosen = [c.strip() for c in choice.split(",") if c.strip()] if choice else []

            user_choices[kw] = [kw] + chosen[:max_syns_per_kw]

        return user_choices

  
    def build_boolean_query(self, user_choices):
        """
        Build a Boolean query combining keyword groups (with synonyms)
        in a distributed 'sum of products' form.
        """

        if self.n_keywords_dropped == 0:
            groups = []
            for kw, syns in user_choices.items():
                if len(syns) == 1:
                    groups.append(f"({syns[0]})")
                else:
                    joined = " OR ".join(syns)
                    groups.append(f"({joined})")
            return " AND ".join(groups)
        
        else:
            keywords = list(user_choices.keys())
            terms_per_group = max(1, len(keywords) - self.n_keywords_dropped)  # Avoid 0 terms

            # Build (kw OR synonyms) groups
            or_groups = []
            for kw, syns in user_choices.items():
                if not syns:
                    or_groups.append(f"({kw})")
                elif len(syns) == 1:
                    or_groups.append(f"({syns[0]})")
                else:
                    joined = " OR ".join(syns)
                    or_groups.append(f"({joined})")

            # Generate combinations of size `terms_per_group`
            and_groups = []
            for combo in combinations(or_groups, terms_per_group):
                and_groups.append("(" + " AND ".join(combo) + ")")

            # Combine all AND-groups with OR
            return " OR ".join(and_groups)
        

    def build_boolean_query_expand(self, user_choices):
        """
        Build a Boolean query combining keyword groups (with synonyms)
        in a fully distributed 'sum of products' form — no nested ORs.
        """

        if self.n_keywords_dropped == 0:
            groups = []
            for kw, syns in user_choices.items():
                if len(syns) == 1:
                    groups.append(f"({syns[0]})")
                else:
                    joined = " OR ".join(syns)
                    groups.append(f"({joined})")
            return " AND ".join(groups)
        
        else:
            keywords = list(user_choices.keys())
            n = len(keywords)
            terms_per_group = max(1, n - self.n_keywords_dropped)

            # Select subsets of keywords based on terms_per_group
            subset_keywords = list(combinations(keywords, terms_per_group))

            all_expanded_groups = []

            # For each combination of keywords, expand all synonym permutations
            for kw_combo in subset_keywords:
                # Collect lists of synonyms for the selected keywords
                synonym_lists = [user_choices[k] for k in kw_combo]

                # Cartesian product to expand all OR possibilities
                for term_combo in product(*synonym_lists):
                    expanded = " AND ".join(term_combo)
                    all_expanded_groups.append(f"({expanded})")

            # Join everything with OR → pure sum-of-products
            return " OR ".join(all_expanded_groups)

    
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
    n_keywords_dropped = 1
    top_n_syns = 5
    threshold = 0.1
    model_name = "en_core_web_md"
    max_syns_per_kw = 2

    query_builder = SynonymQueryBuilder(
        sentence=claim, 
        max_keywords=max_keywords, 
        n_keywords_dropped=n_keywords_dropped,
        model_name=model_name,
        top_n_syns=top_n_syns, 
        threshold=threshold, 
        max_syns_per_kw=max_syns_per_kw
    )
    query = query_builder.run()
    print(f"\nFinal Boolean query:\n{query}\n")