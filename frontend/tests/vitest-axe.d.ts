declare module 'vitest-axe' {
  export const toHaveNoViolations: Record<string, (...args: unknown[]) => unknown>
}

declare module 'vitest' {
  interface Assertion {
    toHaveNoViolations(): void
  }
}
