package timings

type EmbedField struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Inline bool   `json:"inline"`
}

type Timings struct {
	Id            string `json:"id"`
	TimingsMaster struct {
		Version    string `json:"version"`
		Maxplayers int    `json:"maxplayers"`
		Start      int    `json:"start"`
		End        int    `json:"end"`
		Sampletime int    `json:"sampletime"`
		Server     string `json:"server"`
		Motd       string `json:"motd"`
		Onlinemode bool   `json:"onlinemode"`
		Icon       string `json:"icon"`
		System     struct {
			Timingcost int    `json:"timingcost"`
			Name       string `json:"name"`
			Version    string `json:"version"`
			Jvmversion string `json:"jvmversion"`
			Arch       string `json:"arch"`
			Maxmem     int64  `json:"maxmem"`
			Cpu        int    `json:"cpu"`
			Runtime    int    `json:"runtime"`
			Flags      string `json:"flags"`
			Gc         struct {
				G1YoungGeneration []int `json:"G1 Young Generation"`
				G1OldGeneration   []int `json:"G1 Old Generation"`
			} `json:"gc"`
			Cls int `json:":cls"`
		} `json:"system"`
		Idmap struct {
			GroupMap map[string]string `json:"groupMap"`

			HandlerMap map[string]struct {
				Name  string `json:"name"`
				Group int    `json:"group"`
				Cls   int    `json:":cls"`
			} `json:"handlerMap"`

			WorldMap map[string]string `json:"worldMap"`

			TileEntityTypeMap map[string]string `json:"tileEntityTypeMap"`

			EntityTypeMap map[string]string `json:"entityTypeMap"`
			Cls           int               `json:":cls"`
		} `json:"idmap"`
		Plugins interface{} `json:"plugins"`

		Data []struct {
			Id         int   `json:"id"`
			Start      int   `json:"start"`
			End        int   `json:"end"`
			TotalTicks int   `json:"totalTicks"`
			TotalTime  int64 `json:"totalTime"`
			WorldData  map[string]struct {
				WorldName string `json:"worldName"`
				Regions   map[string]struct {
					RegionId   string `json:"regionId"`
					ChunkCount int    `json:"chunkCount"`
					AreaLocX   int    `json:"areaLocX"`
					AreaLocZ   int    `json:"areaLocZ"`
					Cls        int    `json:":cls"`
				} `json:"regions"`
				Cls int `json:":cls"`
			} `json:"worldData"`
			MinuteReports []struct {
				Time           int     `json:"time"`
				Tps            float64 `json:"tps"`
				AvgPing        int     `json:"avgPing"`
				FullServerTick struct {
					Id       int   `json:"id"`
					Count    int   `json:"count"`
					Total    int64 `json:"total"`
					LagCount int   `json:"lagCount"`
					LagTotal int   `json:"lagTotal"`
					Cls      int   `json:":cls"`
				} `json:"fullServerTick"`
				Ticks struct {
					TimedTicks           int `json:"timedTicks"`
					PlayerTicks          int `json:"playerTicks"`
					EntityTicks          int `json:"entityTicks"`
					ActivatedEntityTicks int `json:"activatedEntityTicks"`
					TileEntityTicks      int `json:"tileEntityTicks"`
					Cls                  int `json:":cls"`
				} `json:"ticks"`
				Cls int `json:":cls"`
			} `json:"minuteReports"`
			Cls int `json:":cls"`
		} `json:"data"`
		Config struct {
			Spigot struct {
				Settings struct {
					Debug                     string `json:"debug"`
					MovedTooQuicklyMultiplier string `json:"moved-too-quickly-multiplier"`
					NettyThreads              string `json:"netty-threads"`
					PlayerShuffle             string `json:"player-shuffle"`
					RestartOnCrash            string `json:"restart-on-crash"`
					UserCacheSize             string `json:"user-cache-size"`
					MovedWronglyThreshold     string `json:"moved-wrongly-threshold"`
					Bungeecord                string `json:"bungeecord"`
					TimeoutTime               string `json:"timeout-time"`
					SaveUserCacheOnStopOnly   string `json:"save-user-cache-on-stop-only"`
					LogVillagerDeaths         string `json:"log-villager-deaths"`
					Attribute                 struct {
						MaxHealth struct {
							Max string `json:"max"`
						} `json:"maxHealth"`
						MovementSpeed struct {
							Max string `json:"max"`
						} `json:"movementSpeed"`
						AttackDamage struct {
							Max string `json:"max"`
						} `json:"attackDamage"`
					} `json:"attribute"`
					SampleCount    string `json:"sample-count"`
					LogNamedDeaths string `json:"log-named-deaths"`
					RestartScript  string `json:"restart-script"`
				} `json:"settings"`
				Advancements struct {
					DisableSaving string   `json:"disable-saving"`
					Disabled      []string `json:"disabled"`
				} `json:"advancements"`
				WorldSettings struct {
					Default struct {
						MobSpawnRange                       string `json:"mob-spawn-range"`
						BelowZeroGenerationInExistingChunks string `json:"below-zero-generation-in-existing-chunks"`
						ViewDistance                        string `json:"view-distance"`
						ThunderChance                       string `json:"thunder-chance"`
						HangingTickFrequency                string `json:"hanging-tick-frequency"`
						ArrowDespawnRate                    string `json:"arrow-despawn-rate"`
						SimulationDistance                  string `json:"simulation-distance"`
						TicksPer                            struct {
							HopperTransfer string `json:"hopper-transfer"`
							HopperCheck    string `json:"hopper-check"`
						} `json:"ticks-per"`
						WitherSpawnSoundRadius          string `json:"wither-spawn-sound-radius"`
						TridentDespawnRate              string `json:"trident-despawn-rate"`
						MaxTntPerTick                   string `json:"max-tnt-per-tick"`
						EnableZombiePigmenPortalSpawns  string `json:"enable-zombie-pigmen-portal-spawns"`
						NerfSpawnerMobs                 string `json:"nerf-spawner-mobs"`
						ZombieAggressiveTowardsVillager string `json:"zombie-aggressive-towards-villager"`
						Verbose                         string `json:"verbose"`
						Hunger                          struct {
							JumpSprintExhaustion string `json:"jump-sprint-exhaustion"`
							SwimMultiplier       string `json:"swim-multiplier"`
							OtherMultiplier      string `json:"other-multiplier"`
							CombatExhaustion     string `json:"combat-exhaustion"`
							SprintMultiplier     string `json:"sprint-multiplier"`
							RegenExhaustion      string `json:"regen-exhaustion"`
							JumpWalkExhaustion   string `json:"jump-walk-exhaustion"`
						} `json:"hunger"`
						EndPortalSoundRadius string `json:"end-portal-sound-radius"`
						EntityTrackingRange  struct {
							Other    string `json:"other"`
							Players  string `json:"players"`
							Monsters string `json:"monsters"`
							Animals  string `json:"animals"`
							Misc     string `json:"misc"`
						} `json:"entity-tracking-range"`
						MaxTickTime struct {
							Tile   string `json:"tile"`
							Entity string `json:"entity"`
						} `json:"max-tick-time"`
						HopperAmount          string `json:"hopper-amount"`
						EntityActivationRange struct {
							IgnoreSpectators string `json:"ignore-spectators"`
							FlyingMonsters   string `json:"flying-monsters"`
							WakeUpInactive   struct {
								VillagersEvery           string `json:"villagers-every"`
								VillagersFor             string `json:"villagers-for"`
								FlyingMonstersFor        string `json:"flying-monsters-for"`
								AnimalsEvery             string `json:"animals-every"`
								VillagersMaxPerTick      string `json:"villagers-max-per-tick"`
								AnimalsFor               string `json:"animals-for"`
								MonstersMaxPerTick       string `json:"monsters-max-per-tick"`
								FlyingMonstersMaxPerTick string `json:"flying-monsters-max-per-tick"`
								FlyingMonstersEvery      string `json:"flying-monsters-every"`
								MonstersEvery            string `json:"monsters-every"`
								AnimalsMaxPerTick        string `json:"animals-max-per-tick"`
								MonstersFor              string `json:"monsters-for"`
							} `json:"wake-up-inactive"`
							VillagersWorkImmunityAfter string `json:"villagers-work-immunity-after"`
							Monsters                   string `json:"monsters"`
							Water                      string `json:"water"`
							VillagersWorkImmunityFor   string `json:"villagers-work-immunity-for"`
							Villagers                  string `json:"villagers"`
							VillagersActiveForPanic    string `json:"villagers-active-for-panic"`
							Animals                    string `json:"animals"`
							TickInactiveVillagers      string `json:"tick-inactive-villagers"`
							Raiders                    string `json:"raiders"`
							Misc                       string `json:"misc"`
						} `json:"entity-activation-range"`
						Growth struct {
							TwistingvinesModifier string `json:"twistingvines-modifier"`
							CarrotModifier        string `json:"carrot-modifier"`
							NetherwartModifier    string `json:"netherwart-modifier"`
							MushroomModifier      string `json:"mushroom-modifier"`
							CocoaModifier         string `json:"cocoa-modifier"`
							KelpModifier          string `json:"kelp-modifier"`
							GlowberryModifier     string `json:"glowberry-modifier"`
							WheatModifier         string `json:"wheat-modifier"`
							VineModifier          string `json:"vine-modifier"`
							SweetberryModifier    string `json:"sweetberry-modifier"`
							MelonModifier         string `json:"melon-modifier"`
							PumpkinModifier       string `json:"pumpkin-modifier"`
							SaplingModifier       string `json:"sapling-modifier"`
							PotatoModifier        string `json:"potato-modifier"`
							WeepingvinesModifier  string `json:"weepingvines-modifier"`
							CavevinesModifier     string `json:"cavevines-modifier"`
							BeetrootModifier      string `json:"beetroot-modifier"`
							BambooModifier        string `json:"bamboo-modifier"`
							CaneModifier          string `json:"cane-modifier"`
							CactusModifier        string `json:"cactus-modifier"`
						} `json:"growth"`
						DragonDeathSoundRadius string `json:"dragon-death-sound-radius"`
						ItemDespawnRate        string `json:"item-despawn-rate"`
						MergeRadius            struct {
							Item string `json:"item"`
							Exp  string `json:"exp"`
						} `json:"merge-radius"`
					} `json:"default"`
					Faweregentempworld struct {
						Verbose string `json:"verbose"`
					} `json:"faweregentempworld"`
				} `json:"world-settings"`
				Stats struct {
					DisableSaving string        `json:"disable-saving"`
					ForcedStats   []interface{} `json:"forced-stats"`
				} `json:"stats"`
				ConfigVersion string `json:"config-version"`
				Players       struct {
					DisableSaving string `json:"disable-saving"`
				} `json:"players"`
				Messages struct {
					OutdatedClient string `json:"outdated-client"`
					UnknownCommand string `json:"unknown-command"`
					Restart        string `json:"restart"`
					OutdatedServer string `json:"outdated-server"`
					Whitelist      string `json:"whitelist"`
					ServerFull     string `json:"server-full"`
				} `json:"messages"`
				Commands struct {
					TabComplete               string   `json:"tab-complete"`
					SendNamespaced            string   `json:"send-namespaced"`
					Log                       string   `json:"log"`
					SilentCommandblockConsole string   `json:"silent-commandblock-console"`
					SpamExclusions            []string `json:"spam-exclusions"`
					ReplaceCommands           []string `json:"replace-commands"`
				} `json:"commands"`
			} `json:"spigot"`
			Bukkit struct {
				Settings struct {
					UpdateFolder       string `json:"update-folder"`
					WarnOnOverload     string `json:"warn-on-overload"`
					QueryPlugins       string `json:"query-plugins"`
					DeprecatedVerbose  string `json:"deprecated-verbose"`
					ConnectionThrottle string `json:"connection-throttle"`
					PluginProfiling    string `json:"plugin-profiling"`
					PermissionsFile    string `json:"permissions-file"`
					AllowEnd           string `json:"allow-end"`
					MinimumApi         string `json:"minimum-api"`
					ShutdownMessage    string `json:"shutdown-message"`
				} `json:"settings"`
				TicksPer struct {
					MonsterSpawns                  string `json:"monster-spawns"`
					Autosave                       string `json:"autosave"`
					AmbientSpawns                  string `json:"ambient-spawns"`
					WaterSpawns                    string `json:"water-spawns"`
					WaterAmbientSpawns             string `json:"water-ambient-spawns"`
					WaterUndergroundCreatureSpawns string `json:"water-underground-creature-spawns"`
					AnimalSpawns                   string `json:"animal-spawns"`
					AxolotlSpawns                  string `json:"axolotl-spawns"`
				} `json:"ticks-per"`
				Aliases     string `json:"aliases"`
				SpawnLimits struct {
					WaterAmbient             string `json:"water-ambient"`
					WaterUndergroundCreature string `json:"water-underground-creature"`
					Monsters                 string `json:"monsters"`
					Ambient                  string `json:"ambient"`
					Animals                  string `json:"animals"`
					WaterAnimals             string `json:"water-animals"`
					Axolotls                 string `json:"axolotls"`
				} `json:"spawn-limits"`
				ChunkGc struct {
					PeriodInTicks string `json:"period-in-ticks"`
				} `json:"chunk-gc"`
			} `json:"bukkit"`
			Paper struct {
				Settings struct {
					AsyncChunks struct {
						Threads string `json:"threads"`
					} `json:"async-chunks"`
					SpamLimiter struct {
						TabSpamIncrement    string `json:"tab-spam-increment"`
						TabSpamLimit        string `json:"tab-spam-limit"`
						RecipeSpamLimit     string `json:"recipe-spam-limit"`
						RecipeSpamIncrement string `json:"recipe-spam-increment"`
					} `json:"spam-limiter"`
					UseDimensionTypeForCustomSpawners string `json:"use-dimension-type-for-custom-spawners"`
					LogPlayerIpAddresses              string `json:"log-player-ip-addresses"`
					Loggers                           struct {
						UseRgbForNamedTextColors string `json:"use-rgb-for-named-text-colors"`
						DeobfuscateStacktraces   string `json:"deobfuscate-stacktraces"`
					} `json:"loggers"`
					FixEntityPositionDesync             string `json:"fix-entity-position-desync"`
					SendFullPosForHardCollidingEntities string `json:"send-full-pos-for-hard-colliding-entities"`
					PlayerAutoSaveRate                  string `json:"player-auto-save-rate"`
					VelocitySupport                     struct {
						OnlineMode string `json:"online-mode"`
						Enabled    string `json:"enabled"`
					} `json:"velocity-support"`
					BookSize struct {
						TotalMultiplier string `json:"total-multiplier"`
						PageMax         string `json:"page-max"`
					} `json:"book-size"`
					TimeCommandAffectsAllWorlds              string `json:"time-command-affects-all-worlds"`
					MaxJoinsPerTick                          string `json:"max-joins-per-tick"`
					TrackPluginScoreboards                   string `json:"track-plugin-scoreboards"`
					ConsoleHasAllPermissions                 string `json:"console-has-all-permissions"`
					SuggestPlayerNamesWhenNullTabCompletions string `json:"suggest-player-names-when-null-tab-completions"`
					ItemValidation                           struct {
						DisplayName string `json:"display-name"`
						LoreLine    string `json:"lore-line"`
						Book        struct {
							Author string `json:"author"`
							Page   string `json:"page"`
							Title  string `json:"title"`
						} `json:"book"`
						LocName string `json:"loc-name"`
					} `json:"item-validation"`
					MaxPlayerAutoSavePerTick string `json:"max-player-auto-save-per-tick"`
					EnablePlayerCollisions   string `json:"enable-player-collisions"`
					ResolveSelectorsInBooks  string `json:"resolve-selectors-in-books"`
					Console                  struct {
						EnableBrigadierHighlighting string `json:"enable-brigadier-highlighting"`
						EnableBrigadierCompletions  string `json:"enable-brigadier-completions"`
					} `json:"console"`
					UseDisplayNameInQuitMessage string `json:"use-display-name-in-quit-message"`
					SaveEmptyScoreboardTeams    string `json:"save-empty-scoreboard-teams"`
					LagCompensateBlockBreaking  string `json:"lag-compensate-block-breaking"`
					PacketLimiter               struct {
						KickMessage string `json:"kick-message"`
						Limits      struct {
							All struct {
								MaxPacketRate string `json:"max-packet-rate"`
								Interval      string `json:"interval"`
							} `json:"all"`
							PacketPlayInAutoRecipe struct {
								MaxPacketRate string `json:"max-packet-rate"`
								Action        string `json:"action"`
								Interval      string `json:"interval"`
							} `json:"PacketPlayInAutoRecipe"`
						} `json:"limits"`
					} `json:"packet-limiter"`
					UnsupportedSettings struct {
						PerformUsernameValidation              string `json:"perform-username-validation"`
						AllowHeadlessPistonsReadme             string `json:"allow-headless-pistons-readme"`
						AllowPermanentBlockBreakExploits       string `json:"allow-permanent-block-break-exploits"`
						AllowPistonDuplicationReadme           string `json:"allow-piston-duplication-readme"`
						AllowHeadlessPistons                   string `json:"allow-headless-pistons"`
						AllowPistonDuplication                 string `json:"allow-piston-duplication"`
						AllowPermanentBlockBreakExploitsReadme string `json:"allow-permanent-block-break-exploits-readme"`
					} `json:"unsupported-settings"`
					UseAlternativeLuckFormula       string `json:"use-alternative-luck-formula"`
					FixTargetSelectorTagCompletion  string `json:"fix-target-selector-tag-completion"`
					LoadPermissionsYmlBeforePlugins string `json:"load-permissions-yml-before-plugins"`
					IncomingPacketSpamThreshold     string `json:"incoming-packet-spam-threshold"`
					RegionFileCacheSize             string `json:"region-file-cache-size"`
					ProxyProtocol                   string `json:"proxy-protocol"`
					Watchdog                        struct {
						EarlyWarningEvery string `json:"early-warning-every"`
						EarlyWarningDelay string `json:"early-warning-delay"`
					} `json:"watchdog"`
					ChunkLoading struct {
						PlayerMaxChunkLoadRate    string `json:"player-max-chunk-load-rate"`
						TargetPlayerChunkSendRate string `json:"target-player-chunk-send-rate"`
						GlobalMaxConcurrentLoads  string `json:"global-max-concurrent-loads"`
						GlobalMaxChunkSendRate    string `json:"global-max-chunk-send-rate"`
						MinLoadRadius             string `json:"min-load-radius"`
						MaxConcurrentSends        string `json:"max-concurrent-sends"`
						AutoconfigSendDistance    string `json:"autoconfig-send-distance"`
						GlobalMaxChunkLoadRate    string `json:"global-max-chunk-load-rate"`
						PlayerMaxConcurrentLoads  string `json:"player-max-concurrent-loads"`
						EnableFrustumPriority     string `json:"enable-frustum-priority"`
					} `json:"chunk-loading"`
					BungeeOnlineMode string `json:"bungee-online-mode"`
				} `json:"settings"`
				WorldSettings struct {
					Default struct {
						PortalSearchRadius            string `json:"portal-search-radius"`
						CreativeArrowDespawnRate      string `json:"creative-arrow-despawn-rate"`
						TntEntityHeightNerf           string `json:"tnt-entity-height-nerf"`
						ZombieVillagerInfectionChance string `json:"zombie-villager-infection-chance"`
						MobEffects                    struct {
							SpidersImmuneToPoisonEffect  string `json:"spiders-immune-to-poison-effect"`
							UndeadImmuneToCertainEffects string `json:"undead-immune-to-certain-effects"`
							ImmuneToWitherEffect         struct {
								WitherSkeleton string `json:"wither-skeleton"`
								Wither         string `json:"wither"`
							} `json:"immune-to-wither-effect"`
						} `json:"mob-effects"`
						AllowPlayerCrammingDamage string `json:"allow-player-cramming-damage"`
						TickRates                 struct {
							Sensor struct {
								Villager struct {
									Secondarypoisensor string `json:"secondarypoisensor"`
								} `json:"villager"`
							} `json:"sensor"`
							Behavior struct {
								Villager struct {
									Validatenearbypoi string `json:"validatenearbypoi"`
								} `json:"villager"`
							} `json:"behavior"`
							ContainerUpdate int `json:"container-update"`
							GrassSpread     int `json:"grass-spread"`
							MobSpawner      int `json:"mob-spawner"`
						} `json:"tick-rates"`
						DuplicateUuidSaferegenDeleteRange    string `json:"duplicate-uuid-saferegen-delete-range"`
						ContainerUpdateTickRate              string `json:"container-update-tick-rate"`
						MobSpawnerTickRate                   string `json:"mob-spawner-tick-rate"`
						PhantomsDoNotSpawnOnCreativePlayers  string `json:"phantoms-do-not-spawn-on-creative-players"`
						ArmorStandsDoCollisionEntityLookups  string `json:"armor-stands-do-collision-entity-lookups"`
						GrassSpreadTickRate                  string `json:"grass-spread-tick-rate"`
						ParrotsAreUnaffectedByPlayerMovement string `json:"parrots-are-unaffected-by-player-movement"`
						MapItemFrameCursorUpdateInterval     string `json:"map-item-frame-cursor-update-interval"`
						UpdatePathfindingOnBlockUpdate       string `json:"update-pathfinding-on-block-update"`
						IronGolemsCanSpawnInAir              string `json:"iron-golems-can-spawn-in-air"`
						BabyZombieMovementModifier           string `json:"baby-zombie-movement-modifier"`
						GeneratorSettings                    struct {
							FlatBedrock string `json:"flat-bedrock"`
						} `json:"generator-settings"`
						RedstoneImplementation               string `json:"redstone-implementation"`
						EnableTreasureMaps                   string `json:"enable-treasure-maps"`
						DisableThunder                       string `json:"disable-thunder"`
						EntitiesTargetWithFollowRange        string `json:"entities-target-with-follow-range"`
						DisableTeleportationSuffocationCheck string `json:"disable-teleportation-suffocation-check"`
						WanderingTrader                      struct {
							SpawnMinuteLength           string `json:"spawn-minute-length"`
							SpawnChanceMax              string `json:"spawn-chance-max"`
							SpawnDayLength              string `json:"spawn-day-length"`
							SpawnChanceMin              string `json:"spawn-chance-min"`
							SpawnChanceFailureIncrement string `json:"spawn-chance-failure-increment"`
						} `json:"wandering-trader"`
						SkeletonHorseThunderSpawnChance string `json:"skeleton-horse-thunder-spawn-chance"`
						AltItemDespawnRate              struct {
							Items struct {
								Cobblestone string `json:"cobblestone"`
							} `json:"items"`
							Enabled string `json:"enabled"`
						} `json:"alt-item-despawn-rate"`
						CountAllMobsForSpawning string `json:"count-all-mobs-for-spawning"`
						ZombiesTargetTurtleEggs string `json:"zombies-target-turtle-eggs"`
						KeepSpawnLoaded         string `json:"keep-spawn-loaded"`
						UnsupportedSettings     struct {
							FixInvulnerableEndCrystalExploit string `json:"fix-invulnerable-end-crystal-exploit"`
						} `json:"unsupported-settings"`
						MaxLeashDistance                  string `json:"max-leash-distance"`
						LightQueueSize                    string `json:"light-queue-size"`
						DuplicateUuidResolver             string `json:"duplicate-uuid-resolver"`
						TreasureMapsFindAlreadyDiscovered struct {
							VillagerTrade string `json:"villager-trade"`
							LootTables    string `json:"loot-tables"`
						} `json:"treasure-maps-find-already-discovered"`
						OptimizeExplosions        string `json:"optimize-explosions"`
						MaxAutoSaveChunksPerTick  string `json:"max-auto-save-chunks-per-tick"`
						MonsterSpawnMaxLightLevel string `json:"monster-spawn-max-light-level"`
						DelayChunkUnloadsBy       string `json:"delay-chunk-unloads-by"`
						PiglinsGuardChests        string `json:"piglins-guard-chests"`
						MobsCanAlwaysPickUpLoot   struct {
							Skeletons string `json:"skeletons"`
							Zombies   string `json:"zombies"`
						} `json:"mobs-can-always-pick-up-loot"`
						DisableExplosionKnockback              string `json:"disable-explosion-knockback"`
						EnderDragonsDeathAlwaysPlacesDragonEgg string `json:"ender-dragons-death-always-places-dragon-egg"`
						FilterNbtDataFromSpawnEggsAndRelated   string `json:"filter-nbt-data-from-spawn-eggs-and-related"`
						NetherCeilingVoidDamageHeight          string `json:"nether-ceiling-void-damage-height"`
						MapItemFrameCursorLimit                string `json:"map-item-frame-cursor-limit"`
						ShouldRemoveDragon                     string `json:"should-remove-dragon"`
						WaterOverLavaFlowSpeed                 string `json:"water-over-lava-flow-speed"`
						PortalCreateRadius                     string `json:"portal-create-radius"`
						FixedChunkInhabitedTime                string `json:"fixed-chunk-inhabited-time"`
						WateranimalSpawnHeight                 struct {
							Maximum string `json:"maximum"`
							Minimum string `json:"minimum"`
						} `json:"wateranimal-spawn-height"`
						FixItemsMergingThroughWalls string `json:"fix-items-merging-through-walls"`
						FrostedIce                  struct {
							Delay struct {
								Min string `json:"min"`
								Max string `json:"max"`
							} `json:"delay"`
							Enabled string `json:"enabled"`
						} `json:"frosted-ice"`
						PreventMovingIntoUnloadedChunks string `json:"prevent-moving-into-unloaded-chunks"`
						AutoSaveInterval                string `json:"auto-save-interval"`
						PerPlayerMobSpawns              string `json:"per-player-mob-spawns"`
						DisableIceAndSnow               string `json:"disable-ice-and-snow"`
						EntityPerChunkSaveLimit         struct {
							Arrow         string `json:"arrow"`
							EnderPearl    string `json:"ender_pearl"`
							Snowball      string `json:"snowball"`
							ExperienceOrb string `json:"experience_orb"`
							Fireball      string `json:"fireball"`
							SmallFireball string `json:"small_fireball"`
						} `json:"entity-per-chunk-save-limit"`
						FishingTimeRange struct {
							MaximumTicks string `json:"MaximumTicks"`
							MinimumTicks string `json:"MinimumTicks"`
						} `json:"fishing-time-range"`
						SpawnLimits struct {
							WaterCreature            string `json:"water_creature"`
							UndergroundWaterCreature string `json:"underground_water_creature"`
							Ambient                  string `json:"ambient"`
							Axolotls                 string `json:"axolotls"`
							Creature                 string `json:"creature"`
							WaterAmbient             string `json:"water_ambient"`
							Monster                  string `json:"monster"`
						} `json:"spawn-limits"`
						ShowSignClickCommandFailureMsgsToPlayer string `json:"show-sign-click-command-failure-msgs-to-player"`
						SpawnerNerfedMobsShouldJump             string `json:"spawner-nerfed-mobs-should-jump"`
						ExperienceMergeMaxValue                 string `json:"experience-merge-max-value"`
						FallingBlockHeightNerf                  string `json:"falling-block-height-nerf"`
						AllowUsingSignsInsideSpawnProtection    string `json:"allow-using-signs-inside-spawn-protection"`
						AntiXray                                struct {
							LavaObscures      string   `json:"lava-obscures"`
							UpdateRadius      string   `json:"update-radius"`
							MaxBlockHeight    string   `json:"max-block-height"`
							ReplacementBlocks []string `json:"replacement-blocks"`
							UsePermission     string   `json:"use-permission"`
							Enabled           string   `json:"enabled"`
							HiddenBlocks      []string `json:"hidden-blocks"`
							EngineMode        string   `json:"engine-mode"`
						} `json:"anti-xray"`
						OnlyPlayersCollide   string `json:"only-players-collide"`
						SplitOverstackedLoot string `json:"split-overstacked-loot"`
						Anticheat            struct {
							Obfuscation struct {
								Items struct {
									HideDurability string `json:"hide-durability"`
									HideItemmeta   string `json:"hide-itemmeta"`
								} `json:"items"`
							} `json:"obfuscation"`
						} `json:"anticheat"`
						AllChunksAreSlimeChunks               string `json:"all-chunks-are-slime-chunks"`
						AllowNonPlayerEntitiesOnScoreboards   string `json:"allow-non-player-entities-on-scoreboards"`
						UseVanillaWorldScoreboardNameColoring string `json:"use-vanilla-world-scoreboard-name-coloring"`
						AllowVehicleCollisions                string `json:"allow-vehicle-collisions"`
						PhantomsOnlyAttackInsomniacs          string `json:"phantoms-only-attack-insomniacs"`
						RemoveCorruptTileEntities             string `json:"remove-corrupt-tile-entities"`
						SlimeSpawnHeight                      struct {
							SlimeChunk struct {
								Maximum string `json:"maximum"`
							} `json:"slime-chunk"`
							SwampBiome struct {
								Maximum string `json:"maximum"`
								Minimum string `json:"minimum"`
							} `json:"swamp-biome"`
						} `json:"slime-spawn-height"`
						DoorBreakingDifficulty struct {
							Vindicator      []string `json:"vindicator"`
							Husk            []string `json:"husk"`
							ZombifiedPiglin []string `json:"zombified_piglin"`
							Zombie          []string `json:"zombie"`
							ZombieVillager  []string `json:"zombie_villager"`
						} `json:"door-breaking-difficulty"`
						ArmorStandsTick string `json:"armor-stands-tick"`
						DespawnRanges   struct {
							WaterCreature struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"water_creature"`
							UndergroundWaterCreature struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"underground_water_creature"`
							Ambient struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"ambient"`
							Axolotls struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"axolotls"`
							Creature struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"creature"`
							WaterAmbient struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"water_ambient"`
							Monster struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"monster"`
							Misc struct {
								Hard string `json:"hard"`
								Soft string `json:"soft"`
							} `json:"misc"`
						} `json:"despawn-ranges"`
						KeepSpawnLoadedRange             string `json:"keep-spawn-loaded-range"`
						FixClimbingBypassingCrammingRule string `json:"fix-climbing-bypassing-cramming-rule"`
						NonPlayerArrowDespawnRate        string `json:"non-player-arrow-despawn-rate"`
						MaxGrowthHeight                  struct {
							Bamboo struct {
								Min string `json:"min"`
								Max string `json:"max"`
							} `json:"bamboo"`
							Reeds  string `json:"reeds"`
							Cactus string `json:"cactus"`
						} `json:"max-growth-height"`
						MaxEntityCollisions           string `json:"max-entity-collisions"`
						DisableCreeperLingeringEffect string `json:"disable-creeper-lingering-effect"`
						GameMechanics                 struct {
							DisableUnloadedChunkEnderpearlExploit string `json:"disable-unloaded-chunk-enderpearl-exploit"`
							NerfPigmenFromNetherPortals           string `json:"nerf-pigmen-from-nether-portals"`
							ShieldBlockingDelay                   string `json:"shield-blocking-delay"`
							DisablePlayerCrits                    string `json:"disable-player-crits"`
							DisableChestCatDetection              string `json:"disable-chest-cat-detection"`
							DisableRelativeProjectileVelocity     string `json:"disable-relative-projectile-velocity"`
							ScanForLegacyEnderDragon              string `json:"scan-for-legacy-ender-dragon"`
							DisablePillagerPatrols                string `json:"disable-pillager-patrols"`
							PillagerPatrols                       struct {
								Start struct {
									Day       string `json:"day"`
									PerPlayer string `json:"per-player"`
								} `json:"start"`
								SpawnChance string `json:"spawn-chance"`
								SpawnDelay  struct {
									Ticks     string `json:"ticks"`
									PerPlayer string `json:"per-player"`
								} `json:"spawn-delay"`
							} `json:"pillager-patrols"`
							DisableSprintInterruptionOnAttack       string `json:"disable-sprint-interruption-on-attack"`
							DisableMobSpawnerSpawnEggTransformation string `json:"disable-mob-spawner-spawn-egg-transformation"`
							FixCuringZombieVillagerDiscountExploit  string `json:"fix-curing-zombie-villager-discount-exploit"`
							DisableEndCredits                       string `json:"disable-end-credits"`
						} `json:"game-mechanics"`
						PortalSearchVanillaDimensionScaling string `json:"portal-search-vanilla-dimension-scaling"`
						Hopper                              struct {
							IgnoreOccludingBlocks string `json:"ignore-occluding-blocks"`
							CooldownWhenFull      string `json:"cooldown-when-full"`
							DisableMoveEvent      string `json:"disable-move-event"`
						} `json:"hopper"`
						PreventTntFromMovingInWater string `json:"prevent-tnt-from-moving-in-water"`
						Lootables                   struct {
							RestrictPlayerReloot string `json:"restrict-player-reloot"`
							AutoReplenish        string `json:"auto-replenish"`
							ResetSeedOnFill      string `json:"reset-seed-on-fill"`
							RefreshMin           string `json:"refresh-min"`
							MaxRefills           string `json:"max-refills"`
							RefreshMax           string `json:"refresh-max"`
						} `json:"lootables"`
					} `json:"default"`
				} `json:"world-settings"`
				ConfigVersion string `json:"config-version"`
				Timings       struct {
					ServerName          string   `json:"server-name"`
					HiddenConfigEntries []string `json:"hidden-config-entries"`
					HistoryInterval     string   `json:"history-interval"`
					HistoryLength       string   `json:"history-length"`
					ServerNamePrivacy   string   `json:"server-name-privacy"`
					Enabled             string   `json:"enabled"`
					Url                 string   `json:"url"`
					Verbose             string   `json:"verbose"`
				} `json:"timings"`
				Messages struct {
					Kick struct {
						ConnectionThrottle        string `json:"connection-throttle"`
						AuthenticationServersDown string `json:"authentication-servers-down"`
						FlyingVehicle             string `json:"flying-vehicle"`
						FlyingPlayer              string `json:"flying-player"`
					} `json:"kick"`
					NoPermission string `json:"no-permission"`
				} `json:"messages"`
				Verbose string `json:"verbose"`
			} `json:"paper"`
		} `json:"config"`
		Cls int `json:":cls"`
	} `json:"timingsMaster"`
}

type PaperVersions struct {
	ProjectId     string   `json:"project_id"`
	ProjectName   string   `json:"project_name"`
	VersionGroups []string `json:"version_groups"`
	Versions      []string `json:"versions"`
}

type PaperVersionBuilds struct {
	ProjectId   string `json:"project_id"`
	ProjectName string `json:"project_name"`
	Version     string `json:"version"`
	Builds      []int  `json:"builds"`
}

type PluginsJson struct {
	Paper []struct {
		Name    string `json:"name"`
		Warning string `json:"warning"`
		Reason  string `json:"reason"`
	} `json:"paper"`
	Purpur []struct {
		Name    string `json:"name"`
		Warning string `json:"warning"`
		Reason  string `json:"reason"`
	} `json:"purpur"`
}

type Plugin struct {
	Name        string  `json:"name"`
	Version     string  `json:"version"`
	Description string  `json:"description"`
	Authors     string  `json:"authors"`
	Cls         float64 `json:":cls"`
}
