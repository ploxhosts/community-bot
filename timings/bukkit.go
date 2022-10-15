package timings

import "strconv"

func getBukkitAdvice(data Timings, advice []EmbedField, plugins []string) []EmbedField {

	PeriodInTicks, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.ChunkGc.PeriodInTicks)
	if err != nil {
		PeriodInTicks = 0
	}
	if PeriodInTicks >= 600 {
		advice = append(advice, EmbedField{
			Name:   "❌️ chunk-gc.period-in-ticks",
			Value:  "Decrease this in `config/bukkit.yml`\nRecommended: 400.",
			Inline: true,
		})
	}

	MonsterSpawns, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.TicksPer.MonsterSpawns)

	if err != nil {
		MonsterSpawns = 0
	}

	if MonsterSpawns == 1 {
		advice = append(advice, EmbedField{
			Name:   "❌️ ticks-per.monster-spawns",
			Value:  "Increase this in `config/bukkit.yml`\nRecommended: 4.",
			Inline: true,
		})
	}

	Monsters, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.SpawnLimits.Monsters)

	if err != nil {
		Monsters = 0
	}

	if Monsters >= 70 {
		advice = append(advice, EmbedField{
			Name:   "❌️ spawn-limits.monsters",
			Value:  "Decrease this in `config/bukkit.yml`\nRecommended: 15.",
			Inline: true,
		})
	}

	Animals, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.SpawnLimits.Animals)

	if err != nil {
		Animals = 0
	}

	if Animals >= 10 {
		advice = append(advice, EmbedField{
			Name:   "❌️ spawn-limits.animals",
			Value:  "Decrease this in `config/bukkit.yml`\nRecommended: 5.",
			Inline: true,
		})
	}

	WaterAnimals, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.SpawnLimits.WaterAnimals)

	if err != nil {
		WaterAnimals = 0
	}

	if WaterAnimals >= 15 {
		advice = append(advice, EmbedField{
			Name:   "❌️ spawn-limits.water-animals",
			Value:  "Decrease this in `config/bukkit.yml`\nRecommended: 5.",
			Inline: true,
		})
	}

	WaterAmbient, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.SpawnLimits.WaterAmbient)

	if err != nil {
		WaterAmbient = 0
	}

	if WaterAmbient >= 15 {
		advice = append(advice, EmbedField{
			Name:   "❌️ spawn-limits.water-ambient",
			Value:  "Decrease this in `config/bukkit.yml`\nRecommended: 5.",
			Inline: true,
		})
	}

	Ambient, err := strconv.Atoi(data.TimingsMaster.Config.Bukkit.SpawnLimits.Ambient)

	if err != nil {
		Ambient = 0
	}

	if Ambient >= 15 {
		advice = append(advice, EmbedField{
			Name:   "❌️ spawn-limits.ambient",
			Value:  "Decrease this in `config/bukkit.yml`\nRecommended: 1.",
			Inline: true,
		})
	}

	return advice
}
