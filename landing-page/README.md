# Daily Learner Landing Page

Modern, dark-mode landing page for Daily Learner built with Svelte and Vite.

## Features

- Dark mode design with modern aesthetics
- Subtle animations inspired by LaunchDarkly
- Fully responsive layout
- Fast and lightweight
- Easy to deploy
- Comprehensive unit tests with Vitest
- ESLint for code quality

## Tech Stack

- **Svelte 4**: Reactive UI framework
- **Vite 5**: Fast build tool and dev server
- **Vitest**: Unit testing framework
- **Testing Library**: Component testing utilities
- **ESLint**: Code linting and quality

## Development

### Prerequisites

- Node.js 18+ or Bun

### Install Dependencies

```bash
npm install
# or
bun install
```

### Run Development Server

```bash
npm run dev
# or
bun run dev
```

The site will be available at `http://localhost:5173`

### Run Tests

```bash
npm test
# or
bun test
```

Run tests with UI:

```bash
npm run test:ui
# or
bun run test:ui
```

Run tests with coverage:

```bash
npm run test:coverage
# or
bun run test:coverage
```

### Lint Code

```bash
npm run lint
# or
bun run lint
```

Fix linting issues automatically:

```bash
npm run lint:fix
# or
bun run lint:fix
```

### Build for Production

```bash
npm run build
# or
bun run build
```

This creates an optimized production build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
# or
bun run preview
```
