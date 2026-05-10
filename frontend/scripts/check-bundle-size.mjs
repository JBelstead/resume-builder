import { readFileSync, readdirSync } from 'fs'
import { gzipSizeSync } from 'gzip-size'
import { join } from 'path'

const DIST = new URL('../dist/assets', import.meta.url).pathname
const LIMIT_BYTES = 250 * 1024 // 250 KB

let totalGzip = 0
const files = readdirSync(DIST).filter(f => f.endsWith('.js') && f.includes('index'))

for (const file of files) {
  const content = readFileSync(join(DIST, file))
  const gz = gzipSizeSync(content)
  totalGzip += gz
  console.log(`  ${file}: ${(gz / 1024).toFixed(1)} KB gzip`)
}

console.log(`\nTotal main bundle: ${(totalGzip / 1024).toFixed(1)} KB gzip`)
console.log(`Limit: ${LIMIT_BYTES / 1024} KB gzip`)

if (totalGzip > LIMIT_BYTES) {
  console.error(`\n❌ Bundle exceeds 250 KB gzip limit!`)
  process.exit(1)
}

console.log(`\n✅ Bundle size within limit.`)
