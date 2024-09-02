<template>
  <table>
    <thead>
      <tr>
        <th v-for="(header, index) in headers" :key="index">{{ header }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in data" :key="index">
        <td v-for="(header, index) in headers" :key="index">
          {{ row[header] }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  props: {
    data: Array,
  },
  computed: {
    headers() {
      return this.data.length ? Object.keys(this.data[0]) : [];
    },
  },
};
</script>
