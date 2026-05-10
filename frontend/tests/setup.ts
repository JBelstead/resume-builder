import { vi } from 'vitest'

// Stub window.open to avoid jsdom navigation errors
vi.stubGlobal('open', vi.fn())

// Stub window.confirm
vi.stubGlobal('confirm', vi.fn(() => true))
