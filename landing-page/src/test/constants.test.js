import { describe, it, expect } from 'vitest'
import { features, commands } from '../constants.js'

describe('Constants', () => {
  describe('features', () => {
    it('exports an array of 4 features', () => {
      expect(Array.isArray(features)).toBe(true)
      expect(features).toHaveLength(4)
    })

    it('each feature has required properties', () => {
      features.forEach(feature => {
        expect(feature).toHaveProperty('icon')
        expect(feature).toHaveProperty('title')
        expect(feature).toHaveProperty('description')
        expect(typeof feature.icon).toBe('string')
        expect(typeof feature.title).toBe('string')
        expect(typeof feature.description).toBe('string')
      })
    })

    it('includes expected feature titles', () => {
      const titles = features.map(f => f.title)
      expect(titles).toContain('Daily Summaries')
      expect(titles).toContain('Tech Tips')
      expect(titles).toContain('Slack Integration')
      expect(titles).toContain('Self-Hosted')
    })
  })

  describe('commands', () => {
    it('exports an array of 4 commands', () => {
      expect(Array.isArray(commands)).toBe(true)
      expect(commands).toHaveLength(4)
    })

    it('each command has required properties', () => {
      commands.forEach(command => {
        expect(command).toHaveProperty('cmd')
        expect(command).toHaveProperty('desc')
        expect(typeof command.cmd).toBe('string')
        expect(typeof command.desc).toBe('string')
      })
    })

    it('includes expected commands', () => {
      const cmds = commands.map(c => c.cmd)
      expect(cmds).toContain('/readme <book>')
      expect(cmds).toContain('/tips <technology>')
      expect(cmds).toContain('/list')
      expect(cmds).toContain('/reset')
    })

    it('each command has a non-empty description', () => {
      commands.forEach(command => {
        expect(command.desc.length).toBeGreaterThan(0)
      })
    })
  })
})
