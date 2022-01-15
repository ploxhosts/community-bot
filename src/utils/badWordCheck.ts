import { badwords, falsePositives } from '../badwords';

function checkNotFalsePositive(word: string): boolean {
  if (falsePositives.indexOf(word) != -1){
    return false;
  }
  return true;
}

export async function badWordCheck(text: string, checkForImplicit: boolean = false) {
  let badWordCount = 0;

  text = text.toLowerCase();

  // loop through text to detect for explicit bad words
  for (let i = 0; i < text.length; i++) {
    const word: string = text.split(" ")[i];
    console.log(word);
    if (checkNotFalsePositive(word)) { // Run if it's not a false positive
      // check for bad word
      if (badwords.indexOf(word) && badwords[badwords.indexOf(word)] != undefined) {
        badWordCount += 1;
      }
    }
  }

  console.log("bad word count", badWordCount);

  if (checkForImplicit){
    // loop through bad words
    for (let i = 0; i < badwords.length; i++) {
      const word: string = badwords[i].toLowerCase();

      if (checkNotFalsePositive(word)) { // Run if it's not a false positive
        if (text.toLowerCase().indexOf(word) != -1 && badwords.indexOf(word) == -1) { // check if text includes any usage of the bad word
          console.log("choice word 2", badwords[i]);
          badWordCount += 1;
        }
      }
    }
  }
 

  return badWordCount;
}