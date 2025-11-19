# 🚀 Quick Setup Guide

Follow these steps to get the AI Code Assistant running in under 5 minutes.

## Step 1: Prerequisites Check

Ensure you have:
- ✅ Node.js 18+ installed (`node --version`)
- ✅ AgentBay API key
- ✅ DashScope API key

## Step 2: Install Dependencies

```bash
npm install
```

Expected output:
```
added 300+ packages in 30s
```

## Step 3: Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your credentials
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

Add your keys:
```env
AGENTBAY_API_KEY=sk_xxxxx...
DASHSCOPE_API_KEY=sk_xxxxx...
DASHSCOPE_MODEL=qwen-max
```

## Step 4: Start the Development Server

```bash
npm run dev
```

You should see:
```
▲ Next.js 14.2.0
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

## Step 5: Open in Browser

Navigate to: **http://localhost:3000**

## Step 6: Test It Out

Try these example prompts:

1. **Simple Math**
   ```
   Calculate the factorial of 10
   ```

2. **Data Analysis**
   ```
   Generate 100 random numbers and show me the distribution statistics
   ```

3. **Visualization**
   ```
   Create a line chart showing the Fibonacci sequence for the first 15 numbers
   ```

## Troubleshooting

### Issue: Port 3000 already in use

```bash
# Use a different port
npm run dev -- -p 3001
```

### Issue: Module not found errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: API key errors

- Check that `.env` file exists in the project root
- Verify keys don't have extra spaces
- Restart the development server after editing `.env`

## What's Next?

- Check out the [README.md](./README.md) for detailed documentation
- Explore the code in `/app` and `/lib` directories
- Customize the UI in `/components`
- Add new AI tools in `/app/api/chat/route.ts`

## Support

Having issues?
1. Check the logs in your terminal
2. Look for errors in browser console (F12)
3. Refer to the troubleshooting section in README.md
4. Open an issue on GitHub

---

**Happy coding! 🎉**
