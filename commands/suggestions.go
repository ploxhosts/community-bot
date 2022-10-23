package commands

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"ploxy/utils"
	"strconv"
)

func SuggestionsCommand(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	// get the subcommand
	subcommand := interaction.ApplicationCommandData().Options[0].Name

	// get the suggestion ID
	suggestionId := interaction.ApplicationCommandData().Options[0].Options[0].StringValue()

	// get the reason
	reason := interaction.ApplicationCommandData().Options[0].Options[1].StringValue()

	var suggestions []Suggestion
	fileErr := utils.ReadJsonFile("suggestions.json", &suggestions)
	if fileErr != nil {
		fmt.Println("Error reading suggestions file: ", fileErr)
		handleError(client, interaction)
		return
	}

	// get the suggestion
	var suggestion Suggestion
	for _, s := range suggestions {
		if s.Id == suggestionId {
			suggestion = s
			break
		}
	}

	// get the suggestion message
	message, err := client.ChannelMessage(utils.Config.SuggestionChannelId, suggestion.MessageId)
	if err != nil {
		fmt.Println("Error getting suggestion message: ", err)
		handleError(client, interaction)
		return
	}

	// get the suggestion embed
	embed := message.Embeds[0]

	var choice = ""
	switch subcommand {
	case "accept":
		choice = "Accepted"
		embed.Color = 0x00ff00
		break
	case "deny":
		choice = "Denied"
		embed.Color = 0xff0000
	}
	if reason != "" {
		embed.Fields[0].Value = suggestion.Suggestion + "\n\n**" + choice + " By " + interaction.Member.User.Mention() + "**\n" + reason + "\n\nVotes:\n✅ " + strconv.FormatInt(int64(suggestion.GoodVotes), 10) + " | 🟧 " + strconv.FormatInt(int64(suggestion.OkayVotes), 10) + " | ❌ " + strconv.FormatInt(int64(suggestion.BadVotes), 10)
	} else {
		embed.Fields[0].Value = suggestion.Suggestion + "\n\n**" + choice + " By " + interaction.Member.User.Mention() + "**\n\nVotes:\n✅ " + strconv.FormatInt(int64(suggestion.GoodVotes), 10) + " | 🟧 " + strconv.FormatInt(int64(suggestion.OkayVotes), 10) + " | ❌ " + strconv.FormatInt(int64(suggestion.BadVotes), 10)
	}
	// send suggestion in other channel
	_, err = client.ChannelMessageSendEmbed(utils.Config.ApprovalChannelId, embed)
	if err != nil {
		fmt.Println("Error sending suggestion in approval channel: ", err)
		handleError(client, interaction)
		return
	}

	// edit the suggestion message
	_, err = client.ChannelMessageEditEmbed(utils.Config.SuggestionChannelId, suggestion.MessageId, embed)
	if err != nil {
		fmt.Println("Error editing suggestion message: ", err)
		handleError(client, interaction)
		return
	}

	// remove the suggestion from the suggestions file
	for i, s := range suggestions {
		if s.Id == suggestionId {
			suggestions = append(suggestions[:i], suggestions[i+1:]...)
			break
		}
	}

	// write the suggestions file
	err = utils.WriteToJsonFile("suggestions.json", suggestions)
	if err != nil {
		fmt.Println("Error writing suggestions file: ", err)
		handleError(client, interaction)
		return
	}

	// send the response
	err = client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Suggestion " + choice + "!",
		},
	})
	if err != nil {
		return
	}
}
