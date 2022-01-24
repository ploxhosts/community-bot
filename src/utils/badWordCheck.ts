import { badwords, falsePositives, subsitutes } from '../data/badwords';

function checkNotFalsePositive(word: string): boolean {
    if (falsePositives.includes(word)) {
        return false;
    }

    return true;
}

function checkForSubsitutes(text: string, word: string): boolean {
    for (const subsitute of subsitutes) {
        console.log(subsitute.words);

        if (subsitute.words.includes(word)) {
            const words = text.toLowerCase().split(' ');
            const wordPosition = words.indexOf(word);

            if (subsitute.before.includes(words[wordPosition - 1])) {
                console.log(
                    'Not a bad word - before',
                    word,
                    words[wordPosition - 1]
                );

                return true;
            }

            if (subsitute.after.includes(words[wordPosition + 1])) {
                return true;
            }
        }
    }

    return false;
}

export async function badWordCheck(
    text: string,
    checkForImplicit: boolean = false
) {
    let badWordCount = 0;

    text = text.toLowerCase();

    // loop through text to detect for explicit bad words

    if (checkForImplicit) {
        // Check for implicit words too
        const usedWords: number[] = [];

        for (const badword of badwords) {
            const word: string = badword.toLowerCase();

            if (checkNotFalsePositive(word)) {
                // Run if it's not a false positive
                const badWordIndex = text.toLowerCase().indexOf(word);

                if (badWordIndex != -1 && !usedWords.includes(badWordIndex)) {
                    // check if text includes any usage of the bad word
                    console.log(checkForSubsitutes(text, word));

                    if (!checkForSubsitutes(text, word)) {
                        usedWords.push(badWordIndex);
                        const regex = new RegExp(word, 'g');
                        const count = (text.match(regex) || []).length;

                        badWordCount += count;
                    }
                }
            }
        }
    } else {
        // check for only plain usage
        for (let index = 0; index < text.length; index++) {
            const word: string = text.split(' ')[index];

            if (
                checkNotFalsePositive(word) && // Run if it's not a false positive
                // check for bad word

                badwords.indexOf(word) &&
                badwords[badwords.indexOf(word)] != undefined
            ) {
                badWordCount += 1;
            }
        }
    }

    return badWordCount;
}
