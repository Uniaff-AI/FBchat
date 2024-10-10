<template>
  <div id="app">
    <header>
      <h1> Website Title</h1>
    </header>
    <main>
      <p>This is the main content of the website. The chat widget should appear in the bottom right corner.</p>
    </main>
    <ChatbotWidget />
  </div>
</template>

<script>
import ChatbotWidget from './components/ChatbotWidget.vue'

export default {
  name: 'App',
  components: {
    ChatbotWidget
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: #110f0f;
  color: #171313;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: #4CAF50;
  color: white;
  padding: 1rem;
  text-align: center;
}

main {
  flex-grow: 1;
  padding: 2rem;
  text-align: center;
  background-color: rgb(32, 29, 29);
  margin: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: white
}
</style>