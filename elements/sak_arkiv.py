from robocorp import browser
from bs4 import BeautifulSoup
import pandas as pd


browser.configure(browser_engine="chrome")
browser.configure_context(viewport={"width": 2250, "height": 1080})
b = browser
page = browser.page()


# ------------------------------------------LOGIN----------------------------------------------------------------------------------
def login_elements(URL, UPN):
    b.goto(URL)
    page.select_option(".select-container.form-control", "nb")
    try:
        page.click("//button[@class='btn btn-primary' and text()='Logg inn']", timeout=10000)
    except:
        pass
    ms_login= browser.context().pages[-1]
    try:
        ms_login.fill("#i0116", UPN)
        ms_login.click('//*[@id="idSIButton9"]')
    except:
        print("SSO")
    try:
        page.locator("span").filter(has_text="Sak/Arkiv").first.click()
    except:
        page.reload()
        page.locator("span").filter(has_text="Sak/Arkiv").first.click()


# ------------------------------------------HTML----------------------------------------------------------------------------------
def elements_read_table_from_html(html_table: None) -> pd.DataFrame:
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


# ------------------------------------------SEARCH----------------------------------------------------------------------------------
def elements_søk_naviger_igjennom_meny(SearchName: str):
    page.click("#tab_searchToggler_button")
    page.click("//span[contains(@class, 'btn-menu-text') and contains(text(), 'Saksbehandl')]")
    page.click(f"//span[contains(text(), '{SearchName}')]")
    page.click("#tab_searchToggler_button")


def elements_søk_naviger_til_journalpost_med_hurtigsøk(searchCase):
    page.click("#tab_searchToggler_button")
    page.fill("input[class*='quick-search']", f"{searchCase}")
    page.click("button[class*='quick-search-btn']")
    page.click("#tab_searchToggler_button")


def elements_søk_sorter_søk_etter_stigende_dokumentdato():
    page.click("//th[@data-field='JP_DOKDATO']")
    sort = page.get_attribute("//th[@data-field='JP_DOKDATO']", "data-dir")
    while sort == None:
        sort = page.get_attribute("//th[@data-field='JP_DOKDATO']", "data-dir")

    while "asc" != sort:
        page.click("//th[@data-field='JP_DOKDATO']")
        sort = page.get_attribute("//th[@data-field='JP_DOKDATO']", "data-dir")


def elements_søk_refresh():
    page.click("refresh-text")


# --------------------------------------JOURNALPOST--------------------------------------------
def elements_journalpost_rediger():
    page.click("//*[@id='resizeMetricsRegistryList']//button[@title='Rediger']")


def elements_journalpost_lagre_og_lukk():
    try:
        page.click("//span[contains(@data-bind, 'SaveAndExit')]", timeout=5000)
    except:
        page.click("//span[contains(@data-bind, 'SaveAndEditDocument')]", timeout=5000)
    
def elements_journalpost_lukk_post():
    page.click("//span[contains(@data-bind, 'DmbClose')]")

def elements_journalpost_lukk_sak():
    page.wait_for_selector("//*[@id='resizeMetricsRegistryList']//button[@title='Rediger']").is_visible()
    header = page.locator('//*[@id="title-censor-container"]/div/h3').text_content()
    page.locator("li").filter(has_text=header).get_by_title("Lukk").click()


def elements_journalpost_les_tittel():
    tittel = page.text_content(".details-header-text")
    return tittel


def elements_journalpost_les_dato_mottatt():
    date = page.text_content(".row-flex:nth-child(2) .no-border-width")
    date = date.replace(".", "")
    return date


def elements_journalpost_les_dokumentvedlegg():
    vedlegg = page.text_content("//span[@class='attachment-name']")
    list = vedlegg.splitlines
    return list


def elements_journalpost_kopimottakere_boolean():
    kopimottaker = page.inner_text("div.details-container.fields")
    if "Kopi" not in kopimottaker:
        kopimottaker = False
    elif "Kopi" in kopimottaker:
        kopimottaker = True
    else:
        kopimottaker = False
    return kopimottaker


def elements_journalpost_les_kopimottakere():
    kopimottaker = page.inner_text(".col-xs-12 > .col-container > .run-in-list")
    list = kopimottaker.splitlines()
    return list


def elements_journalpost_les_motakkere():
    mottaker = page.inner_text(".run-in-list")
    list = mottaker.splitlines()
    return list


def elements_journalpost_les_motakker_og_kopi_grønn():
    sjekk_send_status = page.inner_html('//div[@class="details-container fields"]')
    if "send-unknown" in sjekk_send_status:
        print("Ingen med grønn konvolutt")
        list = []
    else:
        mottaker = page.text_content(".send-success")
        list = mottaker.splitlines()
    return list

def elements_merknad_ny():
    page.get_by_role("link", name="Merknader", exact=True).click()
    page.locator("[data-test=\"new-item-btn\"]").click()
    page.get_by_placeholder("Skriv inn merknad").fill("hello")
    page.get_by_role("button", name="Lagre").click()



# ---------------------------------------- SVAR ----------------------------------------------
def elements_svar_trykk_svar_på_inngående_brev():
    page.click("//button[contains(.,' Svar')]")


def elements_svar_legg_til_kopimottaker_som_saksbehandler(kopimottaker):
    page.fill("//input[@type='search'])[4]", f"{kopimottaker}")


def elements_svar_legg_til_kopimottaker_enhetsregisteret(Organisasjonsnummer):
    page.click("//span[contains(.,'Kopi')]")
    page.click("//option[@value='Enhetsregisteret']")
    page.fill(
        "//input[@placeholder='Organisasjonsnummer' and @type='text' and @class='form-control']",
        "Organisasjonsnummer",
    )
    page.click("(//button[@type='submit'])[2]")
    page.click(f"//span[contains(.,'{Organisasjonsnummer}')")
    page.click(".btn-dialog-list")
    page.click("//button[contains(.,'OK')]")


def elements_svar_tilknytt_dokumentmal_til_utgående_brev(
    DokumentText: str, DokumentMalType: str, DokumentMal: str
):
    page.click("//button[contains(.,'Tilknytt')]")
    page.click("//button[contains(.,'Dokumentmal')]")
    page.click(
        f"//li[contains(@class, 'box-list-item') and contains(., '{DokumentMalType}')]"
    )
    page.click(f"//div[contains(span, '{DokumentMal}')]")
    page.fill("//label[contains(.,'Dokumenttittel')]/../input", f"{DokumentText}")
    page.click("//button[contains(.,' Lagre')]")


def elements_svar_ekspeder_utgående_brev(ekspederingsMetode: str):
    # Ekspiderer utgående brev. På loctator "css:option[Value="X"]" er det viktig å notere verdi E = epost, P = posten, GENERELL = Generell digital forsendelse, ... = ...
    page.click("(//button[@type='button'])[100]")
    page.click("//button[contains(.,'Ferdigstill')]")
    page.click("//button[contains(.,' Ekspeder')]")
    page.click("//span[contains(.,'Ekspeder digitalt')]")
    page.click(f"css:option[value='{ekspederingsMetode}']")
    page.click("//button[text()='Send']")
    page.click("//button[text()='Lukk']")


# --------------------------------------MOTTAKERKORT-------------------------------------------
def elements_mottakerkort_åpne(mottakerNavn):
    page.click(
        f'//*[@id="registryEntryForm"]//span[contains(text(), "{mottakerNavn}")]'
    )


def elements_mottakerkort_flere_detailer():
    page.get_by_role("button", name="Flere felt").click()


def elements_mottakerkort_velg_forsendelsemåte(forsendelsesmåte):
    try:
        page.locator("//*[@class='sendingMethods-field']//b").click(timeout=1000)
        page.click(f"//li[text()='{forsendelsesmåte}']", timeout=1000)
    except:
        print("Form is not editable")


def elements_mottakerkort_velg_forsendelsesstatus(forsendelsesstatus):
    try:
        page.locator('//*[@class="sendingStatuses-field"]//b').click(timeout=1000)
        page.click(f"//li[text()='{forsendelsesstatus}']", timeout=1000)
    except:
        print("Form is not editable")


def elements_mottakerkort_trykk_OK():
    page.get_by_role("button", name="OK", exact=True).click()


def elements_mottakerkort_avbryt():
    page.get_by_role("button", name="Avbryt", exact=True).click()


# -----------------------------------------Profil/Hamburger----------------------------------------------
def elements_profil_velg_rolle(rolle: str):
    page.click('//*[@class="user-name"]')
    page.click("//*[@id='colorSwitchScope']//span[text()='Velg rolle']")
    attributes= page.inner_html(f"//li[contains(button, '{rolle}')]")
    if "disabled" not in attributes:
        page.click(f"//li[contains(button, '{rolle}')]")
    else:
        print("Rolle is already selected")
