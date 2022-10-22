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
		{
			Name:        "suggest",
			Description: "Suggest a new feature",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "suggestion",
					Description: "The suggestion to make",
					Required:    true,
				},
			},
		},
		{
			Name:        "suggestions",
			Description: "Manage suggestions",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "accept",
					Description: "Accept a suggestion",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "id",
							Description: "The ID of the suggestion",
							Required:    true,
						},
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "reason",
							Description: "The reason for accepting the suggestion",
							Required:    false,
						},
					},
				},
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "deny",
					Description: "Deny a suggestion",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "id",
							Description: "The ID of the suggestion",
							Required:    true,
						},
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "reason",
							Description: "The reason for denying the suggestion",
							Required:    false,
						},
					},
				},
			},
		},
	}

	CommandHandlers["ping"] = PingCommand
	CommandHandlers["book"] = Book
	CommandHandlers["suggest"] = SuggestCommand

	client.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		if i.Type != discordgo.InteractionApplicationCommand {
			return
		}

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
