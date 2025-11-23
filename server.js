import express from 'express';
import cors from 'cors';
import { search, getMeme } from 'knowyourmeme-js';

const app = express();
app.use(cors());

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

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`KYM API running on port ${PORT}`);
});
