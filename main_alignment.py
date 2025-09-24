from alignment import AlignmentModel

tweets = [
    {"text": "The sky is blue most days when it's clear.", "created_at_datetime": "2023-10-01T08:00:00Z", "user": "alice"},
    {"text": "Clouds can make the sky look gray.", "created_at_datetime": "2023-10-01T08:30:00Z", "user": "bob"},
    {"text": "At night, the sky turns black and full of stars.", "created_at_datetime": "2023-10-01T09:00:00Z", "user": "carol"},
    {"text": "Today the sky looks more orange than blue because of wildfire smoke.", "created_at_datetime": "2023-10-01T09:15:00Z", "user": "dave"},
    {"text": "Nothing is prettier than a bright blue sky in the morning.", "created_at_datetime": "2023-10-01T09:45:00Z", "user": "erin"},
    {"text": "The ocean is blue, not the sky.", "created_at_datetime": "2023-10-01T10:00:00Z", "user": "frank"},
    {"text": "Sometimes the sky looks purple during sunsets.", "created_at_datetime": "2023-10-01T10:15:00Z", "user": "grace"},
    {"text": "Clear skies are almost always blue.", "created_at_datetime": "2023-10-01T10:30:00Z", "user": "henry"},
    {"text": "Mars has a red sky because of dust in its atmosphere.", "created_at_datetime": "2023-10-01T10:45:00Z", "user": "ivy"},
    {"text": "I love taking pictures of the blue sky.", "created_at_datetime": "2023-10-01T11:00:00Z", "user": "jack"},
]


original_claim = "The sky is blue"

model = AlignmentModel()

aligned_tweets = model.batch_filter_tweets(original_claim, tweets, batch_size=4, verbose=True)
# aligned_tweets = model.filter_tweets(original_claim, tweets, verbose=True)

if aligned_tweets:
    print(model.find_first(aligned_tweets))
else:
    print("No aligned tweets found.")