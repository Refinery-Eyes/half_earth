<template>
<Hud />
<div id="event-stream">
  <Production v-if="!hideProduction" @done="hideProduction = true"/>
  <div id="event-stream--year">
    {{year}}
  </div>
  <IconEvent v-if="focusedIconEvent" :event="focusedIconEvent.event" :region="focusedIconEvent.region"
    @close="focusedIconEvent = null"
    @done="submitIconEvent"
    />
  <Globe id="events-globe" ref="globe" />
  <Project v-if="completedProjects.length > 0" :id="completedProjects[0]" @click="() => completedProjects.shift()"/>
  <Dialogue v-if="event && predialogue" :dialogue="event.dialogue" @done="nextEvent" @select="selectChoice" />
  <Event v-else-if="event && !predialogue" :event="event" @done="nextEvent" @select="selectChoice" />
  <div id="event-stream--toasts">
    <div class="toast" v-for="toast, i in toasts" :style="{opacity: (i+1)/(toasts.length+1)}">
      <div class="toast--body"><img :src="`/assets/icons/pips/${toast.icon}.png`"> {{toast.desc}}</div>
    </div>
  </div>
  <button id="next-year-button" v-if="hideProduction && !yearEnded" @click="endYear">Next Year</button>
</div>
</template>

<script>
import game from '/src/game';
import state from '/src/state';
import {sign} from 'lib/util';
import Event from './Event.vue';
import Project from './Project.vue';
import Production from './Production.vue';
import IconEvent from './IconEvent.vue';
import Hud from 'components/Hud.vue';
import Globe from 'components/Globe.vue'
import EventsMixin from 'components/EventsMixin';
import regionsToTiles from '/assets/surface/regions_to_tiles.json';
import iconEvents from '/assets/content/icon_events.json';

function randChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export default {
  mixins: [EventsMixin],
  data() {
    let events = game.rollWorldStartEvents();
    return {
      events,
      time: 0,
      toasts: [],
      yearEnded: false,
      predialogue: true,
      hideProduction: true,
      focusedIconEvent: null,
      year: state.gameState.world.year,
      completedProjects: [],
      iconEvents: [],
      resolvedIconEvents: [],
      iconEventsData: [],
    };
  },
  components: {
    Hud,
    Globe,
    Event,
    Project,
    Production,
    IconEvent,
  },
  mounted() {
    this.start();
  },
  activated() {
    this.start();
  },
  methods: {
    start() {
      // Show any world start events
      if (this.hasEvent) {
        this.predialogue = true;
        this.showEvent();
      } else {
        this.predialogue = false;
      }

      // Cache starting values for report
      this.startYear = state.gameState.world.year;
      state.cycleStartState = {
        year: this.startYear,
        extinctionRate: state.gameState.world.extinction_rate,
        contentedness: state.gameState.contentedness,
        temperature: state.gameState.world.temperature,
      };

      if (!this.globe) {
        this.$refs.globe.onReady = (globe) => {
          this.globe = globe;
          this.globe.onIconSelect((data) => {
            this.focusedIconEvent = data;
          });
          this.nextYear();
        };
      } else {
        this.nextYear();
      }
    },
    nextYear() {
      this.yearEnded = false;
      this.completedProjects = game.step();
      this.year = state.gameState.world.year;

      this.hideProduction = false;
      this.rollEvent();

      this.iconEvents = game.rollIconEvents();
      this.iconEventsData = [];
      this.resolvedIconEvents = [];
      this.iconEvents.forEach(([eventId, regionId], id) => {
        let icon = this.showEventOnGlobe(id, eventId, regionId);
        this.iconEventsData.push(icon);
      });
    },
    endYear() {
      this.yearEnded = true;
      // Resolve unresolved icon events
      this.iconEvents.forEach(([eventId, regionId], id) => {
        if (!this.resolvedIconEvents.includes(id)) {
          let icon = this.iconEventsData[id];
          let effects = {
            outlook: -icon.event.intensity - 1,
            politicalCapital: 0,
          };
          // TODO if malthusian is among allies
          let hasMalthusian = false;
          if (hasMalthusian && (icon.region.income == 'Low' || icon.region.income == 'LowerMiddle')) {
            this.politicalCapital = 5;
          }

          this.removeIcon(icon, effects);

          if (effects.politicalCapital !== 0) {
            game.changePoliticalCapital(effects.politicalCapital);
          }
          game.changeLocalOutlook(effects.outlook, icon.region.id);
        }
      });

      let prevTeams = [...state.gameState.active_teams];
      game.stepTeams();

      let changedTeams = prevTeams.filter((t, i) => t.status !== state.gameState.active_teams[i].status);
      console.log('Changed teams:');
      console.log(changedTeams);

      setTimeout(() => {
        this.nextYear();
      }, 3500);
    },
    submitIconEvent(effects) {
      let id = this.focusedIconEvent.id;
      this.removeIcon(this.focusedIconEvent, effects);
      this.resolvedIconEvents.push(id);
    },
    rollEvent() {
      // Go to report phase
      if (state.gameState.world.year > this.startYear
        && state.gameState.world.year % 5 == 0) {
        state.phase = 'REPORT';
        return;
      }

      this.events = game.rollWorldEvents();
      console.log('Rolled world events:');
      console.log(this.events);
      this.applyEmissions();

      if (this.hasEvent) {
        this.showEvent();
      } else {
        this.nextYear();
      }
    },
    afterEvents() {
      // TODO
      /* this.predialogue = false; */
      /* this.nextYear(); */
    },
    applyEmissions() {
      let world = state.gameState.world;
      let emissions = {
        // Hector separates out FFI and LUC emissions
        // but we lump them together
        // Units: <https://github.com/JGCRI/hector/wiki/Hector-Units>
        'ffi_emissions': world.co2_emissions * 12/44 * 1e-15, // Pg C/y
        'CH4_emissions': world.ch4_emissions * 1e-12, // Tg/y
        'N2O_emissions': world.n2o_emissions * 1e-12, // Tg/y
      };
      console.log('Applying emissions:');
      console.log(emissions);
      this.globe.addEmissionsThenUpdate(emissions).then((tgav) => {
        game.setTgav(tgav);
      });
    },
    showEventOnGlobe(id, eventId, regionId) {
      let ev = iconEvents[eventId];
      if (this.globe && regionId !== undefined && regionId !== null) {
        // TODO distinguish inland vs coastal events
        let region = state.gameState.world.regions[regionId];
        let tiles = regionsToTiles[region.name];
        let hexIdx = randChoice(tiles.inland.concat(tiles.coasts));
        // let label = sign(ev.effect.value);
        let mesh = this.globe.showIcon(ev.icon, hexIdx, {
          id,
          event: ev,
          region,
        });
        this.toasts.push({
          icon: ev.icon,
          desc: `${ev.name} in ${region.name}`
        });
        if (this.toasts.length > 3) {
          this.toasts.shift();
        }
        return {hexIdx, mesh, region, event: ev};
      }
    },
    removeIcon(eventData, effects) {
      let mesh = eventData.mesh;
      mesh.parent.remove(mesh);
      mesh.geometry.dispose();
      mesh.material.dispose();
      this.focusedIconEvent = null;

      let outlook = Math.abs(effects.outlook) - 1;
      this.globe.pingIcon('discontent', eventData.hexIdx);
      let outlookInterval = setInterval(() => {
        if (outlook <= 0) {
          clearInterval(outlookInterval);
        } else {
          outlook--;
          this.globe.pingIcon('discontent', eventData.hexIdx);
        }
      }, 250);

      let pc = effects.politicalCapital - 1;
      if (pc >= 0) {
        setTimeout(() => {
          this.globe.pingIcon('political_capital', eventData.hexIdx);
          let pcInterval = setInterval(() => {
            if (pc <= 0) {
              clearInterval(pcInterval);
            } else {
              pc--;
              this.globe.pingIcon('political_capital', eventData.hexIdx);
            }
          }, 250);
        }, 500);
      }
    }
  },
}
</script>

<style>
#events-globe {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
}

#event-stream--year {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 2;
  font-size: 1.5em;
  padding: 0.4em;
  font-family: "Andada Pro";
}

#event-stream--toasts {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 1em;
  text-align: center;
  font-size: 0.8em;
}
.toast--body {
  display: inline-block;
  padding: 0.1em 0.25em;
  border-radius: 0.2em;
  background: rgba(20,20,20,0.9);
  color: #fff;
  border: 1px solid black;
  text-align: center;
  margin: 0.15em 0;
  line-height: 1.7;
}
.toast img {
  height: 20px;
  vertical-align: middle;
}

#event-stream .dialogue {
  background: rgba(255,255,255,0.25);
}

#next-year-button {
  position: absolute;
  bottom: 1em;
  left: 50%;
  transform: translate(-50%, 0);
}
</style>
