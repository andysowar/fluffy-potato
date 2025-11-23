# Know Your Meme Heroku API

A minimal Express API for Know Your Meme that uses [`knowyourmeme-js`](https://www.npmjs.com/package/knowyourmeme-js). Deploy to Heroku and call it from your Custom GPT.

## Endpoints

- `GET /` — health check.
- `GET /search?q=<query>&limit=<n>` — search KYM (default limit 10).
- `GET /detail?url=<full-kym-url>` — fetch full details for a meme page.
- `GET /detail?slug=<meme-slug>` — same as above, builds the KYM URL for you.
- `GET /cleanText?slug=<meme-slug>` or `?url=<full-kym-url>` — return the cleaned, markdown-only text for an entry.
- `POST /generate-tts` — proxy ElevenLabs TTS, returning a URL to the generated MP3.

Example calls once deployed (replace `your-app-name`):

```
https://your-app-name.herokuapp.com/search?q=shrek
https://your-app-name.herokuapp.com/detail?slug=shrek
https://your-app-name.herokuapp.com/detail?url=https://knowyourmeme.com/memes/shrek
```

## Local run

```bash
npm install
PROXY_API_KEY=super-secret-kym-key npm start
# then open http://localhost:3000/search?q=shrek with header: x-api-key: super-secret-kym-key
```

To test ElevenLabs locally, set both `ELEVEN_API_KEY` and `PROXY_API_KEY` in your environment and send a request (note the `x-api-key` header is required):

```bash
ELEVEN_API_KEY=your-key PROXY_API_KEY=super-secret-kym-key npm start

curl -X POST http://localhost:3000/generate-tts \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-kym-key" \
  -d '{"text":"Hello world!","voice_id":"your-voice-id"}'
```

## Heroku deploy

1) Create the app (Heroku CLI):

```bash
heroku create your-app-name
```

2) Push the repo (builds automatically):

```bash
git push heroku main
```

3) Open it:

```bash
heroku open
```

Heroku uses the included `Procfile` and `npm start` to boot `server.js`.

### ElevenLabs passthrough (Heroku)

1) Add the environment variable:

```bash
heroku config:set ELEVEN_API_KEY=your-key
heroku config:set PROXY_API_KEY=super-secret-kym-key
```

2) Deploy as usual (`git push heroku main`).

3) Call the endpoint:

```bash
curl -X POST https://your-app-name.herokuapp.com/generate-tts \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-kym-key" \
  -d '{"text":"Hello world!","voice_id":"your-voice-id"}'
```

You will receive JSON containing a public URL to the generated MP3 hosted at `/audio/<file>`.

`/audio/*` URLs are publicly readable and do **not** require the `x-api-key` header so they can be fetched directly by browsers or `<audio>` tags.
