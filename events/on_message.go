package events

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"ploxy/autosupport"
	"ploxy/timings"
)

func OnMessage(client *discordgo.Session, message *discordgo.MessageCreate) {
	if message.Author.ID == client.State.User.ID {
		return
	}

	analysis, err := timings.TimingsAnalysis(message.Content)
	if err != nil {
		fmt.Println(err)

		embed := &discordgo.MessageEmbed{
			Title:       "Timings Analysis",
			Description: "❌️ I could not read the timings file. Please make sure you have uploaded the timings file correctly. This is likely a fault with Ploxy, please report this to the developer.",
			Color:       0xFF0000, // Red
			Fields:      []*discordgo.MessageEmbedField{},
		}

		_, err := client.ChannelMessageSendEmbedReply(message.ChannelID, embed, message.Reference())

		if err != nil {
			fmt.Println(err)
			return
		}

		return
	}

	if analysis != nil {
		// get the first 20 results
		if len(analysis) > 20 {
			analysis = analysis[:20]
		}
		// create a string of the results

		embed := &discordgo.MessageEmbed{
			Title:       "Timings Analysis",
			Description: "Here's what I found:",
			Color:       0x00ff00, // Green
			Fields:      []*discordgo.MessageEmbedField{},
		}

		for _, result := range analysis {
			embed.Fields = append(embed.Fields, &discordgo.MessageEmbedField{
				Name:   result.Name,
				Value:  result.Value,
				Inline: result.Inline,
			})
		}

		_, err = client.ChannelMessageSendEmbed(message.ChannelID, embed)
		if err != nil {
			fmt.Println(err)
			return
		}

	}

	autosupport.ProcessDiscordMessage(message, client)
}
