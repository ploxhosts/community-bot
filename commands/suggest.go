package commands

import (
	"github.com/bwmarrin/discordgo"
	"ploxy/utils"
	"strconv"
	"time"
)

func SuggestCommand(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	// Get options
	options := interaction.ApplicationCommandData().Options
	suggestion := options[0].StringValue()

	embed := &discordgo.MessageEmbed{
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:  "Suggestion:",
				Value: "\n" + suggestion,
			},
		},
		Footer: &discordgo.MessageEmbedFooter{
			Text: "ID: " + strconv.FormatInt(time.Now().UnixNano()/(1<<22), 10) + " | Ploxy suggestions",
		},
		Author: &discordgo.MessageEmbedAuthor{
			Name:    interaction.Member.User.Username,
			IconURL: interaction.Member.User.AvatarURL(""),
		},
	}

	channel, err := client.Channel(utils.Config.SuggestionChannelId)

	if err != nil {
		embed := &discordgo.MessageEmbed{
			Color:       0x36a39f,
			Description: "This server does not have suggestions setup.\nThis can be done with the `p!suggestions setup` command",
			Footer: &discordgo.MessageEmbedFooter{
				Text: "Ploxy | Suggestions",
			},
		}

		err = client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
			},
		})
		if err != nil {
			return
		}
		return
	}

	message, err := client.ChannelMessageSendEmbed(channel.ID, embed)
	if err != nil {
		return
	}

	err = client.MessageReactionAdd(message.ChannelID, message.ID, "✅")
	if err != nil {
		return
	}

	err = client.MessageReactionAdd(message.ChannelID, message.ID, "🟧")
	if err != nil {
		return
	}

	err = client.MessageReactionAdd(message.ChannelID, message.ID, "❌")
	if err != nil {
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
