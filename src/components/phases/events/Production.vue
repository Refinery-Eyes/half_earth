<template>
<div class="production">
  <div class="production--processes" v-if="!showSurplus">
    <div class="production--process" v-for="process in processes">
      <div class="production--process-name">{{process.name}}</div>
      <div class="production--process-amounts">
        <div>{{process.amount}} {{icons[process.output]}}</div>
        <div>{{process.emissions}} {{icons['emissions']}}</div>
      </div>
    </div>
  </div>
  <div class="production--demand">
    <div v-for="v, k in demand">
      {{icons[k]}}{{v}}
    </div>
  </div>
  <div class="production--surplus" v-if="showSurplus">
    <h2>Surplus</h2>
    <div>
      <div>+{{surplus.energy}}<img src="/assets/icons/pips/power.png"></div>
      <div>+{{surplus.food}}<img src="/assets/icons/pips/food.png"></div>
    </div>
    <button @click="$emit('done')">Ok</button>
  </div>
</div>
</template>

<script>
import state from '/src/state';
import anime from 'animejs/lib/anime.es.js';

// TODO iterate through industries and their emissions

const outputDemandUnits = {
  fuel: 1e-9/1e3,            // per 1000 TWh
  electricity: 1e-9/1e3,     // per 1000 TWh
  plant_calories: 1e-9/2e4,  // per 20000 Tcals
  animal_calories: 1e-9/2e4, // per 20000 Tcals
};

const convertOutput = {
  'Fuel': 'fuel',
  'Electricity': 'electricity',
  'PlantCalories': 'plant_calories',
  'AnimalCalories': 'animal_calories',
}

export default {
  created() {
    this.icons = {
      'fuel': '⛽',
      'electricity': '⚡',
      'plant_calories': '🌾',
      'animal_calories': '🥩',
      'emissions': '☁️',
    };
  },
  data() {
    let processes = state.gameState.processes.map((p, i) => {
      let baseAmount = state.gameState.produced_by_process[i];
      let amount = baseAmount * outputDemandUnits[convertOutput[p.output]];
      amount = amount > 0 ? Math.max(Math.round(amount), 1) : 0;

      let emissions = baseAmount * (p.byproducts.co2 + p.byproducts.ch4 * 36 + p.byproducts.n2o * 298);
      emissions *= 1e-15; // Gt CO2eq
      emissions = emissions > 0 ? Math.max(Math.round(emissions), 1) : 0;
      let data = {
        emissions,
        amount, ...p
      };
      data.output = convertOutput[p.output];
      return data;
    }).filter((p) => p.amount > 0);
    let demand = Object.keys(state.gameState.output_demand).reduce((acc, k) => {
        acc[k] = Math.round(state.gameState.output_demand[k] * outputDemandUnits[k]);
        return acc;
      }, {});
    demand['emissions'] = 0;
    return {
      demand,
      processes,
      showSurplus: false,
      surplus: {
        food: 0,
        energy: 0,
      }
    }
  },
  mounted() {
    let timeline = anime.timeline({
      targets: this.demand,
      round: 1,
      easing: 'linear',
      duration: 500,
      complete: () => {
        this.showSurplus = true;
        this.surplus.food -= Math.min(0, this.demand.plant_calories);
        this.surplus.food -= Math.min(0, this.demand.animal_calories);
        this.surplus.energy -= Math.min(0, this.demand.electricity);
        this.surplus.energy -= Math.min(0, this.demand.fuel);
        state.tokens.food += this.surplus.food;
        state.tokens.energy += this.surplus.energy;
      }
    });
    let newDemand = {...this.demand};
    this.processes.forEach((p) => {
      newDemand[p.output] -= p.amount;
      newDemand['emissions'] += p.emissions;
      let demandTarget = {...newDemand};
      timeline.add({
        ...demandTarget,
        complete: () => {
          this.processes.shift();
        }
      }, '+=200');
    });
  },
  methods: {
  },
}
</script>

<style>
/* TODO temp */
.production {
  position: absolute;
  left: 1em;
  right: 1em;
  top: 1em;
  bottom: 1em;
  z-index: 100;
  background: #eee;
  border: 1px solid black;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.production--processes {
  position: absolute;
  top: 2em;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  overflow: hidden;
}
.production--processes .production--process:first-child {
  background: #888;
}
.production--demand {
  display: flex;
  justify-content: space-around;
  padding: 0.5em 1em;
  position: relative;
  z-index: 1;
  background: #111;
  color: #fff;
  border-radius: 0.2em;
}

.production--process {
  text-align: center;
  padding: 1em;
  background: #eee;
  border-radius: 0.5em;
  border: 1px solid;
  margin: 1em;
}

.production--surplus h2 {
  text-align: center;
}
.production--surplus > div {
  display: flex;
  justify-content: space-around;
}
.production--process-amounts {
  display: flex;
  justify-content: space-around;
}
.production--surplus img {
  width: 22px;
  vertical-align: middle;
}
</style>
