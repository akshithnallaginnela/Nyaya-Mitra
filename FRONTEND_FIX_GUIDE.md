# Frontend TypeScript Error Fix

## The Problem

You're seeing this error:
```
This JSX tag requires the module path 'react/jsx-runtime' to exist, but none could be found.
```

This happens because:
1. TypeScript can't find the React type definitions
2. Missing `tsconfig.node.json` file
3. Missing `@types/node` package

## The Solution

I've already fixed the configuration files. Now you just need to reinstall dependencies.

### Option 1: Automated Fix (Recommended)

Run the fix script I created:

```cmd
cd frontend
fix-dependencies.cmd
```

This will:
- Remove old node_modules
- Clear npm cache
- Reinstall all dependencies
- Install missing type definitions

### Option 2: Manual Fix

If you prefer to do it manually:

```cmd
cd frontend

# Remove old installations
rmdir /s /q node_modules
del package-lock.json

# Clear cache
npm cache clean --force

# Install dependencies
npm install

# Install missing types
npm install --save-dev @types/node
```

## What I Fixed

1. ✅ Created `tsconfig.node.json` (was missing)
2. ✅ Added `@types/node` to package.json
3. ✅ Created automated fix script

## Verify the Fix

After running the fix, verify everything works:

```cmd
# Check TypeScript compilation
npm run build

# Start dev server
npm run dev
```

You should see:
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:3000/
```

## If Still Not Working

### Check Node.js Version
```cmd
node --version
```
Should be v18 or higher.

### Check npm Version
```cmd
npm --version
```
Should be v9 or higher.

### Upgrade if Needed
Download latest Node.js LTS from: https://nodejs.org/

### Clear Everything and Start Fresh
```cmd
cd frontend

# Remove everything
rmdir /s /q node_modules
del package-lock.json

# Update npm
npm install -g npm@latest

# Reinstall
npm install
```

## Common Issues

### Issue: "Cannot find module 'vite'"
**Solution:**
```cmd
npm install vite --save-dev
```

### Issue: "Cannot find module '@vitejs/plugin-react'"
**Solution:**
```cmd
npm install @vitejs/plugin-react --save-dev
```

### Issue: Port 3000 already in use
**Solution:**
```cmd
# Find process using port 3000
netstat -ano | findstr :3000

# Kill it (replace PID)
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 5173
```

## Files I Created/Modified

1. `frontend/tsconfig.node.json` - TypeScript config for Vite
2. `frontend/package.json` - Added @types/node
3. `frontend/fix-dependencies.cmd` - Automated fix script

## Next Steps

Once the error is fixed:

1. ✅ Run `npm run dev`
2. ✅ Open http://localhost:3000 (or 5173)
3. ✅ Test the application
4. ✅ Continue with local setup guide

## Still Having Issues?

Check the TypeScript errors in VS Code:
1. Open VS Code
2. View → Problems (Ctrl+Shift+M)
3. Look for specific error messages

Or check the terminal output when running `npm run dev` for detailed error messages.
