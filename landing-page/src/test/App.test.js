import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/svelte";
import App from "../App.svelte";

describe("App Component", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it("renders the main title", () => {
    render(App);
    expect(screen.getByText(/Transform Your Slack Into a/i)).toBeTruthy();
    expect(screen.getByText(/Learning Platform/i)).toBeTruthy();
  });

  it("renders the navigation bar with logo", () => {
    const { container } = render(App);
    const logo = container.querySelector(".logo-text");
    expect(logo).toBeTruthy();
    expect(logo.textContent).toBe("Daily Learner");
    const logoIcon = container.querySelector(".logo-icon");
    expect(logoIcon).toBeTruthy();
    expect(logoIcon.textContent).toBe("📚");
  });

  it("displays all feature cards", () => {
    render(App);
    expect(screen.getByText("Daily Summaries")).toBeTruthy();
    expect(screen.getByText("Tech Tips")).toBeTruthy();
    expect(screen.getByText("Slack Integration")).toBeTruthy();
    expect(screen.getByText("Self-Hosted")).toBeTruthy();
  });

  it("renders feature descriptions", () => {
    render(App);
    expect(screen.getByText(/Get book chapter summaries/i)).toBeTruthy();
    expect(
      screen.getByText(/Receive daily tips about your favorite technologies/i),
    ).toBeTruthy();
    expect(screen.getByText(/Works seamlessly in Slack/i)).toBeTruthy();
    expect(screen.getByText(/Deploy on your own infrastructure/i)).toBeTruthy();
  });

  it("displays slash commands section", () => {
    render(App);
    expect(screen.getByText("Simple Slash Commands")).toBeTruthy();
    expect(screen.getByText("/readme <book>")).toBeTruthy();
    expect(screen.getByText("/tips <technology>")).toBeTruthy();
    expect(screen.getByText("/list")).toBeTruthy();
    expect(screen.getByText("/reset")).toBeTruthy();
  });

  it("shows command descriptions", () => {
    render(App);
    expect(screen.getByText("Start daily book summaries")).toBeTruthy();
    expect(screen.getByText("Get daily tech tips")).toBeTruthy();
    expect(screen.getByText("View all active summaries")).toBeTruthy();
    expect(screen.getByText("Clear schedule and start fresh")).toBeTruthy();
  });

  it("renders the Slack window mockup", () => {
    const { container } = render(App);
    expect(screen.getByText("#daily-learning")).toBeTruthy();
    const messageName = container.querySelector(".message-name");
    expect(messageName).toBeTruthy();
    expect(messageName.textContent).toBe("Daily Learner");
    expect(screen.getByText("9:00 AM")).toBeTruthy();
  });

  it("displays the hero description", () => {
    render(App);
    expect(
      screen.getByText(/Daily Learner delivers bite-sized book summaries/i),
    ).toBeTruthy();
    expect(screen.getByText(/Perfect for continuous learning/i)).toBeTruthy();
  });

  it("renders CTA buttons", () => {
    render(App);
    const getStartedButtons = screen.getAllByText(/Get Started/i);
    expect(getStartedButtons.length).toBeGreaterThan(0);
  });

  it("includes GitHub links", () => {
    const { container } = render(App);
    const links = container.querySelectorAll('a[href*="github.com"]');
    expect(links.length).toBeGreaterThan(0);
  });

  it("displays the footer", () => {
    render(App);
    expect(
      screen.getByText(/Built with ❤️ for continuous learners/i),
    ).toBeTruthy();
    expect(screen.getByText(/MIT License/i)).toBeTruthy();
  });

  it('renders the "Learn Every Day" badge', () => {
    render(App);
    expect(screen.getByText("Learn Every Day")).toBeTruthy();
  });

  it("shows the CTA section", () => {
    render(App);
    expect(screen.getByText("Start Learning Today")).toBeTruthy();
    expect(
      screen.getByText(/Self-host Daily Learner in minutes/i),
    ).toBeTruthy();
  });

  it("becomes visible after mount timeout", () => {
    const { container } = render(App);
    const mainContainer = container.querySelector(".container");

    expect(mainContainer.classList.contains("visible")).toBe(false);
    vi.advanceTimersByTime(100);

    vi.runAllTimers();
  });
});
