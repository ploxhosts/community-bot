package events

import "github.com/bwmarrin/discordgo"

func OnInteraction(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	if interaction.Interaction.Type == discordgo.InteractionMessageComponent {
		println("Message component interaction")
	}
}
