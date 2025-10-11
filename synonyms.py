import subprocess
import sys
from nltk.corpus import wordnet
import nltk
import spacy


class Synonyms:
    def __init__(self, model_name="en_core_web_md"):
        # Ensure necessary NLTK data packages are downloaded
        nltk.download("wordnet", quiet=True)  # WordNet lexical database
        nltk.download("omw-1.4", quiet=True)  # Open Multilingual WordNet

        self.nlp = self.load_spacy_model(model_name)  # Medium-sized English model

    def load_spacy_model(self, model_name="en_core_web_md"):
        """
        Loads a spaCy language model by name. If the specified model is not found,
        it attempts to download the model and then load it.

        Args:
            model_name (str): The name of the spaCy model to load. Defaults to "en_core_web_md".

        Returns:
            spacy.language.Language: The loaded spaCy language model.

        Raises:
            subprocess.CalledProcessError: If downloading the model fails.
            OSError: If the model cannot be loaded after download.
        """
        try:
            return spacy.load(model_name)
        except OSError:
            print(f"Model '{model_name}' not found. Downloading it now...")
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", model_name]
            )
            return spacy.load(model_name)

    def find(self, word: str) -> list:
        """
        Finds and returns a list of synonyms for a given word using the WordNet lexical database.

        Args:
            word (str): The word for which to find synonyms.

        Returns:
            list: A list of unique synonyms (as strings) for the input word.
        """
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name().lower() != word.lower():
                    synonyms.add(lemma.name())
        return list(synonyms)

    def find_contextual(
        self, word: str, sentence: str, top_n: int = 5, threshold: float = 0.1
    ) -> list[str]:
        """
        Finds synonyms of a given word that are contextually relevant to a provided sentence.
        This method retrieves synonyms for the specified word and ranks them based on their semantic similarity
        to the context of the given sentence using a language model. Only synonyms with a similarity score above
        the specified threshold are considered, and the top N most relevant synonyms are returned.
        Args:
            word (str): The target word for which to find contextually relevant synonyms.
            sentence (str): The sentence providing context for evaluating synonym relevance.
            top_n (int, optional): The maximum number of top synonyms to return. Defaults to 5.
            threshold (float, optional): The minimum similarity score required for a synonym to be considered relevant. Defaults to 0.1.
        Returns:
            list[str]: A list of up to `top_n` synonyms that are most relevant to the context of the sentence.
        """
        base_synonyms = self.find(word)
        if not base_synonyms:
            return []

        context_doc = self.nlp(sentence)
        ranked = []
        for syn in base_synonyms:
            syn_doc = self.nlp(syn)
            if not syn_doc.vector.any():  # skip empty vectors
                continue
            score = context_doc.similarity(self.nlp(syn))
            if score >= threshold:
                ranked.append((syn, score))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in ranked[:top_n]]


if __name__ == "__main__":
    finder = Synonyms()
    sentence = "Electric vehicles are actually worse for the environment than gas cars."

    print(finder.find_contextual("electric", sentence))
    # → ['intelligent', 'clever', 'smart', 'brilliant']

    print(finder.find_contextual("vehicles", sentence))
    # → ['luminous', 'radiant', 'vivid', 'shiny']

    print(
        finder.find_contextual(
            "gas", sentence
        )
    )
