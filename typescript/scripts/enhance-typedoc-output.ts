#!/usr/bin/env ts-node
/**
 * Enhanced TypeDoc output post-processor
 * This script injects metadata (tutorials, related resources) into generated markdown files
 */

/* eslint-disable @typescript-eslint/no-var-requires */
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

declare const __dirname: string;
declare const require: any;
declare const module: any;

interface TutorialConfig {
  url: string;
  text: string;
  description: string;
}

interface ResourceConfig {
  name: string;
  module: string;
  category?: string;
}

interface ModuleConfig {
  tutorial?: TutorialConfig;
  related_resources?: ResourceConfig[];
  emoji?: string;
  category?: string;
}

interface Metadata {
  modules: Record<string, ModuleConfig>;
}

function loadMetadata(): Metadata {
  const metadataPath = path.join(__dirname, '../../docs/doc-metadata.yaml');
  const content = fs.readFileSync(metadataPath, 'utf8');
  return yaml.load(content) as Metadata;
}

function extractModuleName(filePath: string): string {
  const basename = path.basename(filePath, '.md');
  return basename;
}

function getTutorialSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.tutorial) {
    return '';
  }

  const emoji = config.emoji || '📖';
  return `## ${emoji} Related Tutorial

- [${config.tutorial.text}](${config.tutorial.url}) - ${config.tutorial.description}

`;
}

function calculateResourcePath(resource: ResourceConfig, moduleConfig: ModuleConfig): string {
  const targetCategory = resource.category || 'common-features/basics';
  const currentCategory = moduleConfig.category || 'common-features/basics';
  const module = resource.module;

  // If same category, just use module name
  if (targetCategory === currentCategory) {
    return `${module}.md`;
  }

  // Calculate relative path from current category to target category
  const currentParts = currentCategory.split('/');
  const targetParts = targetCategory.split('/');

  // Go up from current directory
  let relativePath = '';
  for (let i = 0; i < currentParts.length; i++) {
    relativePath += '../';
  }

  // Go down to target directory
  relativePath += targetParts.join('/') + '/' + module + '.md';

  return relativePath;
}

function getRelatedResourcesSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.related_resources || config.related_resources.length === 0) {
    return '';
  }

  const lines = ['## Related Resources\n'];
  for (const resource of config.related_resources) {
    const resourcePath = calculateResourcePath(resource, config);
    lines.push(`- [${resource.name}](${resourcePath})`);
  }
  lines.push('\n');

  return lines.join('\n');
}

function addAfterTitle(content: string, insertion: string): string {
  const lines = content.split('\n');
  let titleIndex = -1;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('# ')) {
      titleIndex = i;
      break;
    }
  }

  if (titleIndex === -1) {
    return insertion + content;
  }

  lines.splice(titleIndex + 1, 0, '', insertion.trimEnd());
  return lines.join('\n');
}

function addBeforeFooter(content: string, insertion: string): string {
  // Look for the documentation footer marker (standalone line with ---)
  const lines = content.split('\n');
  let footerIndex = -1;

  // Find the last standalone --- line (not in a table)
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim();
    if (line === '---') {
      // Check if this is not part of a table (previous line should not be a table row)
      if (i === 0 || !lines[i - 1].includes('|')) {
        footerIndex = i;
        break;
      }
    }
  }

  if (footerIndex === -1) {
    return content + '\n' + insertion;
  }

  lines.splice(footerIndex, 0, insertion.trimEnd(), '');
  return lines.join('\n');
}

function enhanceMarkdownFile(filePath: string, metadata: Metadata): void {
  let content = fs.readFileSync(filePath, 'utf8');
  const moduleName = extractModuleName(filePath);
  const moduleConfig = metadata.modules?.[moduleName];

  if (!moduleConfig) {
    return;
  }

  // Add tutorial section after title (only if not already present)
  const tutorialSection = getTutorialSection(moduleName, metadata);
  if (tutorialSection && !content.includes('Related Tutorial')) {
    content = addAfterTitle(content, tutorialSection);
  }

  // Add related resources before footer (only if not already present)
  const resourcesSection = getRelatedResourcesSection(moduleName, metadata);
  if (resourcesSection && !content.includes('## Related Resources')) {
    content = addBeforeFooter(content, resourcesSection);
  }

  fs.writeFileSync(filePath, content, 'utf8');
}

function enhanceAllMarkdownFiles(docsDir: string, metadata: Metadata): void {
  if (!fs.existsSync(docsDir)) {
    console.error(`Documentation directory not found: ${docsDir}`);
    return;
  }

  function processDirectory(dir: string): void {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        processDirectory(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.md') && entry.name !== 'README.md') {
        console.log(`Enhancing: ${fullPath}`);
        enhanceMarkdownFile(fullPath, metadata);
      }
    }
  }

  processDirectory(docsDir);
}

function main(): void {
  const metadata = loadMetadata();
  const docsDir = path.join(__dirname, '../docs/api-preview/latest');

  console.log('Enhancing TypeDoc output with metadata...');
  enhanceAllMarkdownFiles(docsDir, metadata);
  console.log('Enhancement complete!');
}

if (require.main === module) {
  main();
}

