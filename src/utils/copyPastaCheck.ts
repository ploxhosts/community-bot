import { fakeDiscordAnnc, shareDeath, unicode } from '../data/copypasta';

export async function copyPastaCheck(text: string) {
    let discordAnnouncementCount = 0;
    let unicodeCount = 0;
    let shareDeathCount = 0;

    for (const element of fakeDiscordAnnc) {
        if (text.toLowerCase().includes(element)) {
            discordAnnouncementCount++;
        }
    }

    for (const element of unicode) {
        if (text.toLowerCase().includes(element)) {
            unicodeCount++;
        }
    }

    for (const element of shareDeath) {
        if (text.toLowerCase().includes(element)) {
            shareDeathCount++;
        }
    }

    return {
        discordAnnouncementCount,
        unicodeCount,
        shareDeathCount,
    };
}
