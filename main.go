package main

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"os"
	"os/signal"
	"ploxy/commands"
	"ploxy/events"
	"ploxy/utils"
	"syscall"
)

var Client *discordgo.Session

func main() {
	config, err := utils.LoadConfig()
	if err != nil {
		return
	}

	Client, err = discordgo.New("Bot " + config.BotToken)
	if err != nil {
		fmt.Println("error starting Discord bot,", err)
		return
	}

	Client.Identify.Intents = discordgo.IntentsGuilds |
		discordgo.IntentsGuildMessages |
		discordgo.IntentsGuildMessageReactions |
		discordgo.IntentsMessageContent

	events.RegisterEvents(Client)

	err = Client.Open()
	if err != nil {
		fmt.Println("error opening connection to Discord,", err)
		return
	}
	commands.RegisterCommands(Client, config.TestGuildId)

	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT, os.Interrupt, os.Kill)
	<-sc

	fmt.Println("Bot is now shutting down.")
	err = Client.Close()
	if err != nil {
		fmt.Println("error closing connection to Discord,", err)
		return
	}

}
