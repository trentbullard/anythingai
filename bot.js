import dotenv from 'dotenv';
import { Client } from '@elastic/elasticsearch';
import { client as twitchClient } from 'tmi.js';
import { Configuration as OpenAIConfig, OpenAIApi } from 'openai';
import { RateLimiterMemory } from 'rate-limiter-flexible';
import { inspect } from 'util';

dotenv.config();

const client = new Client({ node: process.env.ELASTICSEARCH_URL });

// Initialize rate limiter
const limiter = new RateLimiterMemory({
  points: 1,
  duration: 5,
});

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
      const prompt = `you are anythingai, a Twitch chatter in the ${channel} channel. another chatter named ${tags['display-name']} says "${message}". how would you respond? do not say you are an AI. only use their name when greeting or bidding farewell. the tone of your response should be edgy, playful, and friendly. dont use proper grammar. use internet slang. keep your responses shorter than 20 words. only attempt to keep the conversation going if the user seems interested. if the users message is rude or offensive, say you are offended and will only respond to polite messages.`
      const messages = []

      // Index the message in Elasticsearch
      const timestamp = new Date().toISOString();
      const body = {
        user: tags['display-name'],
        userMessage: message,
        timestamp,
      }
      const id = `${tags['display-name']}-${timestamp}`
      const { body: _indexResponse } = await client.index({
        index: 'chat-messages',
        id,
        body,
      }).catch((err) => {
        console.error(`* failed to index message in Elasticsearch: ${err.message}`);
        return;
      });
      
      // Check if we're rate limited
      await limiter.consume(tags['display-name']).catch((err) => {
        console.error(err.message);
        twitch.say(channel, `buh ${tags['display-name']} you're sending too many messages`);
        return;
      });

      // Get the last 5 messages from Elasticsearch for context
      const searchResponse = await client.search({
        index: 'chat-messages',
        body: {
          query: {
            bool: {
              must: [
                {
                  match: {
                    user: tags['display-name'],
                  },
                },
                {
                  exists: {
                    field: 'aiMessage',
                  },
                },
                {
                  exists: {
                    field: 'userMessage',
                  },
                },
                {
                  range: {
                    timestamp: {
                      gte: 'now-12h',
                    },
                  },
                },
              ],
            },
          },
          sort: [
            {
              timestamp: {
                order: 'desc',
              },
            },
          ],
          size: 5,
        },
      }).catch((err) => {
        console.error(`* failed to search for messages in Elasticsearch: ${err.message}`);
        return;
      });

      // Add the last 5 messages to the prompt
      const hits = searchResponse.hits?.hits;
      if (hits && hits.length > 0) {
        for (let i=hits.length-1; i>=0; i--) {
          messages.push({
            role: i === hits.length-1 ? "system" : "user",
            content: i === hits.length-1 ? prompt.replace('${message}', hits[i]._source.userMessage) : hits[i]._source.userMessage,
          });
          messages.push({
            role: "assistant",
            content: hits[i]._source.aiMessage,
          });
        }
        messages.push({
          role: "user",
          content: message,
        });
      } else if (hits && hits.length === 0) {
        messages.push({
          role: "system",
          content: prompt,
        });
      }

      console.log(`messages: ${inspect(messages)}`);
      
      // Call OpenAI API to generate a response
      const gptResponse = await openaiApi.createChatCompletion({
        model: 'gpt-3.5-turbo',
        messages,
        temperature: 0.9,
      }).catch((err) => {
        console.error(err.response.data.error.message);
        if (err.response.data.error.message.includes('overloaded')) {
          twitch.say(channel, "SCHIZO im overloaded gimme a minute");
          return;
        } else {
          twitch.say(channel, "IMDEAD something went wrong");
          return;
        }
      });

      console.log(gptResponse);

      // Send the response back to the Twitch chat
      const gptChatMessage = gptResponse.data.choices[0].message?.content?.trim();
      console.log(`* sending message to ${channel}: ${gptChatMessage}`);
      twitch.say(channel, gptChatMessage);

      // Index the response in Elasticsearch
      const { body: _updateResponse } = await client.update({
        index: 'chat-messages',
        id,
        body: {
          doc: {
            aiMessage: gptChatMessage,
          },
        },
      }).catch((err) => {
        console.error(`* failed to index response in Elasticsearch: ${err.message}`);
        return;
      });
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
