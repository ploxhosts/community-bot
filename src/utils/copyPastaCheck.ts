import {fakeDiscordAnnc, unicode, shareDeath} from '../data/copypasta';

export async function copyPastaCheck(text: string) {
  let discordAnnouncementCount = 0;
  let unicodeCount = 0;
  let shareDeathCount = 0;

  for (let i = 0; i < fakeDiscordAnnc.length; i++) {
    if (text.toLowerCase().indexOf(fakeDiscordAnnc[i]) > -1){
      discordAnnouncementCount++;
    }
  }

  for (let i = 0; i < unicode.length; i++) {
    if (text.toLowerCase().indexOf(unicode[i]) > -1){
      unicodeCount++;
    }
  }

  for (let i = 0; i < shareDeath.length; i++) {
    if (text.toLowerCase().indexOf(shareDeath[i]) > -1){
      shareDeathCount++;
    }
  }

  return {
    discordAnnouncementCount,
    unicodeCount,
    shareDeathCount
  }
}