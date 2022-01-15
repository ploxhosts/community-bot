import { badwords, falsePositives, subsitutes } from '../badwords';

function checkNotFalsePositive(word: string): boolean {
  if (falsePositives.indexOf(word) != -1){
    return false;
  }
  return true;
}

function checkForSubsitutes(text: string, word: string): boolean {
  for (var i = 0; i < subsitutes.length; i++) {
    console.log(subsitutes[i].words);
    if (subsitutes[i].words.includes(word)){
      const words = text.toLowerCase().split(' ');
      const wordPosition = words.indexOf(word);

      if (subsitutes[i].before.includes(words[wordPosition - 1])){
        console.log("Not a bad word - before", word, words[wordPosition - 1]);
        return true;
      }
      
      if (subsitutes[i].after.includes(words[wordPosition + 1])){
        return true;
      }
    }
  }
  return false;
}

export async function badWordCheck(text: string, checkForImplicit: boolean = false) {
  let badWordCount = 0;

  text = text.toLowerCase();

  // loop through text to detect for explicit bad words

  if (checkForImplicit){ // Check for implicit words too
    let usedWords: number[] = []
    for (let i = 0; i < badwords.length; i++) {
      const word: string = badwords[i].toLowerCase();
      if (checkNotFalsePositive(word)) { // Run if it's not a false positive
        const badWordIndex = text.toLowerCase().indexOf(word);
        if ( badWordIndex != -1 && usedWords.indexOf(badWordIndex) == -1) { // check if text includes any usage of the bad word
          console.log(checkForSubsitutes(text, word));
          if (!checkForSubsitutes(text, word)){
            usedWords.push(badWordIndex);
            let regex = new RegExp(word, "g"); 
            let count = (text.match(regex) || []).length;
            badWordCount += count;
          }
        }
      }
    }
  } else { // check for only plain usage
    for (let i = 0; i < text.length; i++) {
      const word: string = text.split(" ")[i];
      if (checkNotFalsePositive(word)) { // Run if it's not a false positive
        // check for bad word
        if (badwords.indexOf(word) && badwords[badwords.indexOf(word)] != undefined) {
          badWordCount += 1;
        }
      }
    }
  
  }
 

  return badWordCount;
}