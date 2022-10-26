package events

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"ploxy/autosupport"
	"ploxy/utils"
	"strings"
)

func OnInteraction(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	if interaction.Interaction.Type == discordgo.InteractionMessageComponent { // If it contains a message component
		handleClick(client, interaction)
	}
}

func handleClick(client *discordgo.Session, interaction *discordgo.InteractionCreate) {

	rCtx := utils.RedisCtx
	rdb := utils.RedisClient

	// Get the message
	author := rdb.Get(rCtx, "message:"+interaction.Interaction.Message.ID).Val()
	if author == "" {
		return
	} else if author != interaction.Member.User.ID {
		return
	}

	customId := interaction.MessageComponentData().CustomID
	fmt.Println("Handler:", customId)

	if strings.Contains(customId, "-") {
		if strings.Split(customId, "-")[1] == "problem_selection" {
			autosupport.ProblemSelected(client, interaction)
		}
	}

	if customId == "service_selection_select" {
		autosupport.ServiceSelected(client, interaction)
	}
}
