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

	return advice
}
