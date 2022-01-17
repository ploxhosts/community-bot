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


linkCheck("Hello world https://link1.com")
console.log("-------------")
linkCheck("Hello world https://link1.com and https://link2.co.uk")
console.log("-------------")
linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk")
console.log("-------------")

linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk https:// link5.com https://link6 .com")
console.log("-------------")

linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk https:// link5.com https://link6 .com | https: //link7.com")
console.log("-------------")

linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk https:// link5.com https://link6 .com | https: //link7.com | https: // link8.com")
console.log("-------------")

linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk https:// link5.com https://link6 .com | https: //link7.com | https: // link8.com | https: // link9 .com ")
console.log("-------------")

linkCheck("Hello world https://link1.com and https://link2.co.uk/link3.com and link4.co.uk https:// link5.com https://link6 .com | https: //link7.com | https: // link8.com | https: // link9 .com | https: // link10 . com")
console.log("-------------")

linkCheck("https://link1.com | https://link2.co.uk/link3.com | link4.co.uk https:// link5.com https://link6 .com | https: //link7.com | https: // link8.com | https: // link9 .com | https: // link10 . com | https: // link11. com")
console.log("-------------")