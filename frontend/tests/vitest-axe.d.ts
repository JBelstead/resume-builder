export {}

declare module 'vitest-axe' {
  export const toHaveNoViolations: Record<string, unknown>
  export function axe(...args: unknown[]): Promise<unknown>
}

declare module 'vitest' {
  interface Assertion {
    toHaveNoViolations(): void
  }
}
