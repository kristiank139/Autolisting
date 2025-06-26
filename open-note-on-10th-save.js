const fs = require('fs');
const { exec } = require('child_process');

const countFile = './.savecount';
const noteFile = './note.md';

// Read current count or start at 0
let count = 0;
if (fs.existsSync(countFile)) {
  count = parseInt(fs.readFileSync(countFile, 'utf8'), 10);
}

count++;
fs.writeFileSync(countFile, count.toString());

// On every 10th save, open the note
if (count % 100 === 0) {
  exec(`code -r ${noteFile}`, (error) => {
    if (error) {
      console.error(`Error opening note: ${error.message}`);
    }
  });
}