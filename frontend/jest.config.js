/** jest.config.js — runs TypeScript tests via ts-jest */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.test.ts'],
  moduleNameMapper: {
    // Stub out electron in tests
    electron: '<rootDir>/src/__mocks__/electron.ts',
  },
};
