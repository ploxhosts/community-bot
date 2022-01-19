import tlds from '../data/tlds';
import { badWordCheck } from './badWordCheck';
import { getLinks, checkLink } from './linkCheck';
export const spamCheck = async (text: string, author_message_count: number, riskScore: number = 0, is_allowed: boolean = false) => {

  if ((text.toLowerCase().includes('@everyone') || text.toLowerCase().includes('@here')) && !is_allowed) {
    riskScore += 5;
  }

  const links = await getLinks(text)

  for (const link of links) {
    let result = await checkLink(link);
    if (typeof result === 'number') {
      riskScore += result;
      console.log("Add risk score by link", link, riskScore)
    }
  }

  if (author_message_count <= 3){
    riskScore += 5;
    console.log("Add risk score by author_message_count 1", "author_message_count: " + author_message_count , riskScore)
  } else if (author_message_count <= 10){
    riskScore += 4;
    console.log("Add risk score by author_message_count 2", "author_message_count: " + author_message_count, riskScore)
  } else if (author_message_count <= 30){
    riskScore += 3;
    console.log("Add risk score by author_message_count 3", "author_message_count: " + author_message_count, riskScore)
  } else if (author_message_count <= 40){
    riskScore += 2;
    console.log("Add risk score by author_message_count 4", "author_message_count: " + author_message_count, riskScore)
  }

  let badwordsScore = await badWordCheck(text, true) // Check for bad words even if disabled to check if it's spam - does not moderate bad words
  riskScore += badwordsScore;
  console.log("Add risk score by badWordCheck", badwordsScore, riskScore)
  
  const mediumRiskWords = ["join", "now", "quick", "running out", "offer", "nitro", "$", "gain", "profit", "free"]
  const highRiskWords = ["!!", "gift", "nitro", "steam", "before the action"]
  for (const mediumWord of mediumRiskWords) {
    if (text.toLowerCase().includes(mediumWord)) {
      console.log("Add risk by mediumRiskWords", mediumWord, riskScore)
      riskScore += 2
    }
  }

  for (const highWord of highRiskWords){
    if (text.toLowerCase().includes(highWord)){
      console.log("Aadd risk by highRiskWords", highWord, riskScore)
      riskScore += 3
    }
  }

  return riskScore;
}
