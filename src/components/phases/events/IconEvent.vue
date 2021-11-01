<template>
<div class="icon-event">
  <h3>{{event.name}}</h3>
  <h4>{{region.name}}</h4>
  <div class="icon-event--pips">
    <img :src="`/assets/src/icons/pips/out/${event.icon}.png`" />
  </div>
  <div class="icon-event--slots">
    <div class="icon-event--slot" @click="activeSlot = 0"></div>
    <div class="icon-event--slot" @click="activeSlot = 1"></div>
    <div class="icon-event--slot" @click="activeSlot = 2"></div>
  </div>
  <ul class="icon-event--effects">
    <template v-for="desc in effectDescs">
      <li v-html="desc"></li>
    </template>
  </ul>
  <div class="icon-event--slot-selection" v-if="activeSlot !== null">
    TODO choose from cards
  </div>
  <button @click="submit">Submit</button>
</div>
</template>

<script>
import {describeEffect} from '/src/effects';

export default {
  props: ['event', 'region'],
  data() {
    return {
      activeSlot: null
    }
  },
  computed: {
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
    submit() {
      // TODO
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
}
.icon-event--slot:hover {
  background: #202020;
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
</style>
