"""Functions for Elements"""
from typing import Literal
from robocorp import browser
from playwright.sync_api import expect
from bs4 import BeautifulSoup
import pandas as pd


browser.configure(browser_engine="chrome")
browser.configure_context(viewport={"width": 1920, "height": 1080})
b = browser
page = b.context().new_page()


# ------------------------------------------LOGIN----------------------------------------------
class Login:
    @staticmethod
    def login(url: str, upn: str, module: Literal["Sak/Arkiv"]):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.locator("#select-database").wait_for()
        page.select_option(".select-container.form-control", "nb")
        login = page.locator(
            "//button[@class='btn btn-primary' and text()='Logg inn']"
        ).is_visible()
        sak_arkiv = page.locator("span").filter(has_text=module).first.is_visible()
        if not login and not sak_arkiv:
            print("REFRESHING PAGE")
            page.reload()
            page.wait_for_load_state("networkidle")
            login = page.locator(
                "//button[@class='btn btn-primary' and text()='Logg inn']"
            ).is_visible()
            sak_arkiv = (
                page.locator("span").filter(has_text="Sak/Arkiv").first.is_visible()
            )
        if login is True:
            page.click(
                "//button[@class='btn btn-primary' and text()='Logg inn']", timeout=5000
            )
            try:
                ms_login = browser.context().pages[-1]  # pylint: disable=no-member
                ms_login.fill("#i0116", upn, timeout=10000)
                ms_login.click('//*[@id="idSIButton9"]')
            except:
                print("SSO")
            page.locator("span").filter(has_text=module).first.click()
            page.wait_for_load_state("networkidle")
        elif sak_arkiv is True:
            page.locator("span").filter(has_text=module).first.click()


# ------------------------------------------HTML----------------------------------------------------
class HTML:
    @staticmethod
    def create_table() -> pd.DataFrame:
        """Parser tabell fra elements søk og gjør det om til pandas dataframes"""
        html_table = page.inner_html('//*[@id="dynamicGrid"]/table')

        table_headers = []
        table_rows = []
        soup = BeautifulSoup(html_table, "html.parser")

        # Extract table headers
        for table_header in soup.find_all("th"):
            header_values = table_header.text.strip()
            table_headers.append(header_values)

        # Extract table rows
        for table_row in soup.select("tr"):
            cells = table_row.find_all("td")
            if len(cells) > 0:
                cell_values = [cell.text.strip() for cell in cells]
                table_rows.append(cell_values)

        # Create a DataFrame
        df = pd.DataFrame(table_rows, columns=table_headers)
        return df


# ------------------------------------------SEARCH--------------------------------------------------
class Search:
    @staticmethod
    def naviger_igjennom_meny(searchname: str):
        """Drar ut menyen til venstre og trykker på definiert søk"""
        page.click("#tab_searchToggler_button")
        visible = page.locator(f"//span[contains(text(), '{searchname}')]").is_visible()
        if visible is False:
            page.click(
                "//span[contains(@class, 'btn-menu-text') and contains(text(), 'Saksbehandl')]"
            )
        page.click(f"//span[contains(text(), '{searchname}')]")
        page.click("#tab_searchToggler_button")

    @staticmethod
    def naviger_til_journalpost_med_hurtigsok(searchcase):
        """Drar ut menyen til venstre og bruker søket til å søke på en sak"""
        page.click("#tab_searchToggler_button")
        page.fill("input[class*='quick-search']", f"{searchcase}")
        page.click("button[class*='quick-search-btn']")
        page.click("#tab_searchToggler_button")

    @staticmethod
    def sorter_sok_etter_stigende_dokumentdato():
        """sorterer dokument etter dokumentdato, per idag er denne litt ustabil"""
        page.click("//th[@data-field='JP_DOKDATO']")
        sort = page.get_attribute("//th[@data-field='JP_DOKDATO']", "data-dir")
        while sort is None:
            sort = page.get_attribute("//th[@data-field='JP_DOKDATO']", "data-dir")

        while "asc" != sort:
            page.click("//th[@data-field='JP_DOKDATO']")
            sort = page.get_attribute("//th[@data-field='JP_DOKDATO']", "data-dir")

    @staticmethod
    def refresh_sok():
        """Trykker på "Refresh" eller "oppfrisk" tabellen fra søket"""
        page.get_by_role("button", name="Oppfrisk").click()


# --------------------------------------SAK---------------------------------------------------
class Sak:
    @staticmethod
    def opprett_sak(
        sak_tittel: str,
        status: str = "Reservert",
        sak_ansvarlig: str = "Ufordelt",
        arkivdel: str = "Generelt saksarkiv",
        journalenhet: str = "Sentralt postmottak",
        delay_ms: int = 100,
    ):
        """Oppretter ny sak"""
        page.get_by_text("Ny sak").click()
        # Fyll ut - Tittel(obligatorisk felt)
        title_field = page.locator("//h1[@id='titleCensor']")
        expect(title_field).to_be_in_viewport()
        title_field.fill(sak_tittel)
        if status:
            # Fyll ut - Status (obligatorisk felt)
            page.locator("//input[@id='CaseStatusId']").press_sequentially(
                status, delay=delay_ms
            )
            page.locator("//div[contains(@id, 'react-select')]").filter(
                has_text=status
            ).click()
        if sak_ansvarlig:
            # Fyll ut - Saksansvarlig (obligatorisk felt)
            page.locator("//input[@id='CaseWorker']").press_sequentially(
                sak_ansvarlig, delay=delay_ms
            )
            page.locator("//div[contains(@id, 'react-select')]").filter(
                has_text=sak_ansvarlig
            ).click()
        if arkivdel:
            # Fyll ut - Arkivdel (obligatorisk felt)
            page.locator("//input[@id='SeriesId']").press_sequentially(
                arkivdel, delay=delay_ms
            )
            page.locator("//div[contains(@id, 'react-select')]").filter(
                has_text=arkivdel
            ).click()
        if journalenhet:
            # Fyll ut - Journalenhet (obligatorisk felt)
            page.locator("//input[@id='RegistryManagementUnitId']").press_sequentially(
                journalenhet, delay=delay_ms
            )
            page.locator("//div[contains(@id, 'react-select')]").filter(
                has_text=journalenhet
            ).click()
        # Lagre sak
        page.get_by_text("Lagre").click()

    @staticmethod
    def les_saksnummer_fra_sak() -> str:
        """Inne på sak - leser og returnerer saksnummer"""
        saksnr = page.get_by_title("Saksnummer").text_content()
        return str(saksnr)


# --------------------------------------JOURNALPOST--------------------------------------------
class Journalpost:
    @staticmethod
    def opprett_journalpost(
        title: str,
        jp_type: str = "Internt notat uten oppfølging",
        status: str = "Ferdig",
        saksbehandler_name: str = "Ufordelt",
        saksbehandler_name_and_department: str = None,
        attachments: list[str] = None,
        delay_ms: int = 100,
    ):
        """Oppretter ny journalpost på valgt sak"""
        new_jp_button = page.locator(
            "//span[contains(@data-bind, 'LinkRegistryEntryLbl')]"
        )
        new_jp_button.wait_for(state="visible")
        new_jp_button.click()
        page.get_by_role("link", name=jp_type).click()
        page.fill(selector="//h4[@id='titleCensor']", value=title)
        if status:  # Fyll ut - Status
            page.locator(
                "//div[contains(@data-bind, 'formField: RecordStatusId')]"
            ).locator("//span[contains(@class, '_arrow')]").click()
            page.get_by_role("treeitem", name=status).click()
        if saksbehandler_name:  # Fyll ut - Saksbehandler
            field_case_worker_input = page.locator(
                selector="//div[contains(@data-bind, 'formField: CaseWorker')]"
            ).locator("//input[contains(@class, 'search')]")
            field_case_worker_input.clear()
            field_case_worker_input.press_sequentially(
                saksbehandler_name, delay=delay_ms
            )
            field_case_worker_input.press("Enter")
            if not saksbehandler_name_and_department:
                saksbehandler_name_and_department = saksbehandler_name
            page.get_by_role("treeitem", name=saksbehandler_name_and_department).click()
        if attachments:  # Legg til vedlegg
            page.get_by_role("button", name="Tilknytt").click()
            with page.expect_file_chooser() as fc_info:
                page.get_by_role("button", name="Filvedlegg").click()
            file_chooser = fc_info.value
            file_chooser.set_files(files=attachments)  # type: ignore
            page.get_by_role("button", name="Lagre").click()
        page.get_by_role("button", name="Lagre og lukk").click()

    @staticmethod
    def rediger():
        """Trykker på rediger knappen på journalpost"""
        page.click("//*[@id='resizeMetricsRegistryList']//button[@title='Rediger']")

    @staticmethod
    def lagre_og_lukk():
        """Trykker lagre og lukk eller save and edit document"""
        # Endre?
        try:
            page.click("//span[contains(@data-bind, 'SaveAndExit')]", timeout=5000)
        except TimeoutError:
            page.click(
                "//span[contains(@data-bind, 'SaveAndEditDocument')]", timeout=5000
            )

    @staticmethod
    def lukk_post():
        """Lukker jornalpost"""
        page.click("//span[contains(@data-bind, 'DmbClose')]")

    @staticmethod
    def lukk_sak():
        """Lukker saken ved å finne tittel på sak og trykke X på fanen"""
        page.wait_for_selector(
            "//*[@id='resizeMetricsRegistryList']//button[@title='Rediger']"
        ).is_visible()
        header = page.locator('//*[@id="title-censor-container"]/div/h3').text_content()
        page.locator("li").filter(has_text=header).get_by_title("Lukk").click()

    @staticmethod
    def les_tittel():
        """Finner tittel på sak"""
        tittel = page.text_content(".details-header-text")
        return tittel

    @staticmethod
    def les_dato_mottatt():
        """Leser av sak mottatt dato"""
        date = page.text_content(".row-flex:nth-child(2) .no-border-width")
        date = date.replace(".", "")
        return date

    @staticmethod
    def les_dokumentvedlegg():
        """Leser dokument vedlegg og lager en liste"""
        vedlegg_list = []
        page.locator('//*[@id="title-censor-container"]/div/h3').wait_for(
            state="visible"
        )
        vedlegg = page.locator("//span[contains (@class, 'attachment-name')]").all()
        for i in vedlegg:
            v = i.inner_text()
            vedlegg_list.append(v)
        return vedlegg_list

    @staticmethod
    def kopimottakere_boolean():
        """sjekker om det finnes kopi mottakere og returerer verdien som True eller False"""
        kopimottaker = page.inner_text("div.details-container.fields")
        if "Kopi" not in kopimottaker:
            kopimottaker = False
        elif "Kopi" in kopimottaker:
            kopimottaker = True
        else:
            kopimottaker = False
        return kopimottaker

    @staticmethod
    def les_kopimottakere():
        """Leser kopimottakere og returnerer det som en liste"""
        kopimottaker = page.inner_text(".col-xs-12 > .col-container > .run-in-list")
        kopimottaker_list = kopimottaker.splitlines()
        return kopimottaker_list

    @staticmethod
    def les_mottakere():
        """Leser mottakere og returnerer det som en liste"""
        mottaker = page.inner_text(".run-in-list")
        mottaker_list = mottaker.splitlines()
        return mottaker_list

    @staticmethod
    def les_mottaker_og_kopi_gronn():
        """Leser mottakere med grønn konvolutt og returnerer det som en liste"""
        sjekk_send_status = page.inner_html('//div[@class="details-container fields"]')
        if "send-unknown" in sjekk_send_status:
            print("Ingen med grønn konvolutt")
            gronn_list = []
        else:
            mottaker = page.text_content(".send-success")
            gronn_list = mottaker.splitlines()
        return gronn_list

    @staticmethod
    def merknad_ny(tekst: str):
        """Lager ny mernad på sak med egendefiniert tekst"""
        page.get_by_role("link", name="Merknader", exact=True).click()
        page.locator('[data-test="new-item-btn"]').click()
        page.get_by_placeholder("Skriv inn merknad").fill(tekst)
        page.get_by_role("button", name="Lagre").click()


# ---------------------------------------- SVAR ----------------------------------------------
class Svar:
    @staticmethod
    def trykk_svar_pa_inngaende_brev():
        """Trykker svar på inngående brev"""
        page.click("//button[contains(.,' Svar')]")

    @staticmethod
    def legg_til_kopimottaker_som_saksbehandler(kopimottaker):
        """Legger til kopimottaker som saksbehandler"""
        # Endres?
        page.fill("//input[@type='search'])[4]", f"{kopimottaker}")

    @staticmethod
    def legg_til_kopimottaker_enhetsregisteret(organisasjonsnummer):
        """Legger orginisasjon som kopimottaker med orgnr"""
        page.click("//span[contains(.,'Kopi')]")
        page.click("//option[@value='Enhetsregisteret']")
        page.fill(
            "//input[@placeholder='Organisasjonsnummer' and @type='text' and @class='form-control']",
            "Organisasjonsnummer",
        )
        page.click("(//button[@type='submit'])[2]")
        page.click(f"//span[contains(.,'{organisasjonsnummer}')")
        page.click(".btn-dialog-list")
        page.click("//button[contains(.,'OK')]")

    @staticmethod
    def tilknytt_dokument_mal_til_utgaende_brev(
        dokument_text: str, dokument_mal_type: str, dokument_mal: str
    ):
        """Tilknytter dokument_mal til utgående brev"""
        page.click("//button[contains(.,'Tilknytt')]")
        page.click("//button[contains(.,'dokument_mal')]")
        page.click(
            f"//li[contains(@class, 'box-list-item') and contains(., '{dokument_mal_type}')]"
        )
        page.click(f"//div[contains(span, '{dokument_mal}')]")
        page.fill("//label[contains(.,'Dokumenttittel')]/../input", f"{dokument_text}")
        page.click("//button[contains(.,' Lagre')]")

    @staticmethod
    def ekspeder_utgaende_brev(ekspederings_metode: str):
        """Ekspiderer utgående brev. På loctator "css:option[Value="X"]" er det viktig å
        notere verdi E = epost, P = posten, GENERELL = Generell digital forsendelse, ... = ...
        """
        page.click("(//button[@type='button'])[100]")
        page.click("//button[contains(.,'Ferdigstill')]")
        page.click("//button[contains(.,' Ekspeder')]")
        page.click("//span[contains(.,'Ekspeder digitalt')]")
        page.click(f"css:option[value='{ekspederings_metode}']")
        page.click("//button[text()='Send']")
        page.click("//button[text()='Lukk']")


# --------------------------------------MOTTAKERKORT-------------------------------------------
class Mottakerkort:
    @staticmethod
    def apne(mottakernavn):
        """Åpner mottakerkort"""
        page.click(
            f'//*[@id="registryEntryForm"]//span[contains(text(), "{mottakernavn}")]'
        )

    @staticmethod
    def flere_detailer():
        """Trykker "Flere detaljer" på mottakerkort"""
        page.get_by_role("button", name="Flere felt").click()

    @staticmethod
    def velg_forsendelsemate(forsendelsesmate):
        """Velger forsendelse måte på bruker. Det er ingen god måte å sjekke om
        feltet er disabled så da bruker vi "try" med raske timeouts"""
        try:
            page.locator("//*[@class='sendingMethods-field']//b").click(timeout=1000)
            page.click(f"//li[text()='{forsendelsesmate}']", timeout=1000)
        except TimeoutError:
            print("Form is not editable")

    @staticmethod
    def velg_forsendelsesstatus(forsendelsesstatus):
        """Velger forsendelse status på bruker.
        Det er ingen god måte å sjekke om feltet er disabled så da bruker vi "try" med raske timeouts
        """
        try:
            page.locator('//*[@class="sendingStatuses-field"]//b').click(timeout=1000)
            page.click(f"//li[text()='{forsendelsesstatus}']", timeout=1000)
        except TimeoutError:
            print("Form is not editable")

    @staticmethod
    def trykk_ok():
        """trykker OK på mottakerkort, denne kan feile innimellom.
        Så her er det lurt å bruke også en annen måte"""
        page.get_by_role("button", name="OK", exact=True).click()

    @staticmethod
    def trykk_avbryt():
        """Trykker avbryt på mottakerkort,
        denne kan feile innimellom så her er det lurt å bruke også en annen måte"""
        page.get_by_role("button", name="Avbryt", exact=True).click()


# -----------------------------------------Profil/Hamburger-----------------------------------------
class Profil_hamburger:
    @staticmethod
    def velg_rolle(rolle: str):
        """Trykker på hamburger menyen øverst til venstre og velger rolle,
        hvis rolle du vil ha er allerede valgt vil den ikke endres"""
        page.click('//*[@class="user-name"]')
        page.click("//*[@id='colorSwitchScope']//span[text()='Velg rolle']")
        attributes = page.inner_html(f"//li[contains(button, '{rolle}')]")
        if "disabled" not in attributes:
            page.click(f"//li[contains(button, '{rolle}')]")
        else:
            print("Rolle is already selected")
