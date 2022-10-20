package events

import (
	"github.com/bwmarrin/discordgo"
	"ploxy/autosupport"
	"strings"
)

func OnInteraction(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	if interaction.Interaction.Type == discordgo.InteractionMessageComponent {
		handleButtonClick(client, interaction)
	}
}

func handleButtonClick(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	customId := interaction.MessageComponentData().CustomID

	if strings.Split(customId, "-")[1] == "problem_selection" {
		autosupport.ProblemSelected(client, interaction)
	}
}
