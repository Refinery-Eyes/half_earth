use serde::Serialize;
use crate::events::Aspect;
use wasm_bindgen::prelude::*;


#[derive(Serialize)]
pub struct Team {
    pub id: usize,
    pub name: &'static str,
    pub locked: bool,
    pub default: bool,
    pub aspects: Vec<Aspect>,
    pub establish_cost: usize,
    pub train_cost: usize,
}

#[wasm_bindgen]
#[derive(Serialize)]
pub enum TeamStatus {
    Ready,
    Injured,
    Lost,
    Training,
    Deployed,
    DeployedAtRisk,
    DeployedInjured,
}

#[derive(Serialize)]
pub struct TeamInstance {
    pub id: usize,
    pub team_id: usize,
    pub status: TeamStatus,
    pub level: usize,
    pub xp: usize,
}

impl TeamInstance {
    pub fn gain_xp(&mut self) {
        self.xp += 1;
        if self.xp >= 3 {
            self.level += 1;
            self.xp = 0;
        }
    }
}
