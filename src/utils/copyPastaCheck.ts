import discord from 'discord.js';
import connection from '../db/mysql';
import {fakeDiscordAnnc, unicode, shareDeath} from '../copypasta';

async function copyPastaCheck(text: string, author: discord.User) {
  let discordAnnouncementCount = 0;
  let unicodeCount = 0;
  let shareDeathCount = 0;

  if (process.env.DB_MODE === "true") {
  } // TODO: Use database to get the limits
}