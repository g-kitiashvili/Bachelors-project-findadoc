<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";
  import LegalPage from "$lib/components/LegalPage.svelte";
</script>

<LegalPage title={m.meta_takedown()}>
  {#if getLocale() === "ka"}
    <h1>პროფილის წაშლა</h1>
    <p class="updated">ბოლო განახლება: 2026 წლის ივნისი</p>
    <p>
      თუ ხართ ექიმი ან კლინიკა და გსურთ თქვენი პროფილის შესწორება ან წაშლა, ჩვენ პატივს ვცემთ ამ
      მოთხოვნას.
    </p>

    <h2>როგორ მოვითხოვო</h2>
    <p>
      მოგვწერეთ <a href="mailto:takedown@findadoc.ge">takedown@findadoc.ge</a> და მიუთითეთ პროფილის
      ბმული (URL) მოკლე შენიშვნით. ვინაიდან ეს საბაკალავრო პროექტია, წაშლა ხდება ხელით, ჩვეულებრივ
      რამდენიმე დღეში.
    </p>

    <h2>რას ვაკეთებთ</h2>
    <p>
      შეგვიძლია სრულად წავშალოთ პროფილი ან შევასწოროთ ცალკეული ველები და ამოვიღოთ იგი საიტიდან.
      ვაჩვენებთ მხოლოდ საჯარო წყაროებიდან მოპოვებულ მონაცემებს - იხილეთ ასევე
      <a href={href("/privacy")}>კონფიდენციალურობის პოლიტიკა</a>.
    </p>
  {:else}
    <h1>Profile removal</h1>
    <p class="updated">Last updated: June 2026</p>
    <p>
      If you are a doctor or clinic and want your profile corrected or removed, we will honor the
      request.
    </p>

    <h2>How to request</h2>
    <p>
      Email <a href="mailto:takedown@findadoc.ge">takedown@findadoc.ge</a> with the profile URL and a
      brief note. As a thesis project, removal is handled manually, usually within a few days.
    </p>

    <h2>What we do</h2>
    <p>
      We can remove a profile entirely or correct specific fields and take it off the site. We display
      only data gathered from public sources - see also our
      <a href={href("/privacy")}>Privacy Policy</a>.
    </p>
  {/if}
</LegalPage>
