import streamlit as st
import pandas as pd
from textblob import TextBlob
from google_play_scraper import Sort, reviews_all, reviews


# Retry decorator with exponential backoff
def fetch_reviews_data(package_name):
    review1 = reviews_all(package_name, sort=Sort.NEWEST)
    Fatakpay_r = pd.json_normalize(review1)

    # Convert the 'at' column to datetime64[ns]
    Fatakpay_r['at'] = pd.to_datetime(Fatakpay_r['at'])

    # Calculate sentiment using TextBlob
    Fatakpay_r['polarity'] = Fatakpay_r['content'].apply(lambda x: TextBlob(x).sentiment.polarity)
    Fatakpay_r['sentiment'] = Fatakpay_r['polarity'].apply(lambda x: 'Positive' if x > 0 else 'Negative' if x < 0 else 'Neutral')

    return Fatakpay_r


def main():
    st.set_page_config(
        page_title="Fatakpay Reviews Sentiment Analysis",
        page_icon=":smiley:",
        layout="wide",
        initial_sidebar_state="auto"
    )
    # Specify the package name of the app you want to fetch reviews for
    package_name = "com.fatakpay"

    # Fetch reviews data and calculate sentiment
    Fatakpay_r = fetch_reviews_data(package_name)

    # Check if the 'score' column exists in Fatakpay_r
    has_score_column = 'score' in Fatakpay_r.columns

    # Sidebar layout (Date range picker and Rating filter)
    st.sidebar.title("Filters")
    date_range = st.sidebar.date_input("Select Date Range:", [Fatakpay_r['at'].min().date(), Fatakpay_r['at'].max().date()])
    if has_score_column:
        rating_filter = st.sidebar.slider("Select Minimum Rating:", min_value=1, max_value=5, value=1)

    # Filter reviews based on date range and rating
    filtered_reviews = Fatakpay_r[
        (Fatakpay_r['at'] >= pd.Timestamp(date_range[0])) &
        (Fatakpay_r['at'] <= pd.Timestamp(date_range[1])) &
        (Fatakpay_r['score'] >= rating_filter) if has_score_column else True
    ]

    # Calculate sentiment counts for the filtered reviews
    sentiment_counts = filtered_reviews['sentiment'].value_counts()
    positive_count = sentiment_counts.get('Positive', 0)
    negative_count = sentiment_counts.get('Negative', 0)
    neutral_count = sentiment_counts.get('Neutral', 0)

    # Check if total_reviews is zero and set sentiment percentages accordingly
    total_reviews = len(filtered_reviews)
    if total_reviews == 0:
        positive_sentiment_percentage = 0
        negative_sentiment_percentage = 0
        neutral_sentiment_percentage = 0
    else:
        # Calculate sentiment percentages for the filtered reviews
        positive_sentiment_percentage = (positive_count / total_reviews) * 100
        negative_sentiment_percentage = (negative_count / total_reviews) * 100
        neutral_sentiment_percentage = (neutral_count / total_reviews) * 100

    # Calculate average rating for the filtered reviews
    average_rating = filtered_reviews['score'].mean() if has_score_column else None

    # Main content layout (Centered output)
    st.container()
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("Logo.jpeg", width=140)

    with col2:
        st.write("##")
        # Main app layout
        st.markdown('''
            <style>
                .custom-header {
                    text-align: center;
                    background-color: #003366;
                    padding: 8px;
                    margin-bottom: 15px;
                }

                @import url('https://fonts.googleapis.com/css2?family=Avro&display=swap');
                .custom-header h2 {
                    color: #FFFFFF;
                    font-family: 'georgia', sans-serif;
                    font-size: 42px;
                }

                .output-container {
                    margin-top: 20px;
                }

            </style>
            <div class="custom-header">
                <h2>Playstore Reviews Analysis</h2>
            </div>
        ''', unsafe_allow_html=True)

        # Introduction Section
        st.write("Total Reviews:", total_reviews)
        if has_score_column:
            st.write("Average Rating: {:.2f}".format(average_rating))
            if 'score' in Fatakpay_r.columns:
                st.subheader("Rating")
                rating_counts = filtered_reviews['score'].value_counts().reset_index()
                rating_counts.columns = ['Rating', 'Count']
                st.table(rating_counts)
        st.write("Positive Sentiment Percentage: {:.2f}%".format(positive_sentiment_percentage))
        st.write("Negative Sentiment Percentage: {:.2f}%".format(negative_sentiment_percentage))
        st.write("Neutral Sentiment Percentage: {:.2f}%".format(neutral_sentiment_percentage))

        # Show most common negative sentences
        negative_df = filtered_reviews[filtered_reviews['sentiment'] == 'Negative']
        negative_sentence_counts = negative_df['content'].value_counts().reset_index()
        negative_sentence_counts.columns = ['Sentence', 'Count']
        sorted_negative_sentences = negative_sentence_counts.sort_values('Count', ascending=False)
        most_common_negative_sentences = sorted_negative_sentences['Sentence'].tolist()

        st.header("Most Common Negative Comments", anchor="negative_sentences")
        if not most_common_negative_sentences:
            st.write("No negative sentences found in the selected date range and rating.")
        else:
            for i, sentence in enumerate(most_common_negative_sentences[:5], start=1):
                st.write(f"{i}. {sentence}", anchor=f"sentence_{i}")


if __name__ == "__main__":
    main()
