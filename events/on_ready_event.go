package events

import (
	"github.com/bwmarrin/discordgo"
	"log"
)

func OnReadyEvent(client *discordgo.Session) {
	log.Printf("Logged in as: %v#%v in %v servers", client.State.User.Username, client.State.User.Discriminator, len(client.State.Guilds))
}
