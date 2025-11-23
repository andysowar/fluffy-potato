# Know Your Meme CLI Wrapper

This project replaces the previous Python scraper with a minimal Node.js CLI that uses [`knowyourmeme-js`](https://www.npmjs.com/package/knowyourmeme-js) to fetch data directly from KnowYourMeme.

## Setup

```bash
npm install
```

## Usage

Search for memes:

```bash
node src/index.js search "shrek" 5
```

Get full details for a specific meme URL:

```bash
node src/index.js detail https://knowyourmeme.com/memes/shrek-rizz
```

If you run the CLI without arguments, it prints usage help. Results are emitted as JSON so they can be piped into other scripts or tools.
