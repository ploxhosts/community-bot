package commands

import (
	"github.com/bwmarrin/discordgo"
	"ploxy/utils"
	"strconv"
	"time"
)

type Suggestion struct {
	Author     string   `json:"author"`
	AuthorId   string   `json:"author_id"`
	Suggestion string   `json:"suggestion"`
	MessageId  string   `json:"message_id"`
	GoodVotes  int      `json:"good_votes"`
	BadVotes   int      `json:"bad_votes"`
	OkayVotes  int      `json:"okay_votes"`
	Status     string   `json:"status"`
	Id         string   `json:"id"`
	Voters     []string `json:"voters"`
}

func handleError(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	embed := &discordgo.MessageEmbed{
		Color:       0x36a39f,
		Description: "There was an error sending your suggestion. Please try again later.",
		Footer: &discordgo.MessageEmbedFooter{
			Text: "Ploxy | Suggestions",
		},
	}

	err := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Embeds: []*discordgo.MessageEmbed{embed},
		},
	})
	if err != nil {
		return
	}
}
func SuggestCommand(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	// Get options
	options := interaction.ApplicationCommandData().Options
	suggestion := options[0].StringValue()

	id := strconv.FormatInt(time.Now().UnixNano()/(1<<22), 10)
	embed := &discordgo.MessageEmbed{
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:  "Suggestion:",
				Value: "\n" + suggestion,
			},
		},
		Footer: &discordgo.MessageEmbedFooter{
			Text: "ID: " + id + " | Ploxy suggestions",
		},
		Author: &discordgo.MessageEmbedAuthor{
			Name:    interaction.Member.User.Username,
			IconURL: interaction.Member.User.AvatarURL(""),
		},
	}

	channel, err := client.Channel(utils.Config.SuggestionChannelId)

	if err != nil {
		handleError(client, interaction)
		return
	}

	message, err := client.ChannelMessageSendEmbed(channel.ID, embed)
	if err != nil {
		handleError(client, interaction)
		return
	}

	err = client.MessageReactionAdd(message.ChannelID, message.ID, "✅")
	if err != nil {
		handleError(client, interaction)
		return
	}

	err = client.MessageReactionAdd(message.ChannelID, message.ID, "🟧")
	if err != nil {
		handleError(client, interaction)
		return
	}

	err = client.MessageReactionAdd(message.ChannelID, message.ID, "❌")
	if err != nil {
		handleError(client, interaction)
		return
	}

	var suggestions []Suggestion
	fileErr := utils.ReadJsonFile("suggestions.json", &suggestions)
	if fileErr != nil {
		handleError(client, interaction)
		return
	}

	suggestions = append(suggestions, Suggestion{
		Author:     interaction.Member.User.Username,
		AuthorId:   interaction.Member.User.ID,
		Suggestion: suggestion,
		MessageId:  message.ID,
		GoodVotes:  0,
		BadVotes:   0,
		OkayVotes:  0,
		Status:     "pending",
		Id:         id,
		Voters:     []string{},
	})

	fileErr = utils.WriteToJsonFile("suggestions.json", suggestions)
	if fileErr != nil {
		handleError(client, interaction)
		return
	}

	err = client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Your suggestion has been sent!",
		},
	})
	if err != nil {
		return
	}

}
