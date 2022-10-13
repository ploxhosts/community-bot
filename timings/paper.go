package timings

import "strconv"

func getPaperAdvice(data Timings, advice []EmbedField) []EmbedField {

	maxAutoSaveChunksPerTick, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.MaxAutoSaveChunksPerTick)
	if err != nil {
		maxAutoSaveChunksPerTick = 0
	}
	if maxAutoSaveChunksPerTick >= 24 {
		advice = append(advice, EmbedField{
			Name:   "❌️ chunks.max-auto-save-chunks-per-tick",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 6.",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.OptimizeExplosions == "false" {
		advice = append(advice, EmbedField{
			Name:   "❌️ environment.optimize-explosions",
			Value:  "Set this to true in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.TickRates.MobSpawner == 1 {
		advice = append(advice, EmbedField{
			Name:   "❌️ tick-rates.mob-spawner",
			Value:  "Set this to 2 or higher in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.TickRates.GrassSpread == 1 {
		advice = append(advice, EmbedField{
			Name:   "❌️ tick-rates.grass-spread",
			Value:  "Set this to 2 or higher in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.TickRates.ContainerUpdate == 1 {
		advice = append(advice, EmbedField{
			Name:   "❌️ tick-rates.container-update",
			Value:  "Set this to 2 or higher in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.GameMechanics.DisableChestCatDetection == "false" {
		advice = append(advice, EmbedField{
			Name:   "❌️ game-mechanics.disable-chest-cat-detection",
			Value:  "Set this to true in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	DespawnRangesAmbientSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Ambient.Soft)
	if err != nil {
		DespawnRangesAmbientSoft = 0
	}
	if DespawnRangesAmbientSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.ambient.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesAmbientHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Ambient.Hard)
	if err != nil {
		DespawnRangesAmbientHard = 0
	}
	if DespawnRangesAmbientHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.ambient.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesMonsterSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Monster.Soft)
	if err != nil {
		DespawnRangesMonsterSoft = 0
	}
	if DespawnRangesMonsterSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.monster.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesMonsterHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Monster.Hard)
	if err != nil {
		DespawnRangesMonsterHard = 0
	}
	if DespawnRangesMonsterHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.monster.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesCreatureSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Creature.Soft)
	if err != nil {
		DespawnRangesCreatureSoft = 0
	}
	if DespawnRangesCreatureSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.creature.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesCreatureHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Creature.Hard)
	if err != nil {
		DespawnRangesCreatureHard = 0
	}
	if DespawnRangesCreatureHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.creature.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesWaterAmbientSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.WaterAmbient.Soft)
	if err != nil {
		DespawnRangesWaterAmbientSoft = 0
	}
	if DespawnRangesWaterAmbientSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.water-ambient.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesWaterAmbientHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.WaterAmbient.Hard)
	if err != nil {
		DespawnRangesWaterAmbientHard = 0
	}
	if DespawnRangesWaterAmbientHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.water-ambient.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesWaterCreatureSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.WaterCreature.Soft)
	if err != nil {
		DespawnRangesWaterCreatureSoft = 0
	}
	if DespawnRangesWaterCreatureSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.water-creature.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesWaterCreatureHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.WaterCreature.Hard)
	if err != nil {
		DespawnRangesWaterCreatureHard = 0
	}
	if DespawnRangesWaterCreatureHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.water-creature.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesUndergroundWaterCreatureSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.UndergroundWaterCreature.Soft)
	if err != nil {
		DespawnRangesUndergroundWaterCreatureSoft = 0
	}
	if DespawnRangesUndergroundWaterCreatureSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.underground-water-creature.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesUndergroundWaterCreatureHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.UndergroundWaterCreature.Hard)
	if err != nil {
		DespawnRangesUndergroundWaterCreatureHard = 0
	}
	if DespawnRangesUndergroundWaterCreatureHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.underground-water-creature.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesMiscSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Misc.Soft)
	if err != nil {
		DespawnRangesMiscSoft = 0
	}
	if DespawnRangesMiscSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.misc.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesMiscHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Misc.Hard)
	if err != nil {
		DespawnRangesMiscHard = 0
	}
	if DespawnRangesMiscHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.misc.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	DespawnRangesAxolotlsSoft, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Axolotls.Soft)
	if err != nil {
		DespawnRangesAxolotlsSoft = 0
	}
	if DespawnRangesAxolotlsSoft >= 32 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.axolotls.soft",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 28.",
			Inline: true,
		})
	}

	DespawnRangesAxolotlsHard, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.DespawnRanges.Axolotls.Hard)
	if err != nil {
		DespawnRangesAxolotlsHard = 0
	}

	if DespawnRangesAxolotlsHard >= 128 {
		advice = append(advice, EmbedField{
			Name:   "❌️ despawn-ranges.axolotls.hard",
			Value:  "Decrease this in `config/paper-world-defaults.yml`\nRecommended: 96.",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.Hopper.DisableMoveEvent == "false" {
		advice = append(advice, EmbedField{
			Name:   "❌️ hopper.disable-move-event",
			Value:  "Set this to `true` in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	NonPlayerArrowDespawnRate, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.NonPlayerArrowDespawnRate)
	if err != nil {
		NonPlayerArrowDespawnRate = 0
	}
	if NonPlayerArrowDespawnRate == -1 {
		advice = append(advice, EmbedField{
			Name:   "❌️ non-player-arrow-despawn-rate",
			Value:  "Set a value or the recommended default `60` in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	CreativeArrowDespawnRate, err := strconv.Atoi(data.TimingsMaster.Config.Paper.WorldSettings.Default.CreativeArrowDespawnRate)
	if err != nil {
		CreativeArrowDespawnRate = 0
	}
	if CreativeArrowDespawnRate == -1 {
		advice = append(advice, EmbedField{
			Name:   "❌️ creative-arrow-despawn-rate",
			Value:  "Set a value or the recommended default `60` in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.PreventMovingIntoUnloadedChunks == "false" {
		advice = append(advice, EmbedField{
			Name:   "❌️ prevent-moving-into-unloaded-chunks",
			Value:  "Set this to `true` in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	if data.TimingsMaster.Config.Paper.WorldSettings.Default.RedstoneImplementation != "ALTERNATE_CURRENT" {
		advice = append(advice, EmbedField{
			Name:   "❌️ redstone-implementation",
			Value:  "Set this to `ALTERNATE_CURRENT` in `config/paper-world-defaults.yml`",
			Inline: true,
		})
	}

	return advice
}
