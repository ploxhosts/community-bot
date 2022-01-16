import axios from 'axios';
const urlRegex = require('url-regex');
import tlds from './tlds';
const whois = require('whois');

export const linkCheck = async (text: string): Promise<Number> => {

  const urls: Set<string> = new Set();

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char == ".") {
      let indexOfSpace = text.indexOf(" ", i);

      if (indexOfSpace == undefined || indexOfSpace == -1) {
        indexOfSpace = text.length;
      }
      
      let textAfterDot = text.substring(i + 1, indexOfSpace); // Get possible domain

      const rawTld = textAfterDot.split("/")[0].split('.') // Accounts for sub domains
      const tld = rawTld[rawTld.length - 1]; // Get the TLD

      const validTld = tlds.includes(tld.toUpperCase()); // check if the tld exists in the list of tlds
      if (!validTld) continue;


      const url = text.substring(0, i);

      var indexOfSpaces = [];
      for(var ii = 0; ii < url.length; ii++) {
        if (url[ii] === " ") {
          indexOfSpaces.push(ii);
        }
      }

      if (indexOfSpaces.length === 0) {
        indexOfSpaces.push(0);
      }
      const urlWithoutSpaces = url.substring(indexOfSpaces[indexOfSpaces.length - 1], i);
      const fullUrl = (urlWithoutSpaces + "." + textAfterDot).replaceAll(" ", "");

      urls.add(fullUrl);

    }
  }
  
  console.log(urls)
  return 0;
}


linkCheck("Hello world https:// link1.com")
console.log("-------------")
linkCheck("Hello world https://link1.com and https://link2.co.uk")
console.log("-------------")
linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk")
console.log("-------------")