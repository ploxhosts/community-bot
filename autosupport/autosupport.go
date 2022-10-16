package autosupport

import (
	"errors"
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/otiai10/gosseract/v2"
	"github.com/rylans/getlang"
	"io"
	"net/http"
	"os"
	"time"
)

// create array and the time the bot lasted responded to them
// if the time is over 5 minutes, remove them from the array

var lastMessaged = make(map[string]struct {
	toldToCreateTicket time.Time
	lastSupportMessage time.Time
})

func handleOutdatedCache(author string) {
	// Prevent memory leak
	if time.Since(lastMessaged[author].lastSupportMessage) > 5*time.Minute && time.Since(lastMessaged[author].toldToCreateTicket) > 5*time.Minute {
		delete(lastMessaged, author)
		return
	}

	if time.Since(lastMessaged[author].lastSupportMessage) > 5*time.Minute {
		lastMessaged[author] = struct {
			toldToCreateTicket time.Time
			lastSupportMessage time.Time
		}{
			toldToCreateTicket: lastMessaged[author].toldToCreateTicket,
			lastSupportMessage: time.Now(),
		}
	}

	if time.Since(lastMessaged[author].toldToCreateTicket) > 5*time.Minute {
		lastMessaged[author] = struct {
			toldToCreateTicket time.Time
			lastSupportMessage time.Time
		}{
			toldToCreateTicket: time.Now(),
			lastSupportMessage: lastMessaged[author].lastSupportMessage,
		}
	}
}
func givenSupportMessage() {

}

func toldToCreateTicket(author string) {
	lastMessaged[author] = struct {
		toldToCreateTicket time.Time
		lastSupportMessage time.Time
	}{
		toldToCreateTicket: time.Now(),
		lastSupportMessage: lastMessaged[author].lastSupportMessage,
	}
}

func ProcessDiscordMessage(message *discordgo.MessageCreate, session *discordgo.Session) {
	lastMessaged[message.Author.ID] = struct {
		toldToCreateTicket time.Time
		lastSupportMessage time.Time
	}{
		toldToCreateTicket: time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
		lastSupportMessage: time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC),
	}

	// if the user has not been told to create a ticket in the last 5 minutes
	handleOutdatedCache(message.Author.ID)

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

	if len(textContents) == 0 {
		textContents = append(textContents, message.Content)
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

}

func processText(text string) string {

	info := getlang.FromString(text)
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
	client := gosseract.NewClient()
	defer func(client *gosseract.Client) {
		err := client.Close()
		if err != nil {
			fmt.Println(err)
		}
	}(client)
	err := client.SetImage(linkToImage)
	if err != nil {
		fmt.Println(err)
		return ""
	}
	text, err := client.Text()

	if err != nil {
		fmt.Println(err)
		return ""
	}

	return text
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
