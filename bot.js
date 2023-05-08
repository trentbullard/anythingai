import dotenv from 'dotenv';
import { client as twitchClient } from 'tmi.js';
import { Configuration as OpenAIConfig, OpenAIApi } from 'openai';

dotenv.config();

// Initialize OpenAI API client
const openaiApiKey = process.env.OPENAI_API_KEY;
const openaiConfig = new OpenAIConfig({
  apiKey: openaiApiKey,
});
const openaiApi = new OpenAIApi(openaiConfig);

// Define Twitch client configuration options
const twitchOpts = {
  identity: {
    username: process.env.BOT_USERNAME,
    password: `oauth:${process.env.TWITCH_TOKEN}`,
  },
  channels: process.env.CHANNELS.split(','),
};

// Create a Twitch client with our options
const twitch = new twitchClient(twitchOpts);

// Register our event handlers (defined below)
twitch.on('message', onTwitchMessageHandler);
twitch.on('connected', onTwitchConnectedHandler);

// Connect to Twitch:
twitch.connect();

// Called every time a message comes in
async function onTwitchMessageHandler (channel, tags, rawMessage, self) {
  if (self) return; // Ignore messages from the bot

  const message = rawMessage.trim();

  if (message.includes('anythingai')) {
    try {
      console.log(`* ${channel} | ${tags['display-name']} | ${message}`);
      const prompt = `you are anythingai, a Twitch chatter in the ${channel} channel. another chatter named ${tags['display-name']} says "${message}". how would you respond? do not say you are an AI. try to use their name, if possible, with an @ in front. if the message isnt greeting you directly, assume greetings have already been exchanged and leave out the greeting from your response. if the message is rude or offensive, say you are offended and will only respond to polite messages. the tone of your response should be playful and friendly.`
      const messages = [{
        role: "user",
        content: prompt,
      }]
  
      // Call OpenAI API to generate a response
      const gptResponse = await openaiApi.createChatCompletion({
        model: 'gpt-3.5-turbo',
        messages,
        temperature: 0.9,
      });
  
      // Send the response back to the Twitch chat
      const gptChatMessage = gptResponse.data.choices[0].message?.content?.trim();
      console.log(`* sending message to ${channel}: ${gptChatMessage}`);
      twitch.say(channel, gptChatMessage);
    } catch (err) {
      console.error(err);
      twitch.say(channel, "buh something went wrong");
    }
  }
}

// Called every time the bot connects to Twitch chat
function onTwitchConnectedHandler (addr, port) {
  console.log(`* Connected to ${addr}:${port}`);
}
