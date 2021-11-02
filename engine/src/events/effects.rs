use crate::game::{Game, Request};
use crate::regions::Region;
use crate::production::ProcessFeature;
use crate::kinds::{Resource, Output, Feedstock, Byproduct};
use super::{WorldVariable, LocalVariable, PlayerVariable};
use serde::Serialize;

const MIGRATION_WAVE_PERCENT_POP: f32 = 0.1;

#[derive(Serialize, PartialEq, Debug, Clone, Copy)]
pub enum Flag {
    Electrified,
    EnergyStorage1,
    EnergyStorage2,
    EnergyStorage3,
    Vegetarian,
    Vegan,
}

#[derive(Serialize, Debug, Clone)]
pub enum Effect {
    LocalVariable(LocalVariable, f32),
    WorldVariable(WorldVariable, f32),
    PlayerVariable(PlayerVariable, f32),

    Resource(Resource, f32),
    Demand(Output, f32),
    Output(Output, f32),
    DemandAmount(Output, f32),
    OutputForFeature(ProcessFeature, f32),
    OutputForProcess(usize, f32),
    Feedstock(Feedstock, f32),

    AddEvent(usize),
    TriggerEvent(usize, usize),
    UnlocksProject(usize),
    UnlocksProcess(usize),

    ProjectRequest(usize, bool, usize),
    ProcessRequest(usize, bool, usize),

    Migration,
    RegionLeave,
    AddRegionFlag(String),

    AddFlag(Flag),
    AutoClick(usize, f32),
    NPCRelationship(usize, f32),

    ModifyIndustryByproducts(usize, Byproduct, f32),
    ModifyIndustryResources(usize, Resource, f32),
    ModifyEventProbability(usize, f32),
    ModifyIndustryDemand(usize, f32),
    DemandOutlookChange(Output, f32),
    IncomeOutlookChange(f32),
    ProjectCostModifier(usize, f32),

    ProtectLand(f32),
}

impl Effect {
    pub fn apply(&self, game: &mut Game, region_id: Option<usize>) {
        match self {
            Effect::LocalVariable(var, change) => {
                if let Some(id) = region_id {
                    let region = &mut game.state.world.regions[id];
                    match var {
                        LocalVariable::Population => region.population *= 1. + *change/100.,
                        LocalVariable::Outlook => region.outlook += *change,
                        LocalVariable::Habitability => region.base_habitability += *change,
                    }
                }
            },
            Effect::WorldVariable(var, change) => {
                match var {
                    WorldVariable::Year => game.state.world.year += *change as usize,
                    WorldVariable::Population => game.state.world.change_population(*change/100.),
                    WorldVariable::PopulationGrowth => game.state.world.population_growth_modifier += *change/100.,
                    WorldVariable::Emissions => game.state.world.byproduct_mods.co2 += *change,
                    WorldVariable::ExtinctionRate => game.state.world.byproduct_mods.biodiversity -= *change,
                    WorldVariable::Outlook => game.state.world.change_outlook(*change),
                    WorldVariable::Temperature => game.state.world.temperature_modifier += *change,
                    WorldVariable::WaterStress => game.state.world.water_stress += *change,
                    WorldVariable::SeaLevelRise => game.state.world.sea_level_rise += *change,
                    WorldVariable::Precipitation => game.state.world.precipitation += *change,
                }
            }
            Effect::PlayerVariable(var, change) => {
                match var {
                    PlayerVariable::PoliticalCapital => game.state.political_capital += *change as isize,
                    PlayerVariable::MalthusianPoints => game.state.malthusian_points += *change as usize,
                    PlayerVariable::HESPoints => game.state.hes_points += *change as usize,
                    PlayerVariable::FALCPoints => game.state.falc_points += *change as usize,
                }
            },
            Effect::Resource(resource, pct_change) => {
                game.state.resources[*resource] *= 1. + pct_change;
            }
            Effect::Demand(output, pct_change) => {
                game.state.output_demand_modifier[*output] += pct_change;
            },
            Effect::DemandAmount(output, amount) => {
                game.state.output_demand_extras[*output] += amount;
            },
            Effect::Output(output, pct_change) => {
                game.state.output_modifier[*output] += pct_change;
            },
            Effect::OutputForFeature(feat, pct_change) => {
                for process in game.state.processes.iter_mut().filter(|p| p.features.contains(feat)) {
                    process.output_modifier += pct_change;
                }
            },
            Effect::OutputForProcess(id, pct_change) => {
                let process = &mut game.state.processes[*id];
                process.output_modifier += pct_change;
            },
            Effect::Feedstock(feedstock, pct_change) => {
                game.state.feedstocks[*feedstock] *= pct_change;
            },
            Effect::AddEvent(id) => {
                game.event_pool.events[*id].locked = false;
            },
            Effect::TriggerEvent(id, years) => {
                game.event_pool.queue_event(*id, region_id, *years);
            },
            Effect::UnlocksProject(id) => {
                game.state.projects[*id].locked = false;
            },
            Effect::UnlocksProcess(id) => {
                game.state.processes[*id].locked = false;
            },
            Effect::ProjectRequest(id, active, bounty) => {
                game.state.requests.push((Request::Project, *id, *active, *bounty));
            },
            Effect::ProcessRequest(id, active, bounty) => {
                game.state.requests.push((Request::Process, *id, *active, *bounty));
            },
            Effect::Migration => {
                if let Some(id) = region_id {
                    let leave_pop = game.state.world.regions[id].population * MIGRATION_WAVE_PERCENT_POP;
                    game.state.world.regions[id].population -= leave_pop;

                    // Find the most habitable regions
                    let mean_habitability: f32 = game.state.world.habitability();
                    let target_regions: Vec<&mut Region> = game.state.world.regions.iter_mut()
                        .filter(|r| r.id != id && r.habitability() > mean_habitability).collect();
                    let per_region = leave_pop/target_regions.len() as f32;
                    for region in target_regions {
                        region.population += per_region;
                    }
                }
                todo!()
            },
            Effect::RegionLeave => {
                if let Some(id) = region_id {
                    game.state.world.regions[id].seceded = true;
                }
            },
            Effect::AddRegionFlag(flag) => {
                if let Some(id) = region_id {
                    game.state.world.regions[id].flags.push(flag.to_string());
                }
            },
            Effect::AddFlag(flag) => {
                game.state.flags.push(*flag);
            },
            Effect::NPCRelationship(id, change) => {
                game.state.npcs[*id].relationship += change;
            },

            Effect::ModifyIndustryByproducts(id, byproduct, mult) => {
                game.state.industries[*id].byproducts[*byproduct] *= mult;
            },
            Effect::ModifyIndustryResources(id, resource, mult) => {
                game.state.industries[*id].resources[*resource] *= mult;
            },
            Effect::ModifyEventProbability(id, change) => {
                game.event_pool.events[*id].prob_modifier += change;
            },
            Effect::ModifyIndustryDemand(id, change) => {
                game.state.industries[*id].demand_modifier += change;
            },
            Effect::DemandOutlookChange(output, mult) => {
                for region in &mut game.state.world.regions {
                    region.outlook += (mult * region.demand()[*output]).round();
                }
            },
            Effect::IncomeOutlookChange(mult) => {
                for region in &mut game.state.world.regions {
                    region.outlook += (mult * region.adjusted_income()).round();
                }
            },
            Effect::ProjectCostModifier(id, change) => {
                game.state.projects[*id].cost_modifier += change;
            },
            Effect::ProtectLand(percent) => {
                game.state.protected_land += percent/100.;
            }

            // Effects like AutoClick have no impact in the engine side
            _ => ()
        }
    }

    pub fn unapply(&self, game: &mut Game, region_id: Option<usize>) {
        match self {
            Effect::LocalVariable(var, change) => {
                if let Some(id) = region_id {
                    let region = &mut game.state.world.regions[id];
                    match var {
                        LocalVariable::Population => region.population /= 1. + *change/100.,
                        LocalVariable::Outlook => region.outlook -= *change,
                        LocalVariable::Habitability => region.base_habitability -= *change,
                    }
                }
            },
            Effect::WorldVariable(var, change) => {
                match var {
                    WorldVariable::Year => game.state.world.year -= *change as usize,
                    WorldVariable::Population => game.state.world.change_population(1./(*change/100.)),
                    WorldVariable::PopulationGrowth => game.state.world.population_growth_modifier -= *change/100.,
                    WorldVariable::Emissions => game.state.world.byproduct_mods.co2 -= *change,
                    WorldVariable::ExtinctionRate => game.state.world.byproduct_mods.biodiversity += *change,
                    WorldVariable::Outlook => game.state.world.change_outlook(-*change),
                    WorldVariable::Temperature => game.state.world.temperature_modifier -= *change,
                    WorldVariable::WaterStress => game.state.world.water_stress -= *change,
                    WorldVariable::SeaLevelRise => game.state.world.sea_level_rise -= *change,
                    WorldVariable::Precipitation => game.state.world.precipitation -= *change,
                }
            }
            Effect::PlayerVariable(var, change) => {
                match var {
                    PlayerVariable::PoliticalCapital => game.state.political_capital -= *change as isize,
                    PlayerVariable::MalthusianPoints => game.state.malthusian_points -= *change as usize,
                    PlayerVariable::HESPoints => game.state.hes_points -= *change as usize,
                    PlayerVariable::FALCPoints => game.state.falc_points -= *change as usize,
                }
            },
            Effect::Resource(resource, pct_change) => {
                game.state.resources[*resource] /= 1. + pct_change;
            }
            Effect::Demand(output, pct_change) => {
                game.state.output_demand_modifier[*output] -= pct_change;
            },
            Effect::DemandAmount(output, amount) => {
                game.state.output_demand_extras[*output] -= amount;
            },
            Effect::Output(output, pct_change) => {
                game.state.output_modifier[*output] -= pct_change;
            },
            Effect::OutputForFeature(feat, pct_change) => {
                for process in game.state.processes.iter_mut().filter(|p| p.features.contains(feat)) {
                    process.output_modifier -= pct_change;
                }
            },
            Effect::OutputForProcess(id, pct_change) => {
                let process = &mut game.state.processes[*id];
                process.output_modifier -= pct_change;
            },
            Effect::Feedstock(feedstock, pct_change) => {
                game.state.feedstocks[*feedstock] /= pct_change;
            },
            Effect::NPCRelationship(id, change) => {
                game.state.npcs[*id].relationship -= change;
            },
            Effect::ModifyIndustryByproducts(id, byproduct, mult) => {
                game.state.industries[*id].byproducts[*byproduct] /= mult;
            },
            Effect::ModifyIndustryResources(id, resource, mult) => {
                game.state.industries[*id].resources[*resource] /= mult;
            },
            Effect::ModifyEventProbability(id, change) => {
                game.event_pool.events[*id].prob_modifier -= change;
            },
            Effect::ModifyIndustryDemand(id, change) => {
                game.state.industries[*id].demand_modifier -= change;
            },
            Effect::DemandOutlookChange(output, mult) => {
                for region in &mut game.state.world.regions {
                    region.outlook -= (mult * region.demand()[*output]).round();
                }
            },
            Effect::IncomeOutlookChange(mult) => {
                for region in &mut game.state.world.regions {
                    region.outlook -= (mult * region.adjusted_income()).round();
                }
            },
            Effect::ProjectCostModifier(id, change) => {
                game.state.projects[*id].cost_modifier -= change;
            },
            Effect::ProtectLand(percent) => {
                game.state.protected_land -= percent/100.;
            }

            // Other effects aren't reversible
            _ => ()
        }
    }
}
