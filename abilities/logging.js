import log4js from 'log4js';

log4js.configure({
  appenders: {
    console: { type: 'console' },
    file: { type: 'file', filename: 'logs/bot.log' },
  },
  categories: {
    default: { appenders: ['console', 'file'], level: 'trace' },
  },
});

export default log4js.getLogger('bot');
