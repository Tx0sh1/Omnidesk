# Frontend Troubleshooting Guide

This guide helps resolve common issues with the OmniDesk frontend.

## 🚨 Critical Issue: Tailwind CSS PostCSS Plugin Error

### Error Message
```
Error: It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin. 
The PostCSS plugin has moved to a separate package, so to continue using Tailwind CSS 
with PostCSS you'll need to install `@tailwindcss/postcss` and update your PostCSS configuration.
```

### Quick Fix Options

#### Option 1: Use the Fix Scripts (Recommended)
```bash
# On Linux/Mac
cd frontend
chmod +x fix-tailwind.sh
./fix-tailwind.sh

# On Windows
cd frontend
fix-tailwind.bat
```

#### Option 2: Manual Fix
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Option 3: Using the Startup Script
```bash
# From project root
python start_omnidesk.py --force-frontend-reinstall
```

### Root Cause
This error occurs when:
1. The `node_modules` directory contains the old `tailwindcss` package alongside the new `@tailwindcss/postcss`
2. Cached dependencies from a previous installation are conflicting
3. The PostCSS configuration is trying to use the deprecated plugin

### Verification Steps
After running the fix, verify these files are correct:

**package.json** should have:
```json
{
  "devDependencies": {
    "@tailwindcss/postcss": "^4.1.11",
    // Should NOT have "tailwindcss": "..."
  }
}
```

**postcss.config.js** should have:
```javascript
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  }
}
```

## 🔧 Other Common Issues

### Issue: Frontend Won't Start
**Error**: `npm start` fails with various errors

**Solutions**:
1. Ensure Node.js 14+ is installed: `node --version`
2. Clear npm cache: `npm cache clean --force`
3. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
4. Check for port conflicts (default port 3000)

### Issue: API Connection Errors
**Error**: Frontend can't connect to backend API

**Check**:
1. Backend is running on http://localhost:5000
2. Frontend `.env` file has correct API URL:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```
3. No CORS issues (backend should handle CORS for localhost:3000)

### Issue: TypeScript Compilation Errors
**Error**: Various TypeScript errors

**Solutions**:
1. Ensure TypeScript version compatibility: `npm list typescript`
2. Clear TypeScript cache: `npx tsc --build --clean`
3. Restart the development server
4. Check `tsconfig.json` for any misconfigurations

### Issue: Missing Dependencies
**Error**: Module not found errors

**Solution**:
```bash
cd frontend
npm install
```

Check that all required dependencies are in `package.json`:
- React 18.2.0+
- TypeScript 4.9.5+
- React Router DOM 7.8.0+
- Axios 1.11.0+
- Lucide React 0.539.0+

## 🏗️ Project Structure Verification

Ensure your frontend directory has this structure:
```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   ├── Layout/
│   │   └── Tickets/
│   ├── contexts/
│   ├── services/
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
└── .env
```

## 🚀 Performance Tips

1. **Clean Development Environment**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Clear Browser Cache**: Hard refresh (Ctrl+Shift+R) or clear browser cache

3. **Check Bundle Size**: Run `npm run build` to check for large bundles

4. **Monitor Console**: Check browser dev tools for runtime errors

## 🆘 Getting Help

If issues persist:

1. **Check Logs**: Look at the terminal output for specific error messages
2. **Browser Console**: Check for JavaScript errors in browser dev tools
3. **Network Tab**: Verify API calls are being made correctly
4. **Restart Everything**: Stop both frontend and backend, then restart

## 🔄 Reset to Clean State

To completely reset the frontend:
```bash
cd frontend
rm -rf node_modules package-lock.json .env
cp .env.example .env
npm install
npm start
```

This will give you a completely fresh frontend installation.
