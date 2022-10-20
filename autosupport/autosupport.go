package autosupport

import (
	"errors"
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/robfig/cron/v3"
	"github.com/rylans/getlang"
	"io"
	"net/http"
	"os"
	"os/exec"
	"ploxy/utils"
	"strings"
	"time"
)

// create array and the time the bot lasted responded to them
// if the time is over 5 minutes, remove them from the array

type lastMessagedStruct struct {
	toldToCreateTicket    time.Time
	lastSupportMessage    time.Time
	askedForService       time.Time
	previousMessages      []string
	previousImageContents []string
}

var lastMessaged = make(map[string]lastMessagedStruct)

func handleOutdatedCache(author string) {
	// Prevent memory leak
	if time.Since(lastMessaged[author].lastSupportMessage) > 5*time.Minute && time.Since(lastMessaged[author].toldToCreateTicket) > 5*time.Minute {
		delete(lastMessaged, author)
		return
	}

	if time.Since(lastMessaged[author].lastSupportMessage) > 5*time.Minute {
		lastMessaged[author] = lastMessagedStruct{
			toldToCreateTicket:    lastMessaged[author].toldToCreateTicket,
			lastSupportMessage:    time.Now(),
			askedForService:       lastMessaged[author].askedForService,
			previousMessages:      lastMessaged[author].previousMessages,
			previousImageContents: lastMessaged[author].previousImageContents,
		}
	}

	if time.Since(lastMessaged[author].toldToCreateTicket) > 5*time.Minute {
		lastMessaged[author] = lastMessagedStruct{
			toldToCreateTicket:    time.Now(),
			lastSupportMessage:    lastMessaged[author].lastSupportMessage,
			askedForService:       lastMessaged[author].askedForService,
			previousMessages:      lastMessaged[author].previousMessages,
			previousImageContents: lastMessaged[author].previousImageContents,
		}
	}
}

func toldToCreateTicket(author string) {
	lastMessaged[author] = lastMessagedStruct{
		toldToCreateTicket:    time.Now(),
		lastSupportMessage:    lastMessaged[author].lastSupportMessage,
		askedForService:       lastMessaged[author].askedForService,
		previousMessages:      lastMessaged[author].previousMessages,
		previousImageContents: lastMessaged[author].previousImageContents,
	}
}

func removeOldEntries() {
	for key, _ := range lastMessaged {
		handleOutdatedCache(key)
	}
}

func ProcessDiscordMessage(message *discordgo.MessageCreate, session *discordgo.Session) {
	config := utils.Config

	for _, channel := range config.ForbiddenChannels {
		if message.ChannelID == channel {
			return
		}
	}

	if message.Author.ID == session.State.User.ID {
		return
	}

	if message.Author.Bot {
		return
	}

	// check if user has forbidden role
	for _, role := range message.Member.Roles {
		for _, forbiddenRole := range config.ForbiddenRoles {
			if role == forbiddenRole {
				return
			}
		}
	}

	// Check if author is in lastMessaged cache if not create cache object
	if _, ok := lastMessaged[message.Author.ID]; !ok {
		lastMessaged[message.Author.ID] = lastMessagedStruct{
			toldToCreateTicket:    time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
			lastSupportMessage:    time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
			askedForService:       time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
			previousMessages:      []string{},
			previousImageContents: []string{},
		}
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

		toldToCreateTicket(message.Author.ID)
		return
	}

	textContents := make([]string, 0)
	if len(message.Attachments) > 0 {
		for _, attachment := range message.Attachments {
			if attachment.Width > 0 {
				// Save the image to a file

				text := processImage(attachment.URL, message.ID)

				textContents = append(textContents, text)
			}
		}
	}

	var allText string
	var imageText string

	for _, text := range textContents {
		allText += text
		imageText += text
	}

	if message.Content != "" {
		textContents = append(textContents, message.Content)
		allText += message.Content
	}

	for _, text := range textContents {

		if processText(text) != "en" {

			_, err := session.ChannelMessageSendReply(message.ChannelID, "Hi, I have detected your message is not english. Please create a ticket at https://support.plox.host/en/tickets/create/step1 for the best chances of a response.", message.Reference())
			if err != nil {
				fmt.Println(err)
				return
			}
			toldToCreateTicket(message.Author.ID)
			return
		}
	}

	if len(textContents) == 0 {
		lastMessaged[message.Author.ID] = lastMessagedStruct{
			toldToCreateTicket:    lastMessaged[message.Author.ID].toldToCreateTicket,
			lastSupportMessage:    lastMessaged[message.Author.ID].lastSupportMessage,
			askedForService:       time.Now(),
			previousMessages:      lastMessaged[message.Author.ID].previousMessages,
			previousImageContents: append(lastMessaged[message.Author.ID].previousImageContents, imageText),
		}
		return
	} else {
		lastMessaged[message.Author.ID] = lastMessagedStruct{
			toldToCreateTicket:    lastMessaged[message.Author.ID].toldToCreateTicket,
			lastSupportMessage:    lastMessaged[message.Author.ID].lastSupportMessage,
			askedForService:       time.Now(),
			previousMessages:      append(lastMessaged[message.Author.ID].previousMessages, allText),
			previousImageContents: append(lastMessaged[message.Author.ID].previousImageContents, imageText),
		}
	}

	var discordBotHosting map[string]string = map[string]string{
		"run `npm audit fix` to fix them, or `npm audit` for details": "If you want to remove the error run `npm audit fix` to fix them, or `npm audit` for details` please download your code, run `npm audit fix` **on your own pc** and then upload the code again.",
	}

	for key, value := range discordBotHosting {
		if strings.Contains(allText, key) {
			_, err := session.ChannelMessageSendReply(message.ChannelID, value, message.Reference())
			if err != nil {
				fmt.Println(err)
				return
			}
			return
		}
	}
}

func processText(text string) string {
	info := getlang.FromString(text)
	if info.LanguageCode() == "und" {
		return "en"
	}
	return info.LanguageCode()
}

func processImage(linkToImage string, id string) string {
	err := downloadImage(linkToImage, id+".png")
	if err != nil {
		fmt.Println(err)
		return ""
	}

	text := getTextFromImage(id + ".png")

	err = os.Remove(id + ".png")

	if err != nil {
		fmt.Println(err)
		return ""
	}

	return text
}

func getTextFromImage(linkToImage string) string {

	cmd := exec.Command("tesseract", linkToImage, "stdout")
	out, err := cmd.Output()
	if err != nil {
		fmt.Println(err)
		return ""
	}

	return string(out)
}

func downloadImage(URL, fileName string) error {
	//Get the response bytes from the url
	response, err := http.Get(URL)
	if err != nil {
		return err
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			fmt.Println(err)
		}
	}(response.Body)

	if response.StatusCode != 200 {
		return errors.New("received non 200 response code")
	}
	//Create an empty file
	file, err := os.Create(fileName)
	if err != nil {
		return err
	}
	defer file.Close()

	//Write the bytes to the file
	_, err = io.Copy(file, response.Body)
	if err != nil {
		return err
	}

	return nil
}

// register cron job to remove old entries from lastMessaged
func init() {
	c := cron.New()
	_, err := c.AddFunc("0 5 * * 1", removeOldEntries)
	if err != nil {
		fmt.Println(err)
		return
	}
	c.Start()
}
