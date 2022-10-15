package timings

import "strconv"

func getSpigotAdvice(data Timings, advice []EmbedField, plugins []string) []EmbedField {

	Animals, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.Animals)
	if err != nil {
		Animals = 0
	}

	if Animals >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.animals",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 16.",
			Inline: true,
		})
	}

	Monsters, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.Monsters)

	if err != nil {
		Monsters = 0
	}

	if Monsters >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.monsters",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 16.",
			Inline: true,
		})
	}

	Water, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.Water)

	if err != nil {
		Water = 0
	}

	if Water >= 16 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.water",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 8.",
			Inline: true,
		})
	}

	Misc, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.Misc)

	if err != nil {
		Misc = 0
	}

	if Misc >= 16 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.misc",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 8.",
			Inline: true,
		})
	}

	Villagers, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.Villagers)

	if err != nil {
		Villagers = 0
	}

	if Villagers >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.villagers",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 16.",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.TickInactiveVillagers == "true" {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.tick-inactive-villagers",
			Value:  "Set this to `false` in `config/spigot.yml`",
			Inline: true,
		})
	}

	FlyingMonstersMaxPerTick, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.FlyingMonstersMaxPerTick)

	if err != nil {
		FlyingMonstersMaxPerTick = 0
	}

	FlyingMonstersFor, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.FlyingMonstersFor)

	if err != nil {
		FlyingMonstersFor = 0
	}

	if FlyingMonstersMaxPerTick >= 1 && FlyingMonstersFor >= 100 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.flying-monsters-for",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 60.",
			Inline: true,
		})
	}

	if FlyingMonstersMaxPerTick >= 8 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.flying-monsters-max-per-tick",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 1.",
			Inline: true,
		})
	}
	VillagersFor, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.VillagersFor)

	if err != nil {
		VillagersFor = 0
	}

	VillagersMaxPerTick, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.VillagersMaxPerTick)

	if err != nil {
		VillagersMaxPerTick = 0
	}

	if VillagersMaxPerTick >= 1 && VillagersFor >= 100 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.villagers-for",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 60.",
			Inline: true,
		})
	}

	if VillagersMaxPerTick >= 4 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.villagers-max-per-tick",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 1.",
			Inline: true,
		})
	}

	MonstersFor, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.MonstersFor)

	if err != nil {
		MonstersFor = 0
	}

	MonstersMaxPerTick, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.MonstersMaxPerTick)

	if err != nil {
		MonstersMaxPerTick = 0
	}

	if MonstersMaxPerTick >= 1 && MonstersFor >= 100 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.monsters-for",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 60.",
			Inline: true,
		})
	}

	if MonstersMaxPerTick >= 8 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.monsters-max-per-tick",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 4.",
			Inline: true,
		})
	}

	AnimalsFor, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.AnimalsFor)

	if err != nil {
		AnimalsFor = 0
	}

	AnimalsMaxPerTick, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.EntityActivationRange.WakeUpInactive.AnimalsMaxPerTick)

	if err != nil {
		AnimalsMaxPerTick = 0
	}

	if AnimalsMaxPerTick >= 1 && AnimalsFor >= 100 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.animals-for",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 60.",
			Inline: true,
		})
	}

	if AnimalsMaxPerTick >= 4 {
		advice = append(advice, EmbedField{
			Name:   "❌️ entity-activation-range.wake-up-inactive.animals-max-per-tick",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 2.",
			Inline: true,
		})
	}

	ArrowDespawnRate, err := strconv.Atoi(data.TimingsMaster.Config.Spigot.WorldSettings.Default.ArrowDespawnRate)

	if err != nil {
		ArrowDespawnRate = 0
	}

	if ArrowDespawnRate >= 1200 {
		advice = append(advice, EmbedField{
			Name:   "❌️ arrow-despawn-rate",
			Value:  "Decrease this in `config/spigot.yml`\nRecommended: 300.",
			Inline: true,
		})
	}

	MergeRadiusItem, err := strconv.ParseFloat(data.TimingsMaster.Config.Spigot.WorldSettings.Default.MergeRadius.Item, 64)

	if err != nil {
		MergeRadiusItem = 0
	}

	if MergeRadiusItem <= 2.5 {
		advice = append(advice, EmbedField{
			Name:   "❌️ merge-radius.item",
			Value:  "Increase this in `config/spigot.yml`\nRecommended: 4.0.",
			Inline: true,
		})
	}

	MergeRadiusExp, err := strconv.ParseFloat(data.TimingsMaster.Config.Spigot.WorldSettings.Default.MergeRadius.Exp, 64)

	if err != nil {
		MergeRadiusExp = 0
	}

	if MergeRadiusExp <= 3.0 {
		advice = append(advice, EmbedField{
			Name:   "❌️ merge-radius.exp",
			Value:  "Increase this in `config/spigot.yml`\nRecommended: 6.0.",
			Inline: true,
		})
	}

	return advice
}
