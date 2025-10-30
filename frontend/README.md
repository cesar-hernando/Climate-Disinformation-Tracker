# Climate Disinformation Tracker Frontend
The Climate Disinformation Tracker is a tool designed to trace the earliest online appearance of an input
disinformation claim - particularly those related to climate change. Note that it is also possible to search for claims about other topics, but our main interests lie with climate change. It assists the general public
and researchers in understanding when and by whom a particular claim first appeared - allowing
them to also see how it evolved over time.

## System Features
- Automatically extracts keywords from a given claim (using KeyBERT)
- Builds optimised search queries
- Retrieves relevant tweets from Nitter
- Classifies how each tweet aligns with the claim
- Presents the results through an interactive dashboard

## Source definition
In this tool, the source refers to the earliest retrievable tweet that semantically aligns with the
input claim. It does not imply absolute origin of the idea, but rather the first verifiable occurrence
detected in publicly available data. Accounting for any misalignments by the alignment model,
the system also gives the users the option to view the first ‘k’ tweets related to the claim in
general. This allows the user to manually view other occurrences that may have been
misclassified as ‘neutral’ or ‘contradictory’ to their input claim.


## Parameters
On the main page, users can customize the search process by setting the following parameters
when running the tool:
- Claim – The textual statement to investigate, such as “Electric vehicles are worse for the
environment than gas cars.”
- Initial date and final date – The time span to search.
- Max keywords – The maximum number of keywords extracted from the claim.
- Keywords dropped per clause – Controls how many keywords are removed when
generating Boolean query combinations.
- Synonyms – Enables synonym expansion to increase recall. Users can select a few
synonyms per claim, either by themselves or can be assisted by the system.
- Earliest k – The number of earliest tweets the user would like the system to retrieve,
regardless of alignment with the claim.
- Excludes – Optional filters (e.g., to skip retweets or replies).
- Mode – User can either run the source-finding mode (returns the oldest entailing tweet
and earliest list), or retrieve and classify all tweets in the range

## Dashboard
A dashboard then visualises the retrieved tweets in several ways:
- A chronological timeline of all the tweets mentioning the claim
- Distribution plots illustrating how many tweets entail, contradict or remain neutral
- A filter that allows this timeline and plot but for entailing, neutral and contradicting claims
individually
- A network analysis allowing users to view engagement in terms of replies among users
for a claim. Arrows are coloured to also display entailing, neutral and contradictory
tweets allowing users to notice what kind of information a particular X user usually
spreads per claim.