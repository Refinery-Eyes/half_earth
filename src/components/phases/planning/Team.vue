<template>
<div class="active-team">
  <div class="active-team--aspects">
    <template v-for="aspect in aspects">
      <template v-for="i in team.level">
        <img :src="`/assets/icons/pips/${pips[aspect]}.png`">
      </template>
    </template>
  </div>
  <div class="active-team--text-status">
    {{team.status}}
  </div>
  <div class="active-team--status">
    <div class="active-team--health"><img :src="health" /></div>
    <div class="active-team--xp">
      <div class="active-team--xp-point" v-for="n in 3" :class="{filled: n <= team.xp}"></div>
    </div>
    <div class="active-team--level">{{team.level}}</div>
  </div>
  <button @click="train" v-if="team.status == 'Ready' && isPlanning">
    Train {{trainCost}}<img class="pip" src="/assets/icons/pips/political_capital.png">
  </button>
</div>
</template>

<script>
import game from '/src/game';
import state from '/src/state';

const aspectPips = {
  'Flood': 'flood',
  'Fire': 'wildfires',
  'Heat': 'heatwave',
  'Food': 'food',
  'Energy': 'power',
  'Control': 'resistance',
  'Force': 'attacks',
  'Health': 'disease',
  'Construction': 'initiative',
};

export default {
  props: ['team', 'isPlanning'],
  created() {
    this.pips = aspectPips;
  },
  computed: {
    health() {
      switch (this.team.status) {
        case 'Ready':
          return '/assets/placeholders/ready.svg';
        case 'Injured':
          return '/assets/placeholders/injured.svg';
        case 'Lost':
          return '/assets/placeholders/dead.svg';
        case 'Training':
          return '/assets/placeholders/training.svg';
      }
    },
    aspects() {
      return state.gameState.teams[this.team.team_id].aspects;
    },
    trainCost() {
      return state.gameState.teams[this.team.team_id].train_cost;
    }
  },
  methods: {
    train() {
      let team = state.gameState.teams[this.team.team_id];
      if (state.gameState.political_capital >= team.train_cost) {
        game.changePoliticalCapital(-team.train_cost);
        game.trainTeam(this.team);
      }
    }
  }
}
</script>

<style>
.active-team {
  background: #222;
  padding: 0.5em;
  border-radius: 0.3em;
  text-align: center;
  color: #fff;
  width: 180px;
}
.active-team img {
  width: 18px;
}

.active-team--status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
}

.active-team--xp-point {
  width: 10px;
  height: 4px;
  background: #aaa;
  display: inline-block;
  margin: 0 1px;
}
</style>
