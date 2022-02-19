import axios from 'axios';

import tlds from '../data/tlds';
const lookup = require('web-whois');

import cheerio from 'cheerio';

import { badServers, badTlds } from '../data/badLinks';

export const getLinks = async (text: string): Promise<Set<string>> => {
    const urls: Set<string> = new Set();

    for (let index = 0; index < text.length; index++) {
        const char = text[index];

        if (char == '.') {
            let indexOfSpace = text.indexOf(' ', index);
            let runsOfChecking = 0;

            while (indexOfSpace - index < 2) {
                // Detection if space is between link12 . com
                runsOfChecking++;
                indexOfSpace = text.indexOf(' ', index + runsOfChecking);

                if (runsOfChecking >= 6) {
                    break;
                }
            }

            if (indexOfSpace == undefined || indexOfSpace == -1) {
                indexOfSpace = text.length;
            }

            const textAfterDot = text.slice(index + 1, indexOfSpace); // Get possible domain

            const indexFirstTld = textAfterDot.split('/').at(0);

            if (indexFirstTld == undefined) {
                continue;
            }

            const rawTld = indexFirstTld.split('.').at(-1); // Accounts for sub domains

            if (rawTld == undefined) {
                continue;
            }

            const tld = rawTld.replaceAll(' ', ''); // Get the TLD

            if (tld == undefined) {
                continue;
            }

            const validTld = tlds.includes(tld.toUpperCase()); // check if the tld exists in the list of tlds

            if (!validTld) continue;

            const url = text.slice(0, Math.max(0, index));

            // Get all the index of spaces
            const indexOfSpaces = [];

            for (const [ii, element] of url.split('').entries()) {
                if (element === ' ') {
                    indexOfSpaces.push(ii);
                }
            }

            if (indexOfSpaces.length === 0) {
                // If no space exists before link put 0 to get all text
                indexOfSpaces.push(0);
            }

            // Get the text before the link, even if there is a space
            let urlWithoutSpaces = '.' + tld;
            let indexRound = indexOfSpaces.length;

            while (indexRound > 0) {
                // Get the url without spaces
                urlWithoutSpaces = url.slice(
                    indexOfSpaces[indexRound - 1],
                    index
                );

                if (
                    urlWithoutSpaces != '.' + tld &&
                    urlWithoutSpaces != ' ' &&
                    urlWithoutSpaces != tld
                ) {
                    break;
                }

                indexRound--;
            }

            // End result
            const fullUrl = (urlWithoutSpaces + '.' + textAfterDot).replaceAll(
                ' ',
                ''
            );

            urls.add(fullUrl);
        }
    }

    return urls;
};

const analyseWhois = async (data: any, threatScore: number) => {
    if (data) {
        const maliciousDomains = ['nic.ru'];

        for (const domain of maliciousDomains) {
            if (data.abuse.includes(domain)) {
                threatScore += 10;
            }
        }

        if (data.registrar.includes('RU')) {
            threatScore += 10;
        }

        const registrationDate = Date.parse(data.registration) / 1000;
        const expirationDate = Date.parse(data.expiration) / 1000;

        const now = Date.now() / 1000;

        console.log(now - registrationDate);
        console.log(registrationDate - now);

        if (now - registrationDate < 60 * 60 * 24 * 30) {
            // Domain was registered less than 30 days ago
            threatScore += 30;
        }

        if (expirationDate - registrationDate <= 60 * 60 * 24 * 366) {
            // Domain was registered for less than a year (Normally they don't expect it to last long)
            threatScore += 30;
        }
    }

    return threatScore;
};

const checkHtml = async (
    parsedHtml: cheerio.Root,
    threatScore: number,
    round: number
) => {
    const scriptUrls = parsedHtml('script').get();
    const linkUrls = parsedHtml('link').get();
    const pageTitle = parsedHtml('head > title').text();
    const splitTitle = pageTitle.split(' ');

    const pageDescription = parsedHtml('head > meta[name="description"]').attr(
        'content'
    );
    const splitDescription = pageDescription?.split(' ');

    const pageKeywords = parsedHtml('head > meta[name="keywords"]').attr(
        'content'
    );
    const splitKeywords = pageKeywords?.split(',');

    const pageH1 = parsedHtml('h1').text();
    const splitH1 = pageH1?.split(' ');

    const spamLikelyWords = new Set([
        'free',
        'nitro',
        'steam',
        'win',
        'download',
        'downloads',
        'now',
    ]);

    // SECTION: TITLE checks
    if (pageTitle !== undefined || pageDescription == '') {
        threatScore += 2;
    }

    for (const titleWord in splitTitle) {
        // loop through page title to check if it contains anything that is known spam
        if (spamLikelyWords.has(titleWord.toLowerCase())) {
            threatScore += 4;
        }
    }

    // SECTION: Description checks
    if (pageDescription == undefined || pageDescription == '') {
        // If no page description exists
        threatScore += 6;
    } else if (splitDescription && splitDescription.length < 5) {
        // If the page description is too short
        threatScore += 2;
    }

    for (const descWord in splitDescription) {
        // loop through page description to check if it contains anything that is known spam
        if (spamLikelyWords.has(descWord.toLowerCase())) {
            threatScore += 3;
        }
    }

    // SECTION: Keyword checks
    if (pageKeywords == undefined || pageKeywords == '') {
        threatScore += 2;
    }

    for (const keyWord in splitKeywords) {
        // loop through page keywords to check if it contains anything that is known spam
        if (spamLikelyWords.has(keyWord.toLowerCase())) {
            threatScore += 3;
        }
    }

    // SECTION: Heading 1 check
    if (pageH1 == undefined || pageH1 == '') {
        threatScore += 4;
    }

    for (const headingWord in splitH1) {
        // loop through h1 words to check if it contains anything that is known spam
        if (spamLikelyWords.has(headingWord.toLowerCase())) {
            threatScore += 3;
        }
    }

    for (const scriptUrl_ of scriptUrls) {
        // check urls for script tags
        const scriptUrl = scriptUrl_.attribs['src'];

        if (scriptUrl) {
            if (round == 10) {
                // Prevent more than 10 rounds of checking urls
                return 0;
            }

            round += 1;
            const returnThreat = await checkLink(scriptUrl, threatScore, round);

            if (typeof returnThreat == 'number') {
                threatScore += returnThreat;
            }
        }
    }

    for (const linkUrl of linkUrls) {
        // check urls for stylesheets
        const scriptUrl = linkUrl.attribs['href'];

        if (scriptUrl) {
            if (round == 4) {
                // Prevent more than 4 rounds of checking urls
                return 0;
            }

            round += 1;
            const returnThreat = await checkLink(scriptUrl, threatScore, round);

            if (typeof returnThreat == 'number') {
                threatScore += returnThreat;
            }
        }
    }

    const language = parsedHtml('html').attr('lang');

    if (language == 'ru') {
        threatScore += 6;
    } else if (language == 'en') {
        threatScore += 0;
    } else {
        // Promotes best practices
        threatScore += 2;
    }

    return threatScore;
};

export const checkLink = async (
    url: string,
    threatScore: number = 0,
    round: number = 0
): Promise<number | boolean> => {
    let response;

    try {
        response = await axios.get(url);
    } catch {
        console.log('Url issue: ' + url);

        return false;
    }

    const { headers, data } = response; // get the website's headers

    const badServer = badServers.find((o) => o.name == headers['server']); // Check if the server is a bad server i.e typically used for phishing

    if (badServer !== undefined) {
        threatScore += badServer.score; // add the threat score
    }

    const parsedHtml = cheerio.load(data, { xmlMode: false });

    threatScore += await checkHtml(parsedHtml, threatScore, round);

    const { hostname } = new URL(url);

    console.log('hostname', hostname);
    const re = /\.([^.]+?)$/;

    const domain = re.exec(hostname);

    let tld: string | undefined;

    if (domain) {
        tld = domain.at(1);
    }

    if (!tld || !domain) {
        return false;
    }

    for (const element of badTlds) {
        if (tld == element.name) {
            threatScore += element.score;
        }
    }

    // TODO: Index the site and not do whois again

    const whois = await lookup(domain.input);

    threatScore += await analyseWhois(whois, threatScore);

    console.log('threat score: ' + threatScore + ' for domain: ' + url);

    return threatScore;
};

checkLink('http://discoerd.gift/Zg82N4Zemc');
checkLink('https://xulgos.com/');

// TODO: If the file ends in .png .ico or .css then ignore
// TODO: If the content url starts with  https://cdn.jsdelivr.net/npm/bulma then ignore
// TODO: If the content url starts with  https://static.cloudflareinsights.com/
// TODO: If the content url starts with https://www.google-analytics.com/ then ignore
// TODO: If the content url starts with https://www.googletagmanager.com/ then ignore
// TODO: If the content url starts with  https://www.google.com/ then ignore
// TODO: If the content url starts with  https://kit.fontawesome.com/ then ignore
// TODO: if the content url starts with https://unpkg.com/react-dom then ignore
