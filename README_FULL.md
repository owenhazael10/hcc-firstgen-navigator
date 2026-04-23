# HC First-Gen Navigator

An AI-powered guidance system for first-generation college students at Hillsborough College (HC) in Tampa, Florida. Built with Claude Opus 4.6, Supabase PostgreSQL with pgvector for RAG, and deployed on Netlify.

![HC First-Gen Navigator](https://img.shields.io/badge/AI-Claude%20Opus%204.6-blue) ![Database](https://img.shields.io/badge/Database-Supabase-green) ![RAG](https://img.shields.io/badge/RAG-pgvector-orange)

## Overview

The HC First-Gen Navigator helps students who are the first in their family to attend college navigate the complex college journey. It provides personalized guidance on financial aid, major selection, FAFSA, support services, and academic planning — all in plain language with zero jargon, available in both English and Spanish.

## Key Features

### 🎯 Personalized Guidance
- Asks 2-3 intake questions before giving advice
- Tailors responses based on student's situation
- Never provides generic wall-of-text responses

### 🌐 Bilingual Support
- Full English and Spanish support
- Student can switch languages anytime by saying "en español"
- Entire conversation switches seamlessly

### 📚 RAG-Enhanced Answers
- Retrieval Augmented Generation pulls from HC Student Handbook
- Searches 30+ document chunks with keyword matching
- Combines real HC documents with hardcoded institutional knowledge

### 💰 Financial Aid Intelligence
- All HC deadlines: FAFSA priority dates, payment due dates, refund dates
- HC FAFSA school code: 007870
- HC Foundation Scholarship cycles
- Bright Futures guidance

### 🎓 Major Matching Pipeline
- Connects student interests to exact HC degree programs
- Shows which campus offers each program
- Links to job titles and Tampa Bay salary ranges
- Flags competitive admissions programs (Nursing, Health Sciences)

### 🤝 TRIO Awareness
- Proactively mentions TRIO Student Support Services
- Most first-gen students qualify but don't know about it
- Free tutoring, advising, scholarships, cultural activities

### 🆘 Support Discovery
- Guides students to free resources:
  - Academic Success Centers (free tutoring)
  - BayCare counseling (free and confidential)
  - Food 2 Finish (food pantries on all campuses)
  - Disability Services (OSSD)
  - Veterans Services

### 📊 Feedback Loop
- Thumbs up/down after every response
- Logs all conversations and feedback to Supabase
- Enables continuous improvement and analysis

## Tech Stack

**Frontend**
- HTML/CSS/JavaScript
- Inter + Space Grotesk fonts
- Gradient background with modern card-based UI
- Responsive design (mobile + desktop)

**AI Model**
- Claude Opus 4.6 by Anthropic
- Chosen for nuanced reasoning and personalization
- Handles complex multi-turn conversations

**Backend**
- Netlify Serverless Functions
- Proxies Anthropic API securely
- API key never exposed to browser
- Includes RAG keyword search

**Database**
- Supabase PostgreSQL
- pgvector extension for future semantic search
- Two tables: conversations (logs) + hc_documents (RAG)

**RAG Pipeline**
- Python script downloads HC PDFs
- Chunks documents with overlap
- Creates embeddings via sentence-transformers (local, free)
- Uploads to Supabase

**Hosting & CI/CD**
- Netlify auto-deploys from GitHub
- Zero-config deployment
- Custom domain support

## Project Structure

```
hcc-firstgen-navigator/
├── index.html                      # Main UI
├── netlify/
│   └── functions/
│       └── chat.js                 # API proxy + RAG search
├── scripts/
│   └── load_hc_documents_local.py  # Document loader
├── supabase/
│   └── schema.sql                  # Database schema
├── requirements_local.txt          # Python dependencies
├── package.json                    # Node metadata
├── netlify.toml                    # Netlify config
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
└── README.md                       # This file
```

## Setup Instructions

### 1. Prerequisites

- Node.js 18+
- Python 3.9+
- Anthropic API account ($5 minimum credit)
- Supabase account (free tier)
- Netlify account (free tier)
- GitHub account

### 2. Database Setup

Create a Supabase project:

1. Go to supabase.com and create a new project
2. Go to Database → Extensions → Enable **vector**
3. Go to SQL Editor and run `supabase/schema.sql`

This creates:
- `conversations` table for chat logs
- `hc_documents` table for RAG chunks
- Vector similarity search function

### 3. Load HC Documents (RAG)

Install Python dependencies:
```bash
pip install -r requirements_local.txt
```

Edit `scripts/load_hc_documents_local.py`:
- Replace `your-supabase-service-role-key-here` with your Supabase service_role key

Run the loader:
```bash
python scripts/load_hc_documents_local.py
```

This downloads the HC Student Handbook, chunks it, creates embeddings locally, and uploads to Supabase. Takes ~5 minutes.

### 4. Deploy to Netlify

**Option A - Auto-deploy from GitHub:**
1. Push code to GitHub
2. Go to netlify.com → New site from Git
3. Connect your GitHub repo
4. Add environment variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key
5. Deploy

**Option B - Netlify CLI:**
```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

Add the environment variable in Netlify dashboard after deployment.

### 5. Test

1. Visit your Netlify URL
2. Ask questions in the chat
3. Check Supabase Table Editor to verify conversations are logging
4. Try questions that should pull from the Student Handbook

## Environment Variables

**Netlify (production):**
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Local (for RAG script):**
- `SUPABASE_URL` - Your Supabase project URL (hardcoded in script)
- `SUPABASE_KEY` - Your Supabase service_role key (NOT anon key)

Never commit API keys to Git. Use `.env` files locally (already in `.gitignore`).

## Data Sources

The agent combines:
- **RAG Database:** HC Student Handbook 2025-2026 (30 chunks)
- **Hardcoded Knowledge:** Deadlines, FAFSA code, campus specialties, degree types, support services
- **Future:** Could add HC Catalog and more policy documents

## System Prompt

The agent uses a detailed system prompt that includes:
- Tone guidelines (warm, plain language, zero jargon)
- Intake requirement (2-3 questions before advising)
- Bilingual switching logic
- All HC deadlines and dates
- TRIO and Food 2 Finish awareness rules
- Major-to-career pipeline
- Transfer pathway guidance (AA → USF/UF/FSU)

RAG results are appended to the system prompt before each API call.

## Future Enhancements

- [ ] Add HC Catalog PDF to RAG database
- [ ] Implement semantic search with embeddings (currently keyword search)
- [ ] Add more HC policy documents
- [ ] Scrape hcfl.edu for live program updates
- [ ] Analytics dashboard showing popular questions
- [ ] Export conversation transcripts for advisors
- [ ] SMS/WhatsApp integration for mobile access
- [ ] Voice interface for accessibility

## Contributing

This is a class project for demonstration purposes. Not currently accepting contributions.

## License

MIT License - See LICENSE file

## Acknowledgments

- **Hillsborough College** for providing public data and serving first-gen students
- **Anthropic** for Claude Opus 4.6 API
- **Supabase** for database and pgvector support
- **Netlify** for serverless hosting
- **First-generation students everywhere** - this project is for you

## Contact

Built by Owen for HC First-Gen Students  
Questions? Open a GitHub issue

---

**Note:** This agent supplements but does not replace official HC advisors. Always verify important information with HC staff.
