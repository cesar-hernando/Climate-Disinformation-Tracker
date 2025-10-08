# Load model directly
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class AlignmentModel:
    def __init__(self, model_name="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)

        # Different models use different label orders, so be sure to use the correct mapping
        self.labels = {
            0: 'ENTAILMENT',
            1: 'NEUTRAL',
            2: 'CONTRADICTION'
        }

    def predict(self, original_claim, claim_to_review, verbose=False):
        """ Compare a single tweet against a claim. Returns label ID. """
        input = self.tokenizer(claim_to_review, original_claim, truncation=True, return_tensors="pt").to(self.device)
        logits = self.model(**input).logits[0]
        probs = torch.nn.functional.softmax(logits, dim=-1).tolist()
        if verbose:
            print(f'Comparing "{claim_to_review}" against "{original_claim}":')
            for label, prob in zip(self.labels.values(), probs):
                print(f'    {label}: {prob:.3f}')

        label = torch.argmax(logits, dim=-1).item()
        if verbose:
            print(f'    => {self.labels[label]}')
        return label
    
    def batch_predict(self, original_claim, tweets, batch_size=16, verbose=False):
        """
        Compare many tweets against a claim in batches.
        Returns list of label IDs in same order as input tweets.
        """
        results = []
        for i in range(0, len(tweets), batch_size):
            batch_texts = [t['text'] for t in tweets[i:i+batch_size]]
            # Tokenize all pairs in the batch
            inputs = self.tokenizer(
                batch_texts,
                [original_claim] * len(batch_texts),
                truncation=True,
                padding=True,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            labels = torch.argmax(probs, dim=-1).tolist()

            results.extend(labels)

            if verbose:
                for txt, label_id in zip(batch_texts, labels):
                    print(f'"{txt}" => {self.labels[label_id]}')

        return results


    def filter_tweets(self, original_claim, tweets, verbose=False):
        """ Filter tweets that entail the original claim """
        tweets = [tweet for tweet in tweets if self.labels[self.predict(original_claim, tweet['text'], verbose)] == 'ENTAILMENT']
        return tweets
    
    def batch_filter_tweets(self, original_claim, tweets, batch_size=16, verbose=False):
        """ Filter tweets that entail the original claim using batch processing """
        labels = self.batch_predict(original_claim, tweets, batch_size, verbose)
        tweets = [tweet for tweet, label in zip(tweets, labels) if self.labels[label] == 'ENTAILMENT']
        return tweets

    def find_first(self, tweets):
        """ Find the earliest tweet """
        tweets = sorted(tweets, key=lambda tweet: tweet['created_at_datetime'])
        return tweets[0]
    

if __name__ == "__main__":
    model = AlignmentModel()
    claim = "Climate change is just caused by natural cycles of the sun"
    tweets = [
        {"text": "The sun's cycles are responsible for climate change.", "created_at_datetime": "2020-01-01"},
        {"text": "Climate change is just caused by natural cycles of the sun.", "created_at_datetime": "2019-01-01"},
        {"text": "Climate change is a complex issue with multiple factors.", "created_at_datetime": "2021-01-01"},
    ]
    print(model.batch_predict(claim, tweets, verbose=True))