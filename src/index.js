import { getMeme, search } from 'knowyourmeme-js';

function printUsage() {
  console.log(`Usage:\n  node src/index.js search <query> [limit]\n  node src/index.js detail <kym-url>`);
}

function parseLimit(raw) {
  if (!raw) return undefined;
  const value = Number.parseInt(raw, 10);
  return Number.isFinite(value) && value > 0 ? value : undefined;
}

async function run() {
  const [command, ...args] = process.argv.slice(2);

  if (!command) {
    printUsage();
    return;
  }

  if (command === 'help' || command === '--help' || command === '-h') {
    printUsage();
    return;
  }

  if (command === 'search') {
    const [query, limitArg] = args;
    if (!query) {
      console.error('Please provide a search query.');
      printUsage();
      process.exitCode = 1;
      return;
    }

    const limit = parseLimit(limitArg);
    const results = await search(query, limit);
    console.log(JSON.stringify(results, null, 2));
    return;
  }

  if (command === 'detail') {
    const [url] = args;
    if (!url) {
      console.error('Please provide a KnowYourMeme meme URL.');
      printUsage();
      process.exitCode = 1;
      return;
    }

    const details = await getMeme(url);
    console.log(JSON.stringify(details, null, 2));
    return;
  }

  console.error(`Unknown command: ${command}`);
  printUsage();
  process.exitCode = 1;
}

run().catch((error) => {
  console.error('Failed to fetch data from KnowYourMeme:', error?.message || error);
  process.exitCode = 1;
});
