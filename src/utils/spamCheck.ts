import tlds from '../data/tlds';
import { badWordCheck } from './badWordCheck';
import { getLinks, checkLink } from './linkCheck';
export const spamCheck = async (text: string, author_message_count: number, riskScore: number = 0, is_allowed: boolean = false) => {

  if ((text.toLowerCase().includes('@everyone') || text.toLowerCase().includes('@here')) && !is_allowed) {
    riskScore += 5;
  }

  const links = await getLinks(text)
  if (links.keys.length > 0) {
    riskScore += 3
  }

  for (const link of links) {
    let result = await checkLink(link);
    if (typeof result === 'number') {
      riskScore += result;
    }
  }
  
  if (author_message_count <= 3){
    riskScore += 5;
  } else if (author_message_count <= 10){
    riskScore += 4;
  } else if (author_message_count <= 30){
    riskScore += 3;
  } else if (author_message_count <= 40){
    riskScore += 2;
  }

  for (const tld in tlds){
    if (text.toUpperCase().includes(tld)){
      riskScore += 2;
    }
  }

  for (const tld in tlds){
    if (text.toUpperCase().includes(tld)){
      riskScore += 2;
    }
  }

  riskScore += await badWordCheck(text, true) // Check for bad words even if disabled to check if it's spam - does not moderate bad words

  const mediumRiskWords = ["join", "now", "quick", "running out", "offer", "nitro", "$", "gain", "profit", "free"]
  const highRiskWords = ["!!", "gift", "nitro", "steam", "before the action"]
  for (const word of text.toLowerCase().split(" ")){
    if (mediumRiskWords.includes(word)){
      riskScore += 2
    } else if (highRiskWords.includes(word)){
      riskScore += 3
    }
  }

  return riskScore;
}
