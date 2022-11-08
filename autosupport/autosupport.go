package autosupport

import (
	"errors"
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/rylans/getlang"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"
)

func ProcessDiscordMessage(message *discordgo.MessageCreate, session *discordgo.Session) {

	if message.Author.ID == session.State.User.ID {
		return
	}

	if message.Author.Bot {
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

	response := autoRespond(allText, imageText)
	if response != "" {
		_, err := session.ChannelMessageSend(message.ChannelID, response)
		if err != nil {
			fmt.Println(err)
			return
		}

		return
	}

	/*
		config := utils.Config

		for _, channel := range config.ForbiddenChannels {
			if message.ChannelID == channel {
				return
			}
			// Check if channel parent is forbidden
			channelInfo, err := session.Channel(message.ChannelID)
			if err != nil {
				fmt.Println(err)
				return
			}
			if channelInfo.ParentID == channel {
				return
			}
		}

		// check if user has forbidden role
		for _, role := range message.Member.Roles {
			for _, forbiddenRole := range config.ForbiddenRoles {
				if role == forbiddenRole {
					return
				}
			}
		}

		rCtx := utils.RedisCtx
		rdb := utils.RedisClient

		userGotSupport, err := rdb.Get(rCtx, message.Author.ID+":lastSupportMessage").Result()
		if err == redis.Nil {
			userGotSupport = "0"
		} else if err != nil {
			fmt.Println(err)
		}

		lstAsked, err := strconv.ParseInt(userGotSupport, 10, 64)
		if err != nil {
			fmt.Println(err)
			lstAsked = 0
		}

		lastAsked := time.Unix(lstAsked, 0)

		if time.Since(lastAsked) < 5*time.Minute {
			return
		}

		if time.Since(lastAsked) < 30*time.Minute {
			return
		}

		IssueSelectionEmbed(message, session)
		err = rdb.Set(rCtx, message.Author.ID+":lastSupportMessage", time.Now().Unix(), 30*time.Minute).Err()
		if err != nil {
			fmt.Println(err)
			return
		}
	*/

}

func autoRespond(allText string, imageText string) string {
	var discordBotHosting = map[string]string{
		"run `npm audit fix` to fix them, or `npm audit` for details": "If you want to remove the error run `npm audit fix` to fix them, or `npm audit` for details` please download your code, run `npm audit fix` **on your own pc** and then upload the code again.",
		"create a ticket":                  "You can create a ticket at: https://support.plox.host/en/tickets/create/step1",
		"open a ticket":                    "You can create a ticket at: https://support.plox.host/en/tickets/create/step1",
		"ip has been banned":               "You have been banned by the looks of it. This usually happens when you input the wrong email/password multiple times. You can try to login from https://billing.plox.host and login with your billing account details(the ones you used to purchase the service/server). You can create a ticket there or access the support panel from there.\n**Hope this helps you!** ",
		"could not open requirements file": "Oh no, sorry to hear that you are having issues with your discord bot hosting.\nThis is quite easy to fix with a `requirements.txt` file. Make sure your file is in the main folder/directory.\n\nYou will need to insert the module/thing you normally install with pip. For example discord.py you could use a `requirements.txt` file with the content of\n```\ndiscord.py\ndnspython\nmotor\n```\nDo note some modules are installed into python by default such as `random` and `os` so if it says `No matching distribution found for...` then likely this is preinstalled into python.\n**Hope this helps you!** ",
		"jar file missing":                 "Please follow the guide at https://support.plox.host/en/knowledgebase/article/how-to-use-a-custom-jar to fix the issue",
	}

	for key, value := range discordBotHosting {
		if strings.Contains(allText, key) {
			return value
		} else if strings.Contains(imageText, key) {
			return value
		}
	}

	return ""
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
