import axios from 'axios';
import tlds from './tlds';
const whois = require('whois');

export const linkCheck = async (text: string): Promise<Number> => {

  const urls: Set<string> = new Set();

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char == ".") {
      let indexOfSpace = text.indexOf(" ", i);
      let runsOfChecking = 0;
      while (indexOfSpace - i < 2) {
        runsOfChecking++;
        indexOfSpace = text.indexOf(" ", i + runsOfChecking);
        if (runsOfChecking >= 6) {
          break;
        }
      }

      if (indexOfSpace == undefined || indexOfSpace == -1) {
        indexOfSpace = text.length;
      }
      
      let textAfterDot = text.substring(i + 1, indexOfSpace); // Get possible domain

      const rawTld = textAfterDot.split("/")[0].split('.') // Accounts for sub domains
      const tld = rawTld[rawTld.length - 1].replaceAll(" ", ""); // Get the TLD

      const validTld = tlds.includes(tld.toUpperCase()); // check if the tld exists in the list of tlds
      if (!validTld) continue;

 
      const url = text.substring(0, i);
      // Get all the index of spaces
      var indexOfSpaces = [];
      for(var ii = 0; ii < url.length; ii++) {
        if (url[ii] === " ") {
          indexOfSpaces.push(ii);
        }
      }

      if (indexOfSpaces.length === 0) { // If no space exists before link put 0 to get all text
        indexOfSpaces.push(0);
      }

      // Get the text before the link, even if there is a space
      let urlWithoutSpaces = "." + tld;
      let indexRound = indexOfSpaces.length
      while (indexRound > 0) { // Get the url without spaces
        urlWithoutSpaces = url.substring(indexOfSpaces[indexRound - 1], i);

        if (urlWithoutSpaces != "." + tld && urlWithoutSpaces != " " && urlWithoutSpaces != tld) {
          break;
        }
        indexRound --;
      }
      
      // End result
      const fullUrl = (urlWithoutSpaces + "." + textAfterDot).replaceAll(" ", "");
      urls.add(fullUrl);

    }
  }
  
  console.log(urls)
  return 0;
}
