<template>
<div class="icon-event">
  <div class="icon-event--close" @click="$emit('close')">Close</div>
  <h3>{{event.name}}</h3>
  <h4>{{region.name}}{{hasMalthusian ? `| ${region.income}` : ''}}</h4>
  <div class="icon-event--pips">
    <img :src="pip" v-for="(_, i) in event.intensity" :class="{filled: i < filledPips.length}"/>
  </div>
  <div class="icon-event--slots">
    <div class="icon-event--slot" v-for="(_, i) in 3" @click="activeSlot = i" :class="{active: activeSlot == i}">
      <div class="risky" v-if="assigned[i] !== null && risky(assigned[i])">⚠️</div>
      <Team v-if="assigned[i] !== null" :team="assigned[i]" :isPlanning="false" @click="removeTeam(i)" />
    </div>
  </div>
  <ul class="icon-event--effects">
    <li>{{outlookEffect}} <img src="/assets/icons/contentedness.png"> locally</li>
    <li v-if="politicalCapital > 0">{{politicalCapital}} <img src="/assets/icons/pips/political_capital.png"></li>
    <template v-for="desc in effectDescs">
      <li v-html="desc"></li>
    </template>
  </ul>
  <div class="icon-event--slot-selection" v-if="activeSlot !== null">
    <div class="team-wrapper" v-for="teams in teamGroups">
      <Team :team="teams[0]" :isPlanning="false" @click="selectTeam(teams[0])" />
      <div class="minicard--count" v-if="teams.length > 1">x{{teams.length}}</div>
    </div>
    <div>
      <template v-for="amount, token in state.tokens">
        <div class="token">
          <img :src="tokenPip(token)">
          <div class="minicard--count">x{{amount}}</div>
        </div>
      </template>
    </div>
  </div>
  <button @click="submit" v-if="filledSlots.length > 0">Submit</button>
</div>
</template>

<script>
import game from '/src/game';
import state from '/src/state';
import Team from 'components/phases/planning/Team.vue';
import {describeEffect} from '/src/effects';

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

const authAspects = ['Control', 'Force'];

export default {
  props: ['event', 'region'],
  components: {
    Team
  },
  data() {
    return {
      state,
      activeSlot: null,
      assigned: [null, null, null],
    }
  },
  computed: {
    availableTeams() {
      return state.gameState.active_teams.filter((t) => (t.status == 'Ready' || t.status == 'Injured') && !this.assigned.includes(t));
    },
    teamGroups() {
      let groups = {};
      this.availableTeams.forEach((team) => {
        let id = `${team.team_id}__${team.status}__${team.xp}`;
        if (!(id in groups)) groups[id] = [];
        groups[id].push(team);
      });
      return groups;
    },
    outlookEffect() {
      return Math.min(-1, -this.event.intensity - 1 + this.filledPips.length);
    },
    politicalCapital() {
      let authPoints = this.assigned.filter((c) => {
        if (c == null) return false;
        let aspects = state.gameState.teams[c.team_id].aspects;
        return !aspects.includes(this.event.aspect) && this.hasAuthoritarian && authAspects.some((a) => aspects.includes(a));
      }).length;
      return ((2*Math.min(this.filledPips.length, this.event.intensity)) ** 2) + authPoints;
    },
    filledSlots() {
      return this.assigned.filter((a) => a !== null);
    },
    hasMalthusian() {
      // TODO if malthusian is among allies
      console.log(state.gameState.npcs)
    },
    hasAuthoritarian() {
      // TODO if authoritarian is among allies
      console.log(state.gameState.npcs)
    },
    filledPips() {
      return this.assigned.filter((c) => c !== null);
      /* return this.assigned.filter((c) => { */
      /*   if (c == null) return false; */
      /*   let aspects = state.gameState.teams[c.team_id].aspects; */
      /*   return aspects.includes(this.event.aspect) */
      /*      || (this.hasAuthoritarian && authAspects.some((a) => aspects.includes(a))); */
      /* }); */
    },
    pip() {
      return `/assets/src/icons/pips/out/${aspectPips[this.event.aspect]}.png`;
    },
    effectDescs() {
      let descs = this.event.effects
        .map((ev) => {
          let desc = describeEffect(ev);
          if (desc) {
            return `${ev.random ? '🎲 ' : ''}${desc}`;
          }
        })
        .filter((desc) => desc !== undefined);
      return descs.filter((item, i) => {
        return descs.indexOf(item) == i;
      });
    },
  },
  methods: {
    tokenPip(t) {
      let token = t[0].toUpperCase() + t.substring(1);
      return `/assets/src/icons/pips/out/${aspectPips[token]}.png`;
    },
    risky(team) {
      let aspects = state.gameState.teams[team.team_id].aspects;
      let authFilled = this.hasAuthoritarian && authAspects.some((a) => aspects.includes(a));
      return !(aspects.includes(this.event.aspect) || authFilled);
    },
    selectTeam(team) {
      if (this.activeSlot !== null) {
        this.assigned[this.activeSlot] = team;
      }
    },
    removeTeam(i) {
      this.assigned[i] = null;
    },
    submit() {
      this.assigned.forEach((t) => {
        if (t !== null) {
          let status = game.TeamStatus.Deployed;
          if (t.status == 'Injured') {
            status = game.TeamStatus.DeployedInjured;
          } else if (this.filledPips.length < this.event.intensity || this.risky(t)) {
            status = game.TeamStatus.DeployedAtRisk;
          }
          game.setTeamStatus(t, status);
        }
      });
      // Apply
      if (this.politicalCapital !== 0) {
        game.changePoliticalCapital(this.politicalCapital);
      }
      game.changeLocalOutlook(this.outlookEffect, this.region.id)
      this.$emit('done', {
        outlook: this.outlookEffect,
        politicalCapital: this.politicalCapital,
      });
    },
  }
}
</script>

<style>
.icon-event {
  position: absolute;
  top: 1em;
  right: 1em;
  bottom: 1em;
  left: 1em;
  background: #111;
  color: #fff;
  border-radius: 0.3em;
  padding: 1em;
  z-index: 200;
  text-align: center;
}
.icon-event--close {
  position: absolute;
  right: 0.5em;
  top: 0.5em;
}

.icon-event img {
  width: 24px;
}
.icon-event h3 {
  font-weight: normal;
  border-bottom: 1px solid #fff;
  margin-bottom: 0;
  font-family: 'Andada Pro';
}
.icon-event h4 {
  font-weight: normal;
  font-family: 'Andada Pro';
  margin-top: 0;
}

.icon-event--pips img {
  opacity: 0.5;
}
.icon-event--pips img.filled {
  opacity: 1;
}

.icon-event--slot {
  display: inline-block;
  border: 1px solid #777;
  border-radius: 0.2em;
  width: 64px;
  height: 98px;
  margin: 0 0.5em;
  box-shadow: inset 2px 2px 0 rgb(0 0 0 / 80%);
  cursor: pointer;
  background: #181818;
  vertical-align: top;
  position: relative;
}
.icon-event--slot:hover {
  background: #202020;
}
.icon-event--slot.active {
  border-color: #43CC70;
}

.icon-event--slot .risky {
  position: absolute;
  right: 0;
  top: 0;
}

.icon-event--effects {
  margin: 1em 0;
}
.icon-event--effects img {
  width: 16px;
  vertical-align: middle;
}

.icon-event--slot-selection {
  margin: 1em 0;
  border-radius: 0.2em;
  border: 1px solid #fff;
  padding: 1em;
}
.icon-event .active-team {
  width: 70px;
  cursor: pointer;
  display: inline-block;
}
.team-wrapper {
  display: inline-block;
  margin: 0 0.25em 0.25em 0.25em;
  position: relative;
}
.icon-event .active-team:hover {
  background: #2a2a2a;
}
.icon-event .active-team .active-team--level {
  display: none;
}
.icon-event .active-team .active-team--status {
  display: block;
}

.icon-event--slot .active-team {
  width: 56px;
  height: 92px;
  margin: 2px 0 0 0;
}
.icon-event--slot .active-team--text-status {
  display: none;
}

.token {
  background: #222;
  padding: 0.5em;
  border-radius: 0.3em;
  text-align: center;
  color: #fff;
  width: 70px;
  display: inline-block;
  margin: 0 0.25em 0.25em 0.25em;
  cursor: pointer;
  position: relative;
}

.minicard--count {
  position: absolute;
  top: 0em;
  text-shadow: 1px 1px 0px black;
  right: 0em;
  transform: translate(25%, -25%);
  font-size: 0.75em;
  background: #222;
  padding: 0.2em;
  border: 1px solid #888;
  border-radius: 2em;
}
</style>
