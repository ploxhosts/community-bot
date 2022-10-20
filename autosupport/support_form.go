package autosupport

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
)

func issueSelectionEmbed(message *discordgo.MessageCreate, session *discordgo.Session) {
	embed := &discordgo.MessageEmbed{
		Title:       "Automated Assistance",
		Description: "Please select an issue from the buttons below for me to better assist you.",
		Color:       0x00ff00,
	}

	_, err := session.ChannelMessageSendComplex(message.ChannelID, &discordgo.MessageSend{
		Embed:     embed,
		Reference: message.Reference(),
		Components: []discordgo.MessageComponent{

			discordgo.ActionsRow{
				Components: []discordgo.MessageComponent{
					discordgo.Button{
						Emoji: discordgo.ComponentEmoji{
							Name: "🖥️",
						},
						Label:    "Server Issues",
						Style:    discordgo.PrimaryButton,
						CustomID: "server_issues-problem_selection",
					},
					discordgo.Button{
						Emoji: discordgo.ComponentEmoji{
							Name: "📦",
						},
						Label:    "Billing/Payment Issues",
						Style:    discordgo.PrimaryButton,
						CustomID: "billing_issues-problem_selection",
					},
					discordgo.Button{
						Emoji: discordgo.ComponentEmoji{
							Name: "📧",
						},
						Label:    "Email Issues",
						Style:    discordgo.PrimaryButton,
						CustomID: "email_issues-problem_selection",
					},
					discordgo.Button{
						Emoji: discordgo.ComponentEmoji{
							Name: "🔒",
						},
						Label:    "Account Issues",
						Style:    discordgo.PrimaryButton,
						CustomID: "account_issues-problem_selection",
					},
					discordgo.Button{
						Emoji: discordgo.ComponentEmoji{
							Name: "📝",
						},
						Label:    "Other",
						Style:    discordgo.PrimaryButton,
						CustomID: "other-problem_selection",
					},
				},
			},
		},
	})

	if err != nil {
		fmt.Println(err)
		return
	}
}
