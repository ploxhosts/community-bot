package timings

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

var myClient = &http.Client{Timeout: 20 * time.Second}

func getJson(url string, target interface{}) error {
	r, err := myClient.Get(url)
	if err != nil {
		return err
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(r.Body)

	return json.NewDecoder(r.Body).Decode(target)
}

type VersionResponse struct {
	isOutdated      bool
	versionOutdated int
	groupOutdated   int
	fixOutdated     int
	buildOutdated   int
	RecommendedRam  int
}

func checkVersion(version string, isPaper bool) (VersionResponse, error) {

	// Get the latest version from paper
	var versions PaperVersions
	err := getJson("https://api.papermc.io/v2/projects/paper/", &versions)
	if err != nil {
		return VersionResponse{}, err
	}

	lastVersionGroup := versions.VersionGroups[len(versions.VersionGroups)-1]
	lastVersion := versions.Versions[len(versions.Versions)-1]

	// Typical version string being: git-Paper-141 (MC: 1.19.2)
	var serverGroupVersion string
	var serverVersionNumber string
	var serverBuildNumber string
	var serverSubVersion int

	// Get the version group
	if strings.Contains(version, "-") {
		serverBuildNumber = strings.Split(version, "-")[2]
		serverBuildNumber = strings.Split(serverBuildNumber, " ")[0]
	} else {
		serverBuildNumber = "000000"
	}

	// Get the version number
	if strings.Contains(version, "-") {
		serverVersionNumber = strings.Split(version, "MC: ")[1]
		serverVersionNumber = strings.Split(serverVersionNumber, ")")[0]
	} else {
		serverVersionNumber = version
	}

	// Get the version group
	if strings.Contains(version, "-") {
		serverGroupVersion = strings.Split(version, "MC: ")[1]
		serverGroupVersion = strings.Split(serverGroupVersion, ")")[0]
		if strings.Count(serverGroupVersion, ".") == 1 {
			serverGroupVersion = serverGroupVersion + ".0"
		} else {
			serverSubVersion, err = strconv.Atoi(strings.Split(serverGroupVersion, ".")[2]) // Get the sub version number
		}
		serverGroupVersion = strings.Split(serverGroupVersion, ".")[0] + "." + strings.Split(serverGroupVersion, ".")[1]
	} else {
		serverGroupVersion = strings.Split(version, ".")[0] + "." + strings.Split(version, ".")[1]
		if strings.Count(serverGroupVersion, ".") == 1 {
			serverGroupVersion = serverGroupVersion + ".0"
		} else {
			serverSubVersion, err = strconv.Atoi(strings.Split(version, ".")[2]) // Get the sub version number
		}
	}
	if err != nil {
		serverSubVersion = -1
	}

	var isLatestVersion = false
	var isLatestGroup = false
	var isLatestBuild = false
	var isLatestFix = false

	// Check if the server is on the latest version
	if serverVersionNumber == lastVersion {
		isLatestVersion = true
	}

	// Check if the server is on the latest version group
	if serverGroupVersion == lastVersionGroup {
		isLatestGroup = true
	}

	// Get the latest version from the server
	var buildVersions PaperVersionBuilds
	err = getJson("https://api.papermc.io/v2/projects/paper/versions/"+serverVersionNumber, &buildVersions)

	// Check if the server is on the latest build
	if serverBuildNumber == strconv.Itoa(buildVersions.Builds[len(buildVersions.Builds)-1]) {
		isLatestBuild = true
	}

	// Calculate the latest sub version for the server's version group

	var latestSubVersion int
	// Get all versions in the group version
	var versionsInGroup []string
	for _, v := range versions.Versions {
		if strings.Split(v, ".")[0] == strings.Split(serverGroupVersion, ".")[0] && strings.Split(v, ".")[1] == strings.Split(serverGroupVersion, ".")[1] {
			versionsInGroup = append(versionsInGroup, v)
		}
	}
	var latestVersionInGroup = versionsInGroup[len(versionsInGroup)-1]
	latestSubVersion, err = strconv.Atoi(strings.Split(latestVersionInGroup, ".")[2]) // Get the sub version number
	if err != nil {
		latestSubVersion = -1
	}

	var response = VersionResponse{
		isOutdated:      false,
		versionOutdated: 0,
		groupOutdated:   0,
		fixOutdated:     0,
		buildOutdated:   0,
	}

	// Check how many versions behind the server is

	// Check if behind on version and how many
	if !isLatestVersion {
		response.versionOutdated = latestSubVersion - serverSubVersion
	}

	// Check if behind version group and how many
	if !isLatestGroup {
		for i := 0; i < len(versions.VersionGroups); i++ {
			if versions.VersionGroups[i] == serverGroupVersion {
				response.groupOutdated = len(versions.VersionGroups) - i
			}
		}
	}
	// Check if behind build and how many
	if !isLatestBuild {
		for i := 0; i < len(buildVersions.Builds); i++ {
			if buildVersions.Builds[i] == buildVersions.Builds[len(buildVersions.Builds)-1] {
				response.buildOutdated = len(buildVersions.Builds) - i
			}
		}
	}
	// Check if subversion is behind and how many
	if serverSubVersion != latestSubVersion {
		response.fixOutdated = latestSubVersion - serverSubVersion
	} else {
		isLatestFix = true
	}

	// Check if the server is outdated

	if !isLatestGroup || !isLatestBuild || !isLatestFix || !isLatestVersion {
		response.isOutdated = true
	}

	switch serverGroupVersion {
	case "1.21":
		response.RecommendedRam = 9
	case "1.20":
		response.RecommendedRam = 9
	case "1.19":
		response.RecommendedRam = 7
	case "1.18":
		response.RecommendedRam = 6
	case "1.17":
		response.RecommendedRam = 5
	case "1.16":
		response.RecommendedRam = 5
	default:
		response.RecommendedRam = 4
	}

	return response, nil
}

func calculateRam(ramRaw string) int {
	var ramInt int
	var ram string

	ram = strings.ReplaceAll(ramRaw, "G", "000")
	ram = strings.ReplaceAll(ram, "g", "000")
	ram = strings.ReplaceAll(ram, "M", "")
	ram = strings.ReplaceAll(ram, "m", "")
	ramInt, err := strconv.Atoi(ram)
	if err != nil {
		ramInt = 256
		ram = "256"
	}
	return ramInt
}

func arrayContains(s []string, str string) bool {
	for _, v := range s {
		if v == str {
			return true
		}
	}

	return false
}

func CheckIfPluginInUse(plugin string, plugins []string) bool {
	for _, v := range plugins {
		if strings.Contains(v, plugin) {
			return true
		}
	}
	return false
}

func TimingsAnalysis(url string) ([]EmbedField, error) {
	if url == "" {
		return nil, nil
	}
	var timingsUrl = ""
	var concerns = make([]EmbedField, 0)

	if !strings.Contains(url, "timin") {
		return nil, nil
	}

	if strings.Contains(url, "/d=") {
		timingsUrl = strings.Replace(url, "/d=", "/?id=", 1)
	} else if strings.Contains(url, "/?id=") {
		timingsUrl = url
	} else if strings.Contains(timingsUrl, "https://www.spigotmc.org/go/timings?url=") || strings.Contains(timingsUrl, "https://timings.spigotmc.org/?url=") {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Spigot",
			Value:  "Spigot has limited information within timings reports. Switch to Paper or Purpur for better performance and timings, all your plugins will work the same.",
			Inline: false,
		})
	} else if strings.Contains(timingsUrl, "https://spark.lucko.me") {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Spark",
			Value:  "Spark is not a timings report, it is a profiler. It is not useful for performance analysis. Use /profile instead.",
			Inline: false,
		})
	} else {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Timings Processing Error",
			Value:  "I'm having trouble processing the timings report. Please try again later or create a new report.",
			Inline: false,
		})
		return concerns, nil
	}

	println("Timings URL: " + timingsUrl)

	if len(concerns) > 0 {
		return concerns, nil
	}

	var timingsHost = strings.Split(timingsUrl, "?id=")[0]
	var timingsId = strings.Split(timingsUrl, "?id=")[1]

	var timingsJson = timingsHost + "data.php?id=" + timingsId

	println("Timings JSON: " + timingsJson)
	var timingsRaw = timingsUrl + "&raw=1"

	var rawTimings, err = http.Get(timingsRaw)
	if err != nil || rawTimings.StatusCode != 200 {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Timings Error",
			Value:  "Timings report is not available. Please try again later or create a new report.",
			Inline: false,
		})
		return concerns, nil
	}

	var timingsData Timings

	err = getJson(timingsJson, &timingsData)
	if err != nil {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Timings Processing Error",
			Value:  "I'm having trouble processing the timings report. Please try again later or create a new report.",
			Inline: false,
		})
		return concerns, err
	}

	versionData, err := checkVersion(timingsData.TimingsMaster.Version, strings.Contains(timingsData.TimingsMaster.Version, "Paper"))
	if err != nil {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Version Processing Error",
			Value:  "I'm having trouble processing the server version. Please try again later or create a new report.",
			Inline: false,
		})
		return concerns, err
	}

	if versionData.isOutdated {
		println("Server is outdated")
		if versionData.fixOutdated > 0 {
			concerns = append(concerns, EmbedField{
				Name:   "⚠️ Outdated Fix Version",
				Value:  "Your server is " + strconv.Itoa(versionData.fixOutdated) + " fix versions behind the latest version. It's recommended to [update](https://purpurmc.org/downloads) to protect against bugs and security issues.",
				Inline: true,
			})
		} else if versionData.groupOutdated > 0 {
			concerns = append(concerns, EmbedField{
				Name:   "❌️ Outdated Version",
				Value:  "Your server is " + strconv.Itoa(versionData.groupOutdated) + " versions behind the latest version. Please [update](https://purpurmc.org/downloads) to get the latest features and bug fixes.",
				Inline: true,
			})
		} else if versionData.buildOutdated > 0 {
			concerns = append(concerns, EmbedField{
				Name:   "⚠️ Outdated Build",
				Value:  "Your server is " + strconv.Itoa(versionData.buildOutdated) + " builds behind the latest version. It's recommended to [update](https://purpurmc.org/downloads) to protect against bugs and security issues.",
				Inline: true,
			})
		}
	}

	if strings.Contains(timingsData.TimingsMaster.Motd, "A Minecraft Server") {
		concerns = append(concerns, EmbedField{
			Name:   "⚠️ Default MOTD",
			Value:  "Your server is using the default MOTD. It's recommended to change it to something unique.",
			Inline: true,
		})
	}

	if timingsData.TimingsMaster.System.Timingcost > 320 {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ High Timing Cost",
			Value:  "Your server's timing cost is " + strconv.Itoa(timingsData.TimingsMaster.System.Timingcost) + ". Your cpu is overloaded and/or slow. Try an [extreme plan](https://plox.host/minecraft?type=extreme).",
			Inline: true,
		})
	} else if timingsData.TimingsMaster.System.Timingcost > 300 {
		concerns = append(concerns, EmbedField{
			Name:   "⚠️ High Timing Cost",
			Value:  "Your server's timing cost is " + strconv.Itoa(timingsData.TimingsMaster.System.Timingcost) + ". Your cpu is overloaded and/or slow. Try an [extreme plan](https://plox.host/minecraft?type=extreme) or get rid of intensive plugins.",
			Inline: true,
		})
	}
	// Check -Xmx value
	var maxMemory = 256
	var minMemory = 0

	if strings.Contains(timingsData.TimingsMaster.System.Flags, "-Xmx") {
		maxMemory = calculateRam(strings.Split(strings.Split(timingsData.TimingsMaster.System.Flags, "-Xmx")[1], " ")[0])
	}

	if strings.Contains(timingsData.TimingsMaster.System.Flags, "-Xms") {
		minMemory = calculateRam(strings.Split(strings.Split(timingsData.TimingsMaster.System.Flags, "-Xms")[1], " ")[0])
	}

	if maxMemory/1000 < versionData.RecommendedRam {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Low Ram",
			Value:  "Your server is using " + strconv.Itoa(maxMemory/1000) + "GB of ram. It's recommended to use at least " + strconv.Itoa(versionData.RecommendedRam) + "GB of ram.",
			Inline: true,
		})
	}

	if strings.Contains(timingsData.TimingsMaster.System.Flags, "-XX:+UseZGC") && strings.Contains(timingsData.TimingsMaster.System.Flags, "-Xmx") {
		if maxMemory < 12000 {
			concerns = append(concerns, EmbedField{
				Name:   "❌️ Low RAM/Memory",
				Value:  "ZGC is better suited for servers with 12GB or more of RAM. You should consider [upgrading](https://support.plox.host/en/knowledgebase/article/how-to-upgrade-or-downgrade-a-service) to get the most out of ZGC.",
				Inline: true,
			})
		}
	} else if strings.Contains(timingsData.TimingsMaster.System.Flags, "-Daikars.new.flags=true") {
		var outdatedFlags = map[string]string{
			"-XX:+PerfDisableSharedMem":  "Add `-XX:+PerfDisableSharedMem` to flags.",
			"-XX:G1MixedGCCountTarget=4": "Add `Add `XX:G1MixedGCCountTarget=4` to flags.",
			"-XX:+UseG1GC":               "Add `-XX:+UseG1GC` to flags.",
		}
		for flag, fix := range outdatedFlags {
			if !strings.Contains(timingsData.TimingsMaster.System.Flags, flag) {
				concerns = append(concerns, EmbedField{
					Name:   "❌️ Outdated Flags",
					Value:  "Your server is using outdated flags. " + fix,
					Inline: true,
				})
			}
		}
		if maxMemory < 5400 {
			concerns = append(concerns, EmbedField{
				Name:   "❌️ Low RAM/Memory",
				Value:  "It's recommended to use at least 6-12GB of ram.",
				Inline: true,
			})
		}
		if timingsData.TimingsMaster.Maxplayers*1000/maxMemory > 6 && maxMemory < 10000 {
			concerns = append(concerns, EmbedField{
				Name:   "❌️ Low RAM/Memory",
				Value:  "Too many players for your ram. It's recommended to use at least 10GB of ram to support that player count, try reducing it in server.properties.",
				Inline: true,
			})
		}
		if minMemory != 0 && minMemory != maxMemory {
			concerns = append(concerns, EmbedField{
				Name:   "❌️ Aikar's Flags",
				Value:  "Your Xmx and Xms values should be equal when using Aikar's flags.",
				Inline: true,
			})
		}

	} else if strings.Contains(timingsData.TimingsMaster.System.Flags, "-Dusing.aikars.flags=mcflags.emc.gs") {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Outdated Flags",
			Value:  "Update [Aikar's flags](https://support.plox.host/en/knowledgebase/article/enabling-aikars-flagsjvm-modifications)",
			Inline: true,
		})
	} else {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Aikar's Flags",
			Value:  "Use [Aikar\\'s flags](https://support.plox.host/en/knowledgebase/article/enabling-aikars-flagsjvm-modifications). ",
			Inline: true,
		})
	}

	if timingsData.TimingsMaster.System.Cpu <= 2 {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Threads",
			Value:  "You only have" + strconv.Itoa(timingsData.TimingsMaster.System.Cpu) + " threads.",
			Inline: true,
		})
	}
	if strings.Contains(timingsData.TimingsMaster.Version, "yatopia") {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Yatopia",
			Value:  "Yatopia is no longer supported. Please use [Paper](https://papermc.io/downloads) or [Purpur](https://purpur.pl3x.net/downloads). ",
			Inline: true,
		})
	} else if strings.Contains(timingsData.TimingsMaster.Version, "tuinity") {
		concerns = append(concerns, EmbedField{
			Name:   "❌️ Tuinity",
			Value:  "Tuinity is no longer supported. Please use [Paper](https://papermc.io/downloads) or [Purpur](https://purpur.pl3x.net/downloads). ",
			Inline: true,
		})
	}

	// Load plugins.json
	pluginsData, err := os.ReadFile("plugins.json")
	if err != nil {
		log.Fatal(err)
	}

	// Unmarshal plugins.json
	var plugins PluginsJson
	err = json.Unmarshal(pluginsData, &plugins)
	if err != nil {
		log.Fatal(err)
	}

	var pluginsInUse []string
	for _, plugin := range timingsData.TimingsMaster.Plugins {
		pluginsInUse = append(pluginsInUse, plugin.Name)
	}

	// Check for plugins
	for _, plugin := range plugins.Paper {
		if CheckIfPluginInUse(plugin.Name, pluginsInUse) {
			concerns = append(concerns, EmbedField{
				Name:   "❌️ " + plugin.Name,
				Value:  plugin.Reason,
				Inline: true,
			})
		}
	}

	// check if purpur is used
	if strings.Contains(timingsData.TimingsMaster.Version, "purpur") {
		for _, plugin := range plugins.Purpur {
			if arrayContains(pluginsInUse, plugin.Name) {
				concerns = append(concerns, EmbedField{
					Name:   "❌️ " + plugin.Name,
					Value:  plugin.Reason,
					Inline: true,
				})
			}
		}
	}

	concerns = getPaperAdvice(timingsData, concerns, pluginsInUse)

	concerns = getBukkitAdvice(timingsData, concerns, pluginsInUse)

	concerns = getSpigotAdvice(timingsData, concerns, pluginsInUse)

	return concerns, nil
}
