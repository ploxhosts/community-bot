package main

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
	"os"
	"os/signal"
	"ploxy/events"
	"syscall"
)

var Client *discordgo.Session

// Bot variables
var (
	BotToken    string
	BotId       string
	TestGuildId string
	Commands    []*discordgo.ApplicationCommand
)

func loadEnv() *error {
	error := godotenv.Load()
	if error != nil {
		fmt.Println("Error loading .env file")
		return &error
	}

	BotToken = os.Getenv("DISCORD_BOT_TOKEN")
	BotId = os.Getenv("DISCORD_BOT_ID")
	TestGuildId = os.Getenv("DISCORD_TEST_GUILD_ID")

	fmt.Println("Loaded environment variables")
	return nil
}

func main() {
	if loadEnv() != nil {
		return
	}

	Client, err := discordgo.New("Bot " + BotToken)
	if err != nil {
		fmt.Println("error starting Discord bot,", err)
		return
	}

	Client.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		events.OnReadyEvent(s)
	})

	err = Client.Open()
	if err != nil {
		fmt.Println("error opening connection to Discord,", err)
		return
	}

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
