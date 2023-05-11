import { Configuration as OpenAIConfig, OpenAIApi } from 'openai';
import dotenv from 'dotenv';
dotenv.config();

const openaiApiKey = process.env.OPENAI_API_KEY;
const openaiConfig = new OpenAIConfig({
  apiKey: openaiApiKey,
});

export const openaiApi = new OpenAIApi(openaiConfig);

export const sendChatGpt = async (messages) => {
  const response = await openaiApi.createChatCompletion({
    model: process.env.OPENAI_ENGINE,
    messages,
    temperature: 0.9,
  });

  return response.data?.choices[0].message?.content?.trim();
}
