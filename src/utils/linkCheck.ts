import axios from 'axios';
import tlds from './tlds';
const whois = require('whois');
import cheerio from 'cheerio';
import {badServers, badTlds} from './badLinks';

export const getLinks = async (text: string): Promise<Set<String>> => {

  const urls: Set<string> = new Set();

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char == ".") {
      let indexOfSpace = text.indexOf(" ", i);
      let runsOfChecking = 0;

      while (indexOfSpace - i < 2) { // Detection if space is between link12 . com 
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
  
  return urls;
}

const analyseWhois = async(text: string, threatScore: number) => {
  
  const maliciousDomains = ["nic.ru"]
  for (const maliciousDomain in maliciousDomains) {
    if (text.includes(maliciousDomain)) {
      threatScore += 12;
    }
  }

  const splitText = text.split("\n");
  for (let i = 0; i < splitText.length; i++) {
    if (splitText[i].includes("Creation Date:")) {
      const creationDate = splitText[i].slice(splitText[i].indexOf(":") + 1, splitText[i].length);
      console.log("Creation date", creationDate);
      threatScore += 8;
    }
  }
  return threatScore;
}

export const checkLink = async (url: string, threatScore: number = 0, round: number = 0): Promise<Number | boolean> => {
  let response;
  try {
    response = await axios.get(url);
  } catch (err) {
    console.log("Url issue: " + url);
    return false;
  }

  const headers = response.headers; // get the website's headers

  let badServer = badServers.find(o => o.name == headers["server"]); // Check if the server is a bad server i.e typically used for phishing

  if (badServer !== undefined) {
    threatScore += badServer.score; // add the threat score
  };

  const html = response.data;
  
  const parsedHtml = cheerio.load(html, {xmlMode: false});

  const scriptUrls = parsedHtml('script').get();
  const linkUrls = parsedHtml('link').get();
  const pageTitle = parsedHtml('head > title').text();
  const splitTitle = pageTitle.split(" ");
  
  const pageDescription = parsedHtml('head > meta[name="description"]').attr('content');
  const splitDescription = pageDescription?.split(" ");

  const pageKeywords = parsedHtml('head > meta[name="keywords"]').attr('content');
  const splitKeywords = pageKeywords?.split(",");

  const pageH1 = parsedHtml('h1').text();
  const splitH1 = pageH1?.split(" ");
  
  const spamLikelyWords = ["free", "nitro", "steam", "win", "download", "downloads", "now"]
  

  // SECTION: TITLE checks
  if (pageTitle !== undefined || pageDescription == "") {
    threatScore += 2;
  }
  for (const titleWord in splitTitle) { // loop through page title to check if it contains anything that is known spam
    if (spamLikelyWords.includes(titleWord.toLowerCase())) {
      threatScore += 4;
    }
  }

  // SECTION: Description checks
  if (pageDescription == undefined || pageDescription == "") { // If no page description exists
    threatScore += 6;
  } else if (splitDescription && splitDescription.length < 5) { // If the page description is too short
    threatScore += 2;
  }

  for (const descWord in splitDescription) { // loop through page description to check if it contains anything that is known spam
    if (spamLikelyWords.includes(descWord.toLowerCase())) {
      threatScore += 3;
    }
  }

  // SECTION: Keyword checks
  if (pageKeywords == undefined || pageKeywords == "") {
    threatScore += 2;
  }
  
  for (const keyWord in splitKeywords) { // loop through page keywords to check if it contains anything that is known spam
    if (spamLikelyWords.includes(keyWord.toLowerCase())) {
      threatScore += 3;
    }
  }

  // SECTION: Heading 1 check
  if (pageH1 == undefined || pageH1 == "") {
    threatScore += 4;
  }

  for (const headingWord in splitH1) { // loop through h1 words to check if it contains anything that is known spam
    if (spamLikelyWords.includes(headingWord.toLowerCase())) {
      threatScore += 3;
    }
  }

  for (let i = 0; i < scriptUrls.length; i++) { // check urls for script tags
    const scriptUrl = scriptUrls[i].attribs['src'];
    if (scriptUrl) {
      if (round == 10) { // Prevent more than 10 rounds of checking urls
        return 0;
      }
      round += 1;
      const returnThreat = await checkLink(scriptUrl, threatScore, round);
      if (typeof returnThreat == "number") {
        threatScore += returnThreat;
      }
    }
  };

  for (let i = 0; i < linkUrls.length; i++) { // check urls for stylesheets
    const scriptUrl = linkUrls[i].attribs['href'];
    if (scriptUrl) {
      if (round == 4) { // Prevent more than 4 rounds of checking urls
        return 0;
      }
      round += 1;
      const returnThreat = await checkLink(scriptUrl, threatScore, round);
      if (typeof returnThreat == "number") {
        threatScore += returnThreat;
      }
    }
  };


  var language = parsedHtml("html").attr("lang");

  if (language == "ru"){
    threatScore += 6;
  } else if (language == "en") {
    threatScore += 0;
  } else { // Promotes best practices
    threatScore += 2;
  }

  let hostname = new URL(url).hostname
  console.log("hostname", hostname);
  var re=/\.([^\.]+?)$/;
 
  let domain = re.exec(hostname);
  let tld: string;
  if (domain) {
    tld = domain[1];
  }

  badTlds.forEach(element => {
    if (tld == element.name) {
      threatScore += element.score;
    }
  });

  // TODO: Index the site and not do whois again
  await whois.lookup(hostname, async function(err: any, data: any) {
    threatScore += await analyseWhois(data, threatScore);
  })

  console.log("threat score: " + threatScore + " for domain: " + url);
  return threatScore;
}
