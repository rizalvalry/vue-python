<template>
  <div class="container">
    <form @submit.prevent="login" class="d-flex justify-content-center">
      <div class="row g-3 align-items-center mt-4">
        <div class="col-auto">
          <input
            type="text"
            class="form-control"
            v-model="username"
            id="username"
            placeholder="username"
            required
          />
        </div>
        <div class="col-auto">
          <input
            type="password"
            class="form-control"
            v-model="password"
            id="password"
            placeholder="password"
            required
          />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-warning">Login</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "",
      password: "",
    };
  },
  methods: {
    async login() {
      try {
        const authHeader = {
          auth: {
            username: this.username,
            password: this.password,
          },
        };

        const response = await axios.post(
          `${process.env.VUE_APP_API_URL}/token`,
          null,
          authHeader
        );

        // Save username and password to localStorage
        localStorage.setItem("username", this.username);
        localStorage.setItem("password", this.password);

        // Jika login berhasil
        alert(response.data.message);
        this.$router.push("/dashboard");
      } catch (error) {
        console.error("Login failed:", error.response.data.detail);
        alert("Login failed: " + error.response.data.detail);
      }
    },
  },
};
</script>
