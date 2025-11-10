import { spawnSync } from 'child_process'
import { existsSync, rmSync } from 'fs'
import path from 'path'

describe('TypeScript API documentation generator', () => {
  const packageRoot = path.resolve(__dirname, '..', '..')
  const docsDir = path.join(packageRoot, 'docs', 'api')

  beforeAll(() => {
    if (existsSync(docsDir)) {
      rmSync(docsDir, { recursive: true, force: true })
    }
  })

  it('recreates typed SDK docs in the expected structure', () => {
    const result = spawnSync('npm', ['run', 'docs:generate'], {
      cwd: packageRoot,
      env: { ...process.env, CI: '1' },
      stdio: 'pipe',
    })

    const output = Buffer.concat([
      result.stdout ?? Buffer.alloc(0),
      result.stderr ?? Buffer.alloc(0),
    ]).toString()

    if (result.status !== 0) {
      // eslint-disable-next-line no-console
      console.error(output)
    }

    expect({ status: result.status, output }).toMatchObject({ status: 0 })

    const expectedFiles = [
      'common-features/basics/session.md',
      'common-features/basics/command.md',
      'common-features/advanced/agent.md',
      'computer-use/computer.md',
      'browser-use/browser.md',
    ]

    for (const relativePath of expectedFiles) {
      const target = path.join(docsDir, relativePath)
      expect(existsSync(target)).toBe(true)
    }
  })
})

