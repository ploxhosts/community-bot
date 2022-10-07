package commands

import (
	"github.com/bwmarrin/discordgo"
)

var Commands []*discordgo.ApplicationCommand
var CommandHandlers = map[string]func(client *discordgo.Session, interaction *discordgo.InteractionCreate){}

func RegisterCommands(client *discordgo.Session, TestGuildId string) {
	Commands = []*discordgo.ApplicationCommand{
		{
			Name:        "ping",
			Description: "Ping the bot",
		},
		{
			Name:        "book",
			Description: "Search the knowledge base",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "query",
					Description: "The query to search for",
					Required:    true,
				},
			},
		},
	}

	CommandHandlers["ping"] = PingCommand
	CommandHandlers["book"] = Book

	client.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		if h, ok := CommandHandlers[i.ApplicationCommandData().Name]; ok {
			h(s, i)
		}
	})

	println("Adding commands...")

	registeredCommands := make([]*discordgo.ApplicationCommand, len(Commands))
	for i, command := range Commands {
		if TestGuildId == "" {
			registeredCommand, err := client.ApplicationCommandCreate(client.State.User.ID, "", command)
			if err != nil {
				println("Error adding command:", err)
			}
			registeredCommands[i] = registeredCommand
		} else {
			registeredCommand, err := client.ApplicationCommandCreate(client.State.User.ID, TestGuildId, command)
			if err != nil {
				println("Error adding command:", err)
			}
			registeredCommands[i] = registeredCommand
		}
	}

}
