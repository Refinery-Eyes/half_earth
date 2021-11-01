<template>
<div class="planning--page">
  <header>
    <img class="back" @click="back" src="/assets/icons/back.svg">
    <button v-if="!showEstablishTeams" @click="showEstablishTeams = true">Establish New Team</button>
  </header>
  <div class="planning--team">
    <div class="teams" v-if="!showEstablishTeams">
      <div v-if="state.gameState.active_teams.length === 0">You have no teams.</div>
      <template v-else>
        <template v-for="team in state.gameState.active_teams">
          <Team :team="team" />
        </template>
      </template>
    </div>
    <div class="establish-teams" v-else>
        <div class="team-template" v-for="team in establishTeams">
          <h3>{{team.name}}</h3>
          <div class="team-template--aspects">
            <template v-for="aspect in team.aspects">
              <img :src="`/assets/icons/pips/${pips[aspect]}.png`">
            </template>
          </div>
          <img :src="`/assets/content/images/${teamImage(team).fname}`">
          <button @click="establishTeam(team)">
            Establish<br />
            {{team.establish_cost}}<img class="pip" src="/assets/icons/pips/political_capital.png">
          </button>
        </div>
    </div>
  </div>
</div>
</template>

<script>
import game from '/src/game';
import state from '/src/state';
import Team from './Team.vue';
import TEAMS from '/assets/content/teams.json';

const aspectPips = {
  'Flood': 'flood',
  'Fire': 'wildfires',
  'Control': 'attacks',
  'Health': 'disease',
  'Construction': 'initiative',
};

export default {
  created() {
    this.pips = aspectPips;
  },
  data() {
    return {
      state,
      showEstablishTeams: false,
      establishTeams: state.gameState.teams.filter((t) => !t.locked),
    }
  },
  components: {
    Team
  },
  methods: {
    back() {
      if (this.showEstablishTeams) {
        this.showEstablishTeams = false;
      } else {
        this.$emit('close');
      }
    },
    establishTeam(team) {
      if (state.gameState.political_capital >= team.establish_cost) {
        game.changePoliticalCapital(-team.establish_cost);
        game.establishTeam(team);
      }
    },
    trainTeam() {
      // TODO
    },
    teamImage(t) {
      return TEAMS[t.id].image;
    }
  }
}
</script>

<style>
.establish-teams {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  padding: 1em;
}
.team-template {
  background: #222;
  color: #fff;
  border-radius: 0.2em;
  padding: 1em;
  text-align: center;
  max-width: 48%;
}
.team-template h3 {
  font-weight: normal;
  font-family: 'Andada Pro';
  border-bottom: 1px solid #fff;
  margin: 0;
}

.team-template--aspects {
  margin: 0.5em 0 1em;
}
.team-template--aspects img {
  width: 24px;
}
</style>
