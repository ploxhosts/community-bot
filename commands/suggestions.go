package commands

import "github.com/bwmarrin/discordgo"

func SuggestionsCommand(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	// get the subcommand
	subcommand := interaction.ApplicationCommandData().Options[0].Name

	// get the suggestion ID
	suggestionId := interaction.ApplicationCommandData().Options[0].Options[0].StringValue()

	// get the reason
	reason := interaction.ApplicationCommandData().Options[0].Options[1].StringValue()
	
}
