import discord from 'discord.js';
import connection from '../db/mysql';
import {fakeDiscordAnnc, unicode, shareDeath} from '../copypasta';

async function copyPastaCheck(text: string, author: discord.User) {
  let discordAnnouncementCount = 0;
  let unicodeCount = 0;
  let shareDeathCount = 0;

  // loop through text
  for (let i = 0; i < text.length; i++) {
    const word: string = text[i]
    // check for discord announcement
    if (fakeDiscordAnnc.indexOf(word)){
      discordAnnouncementCount++;
    }
    // check for unicode
    if (unicode.indexOf(word)){
      unicodeCount++;
    }

    // check for share death
    if (shareDeath.indexOf(word)){
      shareDeathCount++;
    }
  }

  return {
    discordAnnouncementCount,
    unicodeCount,
    shareDeathCount
  }
}