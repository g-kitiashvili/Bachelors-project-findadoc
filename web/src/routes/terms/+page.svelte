<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { getLocale } from "$lib/paraglide/runtime";
  import LegalPage from "$lib/components/LegalPage.svelte";
</script>

<LegalPage title={m.meta_terms()}>
  {#if getLocale() === "ka"}
    <h1>მომსახურების პირობები</h1>
    <p class="updated">ბოლო განახლება: 2026 წლის ივნისი</p>
    <p>
      Find-a-Doc-ის გამოყენებით თქვენ ეთანხმებით ამ პირობებს. საიტი არის არაკომერციული საბაკალავრო
      ნაშრომის პროექტი.
    </p>

    <h2>დანიშნულება</h2>
    <p>
      ეს არის საჯაროდ ხელმისაწვდომი ინფორმაციის ცნობარი, რომელიც დაგეხმარებათ ექიმებისა და
      კლინიკების მოძიებაში. ის არ წარმოადგენს სამედიცინო რჩევას და არ ანაცვლებს პროფესიულ
      კონსულტაციას.
    </p>

    <h2>სიზუსტე</h2>
    <p>
      მონაცემები აგროვებულია საჯარო წყაროებიდან და შესაძლოა იყოს არასრული ან მოძველებული. არ ვიძლევით
      სიზუსტის გარანტიას. ყოველთვის გადაამოწმეთ კლინიკასთან.
    </p>

    <h2>გამოყენების წესები</h2>
    <p>
      არ გამოიყენოთ ავტომატური საშუალებები სერვისის მონაცემების მასობრივად მოსაპოვებლად ან
      გადასატვირთად და არ ბოროტად გამოიყენოთ ინფორმაცია.
    </p>

    <h2>კონტაქტი</h2>
    <p>კითხვებისთვის: <a href="mailto:contact@findadoc.ge">contact@findadoc.ge</a>.</p>
  {:else}
    <h1>Terms of Service</h1>
    <p class="updated">Last updated: June 2026</p>
    <p>
      By using Find-a-Doc you agree to these terms. The site is a non-commercial bachelor's thesis
      project.
    </p>

    <h2>Purpose</h2>
    <p>
      It is a directory of publicly available information to help you find doctors and clinics. It is
      not medical advice and is not a substitute for professional consultation.
    </p>

    <h2>Accuracy</h2>
    <p>
      Data is aggregated from public sources and may be incomplete or out of date. We make no warranty
      as to accuracy. Always confirm with the clinic.
    </p>

    <h2>Acceptable use</h2>
    <p>
      Do not use automated means to scrape or overload the service, and do not misuse the information.
    </p>

    <h2>Contact</h2>
    <p>Questions: <a href="mailto:contact@findadoc.ge">contact@findadoc.ge</a>.</p>
  {/if}
</LegalPage>
