package autosupport

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
)

// IssueSelectionEmbed *-problem_selection buttons
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

// AskWhatServiceTheyHave service_selection_select menu and *-service_selection options
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
					CustomID: "service_selection_select",
				},
			},
		},
	}

	return embed, components, nil
}

// ProblemSelected service_selection that provides service_selection_select menu and *-service_selection options
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
				CustomID:   "service_selection",
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if customId == "billing_issues-problem_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "- If you have recently bought a vps/kvm, you will have to create a ticket at https://support.plox.host/en/tickets/create/step1 to have it manually approved.\n- If you bought something using crypto and haven't recieved your product, please create a ticket at https://support.plox.host/en/tickets/create/step1 and wait for a reply.\n- **If you have been charged twice**, please create a ticket at https://support.plox.host/en/tickets/create/step1 and wait for a reply. This is because you refreshed the page during purchase.\n- If you want to request a refund, please create a ticket at https://support.plox.host/en/tickets/create/step1 and wait for a reply.\n- If you have any other billing/payment issues, please create a ticket at https://support.plox.host/en/tickets/create/step1 and wait for a reply, **we cannot help you over discord.**",
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if customId == "other-problem_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "Please create a ticket at https://support.plox.host/en/tickets/create/step1 and wait for a reply. It may take up to 24 hours for a reply.",
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	}

}

func ServiceSelected(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	customId := interaction.MessageComponentData().CustomID
	fmt.Println("Button clicked:", customId)
	fmt.Println(interaction.MessageComponentData().Values)
	valueClicked := interaction.MessageComponentData().Values[0]

	if valueClicked == "vps-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with VPS hosting.\nDue to the nature of VPS hosting, we are unable to provide automated assistance for this product.\nIf you need help installing packages please use google to your advantage.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds:     []*discordgo.MessageEmbed{embed},
				Components: []discordgo.MessageComponent{},
				CustomID:   "VpsSelectedAndResponded",
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if valueClicked == "dedicated-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Dedicated Server hosting.\nDue to the nature of Dedicated Server hosting, we are unable to provide automated assistance for this product.\nIf you need help installing packages please use google to your advantage.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds:   []*discordgo.MessageEmbed{embed},
				Flags:    discordgo.MessageFlagsEphemeral,
				CustomID: "DedicatedSelectedAndResponded",
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if valueClicked == "shared-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Shared/Web Hosting.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds:     []*discordgo.MessageEmbed{embed},
				Components: []discordgo.MessageComponent{},
				CustomID:   "SharedSelectedAndResponded",
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if valueClicked == "minecraft-service_selection" {
		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Minecraft Hosting. This will be updated in the future with more information to better assist you.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds:     []*discordgo.MessageEmbed{embed},
				Components: []discordgo.MessageComponent{},
				CustomID:   "MinecraftSelectedAndResponded",
			},
		})
		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	} else if valueClicked == "discordbot-service_selection" {

		embed := &discordgo.MessageEmbed{
			Title:       "Automated Assistance",
			Description: "You have selected you are having issues with Discord Bot Hosting. This will be updated in the future with more information to better assist you.\nIf you want to know if what you are doing is allowed, visit https://plox.host/terms-of-service\nFor anything else not listed here or if you are having trouble with instructions please [open a ticket with our support team](https://support.plox.host/en/tickets/create/step1) and they will be happy to assist you.",
			Color:       0x00ff00,
		}

		BotErr := client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseUpdateMessage,
			Data: &discordgo.InteractionResponseData{
				Embeds:     []*discordgo.MessageEmbed{embed},
				Components: []discordgo.MessageComponent{},
				CustomID:   "DiscordBotSelectedAndResponded",
			},
		})

		if BotErr != nil {
			fmt.Println(BotErr)
			return
		}
	}
}
