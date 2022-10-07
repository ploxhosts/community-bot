package events

import "github.com/bwmarrin/discordgo"

func RegisterEvents(client *discordgo.Session) {
	client.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		OnReadyEvent(s)
	})
}
