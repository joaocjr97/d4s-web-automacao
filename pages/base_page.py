import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from recursos.utils.config import Config


class BasePage:
    FORM_UPLOAD = (By.ID, "formUpload")

    def __init__(self, driver: WebDriver, timeout: int | None = None) -> None:
        self.driver = driver
        self.timeout = timeout or Config.TIMEOUT
        self.wait = WebDriverWait(driver, self.timeout)

    def open(self, url: str) -> None:
        self.driver.get(url)

    def wait_visible(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(
        self, locator: tuple[str, str], timeout: int | None = None
    ) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    def wait_present(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_invisible(self, locator: tuple[str, str]) -> bool:
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def click(self, locator: tuple[str, str], dismiss: bool = True) -> None:
        self.safe_click(locator, dismiss=dismiss)

    def safe_click(self, locator: tuple[str, str], dismiss: bool = True) -> None:
        if dismiss:
            self.dismiss_blocking_modals()
        element = self.wait_clickable(locator)
        try:
            element.click()
        except Exception:
            self.js_click(locator)

    def js_click(self, locator: tuple[str, str]) -> None:
        element = self.wait_present(locator)
        self.execute_script("arguments[0].click();", element)

    def select_by_index(self, locator: tuple[str, str], index: int) -> None:
        element = self.wait_visible(locator)
        Select(element).select_by_index(index)

    def type_text(self, locator: tuple[str, str], text: str) -> None:
        element = self.wait_visible(locator)
        element.clear()
        element.send_keys(text)

    def upload_file(self, locator: tuple[str, str], file_path: str) -> None:
        self.wait_present(locator).send_keys(file_path)

    def is_visible(self, locator: tuple[str, str]) -> bool:
        try:
            self.wait_visible(locator)
            return True
        except Exception:
            return False

    def is_present(self, locator: tuple[str, str], timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def page_contains(self, locator: tuple[str, str], timeout: int | None = None) -> bool:
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def execute_script(self, script: str, *args) -> None:
        self.driver.execute_script(script, *args)

    def reload(self) -> None:
        self.driver.refresh()

    def press_escape(self, locator: tuple[str, str]) -> None:
        self.wait_visible(locator).send_keys(Keys.ESCAPE)

    def scroll_into_view(self, locator: tuple[str, str]) -> None:
        element = self.wait_present(locator)
        self.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def click_at_coordinates(self, locator: tuple[str, str], x: int, y: int) -> None:
        from selenium.webdriver.common.action_chains import ActionChains

        element = self.wait_visible(locator)
        ActionChains(self.driver).move_to_element_with_offset(
            element, x, y
        ).click().perform()

    def pause(self, seconds: float) -> None:
        time.sleep(seconds)

    def dismiss_blocking_modals(self) -> None:
        """Fecha modais de aviso/IA sem destruir modais de upload em aberto."""
        for selector in (
            "#modal-aviso-analizer .close",
            "#modal-aviso-analizer button[data-dismiss='modal']",
            "#modal-aviso-analizer button.close",
        ):
            for element in self.driver.find_elements(By.CSS_SELECTOR, selector):
                if element.is_displayed():
                    try:
                        element.click()
                    except Exception:
                        self.execute_script("arguments[0].click();", element)

        upload_aberto = self.is_present(self.FORM_UPLOAD, timeout=1)
        if not upload_aberto:
            for element in self.driver.find_elements(By.CSS_SELECTOR, ".modal-backdrop.in"):
                if element.is_displayed():
                    try:
                        element.click()
                    except Exception:
                        self.execute_script("arguments[0].click();", element)

    def dismiss_modals_if_present(self) -> None:
        """Alias mantido para compatibilidade."""
        self.dismiss_blocking_modals()

    def wait_for_document_loaded(self, loading_locator, canvas_locator) -> None:
        if self.is_present(loading_locator, timeout=10):
            try:
                self.wait_invisible(loading_locator)
            except Exception:
                pass
        self.wait_visible(canvas_locator)
