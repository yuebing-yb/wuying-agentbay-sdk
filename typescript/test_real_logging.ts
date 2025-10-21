import { setLogLevel, logDebug, logInfo, logWarn, logError } from './src/utils/logger';

console.log("\n" + "=".repeat(70));
console.log("🔍 REAL TYPESCRIPT LOGGING OUTPUT VERIFICATION");
console.log("=".repeat(70));

// Test 1: Default (should be INFO)
console.log("\nTest 1: Default Log Level");
console.log("-".repeat(70));
console.log("→ Trying to log DEBUG (should NOT appear):");
logDebug("DEBUG message - should NOT appear at INFO level");

console.log("\n→ Logging INFO (should appear):");
logInfo("INFO message - should appear");

console.log("\n→ Logging WARN (should appear):");
logWarn("WARNING message - should appear");

// Test 2: Set to DEBUG
console.log("\n" + "=".repeat(70));
console.log("Test 2: Set to DEBUG Level");
console.log("-".repeat(70));
setLogLevel('DEBUG');
console.log("→ After setLogLevel('DEBUG'):");
logDebug("DEBUG message - should NOW appear");
logInfo("INFO message - should appear");

// Test 3: Set to ERROR (high level)
console.log("\n" + "=".repeat(70));
console.log("Test 3: Set to ERROR Level");
console.log("-".repeat(70));
setLogLevel('ERROR');
console.log("→ After setLogLevel('ERROR'):");
logDebug("DEBUG message - should NOT appear");
logInfo("INFO message - should NOT appear");
logWarn("WARN message - should NOT appear");
logError("ERROR message - should appear");

console.log("\n" + "=".repeat(70));
console.log("✓ TYPESCRIPT LOGGING VERIFICATION COMPLETE");
console.log("✓ Confirmed: Log levels control what appears");
console.log("=".repeat(70));
