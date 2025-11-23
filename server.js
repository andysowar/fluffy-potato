import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import axios from 'axios';
import { fileURLToPath } from 'url';
import { search, getMeme } from 'knowyourmeme-js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json({ limit: '50mb' }));
app.use(cors());

const AUDIO_DIR = path.join(__dirname, 'audio');
if (!fs.existsSync(AUDIO_DIR)) {
  fs.mkdirSync(AUDIO_DIR, { recursive: true });
}

app.use('/audio', express.static(AUDIO_DIR));

const PROXY_API_KEY = process.env.PROXY_API_KEY;
app.use((req, res, next) => {
  if (req.path.startsWith('/audio')) return next();

  const key = req.header('x-api-key');
  if (key !== PROXY_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});

const ELEVEN_API_KEY = process.env.ELEVEN_API_KEY;
const ELEVEN_BASE_URL = 'https://api.elevenlabs.io/v1/text-to-speech';

const sanitizeFileName = (name) => {
  if (!name) return null;
  const base = path.basename(name);
  if (!base || base === '.' || base === '..') return null;
  return base.replace(/[^\w.-]/g, '_');
};

const extractFullCleanText = (entry) => {
  if (!entry?.sections) return '';

  return entry.sections
    .map((section) => {
      const textParts = (section.contents || [])
        .filter((c) => typeof c === 'string')
        .map((c) =>
          c
            .replace(/<[^>]+>/g, '')
            .replace(/\[\d+\]/g, '')
            .replace(/\s+/g, ' ')
            .trim()
        )
        .filter(Boolean);

      return `## ${section.title}\n${textParts.join('\n\n')}`;
    })
    .join('\n\n');
};

app.get('/', (_req, res) => {
  res.json({ status: 'ok', message: 'KYM scraper API running' });
});

// /search?q=shrek&limit=5
app.get('/search', async (req, res) => {
  try {
    const q = req.query.q;
    const limit = req.query.limit ? parseInt(req.query.limit, 10) : 10;

    if (!q) return res.status(400).json({ error: 'Missing ?q=' });

    const results = await search(q, limit);
    res.json({ query: q, results });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'scrape_failed', details: err.message });
  }
});

// /detail?url=https://knowyourmeme.com/memes/shrek
// or /detail?slug=shrek
app.get('/detail', async (req, res) => {
  try {
    let url = req.query.url;
    const slug = req.query.slug;

    if (!url && !slug) return res.status(400).json({ error: 'Missing ?url= or ?slug=' });

    if (slug) url = `https://knowyourmeme.com/memes/${slug}`;

    const details = await getMeme(url);
    res.json(details);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'detail_failed', details: err.message });
  }
});

// /cleanText?url=https://knowyourmeme.com/memes/shrek
// or /cleanText?slug=shrek
app.get('/cleanText', async (req, res) => {
  try {
    let url = req.query.url;
    const slug = req.query.slug;

    if (!url && !slug) return res.status(400).json({ error: 'Missing ?url= or ?slug=' });

    if (slug) url = `https://knowyourmeme.com/memes/${slug}`;

    const entry = await getMeme(url);
    const cleanText = extractFullCleanText(entry);

    res.json({ title: entry.title || slug || url, cleanText });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'clean_text_failed', details: err.message });
  }
});

app.post('/generate-tts', async (req, res) => {
  try {
    if (!ELEVEN_API_KEY) {
      return res.status(500).json({ error: 'missing_eleven_api_key' });
    }

    const { text, voice_id, output_name, model_id, voice_settings } = req.body || {};

    if (!text || !voice_id) {
      return res.status(400).json({ error: 'Missing text or voice_id' });
    }

    const sanitizedOutput = output_name ? sanitizeFileName(output_name) : null;
    if (output_name && !sanitizedOutput) {
      return res.status(400).json({ error: 'invalid_output_name' });
    }

    const fileName = sanitizedOutput || `audio_${Date.now()}.mp3`;
    const filePath = path.join(AUDIO_DIR, fileName);

    if (!path.resolve(filePath).startsWith(`${path.resolve(AUDIO_DIR)}${path.sep}`)) {
      return res.status(400).json({ error: 'invalid_output_name' });
    }

    const payload = {
      text,
      model_id: model_id || 'eleven_multilingual_v2',
      voice_settings: voice_settings || {
        stability: 0.5,
        similarity_boost: 0.8,
      },
    };

    const ttsResponse = await axios({
      method: 'POST',
      url: `${ELEVEN_BASE_URL}/${voice_id}/stream`,
      headers: {
        'xi-api-key': ELEVEN_API_KEY,
        'Content-Type': 'application/json',
        Accept: 'audio/mpeg',
      },
      data: payload,
      responseType: 'arraybuffer',
    });

    fs.writeFileSync(filePath, Buffer.from(ttsResponse.data), 'binary');

    const publicUrl = `${req.protocol}://${req.get('host')}/audio/${encodeURIComponent(
      fileName
    )}`;

    return res.json({
      status: 'success',
      url: publicUrl,
    });
  } catch (err) {
    console.error(err.response?.data || err.message || err);
    res.status(500).json({
      error: 'tts_generation_failed',
      details: err.response?.data || err.message,
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`KYM API running on port ${PORT}`);
});
