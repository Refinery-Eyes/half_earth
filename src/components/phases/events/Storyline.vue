<template>
  <div class="narrative-line" ref="text" :class="{hide: !play}"></div>
</template>

<script>
const lines = {
  '2022': 'The first year after the revolution was relatively calm...',
  '2023': 'But then we were plagued with more wildfires than seen in living memory...',
  '2024': 'At the next planning session we could start to prepare.',
};

export default {
  props: ['year', 'play'],
  computed: {
    line() {
      return lines[this.year];
    }
  },
  watch: {
    play(val) {
      console.log(val);
      if (val) this.start();
    },
  },
  methods: {
    start() {
      console.log(this.line);
      setTimeout(() => {
        this.revealText(this.line, 1.5);
      }, 1000);
    },
    revealText(text, speed) {
      let revealed = '';
      speed = speed || 3.5;
      const chars = text.split('');
      return new Promise((resolve, reject) => {
        this.revealAnim = setInterval(() => {
          // Have to keep the revealed text
          // separate from innerText
          // b/c innerText will strip trailing spaces
          revealed += chars.shift();
          this.$refs.text.innerText = revealed;
          if (chars.length == 0) {
            clearInterval(this.revealAnim);
            this.revealAnim = null;
            resolve();
          }
        }, 100/speed);
      });
    },
  }
};
</script>

<style>
.narrative-line {
  position: absolute;
  bottom: 3em;
  left: 0;
  right: 0;
  padding: 1em;
  z-index: 300;
  text-align: center;
  font-family: "Andada Pro";
  font-style: italic;
  width: 480px;
}
.narrative-line.hide {
  display: none;
}
</style>
