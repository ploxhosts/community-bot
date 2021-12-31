import discord from 'discord.js';
import connection from '../db/mysql';
import fs from 'fs';

let copypasta = {}

fs.readFile('../copypasta.txt', 'utf8', function(err, data) {
  if (err) throw err;
  copypasta = JSON.parse(data);
});

async function copyPastaCheck(text: string, author: discord.User) {
}