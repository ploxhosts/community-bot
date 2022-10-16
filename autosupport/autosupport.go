package autosupport

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/rylans/getlang"
	"time"
)

// create array and the time the bot lasted responded to them
// if the time is over 5 minutes, remove them from the array

var lastMessaged = make(map[string]struct {
	toldToCreateTicket time.Time
	lastSupportMessage time.Time
})

func ProcessDiscordMessage(message *discordgo.MessageCreate, session *discordgo.Session) {
	lastMessaged[message.Author.ID] = struct {
		toldToCreateTicket time.Time
		lastSupportMessage time.Time
	}{
		toldToCreateTicket: time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
		lastSupportMessage: time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
	}

	if processText(message.Content) != "en" {
		// if the user has not been told to create a ticket in the last 5 minutes
		if time.Since(lastMessaged[message.Author.ID].toldToCreateTicket) < 5*time.Minute {
			return
		}
		_, err := session.ChannelMessageSendReply(message.ChannelID, "Hi, I have detected your message is not english. Please create a ticket at https://support.plox.host/en/tickets/create/step1 for the best chances of a response.", message.Reference())
		if err != nil {
			fmt.Println(err)
			return
		}

		lastMessaged[message.Author.ID] = struct {
			toldToCreateTicket time.Time
			lastSupportMessage time.Time
		}{
			toldToCreateTicket: time.Now(),
			lastSupportMessage: lastMessaged[message.Author.ID].lastSupportMessage,
		}
	}

	// if the user has not been told to create a ticket in the last 5 minutes
	if time.Since(lastMessaged[message.Author.ID].lastSupportMessage) > 5*time.Minute {
		lastMessaged[message.Author.ID] = struct {
			toldToCreateTicket time.Time
			lastSupportMessage time.Time
		}{
			toldToCreateTicket: lastMessaged[message.Author.ID].toldToCreateTicket,
			lastSupportMessage: time.Now(),
		}
	}

	if time.Since(lastMessaged[message.Author.ID].toldToCreateTicket) > 5*time.Minute {
		lastMessaged[message.Author.ID] = struct {
			toldToCreateTicket time.Time
			lastSupportMessage time.Time
		}{
			toldToCreateTicket: time.Now(),
			lastSupportMessage: lastMessaged[message.Author.ID].lastSupportMessage,
		}
	}

}

func processText(text string) string {

	info := getlang.FromString(text)
	return info.LanguageCode()
}
