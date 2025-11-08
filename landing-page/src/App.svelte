<script>
  import { onMount } from 'svelte'
  import { features, commands } from './constants.js'
  import './App.css'

  let visible = false

  onMount(() => {
    setTimeout(() => {
      visible = true
    }, 100)
  })
</script>

<div class="container" class:visible>
  <nav class="nav">
    <div class="nav-content">
      <div class="logo">
        <span class="logo-icon">📚</span>
        <span class="logo-text">Daily Learner</span>
      </div>
      <a href="https://github.com/fleblond07/slack-bot-daily-summary" target="_blank" rel="noopener" class="github-link">
        GitHub
      </a>
    </div>
  </nav>

  <main>
    <section class="hero">
      <div class="hero-content">
        <div class="badge">Learn Every Day</div>
        <h1 class="hero-title">
          Transform Your Slack Into a
          <span class="gradient-text">Learning Platform</span>
        </h1>
        <p class="hero-description">
          Daily Learner delivers bite-sized book summaries and tech tips directly to your Slack workspace.
          Perfect for continuous learning without overwhelming your schedule.
        </p>
        <div class="cta-buttons">
          <a href="https://github.com/fleblond07/slack-bot-daily-summary#-self-hosting" target="_blank" rel="noopener" class="btn btn-primary">
            Get Started
          </a>
          <a href="https://github.com/fleblond07/slack-bot-daily-summary" target="_blank" rel="noopener" class="btn btn-secondary">
            View on GitHub
          </a>
        </div>
      </div>
      <div class="hero-visual">
        <div class="slack-window">
          <div class="window-header">
            <div class="window-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div class="window-title">#daily-learning</div>
          </div>
          <div class="window-content">
            <div class="message">
              <div class="message-avatar">📚</div>
              <div class="message-body">
                <div class="message-header">
                  <span class="message-name">Daily Learner</span>
                  <span class="message-time">9:00 AM</span>
                </div>
                <div class="message-text">
                  <strong>Chapter 3: Clean Code Principles</strong><br/>
                  Today's summary covers naming conventions and function design...
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="section-header">
        <h2>Everything You Need to Learn Daily</h2>
        <p>Simple, powerful features to help you grow every day</p>
      </div>
      <div class="features-grid">
        {#each features as feature, i}
          <div class="feature-card" style="animation-delay: {i * 0.1}s">
            <div class="feature-icon">{feature.icon}</div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </div>
        {/each}
      </div>
    </section>

    <section class="commands">
      <div class="section-header">
        <h2>Simple Slash Commands</h2>
        <p>Control everything directly from Slack</p>
      </div>
      <div class="commands-list">
        {#each commands as command, i}
          <div class="command-item" style="animation-delay: {i * 0.1}s">
            <code class="command-code">{command.cmd}</code>
            <span class="command-desc">{command.desc}</span>
          </div>
        {/each}
      </div>
    </section>

    <section class="cta-section">
      <div class="cta-content">
        <h2>Start Learning Today</h2>
        <p>Self-host Daily Learner in minutes and transform your Slack workspace into a continuous learning environment</p>
        <a href="https://github.com/fleblond07/slack-bot-daily-summary#-self-hosting" target="_blank" rel="noopener" class="btn btn-primary btn-large">
          Get Started Now
        </a>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="footer-content">
      <p>Built with ❤️ for continuous learners</p>
      <p class="footer-links">
        <a href="https://github.com/fleblond07/slack-bot-daily-summary" target="_blank" rel="noopener">GitHub</a>
        <span>•</span>
        <a href="https://github.com/fleblond07/slack-bot-daily-summary#-license" target="_blank" rel="noopener">MIT License</a>
      </p>
    </div>
  </footer>
</div>
