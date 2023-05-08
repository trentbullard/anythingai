import { client } from 'tmi.js';
import dotenv from 'dotenv';
dotenv.config();

// Define configuration options
const opts = {
  identity: {
    username: process.env.BOT_USERNAME,
    password: `oauth:${process.env.TWITCH_TOKEN}`,
  },
  channels: process.env.CHANNELS.split(','),
};

// Create a client with our options
const client = new client(opts);

// Register our event handlers (defined below)
client.on('message', onMessageHandler);
client.on('connected', onConnectedHandler);

// Connect to Twitch:
client.connect();

// Called every time a message comes in
function onMessageHandler (channel, tags, message, self) {
  if (self) return; // Ignore messages from the bot

  if (message.startsWith('!anythingai')) {
    console.log(`* received message ${message}`);
    const prompt = message.split('!anythingai')[1].trim().toLowerCase();
    console.log(`* prompt is ${prompt}`);
  } else {
    console.log(`* 💀 i dont understand ${message}`);
  }
}

// Called every time the bot connects to Twitch chat
function onConnectedHandler (addr, port) {
  console.log(`* Connected to ${addr}:${port}`);
}
