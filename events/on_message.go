package events

import (
	"github.com/bwmarrin/discordgo"
)

func OnMessage(client *discordgo.Session, message *discordgo.MessageCreate) {
	if message.Author.ID == client.State.User.ID {
		return
	}

}
