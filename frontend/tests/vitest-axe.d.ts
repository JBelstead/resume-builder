export {}

declare module 'vitest-axe' {
  export const toHaveNoViolations: Record<string, (...args: unknown[]) => unknown>
  export const axe: (...args: unknown[]) => Promise<unknown>
}

declare module 'vitest' {
  interface Assertion {
    toHaveNoViolations(): void
  }
}
