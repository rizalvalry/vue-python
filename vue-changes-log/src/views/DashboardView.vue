<template>
  <!-- Banner -->

  <!-- Dashboard -->
  <div class="d-flex flex-column flex-lg-row h-lg-full bg-surface-secondary">
    <!-- Vertical Navbar -->

    <!-- Main content -->
    <div class="h-screen flex-grow-1 lg-auto">
      <!-- Header -->
      <header class="bg-surface-primary border-bottom pt-6">
        <div class="container-fluid">
          <div class="mb-npx">
            <div class="row align-items-center">
              <!-- Actions -->
            </div>
          </div>
        </div>
      </header>
      <!-- Main -->
      <main class="py-6 bg-surface-secondary">
        <div class="container-fluid mt-2">
          <!-- Card stats -->
          <div class="row g-6 mb-6">
            <div class="col-xl-3 col-sm-6 col-12"></div>
            <div class="col-xl-3 col-sm-6 col-12">
              <div class="card shadow border-0">
                <router-link to="/changeslog">
                  <div class="card-body">
                    <div class="row">
                      <div class="col">
                        <span
                          class="h6 font-semibold text-muted text-sm d-block mb-2"
                          >Information Changes Log</span
                        >
                        <span class="h3 font-bold mb-0">
                          {{ dateWelcome }}</span
                        >
                      </div>
                      <div class="col-auto">
                        <div
                          class="icon icon-shape bg-primary text-white text-lg rounded-circle"
                        >
                          <i class="bi bi-people"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
            <div class="col-xl-3 col-sm-6 col-12">
              <div class="card shadow border-0">
                <div class="card-body">
                  <div class="row">
                    <div class="col">
                      <span
                        class="h6 font-semibold text-muted text-sm d-block mb-2"
                        >Total Rows this month</span
                      >
                    </div>
                    <div class="col-auto">
                      <!-- Spinner loading -->
                      <div v-if="loading" class="spinner">
                        <span class="visually-hidden">Loading...</span>
                      </div>

                      <!-- List Items -->
                      <ul class="list-group" v-else>
                        <div>PNT Data</div>
                        <li
                          class="list-group-item"
                          v-for="(itemPNTData, index) in itemsByPNT"
                          :key="index"
                        >
                          {{ itemPNTData.dateAndTime }} - (PNT):
                          {{ numberWithCommas(itemPNTData.entryNo) }}
                        </li>
                        <div>PRI Data</div>
                        <li
                          class="list-group-item"
                          v-for="(itemPRIData, index) in itemsByPRI"
                          :key="index"
                        >
                          {{ itemPRIData.dateAndTime }} - (PRI):
                          {{ numberWithCommas(itemPRIData.entryNo) }}
                        </li>
                      </ul>
                      <i class="bi bi-clock-history"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="container mt-4">
            <div class="row">
              <div class="col-sm-6">
                <div class="card">
                  <div class="card-body">
                    <div v-if="loadingChartPNT" class="spinner">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                    <div v-else>
                      <Bar :key="chartKeyPNT" :data="chartDataPNT" />
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="card">
                  <div class="card-body">
                    <div v-if="loadingChartPRI" class="spinner">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                    <div v-else>
                      <Bar :key="chartKeyPRI" :data="chartDataPRI" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);

const now = new Date();
const year = now.getFullYear();
const month = String(now.getMonth() + 1).padStart(2, "0");
const currentDate = `${year} ${month}`;
export default {
  name: "BarChart",
  components: { Bar },
  data() {
    return {
      username: localStorage.getItem("username") || "",
      password: localStorage.getItem("password") || "",
      filterPNT: "PNT",
      filterPRI: "PRI",
      itemsPNT: [],
      itemsPRI: [],
      itemsByPRI: this.itemsByPRI,
      itemsByPNT: this.itemsByPNT,
      loading: true,
      dateWelcome: currentDate,
      chartDataPNT: {
        labels: [],
        datasets: [
          {
            label: "PNT",
            backgroundColor: "#f2b949",
            data: [],
          },
        ],
      },
      chartDataPRI: {
        labels: [],
        datasets: [
          {
            label: "PRI",
            backgroundColor: "#ed80e9",
            data: [],
          },
        ],
      },
      chartKey: 0,
      loadingPNT: false,
      loadingPRI: false,
      loadingChartPNT: true,
      loadingChartPRI: true,
    };
  },
  methods: {
    numberWithCommas(x) {
      x = x.toString();
      var pattern = /(-?\d+)(\d{3})/;
      while (pattern.test(x)) x = x.replace(pattern, "$1,$2");
      return x;
    },
    async fetchDataPNT() {
      if (this.loadingPNT) return;
      this.loadingPNT = true;
      this.loadingChartPNT = true;

      try {
        const response = await axios.get(
          `${process.env.VUE_APP_API_URL}/materialized_views_data${currentDate}_PNT`,
          {
            headers: {
              Authorization: `Basic ${btoa(
                `${this.username}:${this.password}`
              )}`,
            },
          }
        );

        if (response.data.top_users_pnt && response.data.top_users_pnt.length) {
          const newChartData = {
            labels: response.data.top_users_pnt.map((item) => item.userID),
            datasets: [
              {
                label: "Usage PNT",
                backgroundColor: "#f2b949",
                data: response.data.top_users_pnt.map(
                  (item) => item.baris_penggunaan
                ),
              },
            ],
          };
          this.chartDataPNT = newChartData;
          this.itemsByPNT = response.data.max_pnt;
          this.chartKeyPNT += 1;
        } else {
          this.chartDataPNT = {
            labels: [],
            datasets: [
              {
                label: "Usage PNT",
                backgroundColor: "#f2b949",
                data: [],
              },
            ],
          };
        }
      } catch (error) {
        console.error("Error fetching data PNT:", error);
      } finally {
        this.loadingPNT = false;
        this.loadingChartPNT = false;
      }
    },
    async fetchDataPRI() {
      if (this.loadingPRI) return;
      this.loadingPRI = true;
      this.loadingChartPRI = true;

      try {
        const response = await axios.get(
          `${process.env.VUE_APP_API_URL}/materialized_views_data`,
          {
            headers: {
              Authorization: `Basic ${btoa(
                `${this.username}:${this.password}`
              )}`,
            },
          }
        );

        if (response.data.top_users_pri && response.data.top_users_pri.length) {
          const newChartData = {
            labels: response.data.top_users_pri.map((item) => item.userID),
            datasets: [
              {
                label: "Usage PRI",
                backgroundColor: "#ed80e9",
                data: response.data.top_users_pri.map(
                  (item) => item.baris_penggunaan
                ),
              },
            ],
          };
          this.chartDataPRI = newChartData;
          this.itemsByPRI = response.data.max_pri;
          this.chartKeyPRI += 1;
        } else {
          this.chartDataPRI = {
            labels: [],
            datasets: [
              {
                label: "Usage PRI",
                backgroundColor: "#ed80e9",
                data: [],
              },
            ],
          };
        }
      } catch (error) {
        console.error("Error fetching data PRI:", error);
      } finally {
        this.loadingPRI = false;
        this.loadingChartPRI = false;
      }
    },
  },

  async mounted() {
    await this.fetchDataPNT();
    await this.fetchDataPRI();
    this.loading = false;
  },
};
</script>
