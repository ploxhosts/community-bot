import { badwords, falsePositives } from '../badwords';

function checkNotFalsePositive(word: string): boolean {
  if (falsePositives.indexOf(word)){
    return false;
  }
  return true;
}

export async function badWordCheck(text: string, checkForImplicit: boolean = false) {
  let badWordCount = 0;
  
  // loop through text to detect for explicit bad words
  for (let i = 0; i < text.length; i++) {
    const word: string = text.split(" ")[i].toLowerCase();

    if (checkNotFalsePositive(word)) { // Run if it's not a false positive

      // check for bad word
      if (badwords.indexOf(word)){
        badWordCount ++;
      }
    }
  }

  if (checkForImplicit){
    // loop through bad words
    for (let i = 0; i < badwords.length; i++) {
      const word: string = badwords[i].toLowerCase();

      if (checkNotFalsePositive(word)) { // Run if it's not a false positive
        if (text.toLowerCase().indexOf(word) > -1){ // check if text includes any usage of the bad word
          badWordCount ++;
        }
      }
    }
  }
 

  return badWordCount;
}