import streamlit as st
import pandas as pd
from textblob import TextBlob
from google_play_scraper import Sort, reviews_all

# ... (Rest of the functions and imports remain unchanged)

def main():
    # ... (Rest of the function remains unchanged)

    # Filter reviews based on date range
    filtered_reviews = Fatakpay_r[
        (Fatakpay_r['at'] >= pd.Timestamp(date_range[0])) &
        (Fatakpay_r['at'] <= pd.Timestamp(date_range[1]))
    ]

    # Calculate sentiment counts for filtered reviews
    sentiment_counts_filtered = filtered_reviews['sentiment'].value_counts()
    positive_count_filtered = sentiment_counts_filtered.get('Positive', 0)
    negative_count_filtered = sentiment_counts_filtered.get('Negative', 0)
    neutral_count_filtered = sentiment_counts_filtered.get('Neutral', 0)

    # Calculate sentiment percentages for filtered reviews
    total_reviews_filtered = len(filtered_reviews)
    positive_sentiment_percentage_filtered = (positive_count_filtered / total_reviews_filtered) * 100
    negative_sentiment_percentage_filtered = (negative_count_filtered / total_reviews_filtered) * 100
    neutral_sentiment_percentage_filtered = (neutral_count_filtered / total_reviews_filtered) * 100

    # Calculate average rating for filtered reviews
    average_rating_filtered = filtered_reviews['score'].mean() if has_score_column else None

    # Main app layout
    st.markdown('''
        <style>
            /* ... (Rest of the CSS styling remains unchanged) */
        </style>
        <div class="output-container">
            <h3>Reviews Analysis for selected date range:</h3>
            <p>Total Reviews: {}</p>
    '''.format(total_reviews_filtered), unsafe_allow_html=True)

    if has_score_column:
        st.write("Average Rating: {:.2f}".format(average_rating_filtered))
        if 'score' in Fatakpay_r.columns:
            st.subheader("Rating")
            rating_counts_filtered = filtered_reviews['score'].value_counts().reset_index()
            rating_counts_filtered.columns = ['Rating', 'Count']
            st.table(rating_counts_filtered)

    st.write("Positive Sentiment Percentage: {:.2f}%".format(positive_sentiment_percentage_filtered))
    st.write("Negative Sentiment Percentage: {:.2f}%".format(negative_sentiment_percentage_filtered))
    st.write("Neutral Sentiment Percentage: {:.2f}%".format(neutral_sentiment_percentage_filtered))

    # Show most common negative sentences for filtered reviews
    negative_df_filtered = filtered_reviews[filtered_reviews['sentiment'] == 'Negative']
    negative_sentence_counts_filtered = negative_df_filtered['content'].value_counts().reset_index()
    negative_sentence_counts_filtered.columns = ['Sentence', 'Count']
    sorted_negative_sentences_filtered = negative_sentence_counts_filtered.sort_values('Count', ascending=False)
    most_common_negative_sentences_filtered = sorted_negative_sentences_filtered['Sentence'].tolist()

    st.header("Most Common Negative Comments (for selected date range)", anchor="negative_sentences_filtered")
    if not most_common_negative_sentences_filtered:
        st.write("No negative sentences found in the selected date range.")
    else:
        for i, sentence in enumerate(most_common_negative_sentences_filtered[:5], start=1):
            st.write(f"{i}. {sentence}", anchor=f"sentence_{i}")

if __name__ == "__main__":
    main()
