import { NextRequest, NextResponse } from 'next/server';
import Groq from 'groq-sdk';

// Types for the chat API
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatRequest {
  messages: ChatMessage[];
  system?: string;
}

// Environment variables
const GROQ_API_KEY = process.env.GROQ_API_KEY;

// Rate limiting store
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

function checkRateLimit(ip: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  const record = rateLimitStore.get(ip);
  if (!record || now > record.resetTime) {
    rateLimitStore.set(ip, { count: 1, resetTime: now + windowMs });
    return true;
  }
  if (record.count >= limit) return false;
  record.count++;
  return true;
}

// Live KPI context loader (placeholder – implement your DB queries)
async function getLiveKpiContext(): Promise<string> {
  try {
    // Replace with actual database queries
    return `
You are Gladwell — an expert retail data analyst for Msingi Retail System, a multi-branch retail
chain in Kenya. Your name is Gladwell. If anyone asks your name, tell them you are
Gladwell, the Msingi Retail Intelligence AI Analyst.

You have access to live operational data and answer questions about branch
performance, product margins, stockout risks, revenue trends, and department
performance. Be concise, specific, and always reference actual numbers from
the data below. Use KES for all currency values. Format large numbers with
commas. If asked something outside retail operations, politely redirect to
business topics.

=== LIVE DATA SNAPSHOT ===
Latest data date : N/A
Total branches   : 0
Total products   : 0
Total revenue    : KES 0
Average margin   : 0.0%

Note: Live data connection is not implemented yet. Please implement the database queries.
    `.trim();
  } catch (error) {
    console.error('Failed to load KPI context for Gladwell:', error);
    return "You are Gladwell, the Msingi Retail System AI Analyst for Msingi Kenya. Your name is Gladwell. Live data is temporarily unavailable — answer based on general retail best practices and let the user know that live data could not be loaded right now.";
  }
}

// Main POST handler – supports both standard and analyst modes via ?analyst=true query param
export async function POST(request: NextRequest) {
  // Get IP from headers (request.ip doesn't exist in Next.js App Router)
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0] ||
             request.headers.get('x-real-ip') ||
             'unknown';

  // Check if this is an analyst request (query param ?analyst=true)
  const url = new URL(request.url);
  const isAnalyst = url.searchParams.get('analyst') === 'true';

  const rateLimit = isAnalyst ? 15 : 20;
  if (!checkRateLimit(ip, rateLimit, 60 * 1000)) {
    return NextResponse.json(
      { error: "Too many requests. Please wait a moment." },
      { status: 429 }
    );
  }

  if (!GROQ_API_KEY) {
    return NextResponse.json(
      { error: "Gladwell is currently unavailable" },
      { status: 503 }
    );
  }

  try {
    const body: ChatRequest = await request.json();
    if (!body.messages || !Array.isArray(body.messages)) {
      return NextResponse.json({ error: "Invalid request format" }, { status: 400 });
    }

    const client = new Groq({ apiKey: GROQ_API_KEY });

    let systemPrompt = body.system || '';
    if (isAnalyst) {
      systemPrompt = await getLiveKpiContext();
    }

    const messages: any[] = [];
    if (systemPrompt) {
      messages.push({ role: 'system', content: systemPrompt });
    }
    messages.push(...body.messages.map(m => ({ role: m.role, content: m.content })));

    const response = await client.chat.completions.create({
      model: 'llama-3.1-8b-instant',
      messages,
      max_tokens: isAnalyst ? 800 : 512,
      temperature: isAnalyst ? 0.4 : 0.7,
    });

    const reply = response.choices[0]?.message?.content || '';
    return NextResponse.json({ reply });
  } catch (error: any) {
    console.error('Chat API error:', error);
    const errorMsg = error.message?.toLowerCase() || '';
    if (errorMsg.includes('rate limit')) {
      return NextResponse.json({ error: "Too many requests. Please wait a moment." }, { status: 429 });
    }
    if (errorMsg.includes('authentication') || errorMsg.includes('api key')) {
      return NextResponse.json({
        reply: "I'm sorry, Gladwell is having trouble connecting right now. Please check the Groq API key in the server configuration."
      });
    }
    return NextResponse.json({ reply: "Gladwell is temporarily unavailable. Please try again later." });
  }
}