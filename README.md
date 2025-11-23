# Know Your Meme Heroku API

A minimal Express API for Know Your Meme that uses [`knowyourmeme-js`](https://www.npmjs.com/package/knowyourmeme-js). Deploy to Heroku and call it from your Custom GPT.

## Endpoints

- `GET /` — health check.
- `GET /search?q=<query>&limit=<n>` — search KYM (default limit 10).
- `GET /detail?url=<full-kym-url>` — fetch full details for a meme page.
- `GET /detail?slug=<meme-slug>` — same as above, builds the KYM URL for you.

Example calls once deployed (replace `your-app-name`):

```
https://your-app-name.herokuapp.com/search?q=shrek
https://your-app-name.herokuapp.com/detail?slug=shrek
https://your-app-name.herokuapp.com/detail?url=https://knowyourmeme.com/memes/shrek
```

## Local run

```bash
npm install
npm start
# then open http://localhost:3000/search?q=shrek
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
