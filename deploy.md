# 🚀 Vercel Deployment Guide

## Prerequisites
1. Install Vercel CLI: `npm i -g vercel`
2. Have a Vercel account (free tier works fine)

## Deployment Steps

### 1. Prepare the Project
```bash
# Make sure all files are ready
ls -la
# You should see: app.py, vercel.json, requirements.txt, templates/, static/
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel
```

### 4. Follow the Prompts
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **What's your project's name?** → `eduwaves-invoice-generator` (or your preferred name)
- **In which directory is your code located?** → `./`

### 5. Production Deployment
```bash
vercel --prod
```

## File Structure for Vercel
```
├── app.py                 # Main Flask application
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Frontend template
├── static/              # Static files (if any)
├── books_database.json  # Books data
├── unique_schools.csv   # Schools data
└── WhatsApp_Image_2025-08-01_at_12.46.28_e1c96073-removebg-preview.png # Logo
```

## Environment Variables (if needed)
```bash
vercel env add PYTHONPATH .
```

## Testing the Deployment
1. Visit your Vercel URL
2. Test book search functionality
3. Test school search functionality
4. Generate a test invoice
5. Verify PDF download works

## Troubleshooting

### Common Issues:
1. **Import errors**: Make sure all dependencies are in `requirements.txt`
2. **File not found**: Ensure data files are in the root directory
3. **PDF generation fails**: Check ReportLab installation
4. **Logo not loading**: Verify image file is in root directory

### Logs:
```bash
vercel logs
```

## Features Included:
✅ **Book Search**: 93 books from catalog
✅ **School Search**: 2,032 unique schools
✅ **Invoice Types**: Floating Stock, Credit School, Special Market
✅ **Bank Selection**: Zenith Bank (normal) / Globus Bank (special market)
✅ **PDF Generation**: Professional invoices with logo
✅ **Responsive Design**: Works on all devices
✅ **Real-time Calculations**: Automatic totals and discounts

## Support:
- Vercel Documentation: https://vercel.com/docs
- Flask on Vercel: https://vercel.com/docs/functions/serverless-functions/runtimes/python
