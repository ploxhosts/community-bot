package events

import "github.com/bwmarrin/discordgo"

func RegisterEvents(client *discordgo.Session) {
	client.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		OnReady(s)
	})
	client.AddHandler(func(s *discordgo.Session, m *discordgo.MessageCreate) {
		OnMessage(s, m)
	})
	client.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		OnInteraction(s, i)
	})
	client.AddHandler(func(s *discordgo.Session, r *discordgo.MessageReactionAdd) {
		ReactionAdd(s, r)
	})
	client.AddHandler(func(s *discordgo.Session, r *discordgo.MessageReactionRemove) {
		ReactionRemove(s, r)
	})

}
