import { badwords } from '../badwords';

async function badWordCheck(text: string, checkForImplicit: boolean = false) {
  let badWordCount = 0;
  
  // loop through text to detect for explicit bad words
  for (let i = 0; i < text.length; i++) {
    const word: string = text.split(" ")[i];

    // check for bad word
    if (badwords.indexOf(word)){
      badWordCount ++;
    }
  }

  if (checkForImplicit){
    // loop through bad words
    for (let i = 0; i < badwords.length; i++) {
      const word: string = badwords[i];
      if (text.indexOf(word) > -1){ // check if text includes any usage of the bad word
        badWordCount ++;
      }
    }
  }
 

  return badWordCount;
}