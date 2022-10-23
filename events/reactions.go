package events

import (
	"github.com/bwmarrin/discordgo"
	"ploxy/commands"
	"ploxy/utils"
)

func addVotes(reaction *discordgo.MessageReactionAdd, goodVote bool, okayVote bool, badVote bool) {
	var suggestions []commands.Suggestion
	err := utils.ReadJsonFile("suggestions.json", &suggestions)
	if err != nil {
		return
	}

	// get the suggestion
	var suggestion commands.Suggestion
	for _, s := range suggestions {
		if s.MessageId == reaction.MessageID {
			suggestion = s
			break
		}
	}

	// add the votes
	if goodVote {
		suggestion.GoodVotes++
	} else if okayVote {
		suggestion.OkayVotes++
	} else if badVote {
		suggestion.BadVotes++
	}

	// Add to Voters
	suggestion.Voters = append(suggestion.Voters, reaction.UserID)

	// update the file
	for i, s := range suggestions {
		if s.MessageId == reaction.MessageID {
			suggestions[i] = suggestion
			break
		}
	}

	err = utils.WriteToJsonFile("suggestions.json", suggestions)
	if err != nil {
		return
	}

}

func removeVotes(reaction *discordgo.MessageReactionRemove, goodVote bool, okayVote bool, badVote bool) {
	var suggestions []commands.Suggestion
	err := utils.ReadJsonFile("suggestions.json", &suggestions)
	if err != nil {
		return
	}

	// get the suggestion
	var suggestion commands.Suggestion
	for _, s := range suggestions {
		if s.MessageId == reaction.MessageID {
			suggestion = s
			break
		}
	}

	// remove the votes
	if goodVote {
		suggestion.GoodVotes--
	} else if okayVote {
		suggestion.OkayVotes--
	} else if badVote {
		suggestion.BadVotes--
	}

	// Remove from Voters
	for i, v := range suggestion.Voters {
		if v == reaction.UserID {
			suggestion.Voters = append(suggestion.Voters[:i], suggestion.Voters[i+1:]...)
			break
		}
	}

	// update the file
	for i, s := range suggestions {
		if s.MessageId == reaction.MessageID {
			suggestions[i] = suggestion
			break
		}
	}

	err = utils.WriteToJsonFile("suggestions.json", suggestions)
	if err != nil {
		return
	}

}

// ReactionAdd is called when a reaction is added to a message.
func ReactionAdd(client *discordgo.Session, reaction *discordgo.MessageReactionAdd) {
	// If the reaction was added by a bot, ignore it.
	if reaction.Member.User.Bot {
		return
	}

	// If the reaction was added to a message in the #suggestions channel, and the reaction was a checkmark, then
	// accept the suggestion.
	if reaction.ChannelID == utils.Config.SuggestionChannelId && reaction.Emoji.Name == "✅" {
		addVotes(reaction, true, false, false)
	} else if reaction.ChannelID == utils.Config.SuggestionChannelId && reaction.Emoji.Name == "🟧" {
		addVotes(reaction, false, true, false)
	} else if reaction.ChannelID == utils.Config.SuggestionChannelId && reaction.Emoji.Name == "❌" {
		addVotes(reaction, false, false, true)
	} else {
		// Remove the reaction if it was not a checkmark.
		err := client.MessageReactionRemove(reaction.ChannelID, reaction.MessageID, reaction.Emoji.APIName(), reaction.UserID)
		if err != nil {
			return
		}
	}
}

// ReactionRemove is called when a reaction is removed from a message.
func ReactionRemove(client *discordgo.Session, reaction *discordgo.MessageReactionRemove) {
	// Get the user
	user, err := client.User(reaction.UserID)
	if err != nil {
		return
	}

	// If the reaction was removed by a bot, ignore it.
	if user.Bot {
		return
	}

	// If the reaction was added to a message in the #suggestions channel, and the reaction was a checkmark, then
	// accept the suggestion.
	if reaction.ChannelID == utils.Config.SuggestionChannelId && reaction.Emoji.Name == "✅" {
		removeVotes(reaction, true, false, false)
	} else if reaction.ChannelID == utils.Config.SuggestionChannelId && reaction.Emoji.Name == "🟧" {
		removeVotes(reaction, false, true, false)
	} else if reaction.ChannelID == utils.Config.SuggestionChannelId && reaction.Emoji.Name == "❌" {
		removeVotes(reaction, false, false, true)
	}

}
