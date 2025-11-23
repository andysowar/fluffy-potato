# Know Your Meme CLI Wrapper

This project replaces the previous Python scraper with a minimal Node.js CLI that uses [`knowyourmeme-js`](https://www.npmjs.com/package/knowyourmeme-js) to fetch data directly from KnowYourMeme.

## Setup

Prerequisites:

- Node.js 18+ (ES modules enabled)
- Internet access (required for `npm install` and scraping KnowYourMeme)

Install dependencies:

```bash
npm install
```

If you run into registry/network restrictions, try again from a network that can reach npmjs.com.

## Usage

The CLI exposes two commands—`search` and `detail`. You can invoke it directly with `node` or through `npm start --`.

### Search for memes

```bash
# Direct execution
node src/index.js search "shrek" 5

# Or via npm (note the double dash before arguments)
npm start -- search "shrek" 5
```

- The final number is an optional limit (defaults to 10).
- Results are printed as formatted JSON containing each entry's title, link, and thumbnail metadata.

### Get full details for a specific meme URL

```bash
node src/index.js detail https://knowyourmeme.com/memes/shrek-rizz
# or
npm start -- detail https://knowyourmeme.com/memes/shrek-rizz
```

This returns the complete payload from `knowyourmeme-js`, including images, tags, origin, and other metadata.

### Tips

- Run `node src/index.js --help` (or `npm start -- --help`) for inline usage help.
- Pipe the JSON anywhere you need: `node src/index.js search "shrek" | jq '.'`.
- If you only know a meme slug, build the URL as `https://knowyourmeme.com/memes/<slug>` and pass that to `detail`.
