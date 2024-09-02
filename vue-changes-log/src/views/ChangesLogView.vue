<template>
  <div class="container">
    <h1 style="padding: 1rem; color: aqua">Changes Log</h1>

    <!-- Filter Selection -->
    <div class="row justify-content-between">
      <div class="col-sm-3">
        <select
          v-model="filter"
          id="filter"
          class="form-control"
          @change="resetDataAndFetch"
        >
          <option value="PNT">PNT</option>
          <option value="PRI">PRI</option>
        </select>
      </div>
      <div class="col-sm-3">
        <input
          type="text"
          class="form-control mb-3"
          placeholder="Primary Key 1"
          v-model="primaryKeyField1Value"
          @change="fetchData"
        />
      </div>
      <div class="col-sm-3">
        <input
          type="text"
          class="form-control mb-3"
          placeholder="Primary Key 2"
          v-model="primaryKeyField2Value"
          @change="fetchData"
        />
      </div>
      <div class="col-sm-3">
        <input
          type="text"
          class="form-control mb-3"
          placeholder="Primary Key 3"
          v-model="primaryKeyField3Value"
          @change="fetchData"
        />
      </div>
      <div class="col-sm-3">
        <button @click="exportToExcel" class="btn btn-danger btn-xl mb-3">
          Export Excel
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div style="overflow-x: auto">
      <table
        id="dataTable"
        class="table is-striped table-bordered table-hover"
        style="width: 100%"
      >
        <span v-if="loading" class="spinner">
          <span class="visually-hidden">Loading...</span>
        </span>
      </table>
    </div>

    <!-- Pagination Controls -->
    <div class="pagination-controls m-4">
      <button
        @click="previousPage"
        :disabled="page <= 1"
        class="btn btn-primary btn-sm"
      >
        Previous
      </button>
      <button
        @click="nextPage"
        :disabled="!hasMoreData"
        class="btn btn-primary btn-sm"
      >
        Next
      </button>
    </div>

    <span v-if="loadingNext" class="spinner">
      <span class="visually-hidden">Loading...</span>
    </span>
  </div>
</template>

<script>
import axios from "axios";
import $ from "jquery";
import "datatables.net";
import "datatables.net-bs5";
import "datatables.net-fixedheader-bs5";
import * as XLSX from "xlsx";
import FileSaver from "file-saver";
import { ref } from "vue";

export default {
  data() {
    return {
      filter: "PNT",
      primaryKeyField1Value: "",
      primaryKeyField2Value: "",
      primaryKeyField3Value: "",
      data: ref([]),
      page: ref(1),
      pageSize: 100,
      totalRecords: 0,
      loading: false,
      loadingNext: false,
      hasMoreData: true,
      dataTable: null,
    };
  },
  methods: {
    async fetchData() {
      if (this.loading) return;
      this.loading = true;

      try {
        const params = {
          corporation: this.filter,
          page: this.page,
          page_size: this.pageSize,
        };

        if (this.primaryKeyField1Value)
          params.primary_1_value = this.primaryKeyField1Value;
        if (this.primaryKeyField2Value)
          params.primary_2_value = this.primaryKeyField2Value;
        if (this.primaryKeyField3Value)
          params.primary_3_value = this.primaryKeyField3Value;

        const response = await axios.get(
          `${process.env.VUE_APP_API_URL}/global_search`,
          {
            params,
            headers: {
              Authorization: `Basic ${btoa(
                `${localStorage.getItem("username")}:${localStorage.getItem(
                  "password"
                )}`
              )}`,
            },
          }
        );

        if (response.data.data.length) {
          this.data = response.data.data;
          this.totalRecords = response.data.total_records;
          this.hasMoreData = response.data.data.length === this.pageSize;
        } else {
          this.data = [];
          this.hasMoreData = false;
        }
        this.updateDataTable();
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        this.loading = false;
      }
    },

    updateDataTable() {
      if (this.dataTable) {
        this.dataTable.clear();
        this.dataTable.rows.add(this.data);
        this.dataTable.draw();
      } else {
        this.dataTable = $("#dataTable").DataTable({
          data: this.data,
          columns: [
            {
              title: "Select",
              data: null,
              defaultContent: "<input type='checkbox' class='select-row'>",
              orderable: false,
            },
            { title: "Date and Time", data: "dateAndTime" },
            { title: "Time", data: "time" },
            { title: "PK", data: "primaryKey" },
            { title: "Field No", data: "fieldNo" },
            { title: "Field Caption", data: "fieldCaption" },
            { title: "Table No", data: "tableNo", className: "text-nowrap" },
            { title: "Table Caption", data: "tableCaption" },
            { title: "Old Value", data: "oldValue" },
            { title: "New Value", data: "newValue" },
            { title: "User", data: "userID", className: "text-nowrap" },
            { title: "Entry No", data: "entryNo", className: "text-nowrap" },
            {
              title: "PrimaryKey Value 1",
              data: "primaryKeyField1Value",
              className: "text-nowrap",
            },
            {
              title: "PrimaryKey Value 2",
              data: "primaryKeyField2Value",
              className: "text-nowrap",
            },
            {
              title: "PrimaryKey Value 3",
              data: "primaryKeyField3Value",
              className: "text-nowrap",
            },
            {
              title: "Type of Changes",
              data: "typeOfChange",
              className: "text-nowrap",
            },
          ],
          responsive: true,
          scrollX: true,
          scrollY: "500px",
          scrollCollapse: true,
          fixedHeader: true,
          autoWidth: true,
          language: { search: "" },
          paging: false,
          dom: "rtip",
          buttons: [
            {
              extend: "excelHtml5",
              text: "Export Excel",
              title: "Data Export",
              exportOptions: {
                columns: ":visible",
              },
            },
          ],
          columnDefs: [
            {
              targets: 0,
              searchable: false,
              visible: true,
            },
          ],
        });
      }
    },

    async nextPage() {
      if (this.hasMoreData && !this.loading) {
        this.page += 1;
        this.pageSize += 100; // Increase pageSize by 100 for next page
        this.fetchData();
      }
    },

    async previousPage() {
      if (this.page > 1 && !this.loading) {
        this.page -= 1;
        this.pageSize -= 100; // Decrease pageSize by 100 for previous page
        this.fetchData();
      }
    },

    exportToExcel() {
      const table = $("#dataTable").DataTable();
      const selectedData = [];
      table.rows().every(function () {
        const row = this.node();
        const isChecked = $(row).find(".select-row").is(":checked");
        if (isChecked) {
          selectedData.push(this.data());
        }
      });
      if (selectedData.length === 0) {
        alert("No rows selected for export.");
        return;
      }
      const worksheet = XLSX.utils.json_to_sheet(selectedData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, "Data");
      const wbout = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
      const fileName = `DataExport_${new Date()
        .toISOString()
        .slice(0, 10)}.xlsx`;
      FileSaver.saveAs(
        new Blob([wbout], { type: "application/octet-stream" }),
        fileName
      );
    },

    resetDataAndFetch() {
      this.data = [];
      this.page = 1;
      this.pageSize = 100;
      this.fetchData();
    },
  },
  created() {
    this.fetchData();
  },
  beforeUnmount() {
    if (this.dataTable) {
      this.dataTable.destroy();
    }
  },
};
</script>

<style>
/* Mengatur agar tabel bisa di-scroll secara horizontal */
table#dataTable {
  border-collapse: collapse;
  table-layout: fixed;
}

/* Header tetap terlihat saat di-scroll ke bawah */
.dt-fixed-header {
  background-color: white;
  z-index: 1;
}

.container {
  max-width: 100%;
  overflow-x: auto;
}
</style>
