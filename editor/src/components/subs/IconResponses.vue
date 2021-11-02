<template>
<div class="icon-responses">
  <label>
    Responses
    <button @click="addResponse()">+ Response</button>
  </label>
  <div class="field-group" v-for="(response, i) in localData">
    <div>
      <label>
        Required Aspects
        <button @click="addAspect(i)">+ Aspect</button>
      </label>
      <ul class="icon-responses-aspects">
        <li v-for="(aspect, j) in response.aspects" :key="j">
          <select v-model="response.aspects[j]">
            <option v-for="k in ASPECTS" :value="k">{{k}}</option>
          </select>
          <div class="subitem-actions">
            <button @click="() => deleteAspect(i, j)">X</button>
            <button v-if="j > 0" @click="() => moveAspect(i, j, j-1)">&lt;</button>
            <button v-if="j < response.aspects.length - 1" @click="() => moveAspect(i, j, j+1)">&gt;</button>
          </div>
        </li>
      </ul>
    </div>
    <Effects :effects="response.effects" @update="saveResponseEffects(i, $event)" />
  </div>
</div>
</template>

<script>
import uuid from '../../uuid';
import Tip from '../Tip.vue';
import Effects from './Effects.vue';

export default {
  props: ['responses'],
  components: {
    Tip, Effects
  },
  data() {
    return {
      localData: this.responses || []
    };
  },
  methods: {
    update() {
      this.$emit('update', this.localData);
    },
    saveResponseEffects(i, effects) {
      this.localData[i].effects = effects;
      this.update();
    },
    // https://stackoverflow.com/a/6470794
    moveAspect(i, fromIdx, toIdx) {
      let item = this.localData[i].aspects[fromIdx];
      this.localData[i].aspects.splice(fromIdx, 1);
      this.localData[i].aspects.splice(toIdx, 0, item);
      this.update();
    },
    deleteAspect(i, j) {
      this.localData[i].aspects.splice(j, 1);
      this.update();
    },
    addAspect(i) {
      this.localData[i].aspects.push(null);
      this.update();
    },
    addResponse() {
      this.localData.push({
        id: uuid(),
        aspects: [],
        effects: [],
      });
      this.update();
    }
  }
}
</script>

<style>
.icon-responses .field-group {
  display: flex;
}
.icon-responses .field-group > div {
  flex: 1;
}
.icon-responses .effects {
  flex: 1;
  border: none;
  padding: 0;
  margin: 0 0 0 0.5em;
}
.icon-responses-aspects {
  display: flex;
}
.icon-responses-aspects .subitem-actions {
  display: flex;
}
</style>
