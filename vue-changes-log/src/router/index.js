import DashboardView from "../views/DashboardView.vue";
import LoginView from "@/views/LoginView.vue";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";
import { createMemoryHistory, createRouter } from "vue-router";
import ChangesLogView from "@/views/ChangesLogView.vue";

const routes = [
  { path: "/dashboard", name: "Dashboard", component: DashboardView },
  { path: "/login", name: "Login", component: LoginView },
  { path: "/", redirect: "/login" },
  { path: "/changeslog", name: "/changeslog", component: ChangesLogView },
];

const router = createRouter({
  history: createMemoryHistory(),
  routes,
});

// Route guard to protect routes
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("isAuthenticated");
  if (
    to.matched.some((record) => record.meta.requiresAuth) &&
    !isAuthenticated
  ) {
    next("/");
  } else {
    next();
  }
});

export default router;
