package autosupport

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
)

func IssueSelectionEmbed(message *discordgo.MessageCreate, session *discordgo.Session) {
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

func AskWhatServiceTheyHave() (*discordgo.MessageEmbed, *[]discordgo.MessageComponent, *error) {
	embed := &discordgo.MessageEmbed{
		Title:       "Automated Assistance",
		Description: "Please select the plan/product you are having issues with.",
		Color:       0x00ff00,
	}

	components := &[]discordgo.MessageComponent{
		discordgo.ActionsRow{
			Components: []discordgo.MessageComponent{

				discordgo.SelectMenu{
					Placeholder: "Select a service/product/plan",
					Options: []discordgo.SelectMenuOption{
						{
							Label:       "VPS",
							Description: "Virtual Private Server or KVM vps issues",
							Value:       "vps-service_selection",
						},
						{
							Label:       "Dedicated Server",
							Description: "Dedicated server issues",
							Value:       "dedicated-service_selection",
						},
						{
							Label:       "Shared/Web Hosting",
							Description: "Shared or web hosting issues",
							Value:       "shared-service_selection",
						},
						{
							Label:       "Minecraft Hosting",
							Description: "Minecraft hosting issues",
							Value:       "minecraft-service_selection",
						},
						{
							Label:       "Discord Bot Hosting",
							Description: "Discord bot hosting issues",
							Value:       "discordbot-service_selection",
						},
					},
				},
			},
		},
	}

	return embed, components, nil
}

func ProblemSelected(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	customId := interaction.MessageComponentData().CustomID
	fmt.Println("Button clicked:", customId)

	if customId == "server_issues-problem_selection" {
		embed, components, err := AskWhatServiceTheyHave()
		if err != nil {
			fmt.Println(err)
			return
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds:     []*discordgo.MessageEmbed{embed},
				Components: *components,
				Flags:      discordgo.MessageFlagsEphemeral,
			},
		})
		if BotErr != nil {
			return
		}
	}

}

func ServiceSelected(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	customId := interaction.MessageComponentData().CustomID
	fmt.Println("Button clicked:", customId)

	if customId == "vps-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with VPS hosting.\nDue to the nature of VPS hosting, we are unable to provide automated assistance for this product.\nIf you need help installing packages please use google to your advantage.\nIf you are downtime issues, create a ticket.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
				Flags:  discordgo.MessageFlagsEphemeral,
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if customId == "dedicated-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Dedicated Server hosting.\nDue to the nature of Dedicated Server hosting, we are unable to provide automated assistance for this product.\nIf you need help installing packages please use google to your advantage.\nIf you are downtime issues, create a ticket.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
				Flags:  discordgo.MessageFlagsEphemeral,
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if customId == "shared-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Shared/Web Hosting.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
				Flags:  discordgo.MessageFlagsEphemeral,
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if customId == "minecraft-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Minecraft Hosting. This will be updated in the future with more information to better assist you.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
				Flags:  discordgo.MessageFlagsEphemeral,
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if customId == "discordbot-service_selection" {

		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Discord Bot Hosting. This will be updated in the future with more information to better assist you.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
				Flags:  discordgo.MessageFlagsEphemeral,
			},
		})

		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	}
}
