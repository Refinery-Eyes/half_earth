<template>
  <div class="narrative-area" :class="{hide: !play}">
    <div class="narrative-line" ref="text"></div>
  </div>
</template>

<script>
const lines = {
  '2022': 'The first year after the revolution was relatively calm...',
  '2023': 'But then we were plagued with more <img src="/assets/icons/pips/wildfires.png" /><span class="highlight">wildfires</span><img class="narrative-floater" ref="floater" src="/assets/icons/pips/discontent.png" /> than seen in living memory...',
  '2024': 'At the next planning session we could start to prepare.',
};

function extractChars(el) {
	let chars = [];
  el.childNodes.forEach((n) => {
    switch (n.nodeType) {
      case Node.TEXT_NODE:
        chars = chars.concat(n.textContent.split(''))
        return;
      case Node.ELEMENT_NODE:
        if (n.childNodes.length === 0) {
          chars.push(n);
        } else {
          let node = n.cloneNode();
          node.innerHTML = '';
          chars.push({
            node,
            chars: extractChars(n)
          });
        }
        return;
    }
  });
  return chars;
}

function revealChars(parentEl, chars, onRevealFn, speed) {
  speed = speed || 3.5;
  let currentNode = null;
  return new Promise((resolve, reject) => {
    let revealAnim = setInterval(() => {
   		let char = chars.shift();
      if (char == '<END>') {
        currentNode = null;
      } else if (typeof char == 'string') {
      	if (!currentNode || currentNode.nodeType == Node.TEXT_NODE) {
        	currentNode = document.createTextNode('');
          parentEl.appendChild(currentNode);
        }
        currentNode.textContent += char;
      } else if (char instanceof HTMLElement){
      	parentEl.appendChild(char);
      } else {
      	currentNode = char.node;
        parentEl.appendChild(currentNode);
        chars = char.chars.concat(['<END>']).concat(chars);
      }
      if (onRevealFn) onRevealFn(char);
      if (chars.length == 0) {
        clearInterval(revealAnim);
        resolve();
      }
    }, 100/speed);
  });
}

export default {
  props: ['year', 'play'],
  data() {
    return {
      showIcons: false,
    }
  },
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
      setTimeout(() => {
        this.$refs.text.innerHTML = '';
        let el = document.createElement('div');
        el.innerHTML = this.line;
        let chars = extractChars(el);
        revealChars(this.$refs.text, chars, (char) => {
          if (char instanceof HTMLElement && char.classList.contains('narrative-floater')) {
            let float = () => {
              let top = parseInt(char.style.top || 0);
              top -= 1;
              char.style.top = `${top}px`;
              requestAnimationFrame(float);
            };
            float();
          }
        }, 1.5);
      }, 1000);
    },
  }
};
</script>

<style>
.narrative-area {
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
.narrative-area img {
  width: 16px;
  height: 16px;
  vertical-align: middle;
}
.narrative-area.hide {
  display: none;
}
.narrative-floater {
  top: 0;
  right: 150px;
  position: absolute;
}
.highlight {
  border-bottom: 1px solid red;
}
</style>
