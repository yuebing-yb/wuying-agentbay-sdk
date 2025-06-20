# Session Parameters and Labels Example

This example demonstrates how to use the AgentBay SDK to create sessions with custom parameters and labels, and how to query sessions using these labels.

## Features Demonstrated

- Session Creation with Custom Labels:
  - Creating a session with custom labels to categorize or identify it
  - Using the labels for tracking and organization

- Session Management:
  - Listing sessions by labels
  - Filtering sessions based on label values

## Running the Example

Make sure you have set your AgentBay API key as an environment variable:

```bash
export AGENTBAY_API_KEY="your-api-key-here"
```

Then run the example:

```bash
npx ts-node session-params.ts
```

## Use Cases

Labels are useful for:

1. Organizing sessions by project
2. Identifying sessions created by specific users
3. Categorizing sessions by purpose or environment
4. Creating groups of related sessions
5. Implementing custom filtering and sorting logic in your application 