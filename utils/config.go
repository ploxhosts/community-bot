package utils

import (
	"encoding/json"
	"fmt"
	"os"
)

type ConfigType struct {
	BotToken          string   `json:"DISCORD_BOT_TOKEN"`
	TestGuildId       string   `json:"DISCORD_GUILD_ID"`
	ForbiddenChannels []string `json:"FORBIDDEN_CHANNELS"`
	ForbiddenRoles    []string `json:"FORBIDDEN_ROLES"`
}

var Config ConfigType

func LoadConfig() (*error, *ConfigType) {

	// Get from config.json
	configFile, err := os.Open("config.json")
	defer func(configFile *os.File) {
		err := configFile.Close()
		if err != nil {
			fmt.Println(err)
		}
	}(configFile)
	if err != nil {
		fmt.Println(err.Error() + " - Please create a config.json file or repair it.")
		return &err, nil
	}
	jsonParser := json.NewDecoder(configFile)
	err = jsonParser.Decode(&Config)
	if err != nil {
		return &err, nil
	}

	fmt.Println("Loaded config.json")
	return nil, &Config
}
