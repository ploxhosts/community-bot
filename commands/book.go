package commands

import (
	"github.com/PuerkitoBio/goquery"
	"github.com/bwmarrin/discordgo"
	"net/http"
	"net/http/cookiejar"
	"strconv"
	"strings"
)

func Book(client *discordgo.Session, interaction *discordgo.InteractionCreate) {
	var csrfToken string

	res, err := http.Get("https://support.plox.host/en")
	if err != nil {
		println("Error getting csrf token:", err)
		return
	}

	doc, err := goquery.NewDocumentFromReader(res.Body)

	if err != nil {
		println("Error parsing HTML:", err)
		return
	}
	doc.Find("meta").Each(func(i int, s *goquery.Selection) {
		if s.AttrOr("name", "") == "csrf_token" {
			csrfToken = s.AttrOr("content", "")
		}
	})

	// define cookies
	Jar, _ := cookiejar.New(nil)
	Jar.SetCookies(res.Request.URL, res.Cookies())
	httpClient := &http.Client{
		Jar: Jar,
	}

	res, err = httpClient.Post("https://support.plox.host/en/search", "application/json",
		strings.NewReader(`{"query":"`+interaction.ApplicationCommandData().Options[0].StringValue()+`", "_token":"`+csrfToken+`"}`))

	if err != nil {
		println("Error searching:", err)
		return
	}

	doc, err = goquery.NewDocumentFromReader(res.Body)

	if err != nil {
		println("Error searching by reading document:", err)
		return
	}

	var results []string

	// Get all the articles
	doc.Find(".sp-article-list").Each(func(i int, s *goquery.Selection) {
		s.Find("a").Each(func(i int, s *goquery.Selection) {
			// Get href string and append to results
			href, _ := s.Attr("href")
			if href != "" && strings.Contains(href, "article") {
				results = append(results, "[`"+strconv.Itoa(len(results)+1)+". "+strings.ReplaceAll(s.Find("h4").Text(), "\n", "")+"`]("+href+")\n")
			}
		})
	})

	responseEmbed := &discordgo.MessageEmbed{
		Title:       "Search Results",
		Description: "Found " + strconv.Itoa(len(results)) + " results`\n\n" + strings.Join(results, ""),
	}

	err = client.InteractionRespond(interaction.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Embeds: []*discordgo.MessageEmbed{responseEmbed},
		},
	})
	if err != nil {
		return
	}
}
