# CreditClear 2.0 - Deployment Guide

## Frontend Deployment (Vercel)

### Deployment Steps

1. Push your code to a GitHub repository
2. Log in to your Vercel account and create a new project
3. Import your repository
4. Configure the following settings:
   - Framework: Vite
   - Root Directory: `src/dashboard`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install --legacy-peer-deps`
5. Add the following environment variables:
   - `VITE_API_URL`: Your Render backend URL (e.g., https://creditclear-backend.onrender.com)
6. Deploy the project

### Important Notes

- We're using React 18.2.0 to maintain compatibility with other dependencies
- We're using `--legacy-peer-deps` flag to avoid dependency conflicts
- TanStack Query (v5) is used instead of the older react-query

## Backend Deployment (Render)

### Deployment Steps

1. Log in to your Render account and create a new Web Service
2. Connect your repository
3. Configure the following settings:
   - Name: creditclear-backend
   - Root Directory: `.`
   - Runtime: Python 3.9
   - Build Command: `pip install -r render-requirements.txt`
   - Start Command: `python simple_start.py`
4. Add the following environment variables:
   - `PORT`: 10000
   - `ORIGIN`: Your Vercel frontend URL (e.g., https://creditclear.vercel.app)
5. Deploy the service

### Important Notes

- We're using `render-requirements.txt` which excludes `pickle5` to avoid build failures
- The backend is configured to accept CORS requests from your Vercel frontend

## Troubleshooting

### Vercel Build Failures

If you encounter build failures on Vercel:
- Check that React version is 18.x (not 19.x)
- Make sure you're using the `--legacy-peer-deps` flag for npm install
- Verify that the environment variables are set correctly

### Backend Connection Issues

If your frontend can't connect to the backend:
- Ensure CORS is properly configured in `simple_start.py`
- Check that the `VITE_API_URL` environment variable is set correctly in Vercel
- Verify that the rewrites in `vercel.json` match your API endpoints

### Local Testing Before Deployment

To test locally before deploying:

1. Set up your `.env` file with the correct backend URL
2. Run the backend: `python simple_start.py`
3. Run the frontend: `cd src/dashboard && npm run dev`
