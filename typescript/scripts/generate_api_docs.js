'use strict'

const {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} = require('fs')
const path = require('path')
const { runWithFallback } = require('./run_with_fallback')

const projectRoot = path.resolve(__dirname, '..')
const docsRoot = path.join(projectRoot, 'docs', 'api-preview')
const docsDir = path.join(docsRoot, 'latest')
const legacyDocsDir = path.join(docsRoot, 'typescript')
const outputDir = path.join(projectRoot, '.typedoc-output')

const docMappings = [
  { target: 'common-features/basics/agentbay.md', symbol: 'AgentBay', identifiers: ['Class AgentBay', 'AgentBay'] },
  { target: 'common-features/basics/session.md', symbol: 'Session', identifiers: ['Class Session', 'Session'] },
  { target: 'common-features/basics/command.md', symbol: 'Command', identifiers: ['Class Command', 'Command'] },
  {
    target: 'common-features/basics/context.md',
    symbol: 'ContextService',
    identifiers: ['Class ContextService', 'Class Context', 'ContextService', 'Context'],
  },
  { target: 'common-features/basics/context-manager.md', symbol: 'ContextManager', identifiers: ['Class ContextManager', 'ContextManager'] },
  { target: 'common-features/basics/filesystem.md', symbol: 'FileSystem', identifiers: ['Class FileSystem', 'FileSystem'] },
  {
    target: 'common-features/basics/logging.md',
    symbol: 'logger',
    identifiers: ['logger', 'log'],
  },
  { target: 'common-features/advanced/agent.md', symbol: 'Agent', identifiers: ['Class Agent', 'Agent'] },
  { target: 'common-features/advanced/oss.md', symbol: 'Oss', identifiers: ['Class Oss', 'Oss'] },
  { target: 'browser-use/browser.md', symbol: 'Browser', identifiers: ['Class Browser', 'Browser'] },
  {
    target: 'browser-use/extension.md',
    symbol: 'ExtensionsService',
    identifiers: ['Class ExtensionsService', 'Class Extension', 'ExtensionsService', 'Extension'],
  },
  { target: 'codespace/code.md', symbol: 'Code', identifiers: ['Class Code', 'Code'] },
  { target: 'computer-use/computer.md', symbol: 'Computer', identifiers: ['Class Computer', 'Computer'] },
  { target: 'mobile-use/mobile.md', symbol: 'Mobile', identifiers: ['Class Mobile', 'Mobile'] },
]

const symbolToTarget = new Map()
for (const mapping of docMappings) {
  if (mapping.symbol) {
    symbolToTarget.set(mapping.symbol.toLowerCase(), mapping.target)
  }
}

function cleanDirectory(dirPath) {
  if (existsSync(dirPath)) {
    rmSync(dirPath, { recursive: true, force: true })
  }
  mkdirSync(dirPath, { recursive: true })
}

function runTypedoc() {
  cleanDirectory(outputDir)

  const result = runWithFallback(
    'typedoc',
    'typedoc@0.25.0',
    ['--options', 'typedoc.json', '--out', outputDir],
    {
      cwd: projectRoot,
      env: { ...process.env, FORCE_COLOR: '1' },
      stdio: 'pipe',
    },
  )

  if (result.status !== 0) {
    const outputChunks = []
    if (result.stdout) {
      outputChunks.push(result.stdout)
    }
    if (result.stderr) {
      outputChunks.push(result.stderr)
    }
    const output = outputChunks.length ? Buffer.concat(outputChunks).toString() : 'Unknown error'
    throw new Error(`TypeDoc generation failed:\n${output}`)
  }
}

function removeLegacyDocsDir() {
  if (existsSync(legacyDocsDir)) {
    rmSync(legacyDocsDir, { recursive: true, force: true })
  }
}

function findMarkdownFiles(dir) {
  const results = []
  for (const entry of readdirSync(dir)) {
    const fullPath = path.join(dir, entry)
    const stats = statSync(fullPath)
    if (stats.isDirectory()) {
      results.push(...findMarkdownFiles(fullPath))
    } else if (stats.isFile() && entry.endsWith('.md')) {
      results.push(fullPath)
    }
  }
  return results
}

function extractTitle(content) {
  const lines = content.split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed.startsWith('#')) {
      return trimmed.replace(/^#+\s*/, '')
    }
  }
  return ''
}

function loadPages() {
  const files = findMarkdownFiles(outputDir)
  return files.map((file) => {
    const content = readFileSync(file, 'utf8')
    const title = extractTitle(content)
    return { title, content, source: file }
  })
}

function normalize(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
}

function resolvePage(pages, identifiers) {
  for (const identifier of identifiers) {
    const normalizedIdentifier = normalize(identifier)

    const exact = pages.find((page) => normalize(page.title) === normalizedIdentifier)
    if (exact) {
      return exact
    }

    const partial = pages.find((page) => normalize(page.title).includes(normalizedIdentifier))
    if (partial) {
      return partial
    }
  }

  throw new Error(`Unable to locate documentation page for identifiers: ${identifiers.join(', ')}`)
}

function writeDocument(targetRelativePath, markdown) {
  const targetPath = path.join(docsDir, targetRelativePath)
  const parentDir = path.dirname(targetPath)
  if (!existsSync(parentDir)) {
    mkdirSync(parentDir, { recursive: true })
  }

  writeFileSync(targetPath, normalizeContent(markdown, targetRelativePath), 'utf8')
}

function normalizeContent(content, targetRelativePath) {
  const lines = content.split(/\r?\n/)

  while (lines.length && lines[0].includes('**Docs**')) {
    lines.shift()
  }

  while (lines.length && lines[0].trim() === '') {
    lines.shift()
  }

  if (lines.length && lines[0].trim() === '***') {
    lines.shift()
  }

  while (lines.length && lines[0].trim() === '') {
    lines.shift()
  }

  const headingIndex = lines.findIndex((line) => line.trim().startsWith('#'))
  if (headingIndex > 0) {
    const heading = lines[headingIndex].replace(/^#+\s*/, '# ')
    lines.splice(0, headingIndex + 1, heading)
  } else if (headingIndex === 0) {
    lines[0] = lines[0].replace(/^#+\s*/, '# ')
  }

  const normalized = lines.join('\n')
  const rewritten = rewriteLinks(normalized, targetRelativePath)
  return rewritten.trimEnd() + '\n'
}

function rewriteLinks(markdown, targetRelativePath) {
  const currentPath = path.join(docsDir, targetRelativePath)

  return markdown.replace(/\[([^\]]+)]\(([^)]+)\)/g, (match, label, link) => {
    if (link.startsWith('http') || link.startsWith('#')) {
      return match
    }

    const [pathPart, hash] = link.split('#')
    if (!pathPart.endsWith('.md')) {
      return match
    }

    const symbol = path.basename(pathPart, '.md').toLowerCase()
    const mappedTarget = symbolToTarget.get(symbol)

    if (!mappedTarget) {
      return `\`${label}\``
    }

    const toPath = path.join(docsDir, mappedTarget)
    const relative = path.relative(path.dirname(currentPath), toPath).replace(/\\/g, '/')
    const anchor = hash ? `#${hash}` : ''
    return `[${label}](${relative}${anchor})`
  })
}

function collectDirectoryContent(relativeDir) {
  const dirPath = path.join(outputDir, relativeDir)
  if (!existsSync(dirPath)) {
    throw new Error(`TypeDoc output directory not found: ${relativeDir}`)
  }

  const files = findMarkdownFiles(dirPath).sort((a, b) => {
    const aName = path.basename(a)
    const bName = path.basename(b)
    if (aName === 'README.md') {
      return -1
    }
    if (bName === 'README.md') {
      return 1
    }
    return a.localeCompare(b)
  })

  const contents = files.map((file) => readFileSync(file, 'utf8'))
  return contents.join('\n\n')
}

function collectPagesContent(pages, identifiers) {
  const seenSources = new Set()
  const contents = []

  for (const identifier of identifiers) {
    const page = resolvePage(pages, [identifier])
    if (seenSources.has(page.source)) {
      continue
    }
    seenSources.add(page.source)
    contents.push(page.content)
  }

  if (!contents.length) {
    throw new Error(`No pages found for identifiers: ${identifiers.join(', ')}`)
  }

  return contents.join('\n\n')
}

function createReadme() {
  const lines = [
    '# TypeScript SDK API Reference (Preview)',
    '',
    'These documents are generated automatically using TypeDoc. Run `npm run docs:generate` to refresh them after changing the SDK.',
    '',
    '## Structure',
  ]

  const groups = {}

  for (const mapping of docMappings) {
    const parts = mapping.target.split('/')
    const groupKey = parts.slice(0, parts.length - 1).join('/') || '.'
    groups[groupKey] = groups[groupKey] ?? []
    groups[groupKey].push(parts[parts.length - 1])
  }

  const sortedGroups = Object.keys(groups).sort()
  for (const group of sortedGroups) {
    lines.push(`- \`${group}\``)
    const files = groups[group].sort()
    for (const file of files) {
      lines.push(`  - ${file}`)
    }
  }

  lines.push('')

  writeDocument('README.md', lines.join('\n'))
}

function enhanceDocumentation() {
  const enhanceScript = path.join(__dirname, 'enhance-typedoc-output.ts')
  if (!existsSync(enhanceScript)) {
    console.warn('⚠️  Enhancement script not found, skipping metadata injection')
    return
  }

  try {
    const result = runWithFallback(
      'ts-node',
      'ts-node@10.9.2',
      [enhanceScript],
      {
        cwd: projectRoot,
        stdio: 'inherit',
      },
    )

    if (result.status !== 0) {
      console.warn('⚠️  Documentation enhancement failed, continuing without metadata')
    }
  } catch (error) {
    console.warn('⚠️  Documentation enhancement failed:', error.message)
  }
}

function main() {
  runTypedoc()

  removeLegacyDocsDir()
  cleanDirectory(docsDir)

  const pages = loadPages()

  for (const mapping of docMappings) {
    let rawContent
    if (mapping.collectDir) {
      rawContent = collectDirectoryContent(mapping.collectDir)
    } else if (mapping.collectPages && mapping.collectPages.length) {
      rawContent = collectPagesContent(pages, mapping.collectPages)
    } else {
      if (!mapping.identifiers || !mapping.identifiers.length) {
        throw new Error(`No identifiers provided for mapping target ${mapping.target}`)
      }
      const page = resolvePage(pages, mapping.identifiers)
      rawContent = page.content
    }

    writeDocument(mapping.target, rawContent)
  }

  createReadme()

  if (existsSync(outputDir)) {
    rmSync(outputDir, { recursive: true, force: true })
  }

  process.stdout.write('✅ TypeScript API documentation generated at docs/api-preview/latest\n')

  enhanceDocumentation()
}

if (require.main === module) {
  try {
    main()
  } catch (error) {
    if (error instanceof Error) {
      console.error(`❌ Failed to generate TypeScript API documentation\n${error.message}`)
    } else {
      console.error('❌ Failed to generate TypeScript API documentation', error)
    }
    process.exit(1)
  }
}

module.exports = { main }

