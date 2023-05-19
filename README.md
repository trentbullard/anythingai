# AnythingAI #

## Description ##
AnythingAI is a ChatGPT powered Discord chatbot. It utilizes OpenAI's GPT model to provide intelligent and interactive conversations within Discord servers.

## Requirements ##
To install the necessary dependencies, use the provided `requirements.txt` file:
```
pip install -r requirements.txt
```
Make sure you have the required versions of Python and pip installed.

## Configuration ##
The application uses the `dotenv` library to manage environment variables. Create a `.env` file in the root directory of the project and set the following variables:
```
ELASTICSEARCH_URL=<elasticsearch url>
OPENAI_API_KEY=<openai api key>
OPENAI_MODEL=<gpt model>
DISCORD_BOT_TOKEN=<discord bot token>
```

## Usage ##
Run the application using the following command:
```
python main.py
```

## Features ##
The application is still a work in progress. Here are the features currently being implemented:
- Fix voice channel text-to-speech functionality
- Finish implementing random bot messages
- Add bot commands for the following features:
  - Change the bot's name
  - Enable/disable random bot messages
  - Enable/disable text-to-speech
  - Implement different bot personalities

## Contributing ##
Contributions to the project are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License ##
This project is licensed under the [MIT License](LICENSE.md).
