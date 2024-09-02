<template>
  <div id="app">
    <nav class="navbar navbar-light bg-dark mt-3">
      <div class="container">
        <a class="navbar-brand" href="/">
          <img
            src="https://panatrade.id/wp-content/uploads/2023/12/cropped-01-PNT-32x32.png"
            alt=""
            width="30"
            height="24"
          />
          <label> &nbsp;Portal Micro Application</label>
        </a>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  created() {
    const sessionExists =
      localStorage.getItem("username") && localStorage.getItem("password");
    if (!sessionExists) {
      this.$router.push("/login");
    } else {
      this.$router.push("/dashboard");
    }
  },
};
</script>

<style>
body {
  background-color: black !important;
  max-height: 100%;
}
.container {
  background: linear-gradient(
    90deg,
    rgba(2, 0, 36, 1) 0%,
    rgba(108, 108, 201, 1) 50%,
    rgba(0, 212, 255, 1) 100%
  );
  height: 100%;
  position: fixed;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #ebedf0;
  font-size: 12px;
  background-color: #000000 !important;
  max-height: 100%;
}

label {
  color: white;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 5px solid #f1a791;
  border-radius: 50%;
  display: inline-block;
  box-sizing: border-box;
  position: relative;
  animation: pulse 1s linear infinite;
  margin: 20px 0;
  text-align: center;
}
.spinner:after {
  content: "";
  position: absolute;
  width: 48px;
  height: 48px;
  border: 5px solid #fc420a;
  border-radius: 50%;
  display: inline-block;
  box-sizing: border-box;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: scaleUp 1s linear infinite;
  text-align: center;
}

@keyframes scaleUp {
  0% {
    transform: translate(-50%, -50%) scale(0);
  }
  60%,
  100% {
    transform: translate(-50%, -50%) scale(1);
  }
}
@keyframes pulse {
  0%,
  60%,
  100% {
    transform: scale(1);
  }
  80% {
    transform: scale(1.2);
  }
}
a:link {
  text-decoration: none;
}
a:visited {
  text-decoration: none;
}
a:hover {
  text-decoration: none;
}
a:active {
  text-decoration: none;
}
</style>
