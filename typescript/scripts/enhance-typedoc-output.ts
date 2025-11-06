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

interface DataTypeInfo {
  name: string;
  description: string;
}

interface ModuleConfig {
  tutorial?: TutorialConfig;
  related_resources?: ResourceConfig[];
  overview?: string;
  requirements?: string[];
  best_practices?: string[];
  data_types?: DataTypeInfo[];
  important_notes?: string[];
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

  // Calculate correct relative path based on category depth
  // From: typescript/docs/api-preview/latest/{category}/{file}.md
  // To: project_root/docs/guides/...
  // Need to go up: {category_depth} + 3 (latest, api-preview, docs) + 1 (typescript) = category_depth + 4
  const category = config.category || 'common-features/basics';
  const categoryDepth = category.split('/').length;
  const depth = categoryDepth + 4; // +4 for latest/api-preview/docs/typescript
  const upLevels = '../'.repeat(depth);

  // Replace the hardcoded path with dynamically calculated one
  let tutorialUrl = config.tutorial.url;
  // Extract the part after 'docs/' from the URL
  const docsMatch = tutorialUrl.match(/docs\/(.+)$/);
  if (docsMatch) {
    tutorialUrl = `${upLevels}docs/${docsMatch[1]}`;
  }

  return `## ${emoji} Related Tutorial

- [${config.tutorial.text}](${tutorialUrl}) - ${config.tutorial.description}

`;
}

function getOverviewSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.overview) {
    return '';
  }

  return `## Overview

${config.overview}

`;
}

function getRequirementsSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.requirements || config.requirements.length === 0) {
    return '';
  }

  const lines = ['## Requirements\n'];
  for (const req of config.requirements) {
    lines.push(`- ${req}`);
  }
  lines.push('\n');

  return lines.join('\n');
}

function getDataTypesSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.data_types || config.data_types.length === 0) {
    return '';
  }

  const lines = ['## Data Types\n'];
  for (const dataType of config.data_types) {
    lines.push(`### ${dataType.name}\n`);
    lines.push(`${dataType.description}\n`);
  }
  lines.push('');

  return lines.join('\n');
}

function getImportantNotesSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.important_notes || config.important_notes.length === 0) {
    return '';
  }

  const lines = ['## Important Notes\n'];
  for (const note of config.important_notes) {
    lines.push(`- ${note}`);
  }
  lines.push('\n');

  return lines.join('\n');
}

function getBestPracticesSection(moduleName: string, metadata: Metadata): string {
  const config = metadata.modules?.[moduleName];
  if (!config?.best_practices || config.best_practices.length === 0) {
    return '';
  }

  const lines = ['## Best Practices\n'];
  for (let i = 0; i < config.best_practices.length; i++) {
    lines.push(`${i + 1}. ${config.best_practices[i]}`);
  }
  lines.push('\n');

  return lines.join('\n');
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

function addAfterSection(content: string, sectionName: string, insertion: string): string {
  const lines = content.split('\n');
  let sectionIndex = -1;

  // Find the section
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() === `## ${sectionName}`) {
      sectionIndex = i;
      break;
    }
  }

  if (sectionIndex === -1) {
    // Section not found, add after title
    return addAfterTitle(content, insertion);
  }

  // Find the end of this section (next ## or end of file)
  let endIndex = lines.length;
  for (let i = sectionIndex + 1; i < lines.length; i++) {
    if (lines[i].trim().startsWith('## ')) {
      endIndex = i;
      break;
    }
  }

  lines.splice(endIndex, 0, insertion.trimEnd(), '');
  return lines.join('\n');
}

function insertAfterTitle(content: string, sections: string[]): string {
  const lines = content.split('\n');
  let titleIndex = -1;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('# ')) {
      titleIndex = i;
      break;
    }
  }

  if (titleIndex === -1) {
    return sections.join('') + content;
  }

  // Insert all sections after title
  const combinedSections = sections.join('');
  lines.splice(titleIndex + 1, 0, '', combinedSections.trimEnd());
  return lines.join('\n');
}

function enhanceMarkdownFile(filePath: string, metadata: Metadata): void {
  let content = fs.readFileSync(filePath, 'utf8');
  const moduleName = extractModuleName(filePath);
  const moduleConfig = metadata.modules?.[moduleName];

  if (!moduleConfig) {
    return;
  }

  // Collect all sections to insert after title
  const sectionsAfterTitle: string[] = [];

  // 1. Tutorial section (only if not already present)
  const tutorialSection = getTutorialSection(moduleName, metadata);
  if (tutorialSection && !content.includes('Related Tutorial')) {
    sectionsAfterTitle.push(tutorialSection);
  }

  // 2. Overview section (only if not already present)
  const overviewSection = getOverviewSection(moduleName, metadata);
  if (overviewSection && !content.includes('## Overview')) {
    sectionsAfterTitle.push(overviewSection);
  }

  // 3. Requirements section (only if not already present)
  const requirementsSection = getRequirementsSection(moduleName, metadata);
  if (requirementsSection && !content.includes('## Requirements')) {
    sectionsAfterTitle.push(requirementsSection);
  }

  // 4. Data types section (only if not already present)
  const dataTypesSection = getDataTypesSection(moduleName, metadata);
  if (dataTypesSection && !content.includes('## Data Types')) {
    sectionsAfterTitle.push(dataTypesSection);
  }

  // 5. Important notes section (only if not already present)
  const importantNotesSection = getImportantNotesSection(moduleName, metadata);
  if (importantNotesSection && !content.includes('## Important Notes')) {
    sectionsAfterTitle.push(importantNotesSection);
  }

  // Insert all sections after title at once
  if (sectionsAfterTitle.length > 0) {
    content = insertAfterTitle(content, sectionsAfterTitle);
  }

  // Add best practices before related resources (only if not already present)
  const bestPracticesSection = getBestPracticesSection(moduleName, metadata);
  if (bestPracticesSection && !content.includes('## Best Practices')) {
    content = addBeforeFooter(content, bestPracticesSection);
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

