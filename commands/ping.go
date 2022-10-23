package commands

import "github.com/bwmarrin/discordgo"

func PingCommand(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	err := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Pong!",
		},
	})
	if err != nil {
		return
	}
}
