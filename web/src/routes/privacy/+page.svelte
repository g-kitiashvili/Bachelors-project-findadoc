<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";
  import LegalPage from "$lib/components/LegalPage.svelte";
</script>

<LegalPage title={m.meta_privacy()}>
  {#if getLocale() === "ka"}
    <h1>კონფიდენციალურობის პოლიტიკა</h1>
    <p class="updated">ბოლო განახლება: 2026 წლის ივნისი</p>
    <p>
      Find-a-Doc არის თავისუფალი უნივერსიტეტის საბაკალავრო ნაშრომის პროექტი. ის აერთიანებს
      საქართველოში ექიმებისა და კლინიკების შესახებ საჯაროდ ხელმისაწვდომ ინფორმაციას. ეს პოლიტიკა
      განმარტავს, რა მონაცემებს ვამუშავებთ და რა უფლებები გაქვთ პერსონალურ მონაცემთა დაცვის შესახებ
      საქართველოს კანონის მიხედვით.
    </p>

    <h2>ექიმებისა და კლინიკების მონაცემები</h2>
    <p>
      ვაჩვენებთ მხოლოდ იმ ინფორმაციას, რომელიც ექიმებმა ან მათმა კლინიკებმა აშკარად საჯარო გახადეს
      (კლინიკის ვებგვერდის ბიოგრაფიები, საჯარო ჩამონათვალები). არ ვაგროვებთ და არ ვაჩვენებთ პირად
      საკონტაქტო მონაცემებს, როგორიცაა პირადი მობილური ან საცხოვრებელი მისამართი.
    </p>

    <h2>თქვენი ვიზიტის შესახებ</h2>
    <p>
      საიტი იყენებს ერთ აუცილებელ ქუქის თქვენი ენის დასამახსოვრებლად. წვდომის ჟურნალები მცირე ხნით
      ინახება ბოროტად გამოყენების მონიტორინგისთვის და არ გამოიყენება ცალკეული ვიზიტორის
      იდენტიფიცირებისთვის.
    </p>

    <h2>თქვენი უფლებები</h2>
    <p>
      შეგიძლიათ მოითხოვოთ თქვენ შესახებ არსებულ პერსონალურ მონაცემებზე წვდომა, მათი შესწორება ან
      წაშლა. მოგვწერეთ <a href="mailto:privacy@findadoc.ge">privacy@findadoc.ge</a>. მოთხოვნები
      მუშავდება ხელით.
    </p>
    <p>
      ექიმები და კლინიკები, რომელთაც სურთ პროფილის წაშლა, იხილეთ
      <a href={href("/takedown")}>პროფილის წაშლა</a>.
    </p>

    <h2>გაფრთხილება</h2>
    <p>
      ინფორმაცია მოპოვებულია საჯარო ვებგვერდებიდან და შესაძლოა მოძველებული იყოს. ის არ წარმოადგენს
      სამედიცინო რჩევას. ქმედებამდე გადაამოწმეთ დეტალები კლინიკასთან.
    </p>
  {:else}
    <h1>Privacy Policy</h1>
    <p class="updated">Last updated: June 2026</p>
    <p>
      Find-a-Doc is a bachelor's thesis project at the Free University of Tbilisi. It indexes
      publicly available information about doctors and clinics in Georgia. This policy explains what
      data we handle and your rights under Georgia's Personal Data Protection Law.
    </p>

    <h2>Doctor and clinic data</h2>
    <p>
      We display only information that doctors or their clinics have made manifestly public (clinic
      website biographies, public listings). We do not scrape or display private contact details such
      as personal mobile numbers or home addresses.
    </p>

    <h2>How we use your visit</h2>
    <p>
      The site uses one essential cookie to remember your language. Access logs are retained briefly
      for abuse monitoring and are not used to identify individual visitors.
    </p>

    <h2>Your rights</h2>
    <p>
      You may request access to, correction of, or deletion of personal data we hold about you. Email
      <a href="mailto:privacy@findadoc.ge">privacy@findadoc.ge</a>. Requests are handled manually.
    </p>
    <p>
      Doctors and clinics who want a profile removed: see
      <a href={href("/takedown")}>Profile removal</a>.
    </p>

    <h2>Disclaimer</h2>
    <p>
      Information is sourced from public websites and may be out of date. It is not medical advice.
      Verify details with the clinic before acting.
    </p>
  {/if}
</LegalPage>
