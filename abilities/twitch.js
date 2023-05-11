import dotenv from 'dotenv';
import handlebars from 'handlebars';
import { inspect } from 'util';
import * as fs from 'fs';
import { RateLimiterMemory } from 'rate-limiter-flexible';
import { client } from 'tmi.js';
import logger from './logging.js';
import {
  indexMessage,
  searchMessages,
  filterAiUpdate,
  anythingAiUpdate
} from './elasticsearch.js';
import { sendChatGpt } from './chatgpt.js';

dotenv.config();

const botName = process.env.BOT_USERNAME;

const limiter = new RateLimiterMemory({
  points: 1,
  duration: 5,
});

const twitchOpts = {
  identity: {
    username: process.env.BOT_USERNAME,
    password: `oauth:${process.env.TWITCH_TOKEN}`,
  },
  channels: process.env.CHANNELS.split(','),
};

const twitch = new client(twitchOpts);

twitch.on('message', onTwitchMessageHandler);
twitch.on('connected', onTwitchConnectedHandler);

async function onTwitchMessageHandler(channel, tags, rawMessage, self) {
  if (self) return;

  const userMessage = rawMessage.trim();

  if (userMessage.includes(botName)) {
    const user = tags['display-name'];

    try {
      logger.trace(`* ${user} said ${userMessage}`);
      await limiter.consume(user).catch((err) => {
        logger.warn(err.message);
        return;
      });
      logger.trace(`* ${user} passed rate limit check`);

      const id = await indexMessage(user, userMessage, botName).catch((err) => {
        logger.warn(`* failed to index user message in Elasticsearch: ${err.message}`);
        return;
      });
      logger.trace(`* indexed as ${id}`);

      const filterGptTemplate = fs.readFileSync("prompts/FilterGPT.hbs", "utf8");
      const filterGptRendered = handlebars.compile(filterGptTemplate)({ botName, user, userMessage });
      logger.trace(`* rendered FilterGPT template: ${filterGptRendered}`);

      const filtered = await sendChatGpt([{role: "system", content: filterGptRendered}]).catch((err) => {
        logger.error(err.response.data.error.message);
        if (err.response.data.error.message.includes('overloaded')) {
          twitch.say(channel, "SCHIZO im overloaded gimme a minute");
          return;
        } else {
          twitch.say(channel, "IMDEAD something went wrong");
          return;
        }
      });
      logger.trace(`* received FilterGPT response: ${filtered}`);

      await filterAiUpdate(id, filtered, botName).catch((err) => {
        logger.warn(`* failed to update ${id} with FilterGPT response in Elasticsearch: ${err.message}`);
        return;
      });
      logger.trace(`* updated ${id} with FilterGPT response`);

      const anythingAiTemplate = fs.readFileSync("prompts/AnythingAI.hbs", "utf8");
      const anythingAiRendered = handlebars.compile(anythingAiTemplate)({ botName, filtered });
      logger.trace(`* rendered AnythingAI template: ${anythingAiRendered}`);

      const searchResponse = await searchMessages(user, botName).catch((err) => {
        logger.warn(`* failed to search messages in Elasticsearch: ${err.message}`);
        return;
      });
      logger.trace(`* searched messages in Elasticsearch`);

      const hits = searchResponse.hits?.hits ?? [];
      logger.trace(`* hits from Elasticsearch: ${inspect(hits)}`);
      const filterAiMessages = hits.map(hit => ({ role: "system", content: hit._source.filterAiMessage }));

      const messages = [...filterAiMessages, {role: "system", content: anythingAiRendered}];
      logger.info(`* messages to send to ChatGPT: ${inspect(messages)}`);

      const gptChatMessage = await sendChatGpt(messages).catch((err) => {
        logger.error(err.response.data.error.message);
        if (err.response.data.error.message.includes('overloaded')) {
          twitch.say(channel, "SCHIZO im overloaded gimme a minute");
          return;
        } else {
          twitch.say(channel, "IMDEAD something went wrong");
          return;
        }
      });
      logger.trace(`* received ChatGPT response: ${gptChatMessage}`);

      logger.log(`* sending message to ${channel}: ${gptChatMessage}`);
      twitch.say(channel, gptChatMessage);

      await anythingAiUpdate(id, gptChatMessage, botName).catch((err) => {
        logger.warn(`* failed to update ${id} with FilterGPT response in Elasticsearch: ${err.message}`);
        return;
      });
    } catch (err) {
      logger.error(err);
      twitch.say(channel, "MrDestructoid something went wrong");
    }
  }
}

// Called every time the bot connects to Twitch chat
function onTwitchConnectedHandler(addr, port) {
  logger.info(`* Connected to ${addr}:${port}`);
}

export default twitch;
