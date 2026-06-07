const fs = require('fs');
const path = require('path');

// Read the HTML file
let html = fs.readFileSync(path.join(__dirname, 'lucky-shop.html'), 'utf8');

// Replace placeholders with environment variables
const replacements = {
  'AIzaSyDq7vRIO9qlhV0yN5VWyz5pFrWXOX6AosU': process.env.FIREBASE_API_KEY || '',
  'ai-chat-8fda5.firebaseapp.com':            process.env.FIREBASE_AUTH_DOMAIN || '',
  'ai-chat-8fda5':                            process.env.FIREBASE_PROJECT_ID || '',
  'ai-chat-8fda5.firebasestorage.app':        process.env.FIREBASE_STORAGE_BUCKET || '',
  '642285283509':                             process.env.FIREBASE_MESSAGING_SENDER_ID || '',
  '1:642285283509:web:edaa187037cbd4fec436fc': process.env.FIREBASE_APP_ID || '',
};

for (const [original, envVal] of Object.entries(replacements)) {
  if (envVal) html = html.split(original).join(envVal);
}

// Write to dist folder
if (!fs.existsSync('dist')) fs.mkdirSync('dist');
fs.writeFileSync(path.join(__dirname, 'dist', 'index.html'), html, 'utf8');

console.log('Build complete → dist/index.html');
