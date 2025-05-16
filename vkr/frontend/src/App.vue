<template>
  <div class="app">
    <Header />
    
    <main>
      <HomeHero v-if="$route.path === '/'" />
      <router-view />
    </main>
    
    <Footer />
  </div>
</template>

<script>
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';
import HomeHero from './components/HomeHero.vue';

export default {
  name: 'App',
  components: {
    Header,
    Footer,
    HomeHero
  }
}
</script>

<style>

:root {
  --primary-color: #7950c1;
  --secondary-color: #ff7b54;
  --text-color: #333;
  --light-bg: #ffffff;
  --gray-bg: #f5f5f5;
  --border-radius: 8px;
  --box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', Arial, sans-serif;
  color: var(--text-color);
  line-height: 1.6;
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background-color: var(--light-bg);
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

main {
  flex: 1;
  width: 100%;
  background: linear-gradient(135deg, #EDE7F6 0%, #E3F2FD 100%);
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  background-color: var(--secondary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn:hover {
  background-color: #ff6a40;
}

.card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 20px;
}

@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 10px;
  }
}
</style>