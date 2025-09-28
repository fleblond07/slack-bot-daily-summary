# 📚 Daily Learner

[![CI](https://github.com/fleblond07/slack-bot-daily-summary/actions/workflows/ci.yml/badge.svg)](https://github.com/fleblond07/slack-bot-daily-summary/actions/workflows/ci.yml)
[![Slack](https://img.shields.io/badge/Slack-App-blueviolet?logo=slack&logoColor=white)]
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)]

**Daily Learner** is a Slack app that helps you learn a little bit every day.
Pick a book, and every morning you’ll get a summary of a chapter (or a few pages) in a dedicated Slack channel.

Perfect for continuous learning without overwhelming your schedule.

---

## ✨ Features

- ⏰ **Daily summaries** of the book you choose.
- 💬 Works directly in Slack using slash commands.
- 🛠 Simple setup — self-host or extend as you like.

### Available Commands

- `/readme <book>` → Register the bot to summarize `<book>` every day.
- `/tips <technology>` -> Register the bot to give you a tip about a specific technology.
- `/list` → Show channels + registered summaries.
- `/reset` → Clear the schedule and start fresh.
- `/hello` → Quick test to check the bot is working.

---

## 🚀 Self-Hosting

You can run **Daily Learner** yourself in just a few steps:

1. **Create a Slack app**
   - Go to [api.slack.com/apps](https://api.slack.com/apps).
   - Use the **manifest.json** provided in this repo.

2. **Fork this repository**

3. **Set up secrets**
   - Configure your secrets (SSH keys, tokens, environment variables) in your fork’s GitHub Actions settings.

4. **Deploy with your domain**
   - Point your Slack app’s request URLs to your deployed app (your domain).
   - Restart the app, and you’re ready to go!

---

## 🤝 Contributing

Contributions are always welcome!

- Fork the repo.
- Create your branch.
- Open a Pull Request.

I’ll review it and merge if it makes sense 👍.

---

## 🔮 Upcoming Features

Here’s what’s next for Daily Learner:

- 🌍 Support for **multiple Slack workspaces**.
- 🧩 More flexibility in scheduling & content sources.

---

## 📜 License

MIT License — feel free to use, modify, and share.
