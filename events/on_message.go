package events

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"ploxy/timings"
)

func OnMessage(client *discordgo.Session, message *discordgo.MessageCreate) {
	if message.Author.ID == client.State.User.ID {
		return
	}

	analysis, err := timings.TimingsAnalysis(message.Content)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(analysis)
}
