export const features = [
  {
    icon: '⏰',
    title: 'Daily Summaries',
    description: 'Get book chapter summaries delivered every morning to your Slack channel'
  },
  {
    icon: '💡',
    title: 'Tech Tips',
    description: 'Receive daily tips about your favorite technologies to expand your knowledge'
  },
  {
    icon: '💬',
    title: 'Slack Integration',
    description: 'Works seamlessly in Slack with simple slash commands'
  },
  {
    icon: '🛠',
    title: 'Self-Hosted',
    description: 'Deploy on your own infrastructure with full control'
  }
]

export const commands = [
  { cmd: '/readme <book>', desc: 'Start daily book summaries' },
  { cmd: '/tips <technology>', desc: 'Get daily tech tips' },
  { cmd: '/list', desc: 'View all active summaries' },
  { cmd: '/reset', desc: 'Clear schedule and start fresh' }
]
