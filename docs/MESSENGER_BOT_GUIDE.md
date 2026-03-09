# SocialSync Messenger Bot — Complete Guide

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [Facebook Developer App Setup](#3-facebook-developer-app-setup)
4. [Connecting Your Messenger Bot (4-Step Wizard)](#4-connecting-your-messenger-bot-4-step-wizard)
5. [Webhook Configuration](#5-webhook-configuration)
6. [Local Testing with ngrok](#6-local-testing-with-ngrok)
7. [RAG System (Knowledge Base)](#7-rag-system-knowledge-base)
8. [PDF Upload & Processing](#8-pdf-upload--processing)
9. [Website Crawling (Brand DNA)](#9-website-crawling-brand-dna)
10. [Custom AI Prompts](#10-custom-ai-prompts)
11. [E-Commerce / WooCommerce Integration](#11-e-commerce--woocommerce-integration)
12. [Conversations & Human Takeover](#12-conversations--human-takeover)
13. [Dashboard & Analytics](#13-dashboard--analytics)
14. [Settings Page](#14-settings-page)
15. [API Endpoints Reference](#15-api-endpoints-reference)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. Overview

The **SocialSync Messenger Bot** is an AI-powered Facebook Messenger automation system. It allows businesses to:

- **Auto-reply** to customer messages on Facebook Messenger using OpenAI (GPT-4o, GPT-4o-mini, etc.)
- **Use RAG (Retrieval-Augmented Generation)** to answer from uploaded PDFs, crawled website content, and synced WooCommerce products
- **Understand images** sent by customers (AI Vision)
- **Transcribe voice messages** (Whisper API)
- **Integrate with WooCommerce** to recommend products and generate add-to-cart links
- **Human takeover** — a human agent can jump in at any time and resume AI mode later

---

## 2. Architecture & Data Flow

```
Customer sends message on Facebook Messenger
        │
        ▼
Facebook sends POST to your webhook
POST /messenger/webhook/<page_id>/
        │
        ▼
Django receives webhook → messenger_bot/views.py
        │
        ▼
MessageHandler.process_message()
(messenger_bot/services/message_handler.py)
        │
        ├── Extract text, attachments, images, voice
        ├── Save user message to database
        ├── Check: auto_reply_enabled? human_takeover?
        │
        ▼
RAGEngine.generate_response()
(messenger_bot/services/rag_engine.py)
        │
        ├── Retrieve relevant chunks:
        │   ├── 1. PDF Knowledge Base chunks
        │   ├── 2. Brand DNA chunks (website crawl)
        │   └── 3. Product embeddings (WooCommerce)
        │
        ├── Build system prompt + RAG context
        ├── Call OpenAI API (chat completion)
        ├── Clean markdown formatting
        │
        ▼
Send response back via Facebook Graph API
POST https://graph.facebook.com/v18.0/me/messages
        │
        ▼
Customer receives AI response on Messenger
```

**Key Services:**

| Service | File | Purpose |
|---------|------|---------|
| MessageHandler | `messenger_bot/services/message_handler.py` | Core message processing pipeline |
| RAGEngine | `messenger_bot/services/rag_engine.py` | Knowledge retrieval & response generation |
| OpenAIClient | `messenger_bot/services/openai_client.py` | OpenAI API wrapper (chat, embeddings, vision) |
| PDFProcessor | `messenger_bot/services/pdf_processor.py` | PDF text extraction & chunking |
| WooCommerceService | `messenger_bot/services/woocommerce_service.py` | WooCommerce product sync |
| BrandDNAService | `brands/services.py` | Website crawling & knowledge extraction |

---

## 3. Facebook Developer App Setup

Before connecting the bot, you need a **Facebook Developer App** with Messenger configured.

### Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"Create App"**
3. Select **"Business"** type
4. Fill in app name and details
5. Click **"Create App"**

### Step 2: Add Messenger Product

1. In your app dashboard, click **"Add Products"**
2. Find **"Messenger"** and click **"Set Up"**

### Step 3: Generate Page Access Token

1. Go to **Messenger → Settings**
2. Under **"Access Tokens"**, click **"Add or Remove Pages"**
3. Select your Facebook Page
4. Click **"Generate Token"**
5. **Copy this token** — you'll need it in Step 4

### Step 4: Configure Webhooks

1. In **Messenger → Settings**, scroll to **"Webhooks"**
2. Click **"Add Callback URL"**
3. Enter your **Callback URL**: `https://your-domain.com/messenger/webhook/<page_id>/`
4. Enter your **Verify Token** (you'll get this from the Connections tab after connecting)
5. Click **"Verify and Save"**

### Step 5: Subscribe to Webhook Fields

Subscribe to these **6 webhook fields**:

| Field | What It Does |
|-------|-------------|
| `messages` | Receives all incoming text messages, attachments, images, voice |
| `messaging_postbacks` | Receives button click events (quick replies, menu buttons) |
| `messaging_optins` | Receives opt-in events when users start a conversation |
| `message_deliveries` | Delivery receipts — confirms message was delivered |
| `message_reads` | Read receipts — confirms message was read |
| `messaging_referrals` | Referral events when users come from ads or links |

> **Important:** At minimum, you MUST subscribe to `messages` for the bot to work. The others are recommended for full functionality.

---

## 4. Connecting Your Messenger Bot (4-Step Wizard)

Navigate to **Messenger Bot → Connections** tab and click **"+ Connect Page"** (or "Edit Connection" if already connected).

---

### Step 1 of 4: Connect

Fill in your Facebook Page details:

| Field | Required | Description |
|-------|----------|-------------|
| **Page Name** | Yes | Your Facebook Page name (e.g., "Customoo") |
| **Page ID** | Yes | Facebook Page ID (find in Page Settings → About) |
| **Page Access Token** | Yes | Token generated in Facebook Developer App (from Step 3 above) |
| **Greeting Message** | Yes | First message users see: `"Hi! Thanks for reaching out. How can I help you today?"` |
| **Website URL** | No | Your business website URL (used for Brand DNA crawling) |

Click **"Next →"** to proceed.

---

### Step 2 of 4: AI Config

![AI Configuration — Step 2 of 4](screenshots/02_ai_config.png)

This is where you configure the AI model and RAG settings for your bot.

| Field | Default | Description |
|-------|---------|-------------|
| **OpenAI API Key** | — | Your OpenAI API key (get from [platform.openai.com](https://platform.openai.com)) |
| **OpenAI Model** | GPT-4o (Recommended) | AI model for responses. Options: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| **Embedding Model** | text-embedding-3-small | Model for generating vector embeddings. Options: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002` |
| **Top K Results** | 5 | Number of relevant knowledge chunks to retrieve (1-20) |
| **Similarity Threshold** | 0.7 | Minimum cosine similarity score to consider a chunk relevant (0-1) |
| **Temperature** | 0.7 | Controls response creativity (0 = precise, 2 = creative) |
| **Enable RAG** | Checked | Enable knowledge base retrieval for responses |
| **Enable Image Understanding** | Checked | Enable AI vision to analyze images sent by customers |

Click **"Next →"** to proceed.

---

### Step 3 of 4: Prompt

![System Prompt — Step 3 of 4](screenshots/03_prompt_setup.png)

Configure your bot's personality and behavior with a system prompt.

| Field | Required | Description |
|-------|----------|-------------|
| **Prompt Name** | Yes | Name for this prompt (e.g., "Customer Support") |
| **Conversation Tone** | Yes | Select tone: Professional, Casual & Friendly, Warm & Friendly, Technical & Detailed, Sales-Oriented, Customer Support |
| **System Prompt** | Yes | The system instruction that defines bot behavior |
| **Set as Active** | Checkbox | Whether this prompt is the active one (only one can be active) |

**Example System Prompt:**
```
You are a helpful customer support assistant. Answer questions clearly and professionally.
```

**Prompt Tips (shown in the green info box):**
- Be specific about your bot's role and expertise
- Define clear boundaries for what the bot should/shouldn't do
- Include examples of ideal responses
- Specify how to handle off-topic questions

Click **"Next →"** to proceed.

---

### Step 4 of 4: PDFs (Knowledge Base)

![PDF Upload — Step 4 of 4](screenshots/04_pdf_upload.png)

Upload PDF files to build your AI's knowledge base.

- **Click to upload or drag and drop** PDF files into the upload area
- **PDF files only**, max **50MB** each
- Multiple files can be selected at once
- Files shown below with name and size (e.g., `Customoo.pdf — 0.05 MB`)
- Click the **X** button to remove a file before connecting

Click **"Connect Bot"** to finish setup. Your bot is now connected!

---

## 5. Webhook Configuration

After connecting, go to the **Connections** tab to see your webhook configuration and connection status.

![Connections Tab — Webhook Configuration](screenshots/05_connections_webhook.png)

### Connection Card Details

Your connected Facebook Page card shows:

- **Page Name and Page ID** (e.g., "a", Page ID: a)
- **Status Badges:**
  - **Active** (green) — Connection is enabled
  - **Webhook Pending** (yellow) — Webhook not yet verified by Facebook
  - **Auto-Reply On** (blue) — AI auto-replies are enabled
- **Sync button** (top right) to refresh connection status

### Webhook Configuration Section

| Item | Value | Action |
|------|-------|--------|
| **Callback URL** | `http://127.0.0.1:8000/messenger/webhook/a/` | Copy button to clipboard |
| **Verify Token** | `RbSPVxce...` (auto-generated) | Copy button to clipboard |

**Instructions shown:** *"Use these values in your Facebook App → Messenger → Webhooks settings"*

### Additional Info

- **Greeting Message:** "Hi! Thanks for reaching out. How can I help you today?"
- **Connected:** Mar 10, 02:10 AM
- **Last Synced:** Mar 10, 02:10 AM

### How to Use These Values in Facebook

1. Go to your **Facebook Developer App**
2. Navigate to **Messenger → Settings → Webhooks**
3. Click **"Edit"**
4. Paste the **Callback URL** from the Connections tab
5. Paste the **Verify Token** from the Connections tab
6. Click **"Verify and Save"**
7. Once verified, the badge changes from "Webhook Pending" to "Webhook Verified"

### How Webhook Verification Works

```
1. You enter Callback URL + Verify Token in Facebook
2. Facebook sends GET request to your Callback URL:
   ?hub.mode=subscribe
   &hub.verify_token=RbSPVxce...
   &hub.challenge=random_string
3. Your server checks: does verify_token match?
4. If YES → echoes back hub.challenge
5. Facebook marks webhook as verified
6. Badge changes: "Webhook Pending" → "Webhook Verified"
```

---

## 6. Local Testing with ngrok

To test the Messenger Bot locally, you need **ngrok** to create a public HTTPS tunnel to your local Django server.

### Step 1: Install ngrok

```bash
# Windows (using chocolatey)
choco install ngrok

# Or download from https://ngrok.com/download
# Sign up for free account and get auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 2: Start Your Django Server

```bash
cd d:/Projects/Final_version_socialSync
python manage.py runserver 0.0.0.0:8000
```

### Step 3: Start ngrok Tunnel

Open a **new terminal** and run:

```bash
ngrok http 8000
```

You'll see output like:

```
Session Status    online
Forwarding        https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

### Step 4: Update Django Settings

In `socialsync/settings.py`, add the ngrok URL to allowed hosts:

```python
ALLOWED_HOSTS = ['*']  # Or specifically: ['abc123.ngrok-free.app', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'https://abc123.ngrok-free.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

### Step 5: Update Facebook Webhook

1. Go to your **Facebook Developer App → Messenger → Settings → Webhooks**
2. Click **"Edit"** on your webhook
3. Change Callback URL to: `https://abc123.ngrok-free.app/messenger/webhook/<page_id>/`
4. Keep the same Verify Token
5. Click **"Verify and Save"**

### Step 6: Test the Flow

1. Go to your Facebook Page
2. Send a message from a test account (or use Facebook's built-in test feature)
3. Watch your Django terminal — you should see the webhook POST arrive
4. Check the **Conversations** tab in SocialSync to see the message and AI response

### Important Notes

- **ngrok URL changes** every time you restart ngrok (free tier). You'll need to update the webhook URL each time.
- **ngrok paid plan** gives you a stable URL.
- **Always use HTTPS** — Facebook requires HTTPS for webhooks.
- **Check ngrok dashboard** at `http://127.0.0.1:4040` to inspect webhook requests and responses.

### Quick Reference (ngrok Testing Workflow)

```
Terminal 1: python manage.py runserver 0.0.0.0:8000
Terminal 2: ngrok http 8000
             → Copy HTTPS URL
             → Update Facebook webhook with new URL
             → Send test message on Messenger
             → Check SocialSync Conversations tab
```

---

## 7. RAG System (Knowledge Base)

RAG (Retrieval-Augmented Generation) is the core intelligence of the bot. It allows the AI to answer questions using your actual business data instead of generic knowledge.

### How RAG Works

```
Customer asks: "Do you have red jackets?"
        │
        ▼
1. Create embedding of the question (vector)
        │
        ▼
2. Search 3 knowledge sources for similar content:
   ├── PDF chunks (uploaded documents)
   ├── Brand DNA chunks (crawled website)
   └── Product embeddings (WooCommerce products)
        │
        ▼
3. Rank by cosine similarity score
   - PDF/Website threshold: 0.7 (configurable)
   - Product threshold: 0.35 (lower = more matches)
        │
        ▼
4. Take top K results (default: 5)
        │
        ▼
5. Inject as context into AI prompt:
   <knowledge_context>
   [Source: Product - Apex Kinetic Red Jacket]
   Name: Apex Kinetic Red Jacket
   Price: $550.00
   Stock: In Stock
   Link: https://customoo.com/product/apex-kinetic-red-jacket
   </knowledge_context>
        │
        ▼
6. AI generates response using this context
   → "Yes! We have the Apex Kinetic Red Jacket for $550.
      It's currently in stock. Here's the link: ..."
```

### Three Knowledge Sources (Priority Order)

| Source | How It Gets There | Threshold | Used For |
|--------|------------------|-----------|----------|
| **PDF Chunks** | Upload PDFs in Knowledge Base tab | 0.7 | Company policies, FAQs, product manuals |
| **Brand DNA** | Crawl website in Knowledge Base tab | 0.7 | About page, services, general business info |
| **Products** | Sync from WooCommerce in Settings tab | 0.35 | Product recommendations, pricing, availability |

### Context Format Sent to AI

```
[Source 1: PDF - Customoo.pdf, Page 1]
Our return policy allows returns within 30 days...

[Source 2: Brand Website - About Us, URL: https://customoo.com/about]
Customoo is a premium cycling apparel brand...

[Source 3: Product - Apex Aero-Shield Jacket]
Name: Apex Aero-Shield Jacket | Price: $650.00 | Stock: In Stock
Categories: Jackets, Cycling | Link: https://customoo.com/...
```

---

## 8. PDF Upload & Processing

### How to Upload PDFs

**Method 1: During Connection Setup (Step 4 of wizard)**

![PDF Upload during connection setup](screenshots/04_pdf_upload.png)

Drag and drop or click to upload in the wizard. Files shown with name and size.

---

**Method 2: Knowledge Base Tab (after connection)**

![Knowledge Base — PDF section](screenshots/07_knowledge_base.png)

1. Go to **Messenger Bot → Knowledge Base**
2. Scroll to **"PDF Knowledge Base"** section
3. **Drag and drop** PDF files into the upload area, or **click to browse**
4. Supported format: **PDF only**, max **50MB** per file
5. Click **"Upload PDF"** button (red, top right)

### Uploaded File Display

After uploading, each PDF shows:
- **Filename** (e.g., `Customoo.pdf`)
- **Status badge:** `completed` (green)
- **File size:** 49.7 KB
- **Pages:** 0 pages
- **Chunks:** 2 chunks vectorized
- **Delete button** (trash icon)

### PDF Processing Pipeline

```
Upload PDF file
    │
    ▼
PyPDF2 extracts text (page by page)
    │
    ▼
Text cleaned (remove extra whitespace, special chars)
    │
    ▼
Split into chunks:
  - Chunk size: 1000 characters
  - Overlap: 200 characters (maintains context between chunks)
  - Intelligent sentence-boundary breaking
    │
    ▼
Each chunk embedded via OpenAI Embeddings API
(text-embedding-3-small by default)
    │
    ▼
Chunks + embeddings stored in database
    │
    ▼
Status: pending → processing → completed
```

### PDF Status Tracking

| Status | Meaning |
|--------|---------|
| **Pending** | Uploaded, waiting to be processed |
| **Processing** | Currently extracting text and generating embeddings |
| **Completed** | Ready to use in RAG responses |
| **Failed** | Error during processing (check logs) |

---

## 9. Website Crawling (Brand DNA)

### How to Crawl a Website

![Knowledge Base — Website Crawling](screenshots/07_knowledge_base.png)

1. Go to **Messenger Bot → Knowledge Base**
2. Under **"Website Knowledge Base"** section at the top:
   - Enter your website URL (e.g., `https://customoo.com`)
   - The URL input field is pre-filled if you provided it during connection setup
3. Click **"Crawl Website"** button (red)
4. Wait for the crawl to complete
5. The helper text below says: *"Enter your website URL and click 'Crawl Website' to extract knowledge for the AI"*

### What Happens During Crawling

```
Enter website URL → Click "Crawl Website"
    │
    ▼
BrandDNAService.generate_brand_dna()
    │
    ▼
Crawls website pages (homepage, about, products, etc.)
    │
    ▼
Extracts text content from each page
    │
    ▼
Creates BrandDNAChunk records:
  - page_title: "About Us"
  - source_url: "https://customoo.com/about"
  - text: extracted content
  - embedding: vector embedding
    │
    ▼
Results available in RAG:
  pages_crawled: N
  total_chunks: N
```

### How It's Used

- Brand DNA chunks are searched alongside PDFs and products during RAG retrieval
- They provide context about your business: who you are, what you do, services, policies
- Uses the same cosine similarity threshold as PDFs (0.7 default)

---

## 10. Custom AI Prompts

### Managing Prompts

![AI Prompts Tab](screenshots/08_ai_prompts.png)

Go to **Messenger Bot → AI Prompts** tab. This page shows:

- Header: **"Custom AI Prompts"** — *"Create custom system prompts to personalize your chatbot's behavior"*
- **"+ New Prompt"** button (red, top right)

### Prompt Cards

Each prompt card displays:

| Element | Example |
|---------|---------|
| **Lightning bolt icon** | Yellow for active, gray for inactive |
| **Prompt Name** | "Customer Support" |
| **Status Badge** | `Active` (green) or `Inactive` (gray) |
| **Tone Badge** | `Warm & Friendly` (purple) or `Professional` (purple) |
| **System Prompt Preview** | "You are a helpful customer support assistant..." (truncated to 2 lines) |
| **Last Updated** | "Last updated: Feb 15, 05:20 AM" |
| **Action Buttons** | Play (activate), Edit (pencil), Delete (trash) |

In the screenshot, two prompts are visible:
1. **Customer Support** — `Active`, `Warm & Friendly` — "You are a helpful customer support assistant. Answer questions clearly and professionally."
2. **Customer Support** — `Inactive`, `Professional` — "You are a helpful customer support assistant. Answer questions clearly and professionally. DONT ANSWER FALSE. ALWAYS KEEP ANS FROM PDF."

### Prompt Engineering Tips (shown at bottom)

The green info box at the bottom shows:
- Be specific about your bot's role and expertise
- Define clear boundaries for what the bot should and shouldn't do
- Include examples of ideal responses in your prompt
- Specify how to handle sensitive or off-topic questions

### Available Conversation Tones

| Tone | Best For |
|------|----------|
| **Professional** | B2B, formal business communication |
| **Casual & Friendly** | Lifestyle brands, informal businesses |
| **Warm & Friendly** | Customer support, hospitality |
| **Technical & Detailed** | Tech products, SaaS support |
| **Sales-Oriented** | E-commerce, product recommendations |
| **Customer Support** | Help desks, service businesses |

### How the System Prompt Is Enhanced

Your system prompt is automatically enhanced with:

1. **Language detection** — if customer writes in Bengali, bot responds in Bengali
2. **Formatting rules** — no markdown in responses (plain text for Messenger)
3. **Knowledge boundaries** — only use provided RAG context, don't make things up
4. **Product info rules** — include name, price, stock status, and link for products
5. **Conversation history** — last 10 messages for context continuity

---

## 11. E-Commerce / WooCommerce Integration

### Overview

The E-Commerce integration connects your WooCommerce store to the Messenger Bot. Customers can ask about products, and the AI will recommend matching products with prices, availability, and direct links.

![E-Commerce Settings — Product Catalog & RAG](screenshots/09_ecommerce_settings.png)

### Setup Steps

#### 1. Enable E-Commerce

Go to **Messenger Bot → Settings** (scroll down to E-Commerce Integration section).

Toggle **"Enable E-Commerce"** ON (blue toggle, top right).

The header shows: *"Connect your WooCommerce store for product catalog & AI matching"*

#### 2. Configure WooCommerce Credentials

| Field | Description | Example |
|-------|-------------|---------|
| **Platform** | E-commerce platform dropdown | WooCommerce |
| **Store URL** | Your store URL | `https://customoo.com/` |
| **Consumer Key** | WooCommerce REST API key (starts with `ck_`) | `ck_...` |
| **Consumer Secret** | WooCommerce REST API secret (starts with `cs_`) | `cs_...` |
| **Product Match Threshold** | How loosely to match products (lower = more matches) | `0.35` (recommended) |
| **Currency Symbol** | Currency for display | `$` |

**How to get WooCommerce API keys:**
1. Go to your WordPress admin → WooCommerce → Settings → Advanced → REST API
2. Click **"Add Key"**
3. Set permissions to **"Read"**
4. Click **"Generate API Key"**
5. Copy the **Consumer Key** and **Consumer Secret**

#### 3. Test Connection

Click the **"Test Connection"** button (blue outline). If successful, you'll see store name and WooCommerce version.

#### 4. Save E-Commerce Settings

Click **"Save E-Commerce Settings"** button (red).

#### 5. Sync Products

Click **"Sync from API"** button (green, top right of Product Catalog section). This will:
- Fetch all published products from your WooCommerce store
- Store product data locally (name, price, description, images, stock status, SKU)
- Display synced count (e.g., **"44 products synced"**, Last sync: Feb 15, 06:52 AM)

#### 6. Generate Embeddings

Click **"Regenerate Embeddings"** button (purple, next to Sync). This will:
- Create text for each product: `name + description + categories + price`
- Generate vector embeddings using OpenAI
- Store embeddings for similarity search during RAG

### Product Catalog Display

The screenshot shows a product grid with 4 columns:

| Product | ID | Price | Stock |
|---------|----|-------|-------|
| Man's Premium Tri-Blend Regular Fit Graphic Tee | 30988 | $400.00 | In Stock |
| Apex Aero-Shield: High-Visibility Performance Cy... | 30694 | $650.00 | In Stock |
| Apex Aero-Shield: The Ultimate Performance Cyc... | 30667 | $600.00 | In Stock |
| Apex Kinetic: High-Velocity Moto Shell | 30676 | $550.00 | In Stock |

Each product card shows:
- Product image
- Product name (truncated)
- WooCommerce ID
- Price with currency symbol
- **In Stock** badge (green)

### RAG Configuration (bottom of page)

| Setting | Value | Description |
|---------|-------|-------------|
| **Top K Results** | 5 | Number of relevant chunks to retrieve |
| **Similarity Threshold** | 0.7 | Min score for PDF/website chunks |
| **Embedding Model** | text-embedding-3-small | Model for generating embeddings |

Click **"Save Settings"** (red button, bottom right) to save RAG configuration.

### How Products Appear in Conversations

When a customer asks about a product:

1. RAG engine searches product embeddings (threshold: 0.35)
2. Matching products are injected as context
3. AI responds with product details:
   - Product name
   - Price (with currency symbol)
   - Stock status (In Stock / Out of Stock / Backorder)
   - Direct link to product page
   - Add-to-cart URL: `https://customoo.com/?add-to-cart=12345`

---

## 12. Conversations & Human Takeover

### Viewing Conversations

![Conversations Tab](screenshots/06_conversations.png)

Go to **Messenger Bot → Conversations** tab.

### Layout

**Left Panel — Conversation List:**
- Search bar with **"Refresh"** button
- Each conversation shows:
  - Customer avatar (with green online indicator)
  - **Customer name** (e.g., "Arifuzzaman Swapnil")
  - **Message count** (e.g., "6 messages")
  - **Last active time** (e.g., "Mar 10, 01:10 AM")

**Right Panel — Chat Messages:**

Header shows:
- Customer name: **"Arifuzzaman Swapnil"**
- Customer ID: **"ID: 330463721164819"**
- **"Take Over"** button (orange, top right)

### Message Types Displayed

The screenshot shows a real conversation with multiple message types:

**1. Text Messages:**
- Customer: "Hi"
- Bot: "Hello! How can I help you today? I'm here to assist you with any questions about our products or services. What are you looking for?"

**2. Image Attachments:**
- Customer sends `[Attachment]` — shows a blue thumbs-up icon image
- Below the image: **"AI Vision Analysis"** purple box containing detailed image analysis:
  ```
  ## AI Image Analysis
  **Content type**: Icon/logo image
  **Main subject**: Facebook "thumbs up" like button icon in blue
  **Product details**: Not applicable - this is a digital icon/symbol
  **Text/action**: No visible text
  **Customer intent**: Unclear - could be: Testing the image upload functionality...
  **Business response recommendation**: This appears to be either a test message...
  ```

**3. Bot AI Responses to Images:**
- Bot responds with context-aware message acknowledging the image
- Shows metadata: `Mar 10, 01:06 AM | claude-sonnet-4-20250514 | 503 tokens | 5.8s`

### Message Metadata

Each bot message shows:
- **Timestamp** (e.g., Mar 10, 01:06 AM)
- **Model used** (e.g., claude-sonnet-4-20250514)
- **Tokens used** (e.g., 503 tokens)
- **Processing time** (e.g., 5.8s)

### Human Takeover

When you need a human to handle a conversation:

1. Click **"Take Over"** button (orange) at the top right
2. AI auto-replies are **paused** for this conversation only
3. The message input field becomes active — you can type and send
4. Messages sent are tagged as `model_used='human'`
5. Click **"Resume Bot"** (green) to return to AI auto-reply mode

---

## 13. Dashboard & Analytics

![Messenger Bot Dashboard](screenshots/01_dashboard.png)

Go to **Messenger Bot → Dashboard** tab.

### Stats Cards (top row)

| Card | Icon | Value | Description |
|------|------|-------|-------------|
| **Active Connections** | Link (purple) | 1 | Number of connected Facebook Pages |
| **Total Conversations** | Chat (pink) | 1 | All conversations across all pages |
| **Messages Sent** | Document (orange) | 10 | Total bot + human messages sent |
| **Tokens Used** | Token (red) | 2,072 | Total OpenAI tokens consumed |
| **Unread Notifications** | Bell (red) | 0 | Important messages needing attention |

### Recent Notifications

Section showing recent important events. In the screenshot: *"No recent notifications"* with a bell icon.

Click **"View All"** (top right) to see all notifications.

### Active Conversations

Shows the most recent active conversations:
- **Arifuzzaman Swapnil** — 6 messages — Mar 10, 01:10 AM
- Click on a conversation to open it in the Conversations tab

Click **"View All"** (top right) to see all conversations.

---

## 14. Settings Page

Go to **Messenger Bot → Settings** tab.

### AI Model Configuration

| Setting | Options | Default |
|---------|---------|---------|
| **OpenAI API Key** | Your key (password field) | — |
| **Model** | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo | gpt-4o |
| **Temperature** | 0 (Precise) ←→ 2 (Creative) | 0.7 |
| **Max Tokens** | 100 - 8000 | 1500 |

### Feature Toggles

| Feature | Toggle | Description |
|---------|--------|-------------|
| **RAG (Knowledge Base)** | ON/OFF | Enable/disable knowledge retrieval from PDFs, website, products |
| **Image Understanding** | ON/OFF | Enable/disable AI vision for image messages |
| **Voice Transcription** | ON/OFF | Enable/disable Whisper-based voice-to-text |
| **Voice Replies** | ON/OFF | Enable/disable text-to-speech responses |

### Voice Models (when Voice Replies enabled)

6 voice options: **Alloy**, **Echo**, **Fable**, **Onyx**, **Nova**, **Shimmer**

### RAG Configuration

| Setting | Default | Range |
|---------|---------|-------|
| **Top K Results** | 5 | 1-20 |
| **Similarity Threshold** | 0.7 | 0-1 |
| **Embedding Model** | text-embedding-3-small | 3 options |

### E-Commerce Integration

(See [Section 11](#11-e-commerce--woocommerce-integration) for full details)

---

## 15. API Endpoints Reference

Base URL: `/api/messenger/`

### Connection Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/connections/` | Create/update connection |
| GET | `/connections/` | List all connections |
| PUT | `/connections/<id>/` | Update connection |
| DELETE | `/connections/<id>/` | Delete connection |
| POST | `/connections/<id>/toggle_active/` | Toggle active status |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get dashboard stats |

### AI Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections/<id>/config/` | Get AI config |
| PATCH | `/connections/<id>/config/` | Update AI config |

### PDF Knowledge Base

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections/<id>/pdfs/` | List uploaded PDFs |
| POST | `/connections/<id>/pdfs/` | Upload PDF (FormData) |
| GET | `/connections/<id>/pdfs/<pdf_id>/` | Get PDF details |
| DELETE | `/connections/<id>/pdfs/<pdf_id>/` | Delete PDF |

### Website Crawling

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/connections/<id>/crawl-website/` | Crawl website |
| GET | `/connections/<id>/crawl-website/` | Get crawl status |

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections/<id>/conversations/` | List conversations |
| GET | `/connections/<id>/conversations/<conv_id>/` | Get full conversation with messages |
| POST | `/connections/<id>/conversations/<conv_id>/toggle-takeover/` | Toggle human takeover |
| POST | `/connections/<id>/conversations/<conv_id>/send-message/` | Send manual message |

### Custom Prompts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections/<id>/prompts/` | List prompts |
| POST | `/connections/<id>/prompts/` | Create prompt |
| PUT | `/connections/<id>/prompts/<pid>/` | Update prompt |
| DELETE | `/connections/<id>/prompts/<pid>/` | Delete prompt |
| POST | `/connections/<id>/prompts/<pid>/activate/` | Activate prompt |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications/` | List notifications |
| POST | `/notifications/<id>/mark_read/` | Mark as read |
| POST | `/notifications/<id>/resolve/` | Mark as resolved |
| POST | `/notifications/mark_all_read/` | Mark all read |

### E-Commerce

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections/<id>/ecommerce/` | Get e-commerce settings |
| PATCH | `/connections/<id>/ecommerce/` | Update e-commerce settings |
| POST | `/connections/<id>/ecommerce/test/` | Test WooCommerce connection |
| POST | `/connections/<id>/ecommerce/sync/` | Sync products from WooCommerce |
| POST | `/connections/<id>/ecommerce/embeddings/` | Generate product embeddings |
| GET | `/connections/<id>/ecommerce/products/` | List synced products |

### Webhook (Non-REST)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/messenger/webhook/<page_id>/` | Facebook webhook verification |
| POST | `/messenger/webhook/<page_id>/` | Receive incoming messages |

---

## 16. Troubleshooting

### Webhook Not Verifying

**Problem:** Webhook stays in "Pending" status

**Solutions:**
1. Make sure your server is running and accessible from the internet
2. Check that the Callback URL matches exactly: `https://your-domain.com/messenger/webhook/<page_id>/`
3. Verify the Verify Token matches what's shown in the Connections tab
4. If using ngrok, make sure the tunnel is active
5. Check Django logs for verification errors
6. Ensure `ALLOWED_HOSTS` includes your domain

### Messages Not Being Received

**Problem:** Customer sends message but nothing happens

**Solutions:**
1. Check webhook is verified (green badge)
2. Verify `auto_reply_enabled` is ON
3. Check `human_takeover` is OFF for that conversation
4. Ensure `is_active` is ON for the connection
5. Check OpenAI API key is valid and has credits
6. Check Django server logs for errors
7. If using ngrok, check the ngrok dashboard at `http://127.0.0.1:4040`

### RAG Not Returning Results

**Problem:** Bot gives generic answers instead of using knowledge base

**Solutions:**
1. Make sure RAG is enabled in Settings
2. Check that PDFs are in "completed" status (not "processing" or "failed")
3. Lower the Similarity Threshold (e.g., from 0.7 to 0.5)
4. Increase Top K Results (e.g., from 5 to 10)
5. Verify embeddings were generated (check chunk count in Knowledge Base)
6. For products, ensure embeddings were generated after syncing

### E-Commerce Sync Issues

**Problem:** Products not syncing from WooCommerce

**Solutions:**
1. Test connection first — check store URL, keys, and permissions
2. WooCommerce API keys need at least "Read" permission
3. Store URL must include trailing slash: `https://customoo.com/`
4. Check that products are published (draft products are not synced)
5. Consumer Key starts with `ck_`, Consumer Secret starts with `cs_`

### Bot Responding Slowly

**Problem:** AI responses take too long

**Solutions:**
1. Use a faster model (gpt-4o-mini instead of gpt-4o)
2. Reduce Top K Results (fewer chunks to process)
3. Reduce Max Tokens (shorter responses)
4. Check OpenAI API status at status.openai.com

---

## Screenshots Reference

Save the screenshots in `docs/screenshots/` with these filenames:

| # | Filename | What It Shows |
|---|----------|---------------|
| 1 | `01_dashboard.png` | Messenger Bot Dashboard — stats cards, notifications, active conversations |
| 2 | `02_ai_config.png` | Connection Wizard Step 2 — AI Config (OpenAI key, model, RAG settings) |
| 3 | `03_prompt_setup.png` | Connection Wizard Step 3 — Prompt (name, tone, system prompt) |
| 4 | `04_pdf_upload.png` | Connection Wizard Step 4 — PDF Upload (drag & drop, file list) |
| 5 | `05_connections_webhook.png` | Connections Tab — Facebook Page card, webhook URL, verify token |
| 6 | `06_conversations.png` | Conversations Tab — chat messages, AI Vision Analysis, metadata |
| 7 | `07_knowledge_base.png` | Knowledge Base Tab — website crawl URL, PDF uploads with status |
| 8 | `08_ai_prompts.png` | AI Prompts Tab — prompt cards with Active/Inactive status |
| 9 | `09_ecommerce_settings.png` | E-Commerce Settings — WooCommerce config, product grid, RAG config |

---

## Quick Start Checklist

- [ ] Create Facebook Developer App
- [ ] Add Messenger product
- [ ] Generate Page Access Token
- [ ] Connect bot in SocialSync (4-step wizard)
- [ ] Set up ngrok for local testing
- [ ] Configure webhook in Facebook App with Callback URL + Verify Token
- [ ] Subscribe to webhook fields: messages, messaging_postbacks, messaging_optins, message_deliveries, message_reads, messaging_referrals
- [ ] Verify webhook (green badge on Connections tab)
- [ ] Upload PDFs to Knowledge Base
- [ ] Crawl your website for Brand DNA
- [ ] Create and activate an AI prompt
- [ ] Connect WooCommerce store (if applicable)
- [ ] Sync products and generate embeddings
- [ ] Send a test message on Messenger
- [ ] Verify AI response uses RAG context
- [ ] Test human takeover and resume bot

---

*Last updated: March 2026 | SocialSync v1.2.2*
