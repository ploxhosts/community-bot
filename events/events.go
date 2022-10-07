package events

import "github.com/bwmarrin/discordgo"

func RegisterEvents(client *discordgo.Session) {
	client.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		OnReady(s)
	})
	client.AddHandler(func(s *discordgo.Session, m *discordgo.MessageCreate) {
		OnMessage(s, m)
	})

}
