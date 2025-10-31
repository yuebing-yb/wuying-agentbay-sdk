/**
 * Version information for the AgentBay SDK
 * Automatically read from package.json
 */

import * as fs from "fs";
import * as path from "path";

function getVersionFromPackageJson(): string {
  try {
    // Get the path to package.json (relative to this file)
    // When compiled, this will be in dist/, so we need to go up to find package.json
    const packageJsonPath = path.join(__dirname, "..", "package.json");
    
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf-8"));
      return packageJson.version || "0.0.0";
    }
  } catch (error) {
    // Fallback to default version if reading fails
  }
  
  // Fallback version if package.json cannot be read
  return "0.9.4";
}

/**
 * Check if this is a release build.
 * Returns true only if built by official release workflows:
 * - npm_publish.yml
 */
function isReleaseBuild(): boolean {
  // Check if running in GitHub Actions
  if (process.env.GITHUB_ACTIONS !== "true") {
    return false;
  }
  
  // Check if triggered by npm_publish workflow
  const workflow = process.env.GITHUB_WORKFLOW || "";
  if (workflow.includes("Build and Publish to npm")) {
    return true;
  }
  
  // Check for AGENTBAY_RELEASE_BUILD environment variable
  // This can be set in CI/CD for release builds
  if (process.env.AGENTBAY_RELEASE_BUILD === "true") {
    return true;
  }
  
  return false;
}

export const VERSION = getVersionFromPackageJson();
export const IS_RELEASE = isReleaseBuild();

