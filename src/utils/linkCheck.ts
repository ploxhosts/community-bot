import axios from 'axios';

import tlds from '../data/tlds';
const lookup = require('web-whois');

import cheerio from 'cheerio';

import { badServers, badTlds, urlShorteners } from '../data/badLinks';
import { goodHostnames } from '../data/goodLinks';
import { addLink, checkLinkInDB } from '../db/services/Links';

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

const getProxy = async () => {
    return await axios
        .get(
            'https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all'
        )
        .then((response) => {
            const proxies = [];

            for (const proxy of JSON.parse(response.data)['data']) {
                if (proxy.length > 0) {
                    proxies.push({
                        ip: proxy.ip,
                        port: proxy.port,
                    });
                }
            }

            return proxies;
        })
        .catch((error) => {
            console.log(error);
        });
};

const analyseWhois = async (
    data: any,
    threatScore: number,
    process: { type: string; score: number }[]
) => {
    if (data) {
        const maliciousDomains = ['nic.ru'];

        for (const domain of maliciousDomains) {
            if (data.abuse.includes(domain)) {
                threatScore += 10;

                process.push({ type: 'Abuse email is Russian', score: 10 });
            }
        }

        if (data.registrar.includes('RU')) {
            threatScore += 10;
            process.push({ type: 'Registra is Russian', score: 10 });
        }

        const registrationDate = Date.parse(data.registration) / 1000;
        const expirationDate = Date.parse(data.expiration) / 1000;

        const now = Date.now() / 1000;

        console.log(now - registrationDate);
        console.log(registrationDate - now);

        if (now - registrationDate < 60 * 60 * 24 * 30) {
            // Domain was registered less than 30 days ago
            threatScore += 30;
            process.push({
                type: 'registration was under 30 days ago',
                score: 30,
            });
        }

        if (expirationDate - registrationDate <= 60 * 60 * 24 * 366) {
            // Domain was registered for less than a year (Normally they don't expect it to last long)
            threatScore += 10;

            process.push({
                type: 'Expiration date is only for a year',
                score: 10,
            });
        }
    }

    return { threatScore, process };
};

const checkHtml = async (
    parsedHtml: cheerio.Root,
    threatScore: number,
    round: number,
    process: { type: string; score: number }[],
    urlShortening: boolean = false,
    guildId: string | undefined
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
        process.push({ type: 'Title is empty', score: 2 });
    }

    for (const titleWord in splitTitle) {
        // loop through page title to check if it contains anything that is known spam
        if (spamLikelyWords.has(titleWord.toLowerCase())) {
            threatScore += 4;
            process.push({
                type: `Title contains spam ${titleWord.toLowerCase()}`,
                score: 4,
            });
        }
    }

    // SECTION: Description checks
    if (pageDescription == undefined || pageDescription == '') {
        // If no page description exists
        threatScore += 6;
        process.push({ type: 'Description is empty', score: 6 });
    } else if (splitDescription && splitDescription.length < 5) {
        // If the page description is too short
        threatScore += 2;
        process.push({ type: 'Description is too short', score: 2 });
    }

    for (const descWord in splitDescription) {
        // loop through page description to check if it contains anything that is known spam
        if (spamLikelyWords.has(descWord.toLowerCase())) {
            threatScore += 3;
            process.push({
                type: `Description contains spam ${descWord.toLowerCase()}`,
                score: 3,
            });
        }
    }

    // SECTION: Keyword checks
    if (pageKeywords == undefined || pageKeywords == '') {
        threatScore += 2;
        process.push({ type: 'Keywords are empty', score: 2 });
    }

    for (const keyWord in splitKeywords) {
        // loop through page keywords to check if it contains anything that is known spam
        if (spamLikelyWords.has(keyWord.toLowerCase())) {
            threatScore += 3;
            process.push({
                type: `Keywords contains spam ${keyWord.toLowerCase()}`,
                score: 3,
            });
        }
    }

    // SECTION: Heading 1 check
    if (pageH1 == undefined || pageH1 == '') {
        threatScore += 4;
        process.push({ type: 'H1 is empty', score: 4 });
    }

    for (const headingWord in splitH1) {
        // loop through h1 words to check if it contains anything that is known spam
        if (spamLikelyWords.has(headingWord.toLowerCase())) {
            threatScore += 3;
            process.push({
                type: `H1 contains spam ${headingWord.toLowerCase()}`,
                score: 3,
            });
        }
    }

    for (const scriptUrl_ of scriptUrls) {
        // check urls for script tags
        const scriptUrl = scriptUrl_.attribs['src'];

        if (scriptUrl) {
            if (round == 10) {
                // Prevent more than 10 rounds of checking urls
                return { threatScore, process };
            }

            round += 1;
            const returnThreat = await checkLink(
                scriptUrl,
                threatScore,
                round,
                urlShortening,
                guildId
            );

            process = process.concat(returnThreat.process);

            if (typeof returnThreat.score == 'number') {
                threatScore += returnThreat.score;
            }
        }
    }

    for (const linkUrl of linkUrls) {
        // check urls for stylesheets
        const scriptUrl = linkUrl.attribs['href'];

        if (scriptUrl) {
            if (round == 4) {
                // Prevent more than 4 rounds of checking urls
                return { threatScore, process };
            }

            round += 1;
            const returnThreat = await checkLink(
                scriptUrl,
                threatScore,
                round,
                urlShortening,
                guildId
            );

            if (typeof returnThreat.score == 'number') {
                threatScore += returnThreat.score;
            }

            process = process.concat(returnThreat.process);
        }
    }

    const language = parsedHtml('html').attr('lang');

    if (language == 'ru') {
        threatScore += 6;
        process.push({ type: 'Language is Russian', score: 6 });
    } else if (language == 'en') {
        threatScore += 0;
    } else {
        // Promotes best practices
        threatScore += 2;
        process.push({ type: 'Language is not present', score: 2 });
    }

    return { threatScore, process };
};

function rand(items: any) {
    return items[Math.trunc(items.length * Math.random())];
}
export const checkLink = async (
    url: string,
    threatScore: number = 0,
    round: number = 0,
    urlShortening: boolean = false,
    guildId: string | undefined
): Promise<{
    type: string;
    score: number;
    ignore: boolean;
    process: { type: string; score: number }[];
}> => {
    let response;
    let process: { type: string; score: number }[] = [];
    const { hostname } = new URL(url);

    const LinkCheck = await checkLinkInDB(hostname, guildId);

    if (!LinkCheck.allowed && LinkCheck.score > 0) {
        return {
            type: 'end',
            score: LinkCheck.score,
            ignore: false,
            process: [{ type: 'badLink', score: LinkCheck.score }],
        };
    }

    const proxies = await getProxy();

    const proxy = rand(proxies);
    let attemptsWithProxy = 0;

    // random number between 5 and 15
    const maxAttemptsWithProxy = Math.trunc(Math.random() * 10) + 5;

    while (attemptsWithProxy < maxAttemptsWithProxy) {
        try {
            response = await axios.get(url, {
                headers: {
                    'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                },
                proxy: {
                    host: proxy.ip,
                    port: proxy.port,
                },
            });

            if (response.request._redirectable._redirectCount > 0) {
                threatScore +=
                    4 * response.request._redirectable._redirectCount;
                process.push({
                    type: `redirect ${hostname}`,
                    score: 4 * response.request._redirectable._redirectCount,
                });
            }

            attemptsWithProxy = 100;
        } catch {
            console.log('Url issue: ' + url);
            attemptsWithProxy++;

            return {
                type: 'error',
                score: threatScore,
                ignore: true,
                process,
            };
        }
    }

    if (response == undefined) {
        // Could be sus unsure, might change
        return {
            type: 'error',
            score: threatScore,
            ignore: true,
            process,
        };
    }

    const { headers, data } = response; // get the website's headers

    const badServer = badServers.find((o) => o.name == headers['server']); // Check if the server is a bad server i.e typically used for phishing

    if (badServer !== undefined) {
        threatScore += badServer.score; // add the threat score
        process.push({
            type: `bad server ${hostname}`,
            score: badServer.score,
        });
    }

    const parsedHtml = cheerio.load(data, { xmlMode: false });

    const htmlCheckResult = await checkHtml(
        parsedHtml,
        threatScore,
        round,
        process,
        urlShortening,
        guildId
    );

    threatScore += htmlCheckResult.threatScore;
    process = process.concat(htmlCheckResult.process);

    if (!urlShortening && urlShorteners.includes(hostname)) {
        return {
            type: 'Shortened URL',
            score: threatScore,
            ignore: false,
            process,
        }; // Use some sort of code system/object to tell the user shortened links are not allowed, also tie this into checking for redirection
    }

    console.log('hostname', hostname);

    if (goodHostnames.includes(hostname)) {
        return {
            type: 'good hostname',
            score: 0,
            ignore: true,
            process,
        };
    }

    const re = /\.([^.]+?)$/;

    const domain = re.exec(hostname);

    let tld: string | undefined;

    if (domain) {
        tld = domain.at(1);
    }

    if (!tld || !domain) {
        return {
            type: 'invalid TLD',
            ignore: true,
            score: threatScore,
            process,
        };
    }

    for (const element of badTlds) {
        if (tld == element.name) {
            threatScore += element.score;
            process.push({
                type: `bad tld ${hostname}`,
                score: element.score,
            });
        }
    }

    // TODO: Index the site and not do whois again

    const whois = await lookup(domain.input);

    const whoisResult = await analyseWhois(whois, threatScore, process);

    process = process.concat(whoisResult.process);
    threatScore += whoisResult.threatScore;

    console.log('threat score: ' + threatScore + ' for domain: ' + url);

    // TODO: Work out average score of a normal site + all spam sites

    let trust = true;

    if (threatScore > 100) {
        trust = false;
    }

    addLink(hostname, undefined, threatScore, process, undefined, trust);

    return {
        type: 'end',
        ignore: trust,
        score: threatScore,
        process,
    };
};

//checkLink('http://discoerd.gift/Zg82N4Zemc');
//checkLink('https://tinyurl.com/2p8dmmey');

// TODO: If the file ends in .png .ico or .css then ignore
