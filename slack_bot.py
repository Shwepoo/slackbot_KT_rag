from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import wikipedia
import os
from flask import Flask, request, jsonify

# Initialize Slack client
slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

# Flask app to handle incoming requests
app = Flask(__name__)

# Function to retrieve information from Wikipedia
def get_wikipedia_info(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple options found for {query}: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find anything on {query}."
    except Exception as e:
        return "An error occurred while fetching data."

# Function to send messages back to Slack
def send_message(channel, text):
    try:
        response = client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Handle incoming Slack events (messages)
@app.route('/slack/events', methods=['POST'])
def slack_event():
    data = request.json
    if 'event' in data and 'bot_id' not in data['event']:  # Ensure the bot doesn't respond to itself
        event_data = data['event']
        if 'text' in event_data:
            user_query = event_data['text']  # User's query
            wiki_info = get_wikipedia_info(user_query)  # Fetch Wikipedia info
            send_message(event_data['channel'], wiki_info)  # Send the response back to Slack
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(debug=True, port=3000)
