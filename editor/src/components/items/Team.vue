<template>
<li class="item" :key="item.id" :id="item.id" ref="root">
  <Flags :invalid="invalid" :questions="questions" />
  <button class="edit-toggle" @click="toggleEditing">{{ this.editing ? '⮪' : '✎'}}</button>
  <template v-if="editing">
    <div>
      <label>
        Name
        <Tip>The name of the team.</Tip>
      </label>
      <input class="title" type="text" placeholder="Name" v-model="localData.name" :class="flags('name')" />
    </div>
    <fieldset>
      <div>
        <label>
          Aspects
          <Tip>The aspects of this team.</Tip>
        </label>
        <select v-model="localData.aspects" :class="flags('output')" multiple>
          <option v-for="k in ASPECTS" :value="k">{{k}}</option>
        </select>
      </div>
      <div>
        <label>
          Establish Cost
          <Tip>PC cost to establish a new instance of this team.</Tip>
        </label>
        <input type="number" min="0" v-model="localData.establish_cost" :class="flags('establish_cost')" />
      </div>
      <div>
        <label>
          Train Cost
          <Tip>PC cost to train this team up one level.</Tip>
        </label>
        <input type="number" min="0" v-model="localData.train_cost" :class="flags('train_cost')" />
      </div>
      <div class="checkbox">
        <label :for="`${item.id}_default`">
          Default
          <Tip>Does a player start with this team?</Tip>
        </label>
        <input type="checkbox" :id="`${item.id}_default`" v-model="localData.default">
      </div>
      <div class="checkbox">
        <label :for="`${item.id}_locked`">
          Locked
          <Tip>Is this team available to the player at the start?</Tip>
        </label>
        <input type="checkbox" :id="`${item.id}_locked`" v-model="localData.locked">
      </div>
    </fieldset>
    <Image :image="localData.image" :dimensions="'640x420'" @update="saveData('image', $event)" />

    <Notes :notes="localData.notes" @blur="saveNotes" />

    <div class="additional-actions">
      <button @click="delete">Delete</button>
    </div>
  </template>

  <div v-else class="team-summary item-summary">
    <div class="item-meta">
      <div class="meta-pill split-pill" :class="flags('establish_cost')">
        <div>Establish Cost</div>
        <div>{{flags('establish_cost').invalid ? 'MISSING' : localData.establish_cost }}PC</div>
      </div>
      <div class="meta-pill split-pill" :class="flags('train_cost')">
        <div>Train Cost</div>
        <div>{{flags('train_cost').invalid ? 'MISSING' : localData.train_cost }}PC</div>
      </div>
      <div class="meta-pill" v-if="localData.default">Default</div>
      <div class="meta-pill" v-if="localData.locked" :class="flags('locked')">Locked{{flags('locked').invalid ? ' MISSING UNLOCKER' : ''}}</div>
      <div class="meta-pill" v-else-if="!localData.locked && flags('locked').invalid" :class="flags('locked')">UNLOCKABLE BUT NOT LOCKED</div>
      <template v-for="k in localData.aspects">
        <div class="meta-pill feature-pill"><div>{{k}}</div></div>
      </template>
    </div>
    <fieldset class="big-group">
      <div>
        <div class="item-summary-title" v-if="localData.name">{{localData.name}}</div>
        <div class="item-summary-title invalid" v-else>[MISSING NAME]</div>
      </div>
      <div class="item-summary-image" v-if="localData.image">
        <img class="image-preview" v-if="localData.image.image" :src="`/image/${localData.image.image}`"/>
        <div class="image-attribution">{{localData.image.attribution}}</div>
      </div>
    </fieldset>
    <div class="item-summary-notes" v-if="localData.notes" v-html="notesHtml"></div>
  </div>
</li>
</template>

<script>
import ItemMixin from './ItemMixin';
export default {
  mixins: [ItemMixin]
};
</script>

<style>
</style>
