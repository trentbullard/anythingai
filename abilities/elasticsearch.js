import { Client } from '@elastic/elasticsearch';
import dotenv from 'dotenv';
dotenv.config();

const client = new Client({ node: process.env.ELASTICSEARCH_URL });

export const indexMessage = async (user, userMessage, index) => {
  const timestamp = new Date().toISOString();
  const body = {
    user,
    userMessage,
    timestamp,
  };
  const id = `${user}-${timestamp}`;

  await client.index({
    index,
    id,
    body,
  });

  return id;
};


export const searchMessages = (user, index) => client.search({
  index,
  body: {
    query: {
      bool: {
        must: [
          {
            match: {
              user,
            },
          },
          {
            exists: {
              field: 'filterAiMessage',
            },
          },
          {
            exists: {
              field: 'anythingAiMessage',
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
});

export const filterAiUpdate = (id, filterAiMessage, index) => client.update({
  index,
  id,
  body: {
    doc: {
      filterAiMessage,
    },
  },
});

export const anythingAiUpdate = (id, anythingAiMessage, index) => client.update({
  index,
  id,
  body: {
    doc: {
      anythingAiMessage,
    },
  },
});
