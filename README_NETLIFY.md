# Netlify Deployment Instructions

This application is now configured for Netlify deployment with serverless functions.

## Setup Steps

### 1. Get OpenRouter API Key
1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for an account
3. Get your API key from the dashboard

### 2. Deploy to Netlify

#### Option A: Drag and Drop
1. Copy the entire `frontend` folder contents
2. Go to [Netlify](https://app.netlify.com/drop)
3. Drag and drop the files

#### Option B: Git Deployment
1. Push your code to GitHub/GitLab/Bitbucket
2. Connect your repository to Netlify
3. Set build settings:
   - Build command: `npm install` (in functions directory)
   - Publish directory: `.` (root)
   - Functions directory: `netlify/functions`

### 3. Set Environment Variables
In your Netlify site dashboard:
1. Go to Site settings → Build & deploy → Environment
2. Add environment variable:
   - **Key**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key

### 4. Deploy
1. Trigger a new deployment
2. Wait for deployment to complete
3. Test your application

## Features

✅ **Camera Integration**: Camera automatically starts when assessment begins
✅ **AI Assessment**: Powered by OpenRouter AI (free tier available)
✅ **Learning Plans**: Personalized learning roadmaps
✅ **Responsive Design**: Works on all devices
✅ **No Backend Required**: Everything runs on Netlify serverless functions

## Limitations

- File upload is disabled (users must paste resume text directly)
- Uses free AI tier with rate limits
- Camera permissions must be granted by user

## Troubleshooting

### "Unexpected token <" Error
This usually means:
1. Missing OpenRouter API key in environment variables
2. API rate limits exceeded
3. Network connectivity issues

**Solution**: Check your Netlify environment variables and ensure OPENROUTER_API_KEY is set correctly.

### Camera Not Working
**Solution**: Ensure you're using HTTPS and grant camera permissions when prompted.

### Rate Limit Errors
**Solution**: The free AI tier has limits. Wait for the countdown timer or consider upgrading your OpenRouter plan.

## File Structure
```
frontend/
├── index.html              # Main application
├── styles.css              # Styling
├── netlify.toml           # Netlify configuration
├── netlify/functions/     # Serverless functions
│   ├── package.json
│   └── api/
│       ├── assess.js
│       ├── quick-assessment.js
│       ├── generate-plan.js
│       └── upload-resume.js
└── README_NETLIFY.md      # This file
```

## Support
If you encounter issues:
1. Check Netlify function logs
2. Verify environment variables
3. Ensure OpenRouter API key is valid
4. Check browser console for JavaScript errors
