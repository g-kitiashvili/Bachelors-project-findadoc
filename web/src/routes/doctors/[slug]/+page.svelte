<script lang="ts">
  import DoctorProfile from "$lib/components/DoctorProfile.svelte";

  let { data } = $props();
</script>

<a class="back" href="/doctors">← Back to doctors</a>
<DoctorProfile doctor={data.doctor} />

<style>
  .back {
    display: inline-block;
    margin: 1.5rem 0 1rem 1.5rem;
    color: #2563eb;
    text-decoration: none;
    font-family: system-ui, sans-serif;
  }
</style>
