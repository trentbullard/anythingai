import dotenv from 'dotenv';
import { client as twitchClient } from 'tmi.js';

dotenv.config();

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
function onTwitchMessageHandler (channel, tags, rawMessage, self) {
  if (self) return; // Ignore messages from the bot

  const message = rawMessage.trim();
  console.log(`* ${channel} | ${tags['display-name']}: ${message}`)
  
  if (message.startsWith('!anythingai')) {
    console.log(`* received message ${message}`);
    const prompt = message.split('!anythingai')[1].toLowerCase();
    console.log(`* prompt is ${prompt}`);
  }
}

// Called every time the bot connects to Twitch chat
function onTwitchConnectedHandler (addr, port) {
  console.log(`* Connected to ${addr}:${port}`);
}
