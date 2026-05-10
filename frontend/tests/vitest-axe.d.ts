export {}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare module 'vitest-axe' {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  export const toHaveNoViolations: Record<string, any>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  export const axe: (...args: any[]) => Promise<any>
}

declare module 'vitest' {
  interface Assertion {
    toHaveNoViolations(): void
  }
}
