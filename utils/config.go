package utils

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/go-redis/redis/v9"
	"os"
)

type ConfigType struct {
	BotToken            string   `json:"DISCORD_BOT_TOKEN"`
	TestGuildId         string   `json:"DISCORD_GUILD_ID"`
	ForbiddenChannels   []string `json:"FORBIDDEN_CHANNELS"`
	ForbiddenRoles      []string `json:"FORBIDDEN_ROLES"`
	SuggestionChannelId string   `json:"SUGGESTION_CHANNEL_ID"`
	ApprovalChannelId   string   `json:"APPROVAL_CHANNEL_ID"`
	RedisHost           string   `json:"REDIS_HOST"`
	RedisPassword       string   `json:"REDIS_PASSWORD"`
	RedisDb             int      `json:"REDIS_DB"`
}

var Config ConfigType
var RedisCtx = context.Background()
var RedisClient *redis.Client

func LoadConfig() (*error, *ConfigType) {

	// Get from config.json
	configFile, err := os.Open("config.json")
	defer func(configFile *os.File) {
		err := configFile.Close()
		if err != nil {
			fmt.Println(err)
			fmt.Println("error closing config file")
		}
	}(configFile)
	if err != nil {
		fmt.Println(err.Error() + " - Please create a config.json file or repair it.")
		return &err, nil
	}
	jsonParser := json.NewDecoder(configFile)
	err = jsonParser.Decode(&Config)
	if err != nil {
		fmt.Println(err.Error() + " - Please create a config.json file or repair it.")
		return &err, nil
	}

	fmt.Println("Loaded config.json")

	RedisClient = redis.NewClient(&redis.Options{
		Addr:     Config.RedisHost,
		Password: Config.RedisPassword, // no password set
		DB:       Config.RedisDb,       // use default DB
	})

	return nil, &Config
}

func ReadJsonFile(path string, target interface{}) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer func(file *os.File) {
		err := file.Close()
		if err != nil {
			fmt.Println(err)
		}
	}(file)

	decoder := json.NewDecoder(file)
	err = decoder.Decode(target)
	if err != nil {
		return err
	}

	return nil
}

func WriteToJsonFile(path string, target interface{}) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	defer func(file *os.File) {
		err := file.Close()
		if err != nil {
			fmt.Println(err)
		}
	}(file)

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	err = encoder.Encode(target)
	if err != nil {
		return err
	}

	return nil
}
